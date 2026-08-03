# Recommendations node: asks 1-2 clarifying questions, then suggests products from the mock catalog.

from data import PRODUCT_CATEGORIES

# Quick-reply options shown at each step of the recommendation flow.
ACTIVITY_OPTIONS = ["Hiking", "Camping", "Cold weather"]
SEASON_OPTIONS = ["Summer", "Winter", "Year-round"]


def _map_activity_to_category(activity, season):
    # Map a free-text activity and season answer onto one of the catalog categories.
    activity_low = activity.lower()
    season_low = season.lower()
    if any(k in season_low for k in ("winter", "snow", "cold", "ski", "alpine")):
        return "cold_weather"
    if any(k in activity_low for k in ("hike", "trek", "trail", "walk", "backpack")):
        return "hiking"
    if any(k in activity_low for k in ("camp", "tent", "sleeping")):
        return "camping"
    if any(k in activity_low for k in ("cold", "winter", "snow", "ski")):
        return "cold_weather"
    return "hiking"


def run(state):
    # Walk the user through activity and season questions, then return a product suggestion.
    if state.get("current_flow") is None:
        state["current_flow"] = "recommendations"
        state["stage"] = "ask_activity"
        state["reply"] = "Happy to help you gear up. What activity are you preparing for?"
        state["quick_replies"] = ACTIVITY_OPTIONS
        return state

    if state.get("stage") == "ask_activity":
        # First question answered: store it and ask about season.
        state["rec_answers"]["activity"] = state.get("message", "")
        state["stage"] = "ask_season"
        state["reply"] = "Got it. Will you be out in a particular season?"
        state["quick_replies"] = SEASON_OPTIONS
        return state

    # Second question answered: map answers to a category and suggest products, then end the flow.
    activity = state["rec_answers"].get("activity", "")
    season = state.get("message", "")
    state["rec_answers"]["season"] = season
    category = _map_activity_to_category(activity, season)
    products = PRODUCT_CATEGORIES[category]
    state["reply"] = f"Based on that, I'd recommend checking out: {', '.join(products)}."
    state["quick_replies"] = ["Back to menu"]
    state["current_flow"] = None
    state["stage"] = "done"
    return state
