// MessageBubble: renders a single bot or user chat bubble with the two-tone scheme.

export default function MessageBubble({ message }) {
  const isBot = message.role === 'bot'
  return (
    <div className={`message-row ${isBot ? 'bot' : 'user'}`}>
      <div className={`bubble ${isBot ? 'bubble-bot' : 'bubble-user'}`}>
        <p>{message.text}</p>
      </div>
    </div>
  )
}
