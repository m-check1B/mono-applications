"""
Unit tests for I18n Core Module
Tests internationalization helpers and translations
"""

import pytest
from unittest.mock import MagicMock

from app.core.i18n import (
    I18nHelper,
    TRANSLATIONS,
    get_translation,
)


class TestI18nHelper:
    """Tests for I18nHelper class"""

    def test_supported_locales(self):
        """Supported locales are defined correctly"""
        assert "en" in I18nHelper.SUPPORTED_LOCALES
        assert "cs" in I18nHelper.SUPPORTED_LOCALES
        assert I18nHelper.DEFAULT_LOCALE == "en"

    def test_get_locale_from_query_param(self):
        """Get locale from query parameter"""
        mock_request = MagicMock()
        mock_request.query_params = {"lang": "cs"}
        mock_request.headers = {}

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "cs"

    def test_get_locale_from_query_param_invalid(self):
        """Invalid query param falls back to header or default"""
        mock_request = MagicMock()
        mock_request.query_params = {"lang": "fr"}  # Unsupported
        mock_request.headers = {"Accept-Language": "cs,en"}

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "cs"  # Falls back to header

    def test_get_locale_from_accept_language_header(self):
        """Get locale from Accept-Language header"""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request.headers = {"Accept-Language": "cs,en-US;q=0.9,en;q=0.8"}

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "cs"

    def test_get_locale_from_accept_language_with_region(self):
        """Handle Accept-Language with region code"""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request.headers = {"Accept-Language": "en-US,en;q=0.9"}

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "en"

    def test_get_locale_fallback_to_default(self):
        """Fall back to default when no match"""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request.headers = {"Accept-Language": "de,fr;q=0.9"}  # Unsupported

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "en"

    def test_get_locale_empty_headers(self):
        """Handle empty headers"""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request.headers = {}

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "en"


class TestGetI18nValue:
    """Tests for get_i18n_value method"""

    def test_get_value_for_locale(self):
        """Get value for requested locale"""
        i18n_dict = {"en": "Task", "cs": "Úkol"}
        value = I18nHelper.get_i18n_value(i18n_dict, "cs")
        assert value == "Úkol"

    def test_get_value_fallback_to_english(self):
        """Fall back to English when locale not found"""
        i18n_dict = {"en": "Task"}
        value = I18nHelper.get_i18n_value(i18n_dict, "cs")
        assert value == "Task"

    def test_get_value_fallback_to_any(self):
        """Fall back to any available value"""
        i18n_dict = {"de": "Aufgabe"}
        value = I18nHelper.get_i18n_value(i18n_dict, "cs")
        assert value == "Aufgabe"

    def test_get_value_none_dict(self):
        """Handle None i18n_dict"""
        value = I18nHelper.get_i18n_value(None, "en")
        assert value is None

    def test_get_value_none_dict_with_fallback(self):
        """Return fallback for None dict"""
        value = I18nHelper.get_i18n_value(None, "en", "Default Value")
        assert value == "Default Value"

    def test_get_value_empty_dict(self):
        """Handle empty dict"""
        value = I18nHelper.get_i18n_value({}, "en", "Fallback")
        assert value == "Fallback"

    def test_get_value_empty_string_values(self):
        """Skip empty string values"""
        i18n_dict = {"en": "", "cs": "Úkol"}
        value = I18nHelper.get_i18n_value(i18n_dict, "en")
        assert value == "Úkol"  # Falls through to cs


class TestSetI18nValue:
    """Tests for set_i18n_value method"""

    def test_set_value_new_dict(self):
        """Create new dict when None"""
        result = I18nHelper.set_i18n_value(None, "en", "Task")
        assert result == {"en": "Task"}

    def test_set_value_existing_dict(self):
        """Add to existing dict"""
        i18n_dict = {"en": "Task"}
        result = I18nHelper.set_i18n_value(i18n_dict, "cs", "Úkol")
        assert result == {"en": "Task", "cs": "Úkol"}

    def test_set_value_update_existing(self):
        """Update existing locale"""
        i18n_dict = {"en": "Old Task"}
        result = I18nHelper.set_i18n_value(i18n_dict, "en", "New Task")
        assert result == {"en": "New Task"}

    def test_set_value_preserves_original(self):
        """Original dict is modified in place"""
        i18n_dict = {"en": "Task"}
        result = I18nHelper.set_i18n_value(i18n_dict, "cs", "Úkol")
        assert result is i18n_dict  # Same object


class TestLocalizeDict:
    """Tests for localize_dict method"""

    def test_localize_single_field(self):
        """Localize single i18n field"""
        data = {
            "id": "123",
            "title": "Old Title",
            "title_i18n": {"en": "Task", "cs": "Úkol"}
        }
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "Úkol"
        assert result["id"] == "123"

    def test_localize_multiple_fields(self):
        """Localize multiple i18n fields"""
        data = {
            "id": "123",
            "title": "Old Title",
            "title_i18n": {"en": "Task", "cs": "Úkol"},
            "description": "Old Desc",
            "description_i18n": {"en": "Description", "cs": "Popis"}
        }
        result = I18nHelper.localize_dict(data, "cs", ["title", "description"])
        assert result["title"] == "Úkol"
        assert result["description"] == "Popis"

    def test_localize_missing_i18n_field(self):
        """Handle missing i18n field gracefully"""
        data = {
            "id": "123",
            "title": "Original Title"
        }
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "Original Title"  # Unchanged

    def test_localize_fallback_to_original(self):
        """Fall back to original field when locale missing"""
        data = {
            "id": "123",
            "title": "Original Title",
            "title_i18n": {"en": "English Only"}
        }
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "English Only"  # Falls back to en

    def test_localize_preserves_other_fields(self):
        """Other fields are preserved"""
        data = {
            "id": "123",
            "title_i18n": {"cs": "Úkol"},
            "status": "active",
            "priority": 1
        }
        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["status"] == "active"
        assert result["priority"] == 1


