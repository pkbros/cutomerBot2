# North Star Support Bot

## Updated system according to the review recieved

Repository: https://github.com/pkbros/cutomerBot2

Live Deployment: https://cutomerbot2-1.onrender.com/

---

## What changed since the last build

**Removed the LangGraph layer.** The previous build used a graph runner to orchestrate every step. That was overkill for a single conversational agent, so it is gone. The system is now small and easy to follow: an agent core, deterministic flow actions, and a session state dict.

**LLM-first intent detection.** One structured call to Llama 3.3 70B reads the user's message and returns the intents and the data (order number, activity, season). The model owns all understanding. There is no keyword matching, no phrase guessing, and no forced intents in front of it.

**Simplified the system.** No graph engine, no extra orchestrators, no duplicated logic. Buttons and typed messages share the same actions, so clicking and typing produce identical results.

**Graceful fallbacks everywhere.** Invalid order numbers re-prompt clearly instead of breaking. After two failures the bot offers a human handoff — never forced. If the AI is unreachable, buttons and known phrases still work and the chat shows a clear notice instead of failing.

**Compound requests answered as separate bubbles.** "Order 222 and returns and shipping" returns one bubble per answer, in order. If the first item fails, the rest wait until the current issue is resolved.

**Shipping Info is now a button.** Every main flow is reachable with clicks only: Track Order, Returns, Product Advice, Shipping Info, Talk to Human.

## A real run

```
User:    i need details of order 222 and returns and shipping policy.
Bot:     Order #222 is Processing. Ships in 24 hours
         (then) 30-day returns. Items must be unused. Original packaging required.
         (then) Standard shipping: 3-5 business days. Expedited shipping: 1-2 business days.

User:    what about order 555 and returns system.
Bot:     I couldn't find an order with number '555'. Please double-check and enter a
         valid order number, or go back to menu to restart.

User:    its 222
Bot:     Order #222 is Processing. Ships in 24 hours

User:    i need ideas on what to buy
Bot:     Happy to help you gear up. What activity are you preparing for?

User:    camping
Bot:     Got it. Will you be out in a particular season?

User:    yes in summer
Bot:     Based on that, I'd recommend checking out: Tents, Sleeping bags, Camp stoves.

User:    thanks
Bot:     Hey there! How can I help you gear up today?
```

The run above shows all of it: compound requests, per-intent bubbles, clean invalid-order handling, slot filling with validation, and natural language mixing with buttons throughout.