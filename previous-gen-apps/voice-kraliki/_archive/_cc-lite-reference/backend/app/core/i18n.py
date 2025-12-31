"""
Internationalization (i18n) utilities for Voice by Kraliki
Supports Czech (cs) and English (en)
"""

from typing import Dict, Optional, Any
from enum import Enum


class Locale(str, Enum):
    """Supported locales"""
    CZECH = "cs"
    ENGLISH = "en"


# Default locale
DEFAULT_LOCALE = Locale.ENGLISH

# Supported locales
SUPPORTED_LOCALES = [Locale.CZECH, Locale.ENGLISH]


def get_locale_from_header(accept_language: Optional[str]) -> Locale:
    """
    Extract locale from Accept-Language header

    Args:
        accept_language: Accept-Language header value (e.g., "cs,en;q=0.9")

    Returns:
        Locale enum value (defaults to English if not found)
    """
    if not accept_language:
        return DEFAULT_LOCALE

    # Parse Accept-Language header
    # Format: "cs,en;q=0.9,en-US;q=0.8"
    languages = accept_language.split(',')

    for lang in languages:
        # Remove quality factor (q=0.9)
        lang_code = lang.split(';')[0].strip().lower()

        # Extract base language (cs-CZ -> cs)
        base_lang = lang_code.split('-')[0]

        # Check if supported
        if base_lang == Locale.CZECH:
            return Locale.CZECH
        elif base_lang == Locale.ENGLISH:
            return Locale.ENGLISH

    return DEFAULT_LOCALE


def get_localized_field(data: Dict[str, Any], locale: Locale) -> Any:
    """
    Get localized value from JSONB field

    Args:
        data: Dictionary with locale keys (e.g., {"en": "Hello", "cs": "Ahoj"})
        locale: Requested locale

    Returns:
        Localized value or fallback to English

    Example:
        >>> data = {"en": "Hello", "cs": "Ahoj"}
        >>> get_localized_field(data, Locale.CZECH)
        "Ahoj"
        >>> get_localized_field(data, Locale.ENGLISH)
        "Hello"
    """
    if not isinstance(data, dict):
        return data

    # Try requested locale
    if locale in data:
        return data[locale]

    # Fallback to string key
    locale_str = locale.value
    if locale_str in data:
        return data[locale_str]

    # Fallback to English
    if Locale.ENGLISH in data:
        return data[Locale.ENGLISH]
    if "en" in data:
        return data["en"]

    # Fallback to first available
    if data:
        return next(iter(data.values()))

    return None


def create_multilingual_field(en: str, cs: str) -> Dict[str, str]:
    """
    Create a multilingual JSONB field

    Args:
        en: English text
        cs: Czech text

    Returns:
        Dictionary with locale keys

    Example:
        >>> create_multilingual_field("Hello", "Ahoj")
        {"en": "Hello", "cs": "Ahoj"}
    """
    return {
        "en": en,
        "cs": cs
    }


def localize_model(model_dict: Dict[str, Any], locale: Locale, fields: list[str]) -> Dict[str, Any]:
    """
    Localize multiple fields in a model dictionary

    Args:
        model_dict: Model as dictionary
        locale: Target locale
        fields: List of field names to localize

    Returns:
        Model dictionary with localized fields

    Example:
        >>> model = {"name": {"en": "Campaign", "cs": "Kampaň"}, "status": "active"}
        >>> localize_model(model, Locale.CZECH, ["name"])
        {"name": "Kampaň", "status": "active"}
    """
    result = model_dict.copy()

    for field in fields:
        if field in result and isinstance(result[field], dict):
            result[field] = get_localized_field(result[field], locale)

    return result


# Common translations for API responses
TRANSLATIONS = {
    Locale.ENGLISH: {
        "success": "Success",
        "error": "Error",
        "not_found": "Not found",
        "unauthorized": "Unauthorized",
        "forbidden": "Forbidden",
        "validation_error": "Validation error",
        "internal_error": "Internal server error",
        "created": "Created successfully",
        "updated": "Updated successfully",
        "deleted": "Deleted successfully",
    },
    Locale.CZECH: {
        "success": "Úspěch",
        "error": "Chyba",
        "not_found": "Nenalezeno",
        "unauthorized": "Neautorizováno",
        "forbidden": "Zakázáno",
        "validation_error": "Chyba validace",
        "internal_error": "Interní chyba serveru",
        "created": "Úspěšně vytvořeno",
        "updated": "Úspěšně aktualizováno",
        "deleted": "Úspěšně smazáno",
    }
}


def translate(key: str, locale: Locale = DEFAULT_LOCALE) -> str:
    """
    Get translation for a key

    Args:
        key: Translation key
        locale: Target locale

    Returns:
        Translated string or key if not found
    """
    return TRANSLATIONS.get(locale, {}).get(key, key)
