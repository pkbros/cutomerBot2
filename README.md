# North Star Support Bot

AI customer-support chatbot for a mock outdoor-gear e-commerce business. Built as an Upwork Talent Accelerator submission.

- **Backend:** FastAPI + Groq (Llama). An agent core classifies intent and extracts entities in one structured call; deterministic actions drive the flows; in-memory sessions.
- **Frontend:** Vite + React (JS), plain CSS, "Rugged Minimalism" design system (see `design/DESIGN.md`).
- **State:** in-memory only (central form dict), keyed by session id. Resets on server restart (acceptable for this project).
- **Deployment:** backend on Render, frontend on Vercel. Groq key lives only in Render env vars.

## Features

Four fully working flows, always-available buttons, and graceful degradation:

1. **Track Order** — inline order-number form (digits-only), looks up mock orders (`111`, `222`, `333`). Invalid numbers re-prompt with clear next steps; after 2 failures the bot offers a human handoff while you keep typing.
2. **Shipping Info** — "provide shipping information" / "how long does shipping take" answers directly with standard + expedited details (no order lookup).
3. **Returns** — the exact return policy text plus the returns link.
4. **Product Advice** — validates activity and season answers (free text or buttons), re-prompts on invalid input, then suggests products from the mock catalog.
5. **Talk to Human** — simulated live-agent handoff. Offered (never forced) after repeated failures, reachable any time from the header button.
6. **Fallback** — garbage like "where is my abc" gets a fallback reply with the main menu, not an order prompt.

Free text and buttons mix freely: everything a button does updates the same central state, so the AI always understands where the conversation stands. Compound requests ("order is 111, tell status, and the return policy") are answered one intent at a time in order.

## Project layout

```
backend/
  main.py                # FastAPI app, CORS, routes, ai_available flag
  agent.py               # LLM agent: prompt with form + queue + history, JSON call, guards
  actions.py             # deterministic flow functions (buttons, slot filling, canned replies)
  data.py                # mock orders, return policy, shipping info, product catalog
  session.py             # in-memory session store (central state)
  requirements.txt
  .env.example           # GROQ_API_KEY, ALLOWED_ORIGIN
frontend/
  src/
    App.jsx              # chat window, message log, input box, AI-availability handling
    components/          # MessageBubble, QuickReplies, OrderForm (digits-only)
    api.js               # fetch calls to backend
    styles.css
  index.html
  package.json
  vite.config.js
  .env.example           # VITE_API_URL
```

## Run locally

### Backend (terminal 1)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # set GROQ_API_KEY for full natural-language mode
uvicorn main:app --reload         # http://localhost:8000
```

`GROQ_API_KEY` powers free-text understanding (intent + entity extraction). Without a key the buttons still drive all flows, and free text returns the AI-unavailable notice instead of breaking.

### Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

CORS defaults to `http://localhost:5173`; set `ALLOWED_ORIGIN` in the backend if your frontend runs elsewhere.

## How to test

On the welcome screen, click the quick-reply buttons or type freely:

1. **Track Order** → type `111` (or `222` / `333`) in the inline form → see status. Try `999` → re-prompt; fail twice → human-handoff offer.
2. **Shipping info** → type `"provide shipping information"` → standard/expedited details directly.
3. **Returns** → read the policy text + returns link, then **Back to menu**.
4. **Product Advice** → pick Hiking / Camping / Cold weather, then a season. Type gibberish instead → re-prompt with the options; valid answers only after that.
5. **Talk to Human** (header button or quick reply) → simulated live agent message.
6. **Fallback** → type `"where is my abc"` → fallback reply + menu, never an order prompt.
7. **Compound** → `"order is 111, tell status. and the return policy"` → both answered in order.
8. **Mix** → click "Track Order", then type `"111"`; the AI continues with full context.

## Deployment checklist

- [ ] Backend on Render: build command `pip install -r requirements.txt`, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set `ALLOWED_ORIGIN` (your Vercel URL) and `GROQ_API_KEY`.
- [ ] Frontend on Vercel: framework Vite, set `VITE_API_URL` to the Render URL.
- [ ] Test the live Vercel link in an incognito window.
- [ ] Confirm all flows work on the live link, with and without the key.
- [ ] Record the 2–3 min demo video.

## Out of scope

No real payments, no real order database, no user accounts, no persistence across restarts, no support-hours/agent-photo/phone UI chrome.
