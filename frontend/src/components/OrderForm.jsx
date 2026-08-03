import { useState } from 'react'

// OrderForm: inline numeric input shown during the order-tracking flow to avoid free-text ambiguity.

export default function OrderForm({ onSelect }) {
  const [value, setValue] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (value.trim()) onSelect(value.trim())
  }

  return (
    <form className="order-form" onSubmit={handleSubmit}>
      <input
        className="order-input"
        type="text"
        inputMode="numeric"
        placeholder="e.g. 111"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        aria-label="Order number"
      />
      <button className="order-submit" type="submit">
        Submit
      </button>
    </form>
  )
}
