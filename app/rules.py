# scam_text_api/app/rules.py

GREETINGS = {"hi", "hello", "hii", "helo", "hey", "how are you", "ok", "okay", "thanks", "thank you","how are you?","how are you"}
MIN_SAFE_LENGTH = 15  # Messages shorter than this are less likely to be complex scams

def apply_rules(text: str) -> tuple[str, float] | None:
    """
    Applies rule-based overrides to the input text.
    Returns (label, confidence) if a rule is triggered, otherwise None.
    """
    normalized_text = text.lower().strip()

    # Rule-based override: Greetings
    if normalized_text in GREETINGS:
        return "SAFE", 0.99

    # Rule-based override: Single-word or very short messages
    # This rule is for non-greeting short messages, e.g., "cool", "nope", "yeah"
    # Or messages that are too short to be meaningful scams
    if len(normalized_text.split()) <= 3 or len(normalized_text) < MIN_SAFE_LENGTH:
        # Check if it's potentially a scam based on common scam keywords (optional, for more robustness)
        # For now, default short messages to SAFE
        return "SAFE", 0.98

    return None
