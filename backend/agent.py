# Agent core: one structured Groq call per free-text message (intent + entity extraction),
# backend guards, then deterministic action dispatch. Heuristic tiers run before the LLM.

import json
import os
import re

from groq import Groq

from actions import (
    BACK_BUTTON,
    MAIN_MENU,
    back_to_menu,
    extract_digits,
    fallback,
    greeting,
    handoff,
    recommendations_advance,
    resolve_order,
    returns,
    shipping_info,
    track_order,
    validate_activity,
    validate_season,
)
from data import ORDERS

# Exact-match words that always mean "back to main menu" (deterministic, no LLM).
MENU_WORDS = {"back to menu", "menu", "main menu", "start over", "reset", "go back"}

# First word of a message treated as a greeting -> friendly reply, no LLM.
GREETING_WORDS = {"hi", "hello", "hey", "howdy", "yo", "hiya", "thanks", "thank", "ty", "bye", "goodbye"}

# Exact button/command labels routed deterministically.
BUTTON_ACTIONS = {
    "track order": track_order,
    "returns": returns,
    "product advice": lambda s: recommendations_advance(s),
    "shipping info": shipping_info,
    "talk to human": handoff,
    "talk to a human": handoff,
}

# Containment phrases: the deterministic NLU used ONLY when the AI is unavailable (degraded
# mode). In the normal path, ALL free text goes to the LLM, which extracts intents + data.
PHRASE_ACTIONS = [
    ("product advice", lambda s: recommendations_advance(s)),
    ("shipping information", shipping_info),
    ("shipping details", shipping_info),
    ("shipping options", shipping_info),
    ("shipping speed", shipping_info),
    ("standard shipping", shipping_info),
    ("expedited shipping", shipping_info),
    ("shipping take", shipping_info),
    ("delivery time", shipping_info),
    ("how long does shipping", shipping_info),
    ("shipping info", shipping_info),
    ("talk to a human", handoff),
    ("talk to an agent", handoff),
    ("talk to human", handoff),
]
PHRASE_MAX_WORDS = 6

# Words signaling OTHER intents: when present, a message is never handled by a deterministic
# shortcut (slot fill, track-order). It goes to the LLM intact so compound requests survive.
NON_SLOT_WORDS = ("return", "refund", "policy", "ship", "recommend", "advice", "human", "agent")

# Nouns that make "order_tracking" plausible even without a number (belt-and-suspenders guard).
TRACK_NOUNS = (
    "order", "track", "package", "parcel", "status", "delivery", "shipping",
    "shipment", "arrive", "arriving",
)

VALID_INTENTS = {"order_tracking", "shipping_info", "returns", "recommendations", "handoff", "fallback"}

