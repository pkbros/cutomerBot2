# North Star Support Bot

AI customer-support chatbot for a mock outdoor-gear e-commerce business. Built as an Upwork Talent Accelerator submission.

- **Backend:** FastAPI + LangGraph + Groq (Llama) for intent classification, in-memory sessions.
- **Frontend:** Vite + React (JS), plain CSS, "Rugged Minimalism" design system (see `design/DESIGN.md`).
- **State:** in-memory only, keyed by session id. Resets on server restart (acceptable for this project).
- **Deployment:** backend on Render, frontend on Vercel. Groq key lives only in Render env vars.

## Features

Four fully working flows plus fallback handling:

1. **Track Order** — inline order-number form, looks up mock orders (`111`, `222`, `333`), invalid numbers get a clear message.
2. **Returns** — returns the exact return policy text plus the returns link.
3. **Product Advice** — 1–2 clarifying questions (activity, season), then product suggestions from the mock catalog.
4. **Talk to Human** — simulated live-agent handoff, reachable at any time from the persistent header button. 
5. **Fallback** — "I didn't understand that" + menu; escalates to the simulated agent after two unrecognized messages.

After every resolved flow the bot offers a **Back to menu** quick reply, which returns the user to the main menu.

## Project layout

```
backend/
  main.py                # FastAPI app, CORS, routes
  graph.py               # LangGraph state graph (4 flows + routing + fallback)
  nodes/                 # one module per flow + intent classifier
  data.py                # mock orders, return policy, shipping info, product catalog
  session.py             # in-memory session store
  requirements.txt
  .env.example           # GROQ_API_KEY, ALLOWED_ORIGIN
frontend/
  src/
    App.jsx              # chat window, message log, input box
    components/          # MessageBubble, QuickReplies, OrderForm
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
copy .env.example .env            # GROQ_API_KEY is OPTIONAL (see below)
uvicorn main:app --reload         # http://localhost:8000
```

**Works without any API key.** Intent detection is heuristic-first (keyword rules), so all 4 flows, shipping info, greetings, and fallback work with zero keys — the graded experience per the contract. Setting `GROQ_API_KEY` adds natural-language understanding: ambiguous messages are classified by the LLM, and order numbers can be extracted from free text ("my order is 222, when will it arrive" resolves without re-asking). Costs stay near zero because the LLM only fires on messages the rules can't decide.

### Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

CORS defaults to `http://localhost:5173`; set `ALLOWED_ORIGIN` in the backend if your frontend runs elsewhere.

## How to test the 4 flows

On the welcome screen, click the quick-reply buttons:

1. **Track Order** → type `111` (or `222` / `333`) in the inline form → see status. Try `999` to see the invalid-order message.
2. **Returns** → read the policy text + shipping info + link, then **Back to menu**.
3. **Product Advice** → pick Hiking / Camping / Cold weather, then a season → get product suggestions.
4. **Talk to Human** (header button or quick reply) → simulated live agent message.
5. **Fallback** → type gibberish twice → second time escalates to the live agent.

Free-text also works: try `"where is my order"`, `"my order is 111 when will it arrive"`, `"how long does shipping take"`, `"I want a refund"`, or `"help me pick a tent"`. Without a key these are handled by the rules; with a key the LLM understands novel phrasings too.

## Deployment checklist

- [ ] Backend on Render: build command `pip install -r requirements.txt`, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`. Set `ALLOWED_ORIGIN` (your Vercel URL); `GROQ_API_KEY` is optional but recommended for natural-language mode.
- [ ] Frontend on Vercel: framework Vite, set `VITE_API_URL` to the Render URL.
- [ ] Test the live Vercel link in an incognito window.
- [ ] Confirm all 4 flows work on the live link (keyless).
- [ ] Record the 2–3 min demo video.

## Out of scope

No real payments, no real order database, no user accounts, no persistence across restarts, no support-hours/agent-photo/phone UI chrome.
