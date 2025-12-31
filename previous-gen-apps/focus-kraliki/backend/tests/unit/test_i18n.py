"""
Unit tests for Internationalization (i18n) module
Tests locale detection, translation lookup, and localization utilities
"""

import pytest
from unittest.mock import MagicMock

from app.core.i18n import I18nHelper, TRANSLATIONS, get_translation


class TestI18nHelperConstants:
    """Test I18nHelper class constants"""

    def test_supported_locales(self):
        """Supported locales include English and Czech"""
        assert "en" in I18nHelper.SUPPORTED_LOCALES
        assert "cs" in I18nHelper.SUPPORTED_LOCALES
        assert len(I18nHelper.SUPPORTED_LOCALES) == 2

    def test_default_locale(self):
        """Default locale is English"""
        assert I18nHelper.DEFAULT_LOCALE == "en"


class TestGetLocaleFromRequest:
    """Test locale detection from HTTP requests"""

    def test_locale_from_query_param(self):
        """Query parameter takes priority"""
        mock_request = MagicMock()
        mock_request.query_params.get.return_value = "cs"
        mock_request.headers.get.return_value = "en-US"

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "cs"

    def test_locale_from_accept_language(self):
        """Accept-Language header is used when no query param"""
        mock_request = MagicMock()
        mock_request.query_params.get.return_value = None
        mock_request.headers.get.return_value = "cs,en-US;q=0.9,en;q=0.8"

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "cs"

    def test_locale_from_accept_language_with_region(self):
        """Accept-Language with region code (e.g., en-US) extracts base locale"""
        mock_request = MagicMock()
        mock_request.query_params.get.return_value = None
        mock_request.headers.get.return_value = "en-US,en;q=0.9"

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "en"

    def test_locale_default_when_unsupported(self):
        """Default locale used when Accept-Language has unsupported locales"""
        mock_request = MagicMock()
        mock_request.query_params.get.return_value = None
        mock_request.headers.get.return_value = "de,fr;q=0.9"

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "en"  # Default

    def test_locale_default_when_no_header(self):
        """Default locale used when no Accept-Language header"""
        mock_request = MagicMock()
        mock_request.query_params.get.return_value = None
        mock_request.headers.get.return_value = ""

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "en"

    def test_invalid_query_param_ignored(self):
        """Invalid query param locale falls back to header"""
        mock_request = MagicMock()
        mock_request.query_params.get.return_value = "invalid"
        mock_request.headers.get.return_value = "cs"

        locale = I18nHelper.get_locale_from_request(mock_request)
        assert locale == "cs"


class TestGetI18nValue:
    """Test i18n value extraction from JSONB fields"""

    def test_get_requested_locale(self):
        """Returns value for requested locale"""
        i18n_dict = {"en": "Task", "cs": "Úkol"}
        assert I18nHelper.get_i18n_value(i18n_dict, "cs") == "Úkol"
        assert I18nHelper.get_i18n_value(i18n_dict, "en") == "Task"

    def test_fallback_to_english(self):
        """Falls back to English when requested locale missing"""
        i18n_dict = {"en": "Task"}
        assert I18nHelper.get_i18n_value(i18n_dict, "cs") == "Task"

    def test_fallback_to_any_available(self):
        """Falls back to any available locale when English missing"""
        i18n_dict = {"cs": "Úkol"}
        assert I18nHelper.get_i18n_value(i18n_dict, "de") == "Úkol"

    def test_fallback_value_when_none(self):
        """Returns fallback value when i18n_dict is None"""
        assert I18nHelper.get_i18n_value(None, "en", "Default") == "Default"

    def test_fallback_value_when_empty(self):
        """Returns fallback value when i18n_dict is empty"""
        assert I18nHelper.get_i18n_value({}, "en", "Default") == "Default"

    def test_skip_empty_values(self):
        """Skips empty string values"""
        i18n_dict = {"cs": "", "en": "Task"}
        assert I18nHelper.get_i18n_value(i18n_dict, "cs") == "Task"

    def test_none_fallback_when_no_value(self):
        """Returns None when no value and no fallback"""
        assert I18nHelper.get_i18n_value(None, "en") is None


class TestSetI18nValue:
    """Test setting i18n values"""

    def test_set_value_new_dict(self):
        """Creates new dict when None provided"""
        result = I18nHelper.set_i18n_value(None, "en", "Task")
        assert result == {"en": "Task"}

    def test_set_value_existing_dict(self):
        """Adds to existing dict"""
        existing = {"en": "Task"}
        result = I18nHelper.set_i18n_value(existing, "cs", "Úkol")
        assert result == {"en": "Task", "cs": "Úkol"}

    def test_update_existing_value(self):
        """Updates existing locale value"""
        existing = {"en": "Old Task"}
        result = I18nHelper.set_i18n_value(existing, "en", "New Task")
        assert result == {"en": "New Task"}


