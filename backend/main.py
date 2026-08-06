# FastAPI app: CORS, session creation, and the single /chat endpoint that drives the agent pipeline.

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_pipeline
from session import get_session, new_session_id

load_dotenv()

app = FastAPI(title="North Star Support Bot API")


class ChatRequest(BaseModel):
    # Body shape expected by POST /chat.
    session_id: str
    message: str


# Allow the frontend origin(s) configured via ALLOWED_ORIGIN (comma-separated). Defaults to local Vite dev server.
origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ai_available(session):
    # Report whether the LLM is reachable for this session (lazy: set from real call outcomes).
    return session.get("ai_available", bool(os.getenv("GROQ_API_KEY")))


@app.get("/")
def root():
    # Simple health check for deployment platforms.
    return {"status": "ok"}


@app.post("/session/new")
def create_session():
    # Create a fresh in-memory session and return its id plus current AI availability.
    session_id = new_session_id()
    session = get_session(session_id)
    session["ai_available"] = bool(os.getenv("GROQ_API_KEY"))
    return {"session_id": session_id, "ai_available": session["ai_available"]}


@app.post("/chat")
def chat(req: ChatRequest):
    # Run the agent pipeline for one user message and return every bot bubble plus UI hints.
    # Each resolved intent emits its own bubble (replies array); the top-level reply/quick_replies
    # mirror the first bubble for backward compatibility.
    session = get_session(req.session_id)
    try:
        bubbles = run_pipeline(session, req.message)
        session["messages"].append(
            {"role": "assistant", "content": "\n\n".join(reply for reply, _ in bubbles)}
        )
        replies = [{"reply": reply, "quick_replies": buttons} for reply, buttons in bubbles]
        return {
            "reply": replies[0]["reply"],
            "quick_replies": replies[0]["quick_replies"],
            "replies": replies,
            "pending_slot": session.get("pending_slot"),
            "ai_available": _ai_available(session),
        }
    except Exception as exc:
        # Safety net for unexpected errors; keep the menu available so the chat stays usable.
        return {
            "reply": f"Sorry, I hit an unexpected error: {exc}. Please try again.",
            "quick_replies": ["Track Order", "Returns", "Product Advice", "Talk to Human"],
            "replies": [
                {
                    "reply": f"Sorry, I hit an unexpected error: {exc}. Please try again.",
                    "quick_replies": ["Track Order", "Returns", "Product Advice", "Talk to Human"],
                }
            ],
            "pending_slot": None,
            "ai_available": _ai_available(session),
        }
