import { useState } from 'react'

// OrderForm: inline digits-only input shown while the order slot is being filled (pending_slot=order).

export default function OrderForm({ onSelect }) {
  const [value, setValue] = useState('')

  function handleChange(e) {
    // Accept digits only so the free-text ambiguity can never happen here.
    setValue(e.target.value.replace(/\D/g, ''))
  }

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
        pattern="\d*"
        placeholder="e.g. 111"
        value={value}
        onChange={handleChange}
        aria-label="Order number"
      />
      <button className="order-submit" type="submit">
        Submit
      </button>
    </form>
  )
}
