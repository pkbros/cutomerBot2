// API helpers: talk to the FastAPI backend. Uses VITE_API_URL when set, else local dev backend.

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function newSession() {
  // Ask the backend for a fresh session id and the current AI availability.
  const res = await fetch(`${API_URL}/session/new`, { method: 'POST' })
  if (!res.ok) throw new Error(`Session request failed: ${res.status}`)
  return res.json()
}

export async function sendMessage(sessionId, message) {
  // Send one user message and return the bot's reply object.
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`)
  return res.json()
}
