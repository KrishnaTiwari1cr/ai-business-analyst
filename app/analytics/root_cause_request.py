"""Parse root-cause questions into shared, UI-independent metadata."""


def parse_root_cause_request(question: str) -> dict[str, str]:
    """Return the requested driver focus and revenue direction."""

    text = question.lower()

    if any(term in text for term in ("product", "sku", "item")):
        focus = "products"
    elif any(term in text for term in ("categor", "segment")):
        focus = "categories"
    else:
        focus = "overall"

    if any(term in text for term in ("increase", "increased", "grew", "growth", "gain")):
        direction = "increase"
    elif any(term in text for term in ("drop", "decline", "decrease", "decreased", "fell", "loss")):
        direction = "decline"
    else:
        direction = "change"

    return {"focus": focus, "direction": direction}
