# scam_text_api/app/rules.py

import re

# Raw phrase lists (readable forms). We'll normalize them below so matching
# behavior follows the same preprocessing used in inference.
RAW_GREETINGS = {
    "hi", "hello", "hii", "helo", "hey", "heyy", "helo", "hellooo", "hiiii",
    "good morning", "good afternoon", "good evening", "good night",
    "morning", "afternoon", "evening", 
    "how are you", "how are you?", "how r u", "how r you",
    "ok", "okay", "thanks", "thank you", "thank u", "thx", "ty",
    "hi how are you", "hello how are you", "hey how are you",
    "hi good morning", "hello good morning", "hey good morning",
    "hi good afternoon", "hello good afternoon", "hey good afternoon",
    "hi good evening", "hello good evening", "hey good evening",
    "hii good morning", "hii good afternoon", "hii good evening",
    "good morning how are you", "good afternoon how are you", "good evening how are you",
    "hi there", "hello there", "hey there",
    "whats up", "what's up", "wassup", "sup",
    "nice to meet you", "pleased to meet you"
}

MIN_SAFE_LENGTH = 15  # Messages shorter than this are less likely to be complex scams

# Examples of common genuine / benign messages to classify as SAFE.
# Keep these in a human-friendly form; we'll normalize them for matching.
RAW_GENUINE_MESSAGES = {
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


def normalize_text(text: str) -> str:
    """
    Normalize text for matching: lowercase, remove non-alpha characters,
    collapse whitespace, and strip. Mirrors `preprocess_message` logic.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# Precompute normalized sets for fast matching
GREETINGS = {normalize_text(g) for g in RAW_GREETINGS}
GENUINE_MESSAGES = {normalize_text(p) for p in RAW_GENUINE_MESSAGES}

# Common scam keywords that should not be classified as SAFE even if short
SCAM_KEYWORDS = {
    "otp", "verify", "urgent", "blocked", "suspended", "expired",
    "click", "link", "prize", "won", "winner", "lottery", "claim",
    "account", "bank", "card", "cvv", "pin", "password",
    "reward", "free", "congratulations", "confirm", "update"
}

def apply_rules(text: str) -> tuple[str, float] | None:
    """
    Applies rule-based overrides to the input text.
    Returns (label, confidence) if a rule is triggered, otherwise None.
    """
    # Normalize input the same way stored phrases are normalized
    normalized_text = normalize_text(text)

    # Rule-based override: Greetings (checked first for highest priority)
    if normalized_text in GREETINGS:
        return "SAFE", 0.99
    
    # Check if the message contains greeting words combined with other greetings
    # This handles cases like "hi good morning" even if not in exact list
    words = normalized_text.split()
    greeting_words = {"hi", "hii", "hello", "hey", "morning", "afternoon", "evening", "good", 
                      "night", "how", "are", "you", "r", "u", "there"}
    if len(words) <= 6 and all(word in greeting_words for word in words):
        return "SAFE", 0.99

    # Rule-based override: Common genuine messages
    # If the message matches or contains a known benign phrase, mark SAFE
    for phrase in GENUINE_MESSAGES:
        if phrase in normalized_text:
            return "SAFE", 0.99

    # Rule-based override: Single-word or very short messages
    # This rule is for non-greeting short messages, e.g., "cool", "nope", "yeah"
    # But exclude messages with scam keywords
    if len(normalized_text.split()) <= 3 or len(normalized_text) < MIN_SAFE_LENGTH:
        # Check if it contains scam keywords
        if any(keyword in normalized_text for keyword in SCAM_KEYWORDS):
            return None  # Let the model decide
        # Otherwise, classify as SAFE
        return "SAFE", 0.98

    return None
