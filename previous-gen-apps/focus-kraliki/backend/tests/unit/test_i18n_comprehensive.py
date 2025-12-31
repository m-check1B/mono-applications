"""
Comprehensive i18n tests
Target: Increase coverage of app/core/i18n.py
"""

import pytest
from unittest.mock import MagicMock

from app.core.i18n import I18nHelper


class TestI18nGetLocaleFromRequest:
    """Test locale extraction from request."""

    def test_query_param_cs(self):
        """Test Czech locale from query param."""
        request = MagicMock()
        request.query_params.get.return_value = "cs"
        request.headers.get.return_value = ""

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "cs"

    def test_query_param_en(self):
        """Test English locale from query param."""
        request = MagicMock()
        request.query_params.get.return_value = "en"
        request.headers.get.return_value = ""

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "en"

    def test_query_param_unsupported(self):
        """Test unsupported locale falls back."""
        request = MagicMock()
        request.query_params.get.return_value = "de"  # German not supported
        request.headers.get.return_value = "cs"

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "cs"  # Falls back to header

    def test_accept_language_cs(self):
        """Test Czech from Accept-Language header."""
        request = MagicMock()
        request.query_params.get.return_value = None
        request.headers.get.return_value = "cs,en-US;q=0.9"

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "cs"

    def test_accept_language_en_us(self):
        """Test English from Accept-Language with region."""
        request = MagicMock()
        request.query_params.get.return_value = None
        request.headers.get.return_value = "en-US,en;q=0.9"

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "en"

    def test_accept_language_complex(self):
        """Test complex Accept-Language header."""
        request = MagicMock()
        request.query_params.get.return_value = None
        request.headers.get.return_value = "de,cs;q=0.9,en;q=0.8"

        # German not supported, should pick cs
        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "cs"

    def test_no_locale_info(self):
        """Test default locale when no info provided."""
        request = MagicMock()
        request.query_params.get.return_value = None
        request.headers.get.return_value = ""

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == "en"

    def test_empty_accept_language(self):
        """Test empty Accept-Language header."""
        request = MagicMock()
        request.query_params.get.return_value = None
        request.headers.get.return_value = ""

        locale = I18nHelper.get_locale_from_request(request)
        assert locale == I18nHelper.DEFAULT_LOCALE


class TestI18nGetValue:
    """Test i18n value retrieval."""

    def test_get_value_exact_locale(self):
        """Test getting value for exact locale."""
        i18n = {"en": "Task", "cs": "Úkol"}
        result = I18nHelper.get_i18n_value(i18n, "cs")
        assert result == "Úkol"

    def test_get_value_fallback_to_en(self):
        """Test fallback to English."""
        i18n = {"en": "Task"}
        result = I18nHelper.get_i18n_value(i18n, "cs")
        assert result == "Task"

    def test_get_value_fallback_to_any(self):
        """Test fallback to any available locale."""
        i18n = {"fr": "Tâche"}
        result = I18nHelper.get_i18n_value(i18n, "cs")
        assert result == "Tâche"

    def test_get_value_none_dict(self):
        """Test with None dictionary."""
        result = I18nHelper.get_i18n_value(None, "cs", "Default")
        assert result == "Default"

    def test_get_value_empty_dict(self):
        """Test with empty dictionary."""
        result = I18nHelper.get_i18n_value({}, "cs", "Default")
        assert result == "Default"

    def test_get_value_empty_string(self):
        """Test locale value is empty string."""
        i18n = {"cs": "", "en": "Task"}
        result = I18nHelper.get_i18n_value(i18n, "cs")
        assert result == "Task"

    def test_get_value_all_empty(self):
        """Test all values are empty."""
        i18n = {"cs": "", "en": ""}
        result = I18nHelper.get_i18n_value(i18n, "cs", "Default")
        assert result == "Default"


