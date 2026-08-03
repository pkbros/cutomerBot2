// QuickReplies: row of clickable suggestion buttons that send their label as a message.

export default function QuickReplies({ options, onSelect }) {
  return (
    <div className="quick-replies">
      {options.map((opt) => (
        <button key={opt} className="quick-reply" type="button" onClick={() => onSelect(opt)}>
          {opt}
        </button>
      ))}
    </div>
  )
}
