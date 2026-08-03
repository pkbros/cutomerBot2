# Intent classifier. Layered approach: cheap keyword rules first (works with NO API key),
# then Groq (Llama) only for ambiguous messages when a key is present. Fully deterministic keyless.

import os

from groq import Groq

# System prompt that tells the model exactly which intent labels are valid (key-mode only).
SYSTEM_PROMPT = (
    "You are an intent classifier for an outdoor gear support chatbot. "
    "Classify the user's latest message into exactly one of these intents and "
    "reply with ONLY the label, no punctuation, no extra words.\n"
    "Intents:\n"
    "- order_tracking: user wants to check the status or delivery of an order, or ask about shipping.\n"
    "- returns: user asks about returns, refunds, exchanges, or the return policy.\n"
    "- recommendations: user asks for product advice or gear recommendations.\n"
    "- handoff: user asks to talk to a human, agent, or representative.\n"
    "- fallback: anything else, unclear, greeting, or off-topic.\n"
    "Examples:\n"
    "user: where is my package -> order_tracking\n"
    "user: can I return this jacket -> returns\n"
    "user: what boots should I get -> recommendations\n"
    "user: I need a real person -> handoff\n"
    "user: hello -> fallback"
)

VALID_INTENTS = {"order_tracking", "returns", "recommendations", "handoff", "fallback"}

# Exact-match words that always mean "back to main menu" (handled before any classification).
MENU_WORDS = {"back to menu", "menu", "main menu", "start over", "reset", "go back"}

# First word of a message treated as a greeting -> friendly reply, no classifier needed.
GREETING_WORDS = {"hi", "hello", "hey", "howdy", "yo", "hiya", "thanks", "thank", "ty", "bye", "goodbye"}

# Keyword tiers checked in precedence order; the first tier that matches wins.
# Order matters: handoff > returns > order > recommendations.
HANDOFF_KEYWORDS = [
    "agent", "human", "person", "representative", "live agent", "customer service",
    "support team", "talk to a", "speak to",
]
RETURNS_KEYWORDS = ["return", "refund", "exchange", "policy", "money back", "send back"]
ORDER_KEYWORDS = [
    "order", "track", "package", "parcel", "status", "shipping", "shipment",
    "delivery", "delivered", "arrive", "arriving", "when will", "where is my",
]
RECOMMENDATION_KEYWORDS = [
    "recommend", "advice", "suggest", "gear", "boots", "tent", "jacket",
    "sleeping bag", "choose", "pick", "what should i", "help me", "product",
]


def heuristic_classify(message):
    # Rule-based intent detection; returns None when no rule matches confidently.
    m = message.strip().lower()
    if any(k in m for k in HANDOFF_KEYWORDS):
        return "handoff"
    if any(k in m for k in RETURNS_KEYWORDS):
        return "returns"
    if any(k in m for k in ORDER_KEYWORDS):
        return "order_tracking"
    if any(k in m for k in RECOMMENDATION_KEYWORDS):
        return "recommendations"
    return None


def classify_intent(history, message):
    # LLM intent classification; degrades to fallback when no key is set or the call fails.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "fallback"
    try:
        client = Groq(api_key=api_key)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history[-8:])
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=messages,
            temperature=0,
            max_tokens=16,
        )
        label = (response.choices[0].message.content or "").strip().lower()
        return label if label in VALID_INTENTS else "fallback"
    except Exception:
        # Never crash the chat because Groq is unreachable; fall back gracefully.
        return "fallback"


def run(state):
    # Entry node: menu reset, greetings, then keyword rules, then LLM only if needed and available.
    message = state.get("message", "")
    low = message.strip().lower()

    if low in MENU_WORDS:
        state["reply"] = "You're back at the main menu. How can I help you?"
        state["quick_replies"] = ["Track Order", "Returns", "Product Advice", "Talk to Human"]
        state["current_flow"] = None
        state["stage"] = None
        state["intent"] = "menu"
        return state

    first_word = low.split()[0].rstrip(",.!?") if low.split() else ""
    if first_word in GREETING_WORDS:
        state["reply"] = "Hey there! How can I help you gear up today?"
        state["quick_replies"] = ["Track Order", "Returns", "Product Advice", "Talk to Human"]
        state["current_flow"] = None
        state["stage"] = None
        state["intent"] = "menu"
        return state

    intent = heuristic_classify(message)
    if intent is None and os.getenv("GROQ_API_KEY"):
        intent = classify_intent(state.get("messages", []), message)

    state["intent"] = intent or "fallback"
    if state["intent"] != "fallback":
        state["unrecognized_count"] = 0
    return state
