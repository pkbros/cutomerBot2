import { useEffect, useRef, useState } from 'react'
import MessageBubble from './components/MessageBubble.jsx'
import QuickReplies from './components/QuickReplies.jsx'
import OrderForm from './components/OrderForm.jsx'
import { newSession, sendMessage } from './api.js'

const MAIN_MENU = ['Track Order', 'Returns', 'Product Advice', 'Talk to Human']
const WELCOME = 'Welcome to basecamp. How can I help you gear up today?'

// App: chat window shell — header, message log, quick replies, order form, and input box.
export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [wakingUp, setWakingUp] = useState(true)
  const chatRef = useRef(null)
  const sessionIdRef = useRef(null)

  // On load: create a session and show the welcome message with the 4 quick replies.
  useEffect(() => {
    async function init() {
      try {
        const id = await newSession()
        sessionIdRef.current = id
        setSessionId(id)
        setMessages([
          { id: 1, role: 'bot', text: WELCOME, quickReplies: MAIN_MENU, flow: null, stage: null },
        ])
      } catch (err) {
        setMessages([
          {
            id: 1,
            role: 'bot',
            text: 'Could not reach the backend. Make sure it is running and VITE_API_URL is correct.',
            quickReplies: [],
            flow: null,
            stage: null,
          },
        ])
      } finally {
        setWakingUp(false)
      }
    }
    init()
  }, [])

  // Keep the chat scrolled to the newest message.
  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [messages, loading])

  async function handleSend(text) {
    const trimmed = (text || '').trim()
    if (!trimmed || loading) return
    setInput('')
    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', text: trimmed }])
    setLoading(true)
    try {
      const res = await sendMessage(sessionIdRef.current, trimmed)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'bot',
          text: res.reply,
          quickReplies: res.quick_replies || [],
          flow: res.flow || null,
          stage: res.stage || null,
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'bot',
          text: 'Something went wrong talking to the bot. Please try again.',
          quickReplies: MAIN_MENU,
          flow: null,
          stage: null,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(e) {
    e.preventDefault()
    handleSend(input)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <svg className="brand-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 3 3 17h5l4-6 4 6h5L12 3z" />
          </svg>
          <div>
            <h1 className="brand-title">North Star Support Bot</h1>
            <div className="brand-status">
              <span className="status-dot" />
              <span>Online</span>
            </div>
          </div>
        </div>
        <button className="talk-human" type="button" onClick={() => handleSend('Talk to human')}>
          Talk to Human
        </button>
      </header>

      <main className="chat-area" ref={chatRef}>
        <div className="messages">
          {wakingUp && messages.length === 0 && (
            <div className="message-row bot">
              <div className="bubble bubble-bot waking">
                <p>Server is waking up, please wait...</p>
              </div>
            </div>
          )}
          {messages.map((m) => (
            <div key={m.id}>
              <MessageBubble message={m} />
              {m.role === 'bot' && m.quickReplies && m.quickReplies.length > 0 && (
                <QuickReplies options={m.quickReplies} onSelect={handleSend} />
              )}
              {m.role === 'bot' && m.flow === 'order_tracking' && m.stage === 'ask_order' && (
                <OrderForm onSelect={handleSend} />
              )}
            </div>
          ))}
          {loading && (
            <div className="message-row bot">
              <div className="bubble bubble-bot typing">
                <p>…</p>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <form className="input-bar" onSubmit={onSubmit}>
          <input
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            aria-label="Type your message"
          />
          <button className="send-btn" type="submit">
            Send
          </button>
        </form>
      </footer>
    </div>
  )
}
