# In-memory session store keyed by session id. State resets on server restart (acceptable per PLAN.md).

import uuid

_SESSIONS = {}


def new_session_id():
    # Generate a fresh unique session id for a new chat.
    return str(uuid.uuid4())


def _new_state(session_id):
    # Build the central conversation state: form, pending slot, intent queue, retries, availability.
    return {
        "session_id": session_id,
        "messages": [],
        "form": {"order_number": None, "activity": None, "season": None},
        "pending_slot": None,
        "intent_queue": [],
        "retries": {"order_number": 0, "activity": 0, "season": 0},
        "unrecognized": 0,
        "ai_available": True,
    }


def get_session(session_id):
    # Return the state dict for a session, creating it on first use.
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = _new_state(session_id)
    return _SESSIONS[session_id]