class TestLocalizeDict:
    """Test dictionary localization"""

    def test_localize_with_i18n_fields(self):
        """Localizes dict using i18n JSONB fields"""
        data = {
            "id": "123",
            "title": "Old Title",
            "title_i18n": {"en": "Task", "cs": "Úkol"},
            "description": "Old Desc",
            "description_i18n": {"en": "Description", "cs": "Popis"}
        }

        result = I18nHelper.localize_dict(data, "cs", ["title", "description"])

        assert result["id"] == "123"
        assert result["title"] == "Úkol"
        assert result["description"] == "Popis"

    def test_localize_fallback_to_original(self):
        """Falls back to original field when i18n missing"""
        data = {
            "id": "123",
            "title": "Original Title",
            "title_i18n": {}  # Empty i18n
        }

        result = I18nHelper.localize_dict(data, "cs", ["title"])

        assert result["title"] == "Original Title"

    def test_localize_preserves_other_fields(self):
        """Preserves non-i18n fields"""
        data = {
            "id": "123",
            "title_i18n": {"en": "Task"},
            "count": 42,
            "active": True
        }

        result = I18nHelper.localize_dict(data, "en", ["title"])

        assert result["count"] == 42
        assert result["active"] is True

    def test_localize_missing_i18n_field(self):
        """Handles missing i18n field gracefully"""
        data = {
            "id": "123",
            "title": "Task"
            # No title_i18n field
        }

        result = I18nHelper.localize_dict(data, "cs", ["title"])
        assert result["title"] == "Task"


class TestTranslations:
    """Test TRANSLATIONS dictionary structure"""

    def test_english_translations_exist(self):
        """English translations exist"""
        assert "en" in TRANSLATIONS
        assert "tasks" in TRANSLATIONS["en"]
        assert "projects" in TRANSLATIONS["en"]
        assert "auth" in TRANSLATIONS["en"]
        assert "common" in TRANSLATIONS["en"]

    def test_czech_translations_exist(self):
        """Czech translations exist"""
        assert "cs" in TRANSLATIONS
        assert "tasks" in TRANSLATIONS["cs"]
        assert "projects" in TRANSLATIONS["cs"]
        assert "auth" in TRANSLATIONS["cs"]
        assert "common" in TRANSLATIONS["cs"]

    def test_task_status_translations(self):
        """Task status translations exist in both locales"""
        en_status = TRANSLATIONS["en"]["tasks"]["status"]
        cs_status = TRANSLATIONS["cs"]["tasks"]["status"]

        assert en_status["pending"] == "Pending"
        assert cs_status["pending"] == "Čeká"
        assert en_status["completed"] == "Completed"
        assert cs_status["completed"] == "Dokončeno"

    def test_common_translations(self):
        """Common UI strings translated"""
        assert TRANSLATIONS["en"]["common"]["save"] == "Save"
        assert TRANSLATIONS["cs"]["common"]["save"] == "Uložit"


class TestGetTranslation:
    """Test get_translation function"""

    def test_get_english_translation(self):
        """Get English translation by key"""
        result = get_translation("en", "tasks.create")
        assert result == "Create Task"

    def test_get_czech_translation(self):
        """Get Czech translation by key"""
        result = get_translation("cs", "tasks.create")
        assert result == "Vytvořit úkol"

    def test_nested_key(self):
        """Get nested translation by dot notation"""
        result = get_translation("en", "tasks.status.completed")
        assert result == "Completed"

    def test_fallback_to_english(self):
        """Falls back to English for unsupported locale"""
        result = get_translation("de", "tasks.create")
        assert result == "Create Task"

    def test_missing_key_returns_default(self):
        """Returns default when key not found"""
        result = get_translation("en", "nonexistent.key", "Default Value")
        assert result == "Default Value"

    def test_missing_key_returns_key(self):
        """Returns key when no default provided"""
        result = get_translation("en", "nonexistent.key")
        assert result == "nonexistent.key"

    def test_partial_key_path(self):
        """Returns key when path incomplete"""
        result = get_translation("en", "tasks.nonexistent")
        assert result == "tasks.nonexistent"


class TestI18nMiddleware:
    """Tests for I18nMiddleware class"""

    @pytest.mark.asyncio
    async def test_middleware_sets_locale_in_state(self):
        """Middleware sets locale in request.state"""
        from app.middleware.i18n import I18nMiddleware
        from starlette.requests import Request
        from starlette.responses import Response
        from starlette.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        app.add_middleware(I18nMiddleware)

        captured_locale = None

        @app.get("/test")
        async def test_endpoint(request: Request):
            nonlocal captured_locale
            captured_locale = request.state.locale
            return {"locale": captured_locale}

        client = TestClient(app)
        response = client.get("/test", headers={"Accept-Language": "cs"})

        assert response.status_code == 200
        assert captured_locale == "cs"

    @pytest.mark.asyncio
    async def test_middleware_sets_content_language_header(self):
        """Middleware sets Content-Language response header"""
        from app.middleware.i18n import I18nMiddleware
        from starlette.requests import Request
        from starlette.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        app.add_middleware(I18nMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"locale": request.state.locale}

        client = TestClient(app)
        response = client.get("/test", headers={"Accept-Language": "cs-CZ"})

        assert response.headers.get("Content-Language") == "cs"

    @pytest.mark.asyncio
    async def test_middleware_defaults_to_english(self):
        """Middleware defaults to English when no Accept-Language"""
        from app.middleware.i18n import I18nMiddleware
        from starlette.requests import Request
        from starlette.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        app.add_middleware(I18nMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"locale": request.state.locale}

        client = TestClient(app)
        response = client.get("/test")

        assert response.json()["locale"] == "en"
        assert response.headers.get("Content-Language") == "en"

    @pytest.mark.asyncio
    async def test_middleware_respects_query_param(self):
        """Middleware respects lang query parameter"""
        from app.middleware.i18n import I18nMiddleware
        from starlette.requests import Request
        from starlette.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        app.add_middleware(I18nMiddleware)

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"locale": request.state.locale}

        client = TestClient(app)
        response = client.get("/test?lang=cs")

        assert response.json()["locale"] == "cs"
        assert response.headers.get("Content-Language") == "cs"
