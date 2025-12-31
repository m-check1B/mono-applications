"""Language detection and multi-language support service."""
import logging
from collections import Counter

from langdetect import detect, detect_langs, LangDetectException

logger = logging.getLogger(__name__)

# Supported languages with their display names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "cs": "Czech",
    "sk": "Slovak",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "uk": "Ukrainian",
    "pl": "Polish",
    "nl": "Dutch",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "ar": "Arabic",
    "hi": "Hindi",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "auto": "Auto-detect",
}

# Default language
DEFAULT_LANGUAGE = "en"


def detect_language(text: str) -> str | None:
    """Detect the language of a single text.

    Args:
        text: Text to analyze

    Returns:
        ISO 639-1 language code or None if detection fails
    """
    if not text or len(text.strip()) < 10:
        return None

    try:
        return detect(text)
    except LangDetectException:
        return None


def detect_language_with_confidence(text: str) -> list[tuple[str, float]]:
    """Detect language with confidence scores.

    Args:
        text: Text to analyze

    Returns:
        List of (language_code, probability) tuples sorted by probability
    """
    if not text or len(text.strip()) < 10:
        return []

    try:
        results = detect_langs(text)
        return [(r.lang, r.prob) for r in results]
    except LangDetectException:
        return []


def detect_dominant_language(messages: list[dict]) -> str:
    """Detect the dominant language across multiple messages.

    Uses voting to determine which language is most common.
    Falls back to English if detection fails.

    Args:
        messages: List of message dicts with 'text' key

    Returns:
        ISO 639-1 language code
    """
    if not messages:
        return DEFAULT_LANGUAGE

    language_votes = Counter()

    for msg in messages:
        text = msg.get("text", "")
        if text and len(text.strip()) >= 10:
            lang = detect_language(text)
            if lang:
                language_votes[lang] += 1

    if not language_votes:
        return DEFAULT_LANGUAGE

    # Return most common language
    return language_votes.most_common(1)[0][0]


def get_language_distribution(messages: list[dict]) -> dict[str, int]:
    """Get distribution of languages in messages.

    Args:
        messages: List of message dicts with 'text' key

    Returns:
        Dict mapping language codes to message counts
    """
    distribution = Counter()

    for msg in messages:
        text = msg.get("text", "")
        if text and len(text.strip()) >= 10:
            lang = detect_language(text)
            if lang:
                distribution[lang] += 1
            else:
                distribution["unknown"] += 1
        else:
            distribution["short"] += 1

    return dict(distribution)


def get_language_name(code: str) -> str:
    """Get display name for a language code.

    Args:
        code: ISO 639-1 language code

    Returns:
        Human-readable language name
    """
    return SUPPORTED_LANGUAGES.get(code, code.upper())


def is_supported_language(code: str) -> bool:
    """Check if a language code is supported.

    Args:
        code: ISO 639-1 language code

    Returns:
        True if language is supported
    """
    return code in SUPPORTED_LANGUAGES


def get_summary_language_prompt(language: str) -> str:
    """Get the language instruction for summary generation.

    Args:
        language: Target language code or "auto"

    Returns:
        Prompt instruction for language
    """
    if language == "auto":
        return "Write the summary in the same language as the majority of the messages."

    lang_name = get_language_name(language)
    return f"Write the summary in {lang_name}."
