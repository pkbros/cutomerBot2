# Order tracking node. Slot-filling pattern: never guess an order number from unconstrained text.
# Keyless: ask for the number, then trust the prompted reply. Key-mode: let the LLM extract it.

import os
import re

from groq import Groq

from data import ORDERS, SHIPPING

# Matches a plausible order number: any 3+ digit run, but not a quantity/duration like "100 days".
DIGIT_RUN = re.compile(
    r"\d{3,}(?!\s*(?:days?|hours?|weeks?|months?|years?|minutes?|seconds?|dollars?|"
    r"percent|%|items?|pieces?|left|remaining|overdue|late|due|orders?)\b)"
)

# Phrases that are really about shipping speed/options, not a specific order.
SHIPPING_PHRASES = [
    "how long", "delivery time", "shipping time", "how many days", "standard shipping",
    "expedited", "shipping option", "shipping speed", "take to arrive", "take to ship",
]


def is_shipping_question(message):
    # True when the message asks about shipping speed/options rather than a specific order.
    m = message.strip().lower()
    return any(p in m for p in SHIPPING_PHRASES)


def extract_digits(text):
    # Pull the first 3+ digit run out of text (safe only after we explicitly asked for the order number).
    match = DIGIT_RUN.search(text)
    return match.group(0) if match else None


def extract_order_number_llm(message, history):
    # Ask Groq to extract an order number from free text; returns digits or None. Degrades gracefully.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the customer's order number from their message. "
                        "Reply with ONLY the digits, or NONE if there is no order number."
                    ),
                },
                *history[-8:],
                {"role": "user", "content": message},
            ],
            temperature=0,
            max_tokens=8,
        )
        label = (response.choices[0].message.content or "").strip().lower()
        match = DIGIT_RUN.search(label)
        return match.group(0) if match else None
    except Exception:
        return None


def _resolve(number):
    # Look up an order number and build the status (or not-found) reply.
    order = ORDERS.get(number)
    if order:
        if order["status"] == "Delivered":
            return f"Order #{number} is Delivered. Is there anything else I can help you with?"
        return f"Order #{number} is {order['status']}. {order['detail']}"
    return (
        f"I couldn't find an order with number '{number}'. "
        "Please double-check the number and try again from the main menu."
    )


def run(state):
    # Flow entry: answer shipping questions, or resolve via LLM-extracted number (key mode),
    # otherwise ask for the order number.
    if state.get("current_flow") is None:
        message = state.get("message", "")

        if is_shipping_question(message):
            state["reply"] = (
                f"Standard shipping: {SHIPPING['standard']}. "
                f"Expedited shipping: {SHIPPING['expedited']}."
            )
            state["quick_replies"] = ["Back to menu"]
            state["current_flow"] = None
            state["stage"] = "done"
            return state

        # Only bother the LLM when the text could plausibly contain a number.
        if DIGIT_RUN.search(message):
            number = extract_order_number_llm(message, state.get("messages", []))
            if number:
                state["reply"] = _resolve(number)
                state["quick_replies"] = ["Back to menu"]
                state["current_flow"] = None
                state["stage"] = "done"
                return state

        state["current_flow"] = "order_tracking"
        state["stage"] = "ask_order"
        state["reply"] = "Please enter your order number so I can look it up."
        state["quick_replies"] = ["Back to menu"]
        return state

    # ask_order stage: the user was prompted, so treat their reply as the order number.
    number = extract_digits(state.get("message", ""))
    if not number:
        state["reply"] = "I didn't find an order number in that. Please type it as digits, e.g. 111."
        state["quick_replies"] = ["Back to menu"]
        return state

    state["order_number"] = number
    state["reply"] = _resolve(number)
    state["quick_replies"] = ["Back to menu"]
    state["current_flow"] = None
    state["stage"] = "done"
    return state
