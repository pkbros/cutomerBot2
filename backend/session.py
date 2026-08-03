# In-memory session store keyed by session id. State resets on server restart (acceptable per PLAN.md).

import uuid

_sessions = {}


def new_session_id():
    # Generate a fresh unique session id for a new chat.
    return str(uuid.uuid4())


def get_session(session_id):
    # Return the state dict for a session, creating it on first use.
    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id": session_id,
            "messages": [],
            "current_flow": None,
            "stage": None,
            "order_number": None,
            "rec_answers": {},
            "unrecognized_count": 0,
        }
    return _sessions[session_id]
