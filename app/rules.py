# scam_text_api/app/rules.py

GREETINGS = {"hi", "hello", "hii", "helo", "hey", "how are you", "ok", "okay", "thanks", "thank you","how are you?","how are you"
             ,"Hi How are you","Hello How are you","Hey How are you"
             }
MIN_SAFE_LENGTH = 15  # Messages shorter than this are less likely to be complex scams

# Examples of common genuine / benign messages to classify as SAFE.
# These are longer phrases or common conversational sentences that are
# unlikely to be scam content on their own.
GENUINE_MESSAGES = {
    "i'm on my way",
    "on my way",
    "running late",
    "see you soon",
    "see you later",
    "let's meet",
    "let us meet",
    "let's catch up",
    "call me when you can",
    "call me later",
    "can you call me",
    "received the file",
    "i received the file",
    "thanks for the update",
    "thank you for the update",
    "thank you for your help",
    "thanks for your help",
    "happy birthday",
    "congratulations",
    "congrats",
    "meeting at",
    "see attached",
    "attached is",
    "i will be there",
    "i'll be there",
    "i have received",
    "payment received",
    "invoice received",
}

def apply_rules(text: str) -> tuple[str, float] | None:
    """
    Applies rule-based overrides to the input text.
    Returns (label, confidence) if a rule is triggered, otherwise None.
    """
    normalized_text = text.lower().strip()

    # Rule-based override: Greetings
    if normalized_text in GREETINGS:
        return "SAFE", 0.99

    # Rule-based override: Common genuine messages
    # If the message matches or contains a known benign phrase, mark SAFE
    for phrase in GENUINE_MESSAGES:
        if phrase in normalized_text:
            return "SAFE", 0.99

    # Rule-based override: Single-word or very short messages
    # This rule is for non-greeting short messages, e.g., "cool", "nope", "yeah"
    # Or messages that are too short to be meaningful scams
    if len(normalized_text.split()) <= 3 or len(normalized_text) < MIN_SAFE_LENGTH:
        # Check if it's potentially a scam based on common scam keywords (optional, for more robustness)
        # For now, default short messages to SAFE
        return "SAFE", 0.98

    return None
