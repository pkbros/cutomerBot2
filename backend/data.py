# Mock data used by every flow. Keep this exact per PLAN.md — do not invent order numbers or change policy text.

# Mock order records keyed by order number.
ORDERS = {
    "111": {"status": "Shipped", "detail": "Arriving tomorrow"},
    "222": {"status": "Processing", "detail": "Ships in 24 hours"},
    "333": {"status": "Delivered", "detail": "Ask if there's anything else needed"},
}

# Any order number not in ORDERS is treated as invalid.

# Return policy text and mock returns link.
RETURN_POLICY = "30-day returns.\nItems must be unused.\nOriginal packaging required."
RETURNS_LINK = "https://example.com/returns"  # placeholder, mock only

# Shipping speed options shown to the user when relevant.
SHIPPING = {
    "standard": "3-5 business days",
    "expedited": "1-2 business days",
}

# Small invented catalog for the recommendation flow (not in contract, needed to make the flow work).
PRODUCT_CATEGORIES = {
    "hiking": ["Hiking boots", "Trekking poles", "Daypacks"],
    "camping": ["Tents", "Sleeping bags", "Camp stoves"],
    "cold_weather": ["Insulated jackets", "Thermal layers", "Gloves"],
}