class TestTranslations:
    """Tests for translations dictionary"""

    def test_translations_has_english(self):
        """English translations exist"""
        assert "en" in TRANSLATIONS
        assert "tasks" in TRANSLATIONS["en"]
        assert "create" in TRANSLATIONS["en"]["tasks"]

    def test_translations_has_czech(self):
        """Czech translations exist"""
        assert "cs" in TRANSLATIONS
        assert "tasks" in TRANSLATIONS["cs"]
        assert "create" in TRANSLATIONS["cs"]["tasks"]

    def test_translations_task_statuses(self):
        """Task status translations exist"""
        assert "status" in TRANSLATIONS["en"]["tasks"]
        assert "pending" in TRANSLATIONS["en"]["tasks"]["status"]
        assert "completed" in TRANSLATIONS["en"]["tasks"]["status"]

        assert "status" in TRANSLATIONS["cs"]["tasks"]
        assert "pending" in TRANSLATIONS["cs"]["tasks"]["status"]

    def test_translations_priorities(self):
        """Priority translations exist"""
        assert "priority" in TRANSLATIONS["en"]["tasks"]
        assert "low" in TRANSLATIONS["en"]["tasks"]["priority"]
        assert "medium" in TRANSLATIONS["en"]["tasks"]["priority"]
        assert "high" in TRANSLATIONS["en"]["tasks"]["priority"]

    def test_translations_auth_strings(self):
        """Auth translations exist"""
        assert "auth" in TRANSLATIONS["en"]
        assert "login" in TRANSLATIONS["en"]["auth"]
        assert "register" in TRANSLATIONS["en"]["auth"]

    def test_translations_common_strings(self):
        """Common UI translations exist"""
        assert "common" in TRANSLATIONS["en"]
        assert "save" in TRANSLATIONS["en"]["common"]
        assert "cancel" in TRANSLATIONS["en"]["common"]


class TestGetTranslation:
    """Tests for get_translation function"""

    def test_get_english_translation(self):
        """Get English translation"""
        result = get_translation("en", "tasks.create")
        assert result == "Create Task"

    def test_get_czech_translation(self):
        """Get Czech translation"""
        result = get_translation("cs", "tasks.create")
        assert result == "Vytvořit úkol"

    def test_get_nested_translation(self):
        """Get deeply nested translation"""
        result = get_translation("en", "tasks.status.pending")
        assert result == "Pending"

        result = get_translation("cs", "tasks.status.pending")
        assert result == "Čeká"

    def test_get_missing_translation_returns_default(self):
        """Return default for missing key"""
        result = get_translation("en", "nonexistent.key", "Default")
        assert result == "Default"

    def test_get_missing_translation_returns_key(self):
        """Return key when no default provided"""
        result = get_translation("en", "nonexistent.key")
        assert result == "nonexistent.key"

    def test_get_unsupported_locale_fallback_to_english(self):
        """Unsupported locale falls back to English"""
        result = get_translation("de", "tasks.create")
        assert result == "Create Task"

    def test_get_partial_key_path(self):
        """Handle partial key path"""
        result = get_translation("en", "tasks")
        # Returns the dict, not a string, but should not crash
        assert result is not None

    def test_get_various_translations(self):
        """Test various translation keys"""
        translations_to_check = [
            ("en", "auth.login", "Login"),
            ("cs", "auth.login", "Přihlásit se"),
            ("en", "common.save", "Save"),
            ("cs", "common.save", "Uložit"),
            ("en", "projects.create", "Create Project"),
            ("cs", "projects.create", "Vytvořit projekt"),
        ]

        for locale, key, expected in translations_to_check:
            result = get_translation(locale, key)
            assert result == expected, f"Expected '{expected}' for {locale}:{key}, got '{result}'"


class TestI18nIntegration:
    """Integration tests for i18n functionality"""

    def test_full_localization_workflow(self):
        """Test full localization workflow"""
        # 1. Set i18n values
        i18n_dict = None
        i18n_dict = I18nHelper.set_i18n_value(i18n_dict, "en", "Task Title")
        i18n_dict = I18nHelper.set_i18n_value(i18n_dict, "cs", "Název úkolu")

        # 2. Get values for different locales
        en_value = I18nHelper.get_i18n_value(i18n_dict, "en")
        cs_value = I18nHelper.get_i18n_value(i18n_dict, "cs")

        assert en_value == "Task Title"
        assert cs_value == "Název úkolu"

    def test_request_locale_to_translation(self):
        """Get locale from request and fetch translation"""
        mock_request = MagicMock()
        mock_request.query_params = {"lang": "cs"}
        mock_request.headers = {}

        locale = I18nHelper.get_locale_from_request(mock_request)
        translation = get_translation(locale, "tasks.create")

        assert translation == "Vytvořit úkol"
