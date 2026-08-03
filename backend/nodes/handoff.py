# Handoff node: simulated live-agent handoff, then offers a way back to the menu.

def run(state):
    # Send the simulated live-agent handoff message and end the flow.
    state["reply"] = (
        "You're now connected to a Live Agent (simulated). "
        "A specialist will pick this up shortly. Anything else in the meantime?"
    )
    state["quick_replies"] = ["Back to menu"]
    state["current_flow"] = None
    state["stage"] = "done"
    return state
