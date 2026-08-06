// QuickReplies: row of clickable suggestion buttons that send their label as a message.
// Duplicates (case-insensitive) are dropped so the button row never looks confusing.

export default function QuickReplies({ options, onSelect }) {
  const seen = new Set()
  const clean = (options || []).filter((opt) => {
    const key = String(opt).trim().toLowerCase()
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
  return (
    <div className="quick-replies">
      {clean.map((opt) => (
        <button key={opt} className="quick-reply" type="button" onClick={() => onSelect(opt)}>
          {opt}
        </button>
      ))}
    </div>
  )
}