# System prompt: the LLM only classifies and extracts; it never writes final replies.
SYSTEM_PROMPT = (
    "You are the NLU core of an outdoor gear support chatbot. Classify the user's latest "
    "message and extract entities. Reply with ONLY a JSON object, no markdown, no extra words.\n"
    "JSON schema:\n"
    '{"intents": ["..."], "form_updates": {"order_number": null, "activity": null, "season": null}}\n'
    "intents is an ordered list from: order_tracking, shipping_info, returns, recommendations, "
    "handoff, fallback.\n"
    "- order_tracking: checking the status, location, or delivery of a specific order.\n"
    "- shipping_info: general questions about shipping speed or options (standard vs expedited), "
    "NOT about one specific order.\n"
    "- returns: return policy, refunds, exchanges, sending something back.\n"
    "- recommendations: product advice, gear suggestions, ideas on what to buy, picking gear or "
    "products for an activity or trip.\n"
    "- handoff: talking to a human, agent, or representative.\n"
    "- fallback: off-topic, unclear, gibberish, or anything else.\n"
    "Use multiple intents in order when the message asks for several things. Only include "
    "intents the user explicitly asked about — never add related or nearby intents. Prefer "
    "recommendations for any request about buying products or gear unless it is clearly about "
    "order status, returns, shipping, or a human agent.\n"
    "form_updates: order_number = the customer's order number as digits only, if clearly an order "
    "reference; activity is exactly one of hiking, camping, cold_weather; season is exactly one of "
    "summer, winter, year-round; use null when unknown.\n"
    "Always extract the order number into form_updates.order_number whenever the user mentions "
    "one anywhere in the message, even in compound requests.\n"
    "Examples:\n"
    "user: where is my abc -> {\"intents\": [\"fallback\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: provide shipping information -> {\"intents\": [\"shipping_info\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: how long does shipping take -> {\"intents\": [\"shipping_info\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: where is my order -> {\"intents\": [\"order_tracking\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: track order 333 -> {\"intents\": [\"order_tracking\"], \"form_updates\": {\"order_number\": \"333\", \"activity\": null, \"season\": null}}\n"
    "user: order is 111, tell status. and tell me about the return policy -> {\"intents\": [\"order_tracking\", \"returns\"], \"form_updates\": {\"order_number\": \"111\", \"activity\": null, \"season\": null}}\n"
    "user: about order 222 and shipping details -> {\"intents\": [\"order_tracking\", \"shipping_info\"], \"form_updates\": {\"order_number\": \"222\", \"activity\": null, \"season\": null}}\n"
    "user: tell me about order 111 and also about shipping -> {\"intents\": [\"order_tracking\", \"shipping_info\"], \"form_updates\": {\"order_number\": \"111\", \"activity\": null, \"season\": null}}\n"
    "user: some product advice -> {\"intents\": [\"recommendations\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: i need some ideas on the products i buy -> {\"intents\": [\"recommendations\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: give me gear suggestions for a trip -> {\"intents\": [\"recommendations\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: what boots should I get for camping in summer -> {\"intents\": [\"recommendations\"], \"form_updates\": {\"order_number\": null, \"activity\": \"camping\", \"season\": \"summer\"}}\n"
    "user: talk to a human -> {\"intents\": [\"handoff\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}\n"
    "user: hello -> {\"intents\": [\"fallback\"], \"form_updates\": {\"order_number\": null, \"activity\": null, \"season\": null}}"
)

AI_UNAVAILABLE_REPLY = (
    "Sorry, I can't reach the AI right now. Please use the buttons to navigate, or try typing "
    "again in a moment."
)

NO_NUMBER_REPLY = (
    "I didn't find an order number in that. Please type it as digits, e.g. 111, or use the "
    "Back to menu button."
)


def _llm_available(state):
    # Availability is lazy: set once from the key, flipped to False on any Groq failure.
    if not os.getenv("GROQ_API_KEY"):
        state["ai_available"] = False
    return state.get("ai_available", True)


def call_llm(state, message):
    # One structured NLU call with form + queue + history as context; None on any API failure.
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        context = {
            "current form": state.get("form"),
            "pending_slot": state.get("pending_slot"),
            "intent_queue": state.get("intent_queue"),
            "history": state.get("messages", [])[-8:],
            "user message": message,
        }
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(context, default=str)},
            ],
            temperature=0,
            max_tokens=256,
            response_format={"type": "json_object"},
        )
        raw = (response.choices[0].message.content or "").strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            return None
        return parsed
    except Exception:
        return None


def _guard_intents(state, message, parsed):
    # Whitelist intents, apply the no-number-no-noun order guard, and extract form updates.
    intents = [i for i in parsed.get("intents", []) if i in VALID_INTENTS]
    if not intents:
        return [], {}
    updates = {k: v for k, v in (parsed.get("form_updates") or {}).items() if v}
    if intents == ["order_tracking"] and not updates.get("order_number"):
        low = message.strip().lower()
        if not re.search(r"\d{3,}", message) and not any(n in low for n in TRACK_NOUNS):
            return ["fallback"], {}
    return intents, updates


def _execute_intent(state, intent, updates):
    # Run one intent's deterministic action; returns (reply, buttons, needs_input).
    # needs_input is True when the intent could not complete (slot needed or invalid data),
    # which stops the intent queue so later intents never run.
    if intent == "order_tracking":
        number = updates.get("order_number")
        if number:
            number = re.sub(r"\D", "", str(number))
            reply, buttons = resolve_order(state, number)
            return reply, buttons, number not in ORDERS
        return track_order(state) + (True,)
    if intent == "shipping_info":
        return shipping_info(state) + (False,)
    if intent == "returns":
        return returns(state) + (False,)
    if intent == "recommendations":
        return recommendations_advance(
            state, activity=updates.get("activity"), season=updates.get("season")
        ) + (False,)
    if intent == "handoff":
        return handoff(state) + (False,)
    return fallback(state) + (False,)


