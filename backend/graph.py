# LangGraph state graph: routes each message through intent classification and the 4 flows.
# After a flow finishes (stage == "done") current_flow resets so the next message re-enters intent_router.

from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from nodes import handoff, intent_router, order_tracking, recommendations, returns
from nodes.intent_router import GREETING_WORDS, MENU_WORDS, heuristic_classify

# Intent labels that map 1:1 onto a flow node (mirrors intent_decider's routing table).
FLOW_INTENTS = {
    "order_tracking": "order_tracking",
    "returns": "returns",
    "recommendations": "recommendations",
    "handoff": "handoff",
}


class BotState(TypedDict, total=False):
    # Conversation state carried between graph invocations.
    session_id: str
    message: str
    messages: list
    current_flow: Optional[str]
    stage: Optional[str]
    order_number: Optional[str]
    rec_answers: dict
    unrecognized_count: int
    intent: Optional[str]
    reply: str
    quick_replies: list


def entry_decider(state):
    # Send the message to the active flow node while one is mid-flight, UNLESS it starts a
    # new intent of its own (greeting, or a different flow like "i want to return" during
    # recommendations) — those are re-routed through the intent router to interrupt and restart.
    # "Back to menu" is always routed to the router so it resets to the main menu.
    flow = state.get("current_flow")
    message = (state.get("message") or "").strip().lower()
    if not flow or message in MENU_WORDS:
        return "intent_router"

    first_word = message.split()[0].rstrip(",.!?") if message.split() else ""
    if first_word in GREETING_WORDS:
        return "intent_router"

    intent = heuristic_classify(message)
    if intent is not None and FLOW_INTENTS.get(intent) != flow:
        return "intent_router"

    return flow


def intent_decider(state):
    # Route the classified intent to its flow node (or end on menu / fall back on unknown).
    intent = state.get("intent")
    if intent == "menu":
        return "end"
    if intent in {"order_tracking", "returns", "recommendations", "handoff"}:
        return intent
    return "fallback"


def fallback_node(state):
    # Show the "I didn't understand" reply plus the menu options; escalate to handoff after repeats.
    state["unrecognized_count"] = state.get("unrecognized_count", 0) + 1
    state["current_flow"] = None
    state["stage"] = "done"
    if state["unrecognized_count"] < 2:
        state["reply"] = "I didn't understand that. Here are a few things I can help with:"
        state["quick_replies"] = ["Track Order", "Returns", "Product Advice", "Talk to Human"]
    return state


def fallback_decider(state):
    # Escalate to the simulated live agent after two consecutive unrecognized messages.
    return "handoff" if state.get("unrecognized_count", 0) >= 2 else "end"


def build_graph():
    # Assemble the state graph with all nodes and conditional routing edges.
    graph = StateGraph(BotState)

    graph.add_node("intent_router", intent_router.run)
    graph.add_node("order_tracking", order_tracking.run)
    graph.add_node("returns", returns.run)
    graph.add_node("recommendations", recommendations.run)
    graph.add_node("handoff", handoff.run)
    graph.add_node("fallback", fallback_node)

    graph.add_conditional_edges(
        START,
        entry_decider,
        {
            "intent_router": "intent_router",
            "order_tracking": "order_tracking",
            "returns": "returns",
            "recommendations": "recommendations",
            "handoff": "handoff",
        },
    )
    graph.add_conditional_edges(
        "intent_router",
        intent_decider,
        {
            "order_tracking": "order_tracking",
            "returns": "returns",
            "recommendations": "recommendations",
            "handoff": "handoff",
            "fallback": "fallback",
            "end": END,
        },
    )
    graph.add_conditional_edges("fallback", fallback_decider, {"handoff": "handoff", "end": END})

    for node in ("order_tracking", "returns", "recommendations", "handoff"):
        graph.add_edge(node, END)

    return graph.compile()


compiled_graph = build_graph()


def run_graph(session, message):
    # Run one graph step for a message, persist updated state back into the session store, and return the result.
    state_in = dict(session)
    state_in["message"] = message
    state_in["messages"] = list(session.get("messages", [])) + [{"role": "user", "content": message}]

    result = compiled_graph.invoke(state_in)

    assistant_text = result.get("reply", "")
    result["messages"] = result.get("messages", []) + [{"role": "assistant", "content": assistant_text}]
    session.clear()
    session.update(result)
    return result