class TestI18nSetValue:
    """Test i18n value setting."""

    def test_set_value_new_locale(self):
        """Test setting value for new locale."""
        i18n = {"en": "Task"}
        result = I18nHelper.set_i18n_value(i18n, "cs", "Úkol")
        assert result["cs"] == "Úkol"
        assert result["en"] == "Task"

    def test_set_value_update_existing(self):
        """Test updating existing locale."""
        i18n = {"en": "Task", "cs": "Úkol"}
        result = I18nHelper.set_i18n_value(i18n, "cs", "Nový úkol")
        assert result["cs"] == "Nový úkol"

    def test_set_value_none_dict(self):
        """Test setting value when dict is None."""
        result = I18nHelper.set_i18n_value(None, "en", "Task")
        assert result == {"en": "Task"}

    def test_set_value_empty_dict(self):
        """Test setting value on empty dict."""
        result = I18nHelper.set_i18n_value({}, "cs", "Úkol")
        assert result == {"cs": "Úkol"}


class TestI18nLocalizeDict:
    """Test dictionary localization."""

    def test_localize_dict_simple(self):
        """Test localizing dictionary with i18n fields."""
        data = {
            "id": "123",
            "title": "Fallback",
            "title_i18n": {"en": "Task", "cs": "Úkol"}
        }
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "Úkol"

    def test_localize_dict_no_i18n(self):
        """Test dictionary without i18n fields."""
        data = {"id": "123", "title": "Task"}
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "Task"

    def test_localize_dict_missing_locale(self):
        """Test localization when locale missing."""
        data = {
            "title": "Fallback",
            "title_i18n": {"en": "Task"}
        }
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "Task"  # Falls back to English

    def test_localize_dict_multiple_fields(self):
        """Test localizing multiple i18n fields."""
        data = {
            "title": "Default Title",
            "title_i18n": {"cs": "Úkol", "en": "Task"},
            "description": "Default Desc",
            "description_i18n": {"cs": "Popis", "en": "Description"}
        }
        result = I18nHelper.localize_dict(data, "cs", ["title", "description"])
        assert result["title"] == "Úkol"
        assert result["description"] == "Popis"

    def test_localize_dict_field_not_in_i18n_fields(self):
        """Test field not requested for localization stays unchanged."""
        data = {
            "title": "Default",
            "title_i18n": {"cs": "Úkol"}
        }
        result = I18nHelper.localize_dict(data, "cs", [])  # Empty i18n_fields
        assert result["title"] == "Default"  # Not localized


class TestGetTranslation:
    """Test static translation function."""

    def test_get_translation_cs(self):
        """Test Czech translation."""
        from app.core.i18n import get_translation
        result = get_translation("cs", "tasks.create")
        assert result == "Vytvořit úkol"

    def test_get_translation_en(self):
        """Test English translation."""
        from app.core.i18n import get_translation
        result = get_translation("en", "tasks.create")
        assert result == "Create Task"

    def test_get_translation_nested(self):
        """Test nested translation key."""
        from app.core.i18n import get_translation
        result = get_translation("cs", "tasks.status.completed")
        assert result == "Dokončeno"

    def test_get_translation_not_found(self):
        """Test translation key not found."""
        from app.core.i18n import get_translation
        result = get_translation("en", "nonexistent.key")
        assert result == "nonexistent.key"

    def test_get_translation_default(self):
        """Test default value when not found."""
        from app.core.i18n import get_translation
        result = get_translation("en", "nonexistent.key", "Default")
        assert result == "Default"

    def test_get_translation_unsupported_locale(self):
        """Test unsupported locale falls back to English."""
        from app.core.i18n import get_translation
        result = get_translation("de", "tasks.create")  # German not supported
        assert result == "Create Task"

    def test_get_translation_common(self):
        """Test common translations."""
        from app.core.i18n import get_translation
        assert get_translation("cs", "common.save") == "Uložit"
        assert get_translation("en", "common.save") == "Save"

    def test_get_translation_auth(self):
        """Test auth translations."""
        from app.core.i18n import get_translation
        assert get_translation("cs", "auth.login") == "Přihlásit se"
        assert get_translation("en", "auth.login") == "Login"


class TestI18nHelperConstants:
    """Test i18n constants."""

    def test_supported_locales(self):
        """Test supported locales list."""
        assert "en" in I18nHelper.SUPPORTED_LOCALES
        assert "cs" in I18nHelper.SUPPORTED_LOCALES
        assert len(I18nHelper.SUPPORTED_LOCALES) == 2

    def test_default_locale(self):
        """Test default locale is English."""
        assert I18nHelper.DEFAULT_LOCALE == "en"