def _slot_stuck(state, intents):
    # True when the LLM could not move past the pending slot (fallback or same-flow without input).
    slot = state.get("pending_slot")
    if not slot:
        return False
    if slot == "order":
        return not intents or intents in (["order_tracking"], ["fallback"])
    return not intents or set(intents) <= {"recommendations", "fallback"}


def run_agent(state, message):
    # Free-text pipeline: LLM NLU -> guards -> sequential intent execution.
    # Returns a list of (reply, buttons) bubbles; one per resolved intent, in order.
    parsed = call_llm(state, message)
    if parsed is None:
        state["ai_available"] = False
        return [(AI_UNAVAILABLE_REPLY, MAIN_MENU)]
    intents, updates = _guard_intents(state, message, parsed)
    if _slot_stuck(state, intents):
        # A pending slot was answered with invalid input: re-prompt deterministically.
        slot = state.get("pending_slot")
        if slot == "order":
            return [(NO_NUMBER_REPLY, BACK_BUTTON)]
        if slot == "activity":
            return [recommendations_advance(state, activity=message)]
        return [recommendations_advance(state, season=message)]
    if not intents:
        return [fallback(state)]
    if intents != ["fallback"]:
        state["unrecognized"] = 0
    bubbles = []
    for intent in intents:
        reply, buttons, needs_input = _execute_intent(state, intent, updates)
        bubbles.append((reply, buttons))
        if needs_input:
            # The current intent needs more input (or failed): clear the queue and stop,
            # so the customer focuses on the current issue and later intents never run.
            state["intent_queue"] = []
            break
    return bubbles


def _degraded_nlu(state, message):
    # AI-unavailable NLU: containment phrases + deterministic track-order. Best effort only;
    # in the normal path ALL free text goes to the LLM (which owns intent + data extraction).
    low = (message or "").strip().lower()
    if len(low.split()) <= PHRASE_MAX_WORDS and not re.search(r"\d{3,}", message):
        for phrase, action in PHRASE_ACTIONS:
            if phrase in low:
                return [action(state)]
    if "track order" in low and not any(w in low for w in NON_SLOT_WORDS):
        number = extract_digits(message)
        if number:
            return [resolve_order(state, number)]
        return [track_order(state)]
    return [(AI_UNAVAILABLE_REPLY, MAIN_MENU)]


def run_pipeline(state, message):
    # Route one message: UI-level determinism (menu, greeting, buttons, pure-data slot fills),
    # then the LLM agent for ALL free text. Degraded NLU only when the AI is unavailable.
    # Always returns a list of (reply, buttons) bubbles.
    state["messages"].append({"role": "user", "content": message})

    low = (message or "").strip().lower()
    if not low:
        return [fallback(state)]

    if low in MENU_WORDS:
        return [back_to_menu(state)]

    first_word = low.split()[0].rstrip(",.!?")
    if first_word in GREETING_WORDS or any(w in low for w in ("thank", "thx", "cheers")):
        return [greeting(state)]

    if low in BUTTON_ACTIONS:
        return [BUTTON_ACTIONS[low](state)]

    slot = state.get("pending_slot")
    if slot == "order":
        number = extract_digits(message)
        # Deterministic slot fill for a pure number message. If the message also mentions
        # returns/shipping/etc., route it to the LLM intact so compound requests survive.
        if number and (not any(w in low for w in NON_SLOT_WORDS) or not _llm_available(state)):
            return [resolve_order(state, number)]
        if not _llm_available(state):
            return [(NO_NUMBER_REPLY, BACK_BUTTON)]

    if slot == "activity":
        key = validate_activity(message)
        if key and not any(w in low for w in NON_SLOT_WORDS):
            return [recommendations_advance(state, activity=key)]
        if not _llm_available(state):
            return [recommendations_advance(state, activity=message)]

    if slot == "season":
        key = validate_season(message)
        if key and not any(w in low for w in NON_SLOT_WORDS):
            return [recommendations_advance(state, season=key)]
        if not _llm_available(state):
            return [recommendations_advance(state, season=message)]

    if not _llm_available(state):
        return _degraded_nlu(state, message)

    return run_agent(state, message)
