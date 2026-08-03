# Returns node: returns the exact policy text, shipping info, and the returns link, then ends the flow.

from data import RETURN_POLICY, RETURNS_LINK, SHIPPING


def run(state):
    # Reply with the exact return policy, the shipping options, and the mock returns link.
    state["reply"] = (
        f"{RETURN_POLICY} "
        f"Shipping: Standard {SHIPPING['standard']}, Expedited {SHIPPING['expedited']}. "
        f"You can start a return here: {RETURNS_LINK}"
    )
    state["quick_replies"] = ["Back to menu"]
    state["current_flow"] = None
    state["stage"] = "done"
    return state
