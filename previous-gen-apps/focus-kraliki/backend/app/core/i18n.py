"""
Internationalization (i18n) Support
Handles Czech (cs) and English (en) translations
"""

from typing import Optional, Dict, Any
from fastapi import Request


class I18nHelper:
    """Helper for internationalization operations."""

    SUPPORTED_LOCALES = ["en", "cs"]
    DEFAULT_LOCALE = "en"

    @staticmethod
    def get_locale_from_request(request: Request) -> str:
        """
        Extract locale from Accept-Language header or query param.

        Priority:
        1. Query parameter: ?lang=cs
        2. Accept-Language header
        3. Default locale (en)

        Args:
            request: FastAPI request object

        Returns:
            Locale code ('en' or 'cs')
        """
        # Check query parameter first
        lang_param = request.query_params.get("lang")
        if lang_param and lang_param in I18nHelper.SUPPORTED_LOCALES:
            return lang_param

        # Check Accept-Language header
        accept_language = request.headers.get("Accept-Language", "")

        # Parse Accept-Language header (e.g., "cs,en-US;q=0.9,en;q=0.8")
        for lang_range in accept_language.split(","):
            lang = lang_range.split(";")[0].strip().split("-")[0].lower()
            if lang in I18nHelper.SUPPORTED_LOCALES:
                return lang

        return I18nHelper.DEFAULT_LOCALE

    @staticmethod
    def get_i18n_value(
        i18n_dict: Optional[Dict[str, str]],
        locale: str,
        fallback_value: Optional[str] = None
    ) -> Optional[str]:
        """
        Get localized value from i18n JSONB field.

        Args:
            i18n_dict: JSONB dict with locale keys (e.g., {'en': 'Task', 'cs': 'Úkol'})
            locale: Requested locale ('en' or 'cs')
            fallback_value: Value to return if i18n_dict is None

        Returns:
            Localized string or fallback value

        Examples:
            >>> get_i18n_value({'en': 'Task', 'cs': 'Úkol'}, 'cs')
            'Úkol'

            >>> get_i18n_value({'en': 'Task'}, 'cs')
            'Task'  # Falls back to English

            >>> get_i18n_value(None, 'cs', 'Default Task')
            'Default Task'
        """
        if not i18n_dict:
            return fallback_value

        # Try requested locale
        if locale in i18n_dict and i18n_dict[locale]:
            return i18n_dict[locale]

        # Fall back to English
        if "en" in i18n_dict and i18n_dict["en"]:
            return i18n_dict["en"]

        # Fall back to any available locale
        for value in i18n_dict.values():
            if value:
                return value

        return fallback_value

    @staticmethod
    def set_i18n_value(
        i18n_dict: Optional[Dict[str, str]],
        locale: str,
        value: str
    ) -> Dict[str, str]:
        """
        Set localized value in i18n dict.

        Args:
            i18n_dict: Existing i18n dict or None
            locale: Locale to set ('en' or 'cs')
            value: Localized value

        Returns:
            Updated i18n dict

        Examples:
            >>> set_i18n_value(None, 'en', 'Task')
            {'en': 'Task'}

            >>> set_i18n_value({'en': 'Task'}, 'cs', 'Úkol')
            {'en': 'Task', 'cs': 'Úkol'}
        """
        if not i18n_dict:
            i18n_dict = {}

        i18n_dict[locale] = value
        return i18n_dict

    @staticmethod
    def localize_dict(
        data: Dict[str, Any],
        locale: str,
        i18n_fields: list[str]
    ) -> Dict[str, Any]:
        """
        Localize a dictionary by extracting i18n field values.

        Args:
            data: Dictionary with i18n JSONB fields
            locale: Target locale
            i18n_fields: List of field names that have i18n versions
                         (e.g., ['title', 'description'])

        Returns:
            Dictionary with localized values

        Examples:
            >>> data = {
            ...     'id': '123',
            ...     'title': 'Old Title',
            ...     'title_i18n': {'en': 'Task', 'cs': 'Úkol'},
            ...     'description_i18n': {'en': 'Description', 'cs': 'Popis'}
            ... }
            >>> localize_dict(data, 'cs', ['title', 'description'])
            {
                'id': '123',
                'title': 'Úkol',
                'description': 'Popis'
            }
        """
        result = data.copy()

        for field in i18n_fields:
            i18n_field = f"{field}_i18n"

            if i18n_field in data:
                # Get localized value from i18n field
                localized = I18nHelper.get_i18n_value(
                    data[i18n_field],
                    locale,
                    fallback_value=data.get(field)  # Fall back to original field
                )

                # Set the base field to localized value
                if localized is not None:
                    result[field] = localized

                # Optionally remove i18n field from response
                # result.pop(i18n_field, None)

        return result


# Translations dictionary for static UI strings
TRANSLATIONS = {
    "en": {
        "tasks": {
            "create": "Create Task",
            "edit": "Edit Task",
            "delete": "Delete Task",
            "status": {
                "pending": "Pending",
                "in_progress": "In Progress",
                "completed": "Completed",
                "archived": "Archived"
            },
            "priority": {
                "low": "Low",
                "medium": "Medium",
                "high": "High"
            },
            "energy": {
                "low": "Low Energy",
                "medium": "Medium Energy",
                "high": "High Energy"
            }
        },
        "projects": {
            "create": "Create Project",
            "edit": "Edit Project",
            "delete": "Delete Project",
            "all": "All Projects"
        },
        "auth": {
            "login": "Login",
            "register": "Register",
            "logout": "Logout",
            "email": "Email",
            "password": "Password"
        },
        "common": {
            "save": "Save",
            "cancel": "Cancel",
            "delete": "Delete",
            "search": "Search",
            "filter": "Filter"
        }
    },
    "cs": {
        "tasks": {
            "create": "Vytvořit úkol",
            "edit": "Upravit úkol",
            "delete": "Smazat úkol",
            "status": {
                "pending": "Čeká",
                "in_progress": "Probíhá",
                "completed": "Dokončeno",
                "archived": "Archivováno"
            },
            "priority": {
                "low": "Nízká",
                "medium": "Střední",
                "high": "Vysoká"
            },
            "energy": {
                "low": "Nízká energie",
                "medium": "Střední energie",
                "high": "Vysoká energie"
            }
        },
        "projects": {
            "create": "Vytvořit projekt",
            "edit": "Upravit projekt",
            "delete": "Smazat projekt",
            "all": "Všechny projekty"
        },
        "auth": {
            "login": "Přihlásit se",
            "register": "Registrovat se",
            "logout": "Odhlásit se",
            "email": "E-mail",
            "password": "Heslo"
        },
        "common": {
            "save": "Uložit",
            "cancel": "Zrušit",
            "delete": "Smazat",
            "search": "Hledat",
            "filter": "Filtrovat"
        }
    }
}


def get_translation(locale: str, key: str, default: str = None) -> str:
    """
    Get translation for a key.

    Args:
        locale: Locale code ('en' or 'cs')
        key: Translation key (e.g., 'tasks.create')
        default: Default value if translation not found

    Returns:
        Translated string or default

    Examples:
        >>> get_translation('cs', 'tasks.create')
        'Vytvořit úkol'

        >>> get_translation('en', 'tasks.create')
        'Create Task'
    """
    keys = key.split(".")
    value = TRANSLATIONS.get(locale, TRANSLATIONS["en"])

    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default or key

    return value or default or key
