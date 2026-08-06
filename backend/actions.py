# Deterministic flow actions. Every function mutates the central state and returns (reply, buttons).
# These serve both the button path (exact label clicks) and the agent path (after LLM validation).

import re

from data import ORDERS, PRODUCT_CATEGORIES, RETURN_POLICY, RETURNS_LINK, SHIPPING

MAIN_MENU = ["Track Order", "Returns", "Product Advice", "Talk to Human"]
ACTIVITY_BUTTONS = ["Hiking", "Camping", "Cold weather"]
SEASON_BUTTONS = ["Summer", "Winter", "Year-round"]
BACK_BUTTON = ["Back to menu"]
HANDOFF_BUTTONS = ["Talk to human", "Back to menu"]

# Digits-only order number candidate; rejects quantity/duration phrases like "100 days".
DIGIT_RUN = re.compile(
    r"\d{3,}(?!\s*(?:days?|hours?|weeks?|months?|years?|minutes?|seconds?|dollars?|"
    r"percent|%|items?|pieces?|left|remaining|overdue|late|due|orders?)\b)"
)

# Keyword maps used to validate free-text activity / season answers against the closed enum sets.
ACTIVITY_KEYWORDS = {
    "hiking": ("hike", "trek", "trail", "walk", "backpack"),
    "camping": ("camp", "tent", "sleeping", "stove"),
    "cold_weather": ("cold", "winter", "snow", "ski", "alpine", "ice", "snowboard"),
}
SEASON_KEYWORDS = {
    "summer": ("summer", "spring", "july", "june", "august", "warm", "hot", "sunny"),
    "winter": ("winter", "snow", "ski", "january", "december", "february", "cold"),
    "year-round": ("year", "anytime", "all seasons", "year-round", "always"),
}
ACTIVITY_LABELS = {"hiking": "hiking", "camping": "camping", "cold_weather": "cold weather"}
SEASON_LABELS = {"summer": "summer", "winter": "winter", "year-round": "year-round"}


def _reset(state):
    # Clear the form, pending slot, intent queue, and retry counters (full menu reset).
    state["form"] = {"order_number": None, "activity": None, "season": None}
    state["pending_slot"] = None
    state["intent_queue"] = []
    state["retries"] = {"order_number": 0, "activity": 0, "season": 0}
    state["unrecognized"] = 0


def welcome(state):
    # Fresh session greeting with the main menu buttons.
    _reset(state)
    return ("Welcome to basecamp. How can I help you gear up today?", MAIN_MENU)


def back_to_menu(state):
    # Reset everything and show the main menu.
    _reset(state)
    return ("You're back at the main menu. How can I help you?", MAIN_MENU)


def greeting(state):
    # Friendly reply for a greeting word, with the main menu buttons.
    _reset(state)
    return ("Hey there! How can I help you gear up today?", MAIN_MENU)


def track_order(state):
    # Start the order-tracking slot: ask for the order number (OrderForm renders on pending_slot=order).
    state["pending_slot"] = "order"
    return ("Please enter your order number so I can look it up. For example: 111.", BACK_BUTTON)


def _order_reply(number):
    # Build the exact status reply for a known order number.
    order = ORDERS[number]
    if order["status"] == "Delivered":
        return f"Order #{number} is Delivered. Is there anything else I can help you with?"
    return f"Order #{number} is {order['status']}. {order['detail']}"


def resolve_order(state, number):
    # Look up an order number; valid -> status, invalid -> re-prompt with retry count and handoff offer.
    if number in ORDERS:
        state["form"]["order_number"] = number
        state["pending_slot"] = None
        state["retries"]["order_number"] = 0
        state["unrecognized"] = 0
        return (_order_reply(number), BACK_BUTTON)
    state["retries"]["order_number"] += 1
    state["pending_slot"] = "order"
    if state["retries"]["order_number"] >= 2:
        return (
            f"I still couldn't find an order matching '{number}'. Would you like to talk to a "
            "human, or keep trying with a valid order number?",
            HANDOFF_BUTTONS,
        )
    return (
        f"I couldn't find an order with number '{number}'. Please double-check and enter a valid "
        "order number (e.g. 111, 222, 333), or type Back to menu.",
        BACK_BUTTON,
    )


def extract_digits(text):
    # Pull the first 3+ digit run out of text (quantity/duration phrases excluded).
    match = DIGIT_RUN.search(text)
    return match.group(0) if match else None


