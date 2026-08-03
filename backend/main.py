# FastAPI app: CORS, session creation, and the single /chat endpoint that drives the LangGraph flow.

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph import run_graph
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


@app.get("/")
def root():
    # Simple health check for deployment platforms.
    return {"status": "ok"}


@app.post("/session/new")
def create_session():
    # Create a fresh in-memory session and return its id.
    session_id = new_session_id()
    get_session(session_id)
    return {"session_id": session_id}


@app.post("/chat")
def chat(req: ChatRequest):
    # Run the conversation graph for one user message and return the bot reply plus quick replies.
    session = get_session(req.session_id)
    try:
        result = run_graph(session, req.message)
    except Exception as exc:
        # Safety net for unexpected errors; keep the menu available so the chat stays usable.
        return {
            "reply": f"Sorry, I hit an unexpected error: {exc}. Please try again.",
            "quick_replies": ["Track Order", "Returns", "Product Advice", "Talk to Human"],
            "flow": None,
            "stage": None,
        }
    return {
        "reply": result.get("reply", ""),
        "quick_replies": result.get("quick_replies", []),
        "flow": result.get("current_flow"),
        "stage": result.get("stage"),
    }
