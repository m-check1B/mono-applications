"""
Tests for i18n (internationalization) module
"""

import pytest
from app.core.i18n import (
    Locale,
    get_locale_from_header,
    get_localized_field,
    create_multilingual_field,
    localize_model,
    translate,
    DEFAULT_LOCALE,
)


class TestLocaleDetection:
    """Test locale detection from Accept-Language header"""

    def test_czech_locale(self):
        """Should detect Czech locale"""
        assert get_locale_from_header("cs") == Locale.CZECH
        assert get_locale_from_header("cs-CZ") == Locale.CZECH
        assert get_locale_from_header("cs,en;q=0.9") == Locale.CZECH

    def test_english_locale(self):
        """Should detect English locale"""
        assert get_locale_from_header("en") == Locale.ENGLISH
        assert get_locale_from_header("en-US") == Locale.ENGLISH
        assert get_locale_from_header("en-GB,en;q=0.9") == Locale.ENGLISH

    def test_fallback_to_default(self):
        """Should fallback to default locale for unsupported languages"""
        assert get_locale_from_header("fr") == DEFAULT_LOCALE
        assert get_locale_from_header("de") == DEFAULT_LOCALE
        assert get_locale_from_header("") == DEFAULT_LOCALE
        assert get_locale_from_header(None) == DEFAULT_LOCALE

    def test_quality_factor_ordering(self):
        """Should respect quality factors in Accept-Language"""
        # Czech has higher priority (q=1.0 implicit)
        assert get_locale_from_header("cs,en;q=0.9") == Locale.CZECH
        # English has higher priority
        assert get_locale_from_header("en,cs;q=0.5") == Locale.ENGLISH


class TestLocalizedFields:
    """Test multilingual field handling"""

    def test_get_localized_field_czech(self):
        """Should return Czech translation"""
        data = {"en": "Hello", "cs": "Ahoj"}
        assert get_localized_field(data, Locale.CZECH) == "Ahoj"

    def test_get_localized_field_english(self):
        """Should return English translation"""
        data = {"en": "Hello", "cs": "Ahoj"}
        assert get_localized_field(data, Locale.ENGLISH) == "Hello"

    def test_fallback_to_english(self):
        """Should fallback to English if locale not found"""
        data = {"en": "Hello"}
        assert get_localized_field(data, Locale.CZECH) == "Hello"

    def test_non_dict_passthrough(self):
        """Should pass through non-dict values"""
        assert get_localized_field("plain string", Locale.CZECH) == "plain string"
        assert get_localized_field(123, Locale.ENGLISH) == 123
        assert get_localized_field(None, Locale.CZECH) is None

    def test_empty_dict(self):
        """Should handle empty dictionary"""
        assert get_localized_field({}, Locale.CZECH) is None

    def test_create_multilingual_field(self):
        """Should create multilingual field correctly"""
        field = create_multilingual_field("Campaign", "Kampaň")
        assert field == {"en": "Campaign", "cs": "Kampaň"}
        assert get_localized_field(field, Locale.ENGLISH) == "Campaign"
        assert get_localized_field(field, Locale.CZECH) == "Kampaň"


class TestModelLocalization:
    """Test model localization"""

    def test_localize_single_field(self):
        """Should localize a single field"""
        model = {
            "name": {"en": "Campaign", "cs": "Kampaň"},
            "status": "active",
        }
        result = localize_model(model, Locale.CZECH, ["name"])

        assert result["name"] == "Kampaň"
        assert result["status"] == "active"

    def test_localize_multiple_fields(self):
        """Should localize multiple fields"""
        model = {
            "name": {"en": "Campaign", "cs": "Kampaň"},
            "description": {"en": "Test campaign", "cs": "Testovací kampaň"},
            "status": "active",
        }
        result = localize_model(model, Locale.CZECH, ["name", "description"])

        assert result["name"] == "Kampaň"
        assert result["description"] == "Testovací kampaň"
        assert result["status"] == "active"

    def test_localize_missing_field(self):
        """Should handle missing fields gracefully"""
        model = {"status": "active"}
        result = localize_model(model, Locale.CZECH, ["name"])

        assert "name" not in result
        assert result["status"] == "active"

    def test_localize_non_dict_field(self):
        """Should skip non-dict fields"""
        model = {
            "name": "Plain string",  # Not a multilingual field
            "status": "active",
        }
        result = localize_model(model, Locale.CZECH, ["name"])

        # Should remain unchanged
        assert result["name"] == "Plain string"


class TestTranslations:
    """Test translation function"""

    def test_translate_english(self):
        """Should translate to English"""
        assert translate("success", Locale.ENGLISH) == "Success"
        assert translate("error", Locale.ENGLISH) == "Error"

    def test_translate_czech(self):
        """Should translate to Czech"""
        assert translate("success", Locale.CZECH) == "Úspěch"
        assert translate("error", Locale.CZECH) == "Chyba"

    def test_missing_translation(self):
        """Should return key if translation missing"""
        assert translate("nonexistent_key", Locale.ENGLISH) == "nonexistent_key"

    def test_default_locale(self):
        """Should use default locale when not specified"""
        result = translate("success")
        assert result == "Success"  # DEFAULT_LOCALE is English


@pytest.mark.asyncio
class TestDatabaseI18n:
    """Test database i18n integration (requires database)"""

    async def test_campaign_multilingual_fields(self, db):
        """Should store and retrieve multilingual campaign data"""
        # This would test actual database operations
        # Requires database fixture and Campaign model
        pass

    async def test_locale_based_query(self, db):
        """Should query data with locale-specific sorting"""
        # Test querying and ordering by localized fields
        pass