def shipping_info(state):
    # One-shot: show standard and expedited shipping details directly (no order lookup).
    state["pending_slot"] = None
    state["unrecognized"] = 0
    return (
        f"Standard shipping: {SHIPPING['standard']}. "
        f"Expedited shipping: {SHIPPING['expedited']}.",
        BACK_BUTTON,
    )


def returns(state):
    # One-shot: return the exact policy text and the returns link (shipping has its own intent).
    state["pending_slot"] = None
    state["unrecognized"] = 0
    reply = f"{RETURN_POLICY}\nYou can start a return here: {RETURNS_LINK}"
    return (reply, BACK_BUTTON)


def _match_enum(t, labels, keywords):
    # Match text against enum ids, button labels, then keyword sets; None when unrecognized.
    if t in labels:
        return t
    for key, label in labels.items():
        if label == t:
            return key
    for key, words in keywords.items():
        if any(w in t for w in words):
            return key
    return None


def validate_activity(text):
    # Map free text or button label onto the activity enum; None when unrecognized.
    return _match_enum(text.strip().lower(), ACTIVITY_LABELS, ACTIVITY_KEYWORDS)


def validate_season(text):
    # Map free text or button label onto the season enum; None when unrecognized.
    return _match_enum(text.strip().lower(), SEASON_LABELS, SEASON_KEYWORDS)


def _category(activity, season):
    # Map validated activity + season onto a product category (winter/snow overrides to cold weather).
    if any(k in season for k in ("winter", "snow")):
        return "cold_weather"
    return activity if activity in PRODUCT_CATEGORIES else "hiking"


def recommendations_advance(state, activity=None, season=None):
    # Slot-fill activity and/or season; re-prompt on invalid input; recommend only when both are valid.
    if activity is not None:
        key = validate_activity(activity)
        if not key:
            state["pending_slot"] = "activity"
            state["retries"]["activity"] += 1
            if state["retries"]["activity"] >= 2:
                return (
                    "I'm still not sure what activity you meant. Pick Hiking, Camping, or Cold "
                    "weather, or talk to a human?",
                    ACTIVITY_BUTTONS + HANDOFF_BUTTONS,
                )
            return (
                "That doesn't look like a recognized activity. Please pick Hiking, Camping, or "
                "Cold weather.",
                ACTIVITY_BUTTONS,
            )
        state["form"]["activity"] = key
        state["retries"]["activity"] = 0

    if season is not None:
        key = validate_season(season)
        if not key:
            state["pending_slot"] = "season"
            state["retries"]["season"] += 1
            if state["retries"]["season"] >= 2:
                return (
                    "I'm still not sure about the season. Pick Summer, Winter, or Year-round, or "
                    "talk to a human?",
                    SEASON_BUTTONS + HANDOFF_BUTTONS,
                )
            return (
                "That doesn't look like a recognized season. Please pick Summer, Winter, or "
                "Year-round.",
                SEASON_BUTTONS,
            )
        state["form"]["season"] = key
        state["retries"]["season"] = 0

    if state["form"]["activity"] and state["form"]["season"]:
        state["pending_slot"] = None
        state["unrecognized"] = 0
        category = _category(state["form"]["activity"], state["form"]["season"])
        products = PRODUCT_CATEGORIES[category]
        return (f"Based on that, I'd recommend checking out: {', '.join(products)}.", BACK_BUTTON)
    if not state["form"]["activity"]:
        state["pending_slot"] = "activity"
        return ("Happy to help you gear up. What activity are you preparing for?", ACTIVITY_BUTTONS)
    state["pending_slot"] = "season"
    return ("Got it. Will you be out in a particular season?", SEASON_BUTTONS)


def handoff(state):
    # One-shot: simulated live-agent handoff with a way back to the menu.
    state["pending_slot"] = None
    state["unrecognized"] = 0
    return (
        "You're now connected to a Live Agent (simulated). "
        "A specialist will pick this up shortly. Anything else in the meantime?",
        BACK_BUTTON,
    )


def fallback(state):
    # Unrecognized message: menu buttons, escalating to a handoff offer after 2 misses.
    state["unrecognized"] = state.get("unrecognized", 0) + 1
    if state["unrecognized"] >= 2:
        return (
            "I'm not sure I understood that. Would you like to talk to a human instead, or pick "
            "an option below?",
            MAIN_MENU + ["Talk to human"],
        )
    return ("I didn't understand that. Here are a few things I can help with:", MAIN_MENU)
