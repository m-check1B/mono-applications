"""
Targeted tests to improve coverage for i18n helper
"""
import pytest
from unittest.mock import MagicMock
from app.core.i18n import I18nHelper, get_translation

def test_get_locale_from_request_logic():
    """Test get_locale_from_request logic"""
    # 1. Query param
    mock_request = MagicMock()
    mock_request.query_params = {"lang": "cs"}
    assert I18nHelper.get_locale_from_request(mock_request) == "cs"
    
    # 2. Accept-Language header
    mock_request.query_params = {}
    mock_request.headers = {"Accept-Language": "cs,en-US;q=0.9"}
    assert I18nHelper.get_locale_from_request(mock_request) == "cs"
    
    # 3. Default
    mock_request.headers = {}
    assert I18nHelper.get_locale_from_request(mock_request) == "en"

def test_get_i18n_value_logic():
    """Test get_i18n_value logic"""
    d = {"en": "Hello", "cs": "Ahoj"}
    assert I18nHelper.get_i18n_value(d, "cs") == "Ahoj"
    assert I18nHelper.get_i18n_value(d, "en") == "Hello"
    assert I18nHelper.get_i18n_value({"en": "Only"}, "cs") == "Only"
    assert I18nHelper.get_i18n_value(None, "cs", fallback_value="Default") == "Default"

def test_set_i18n_value_logic():
    """Test set_i18n_value logic"""
    assert I18nHelper.set_i18n_value(None, "en", "Task") == {"en": "Task"}
    assert I18nHelper.set_i18n_value({"en": "Task"}, "cs", "Ukol") == {"en": "Task", "cs": "Ukol"}

def test_localize_dict_logic():
    """Test localize_dict logic"""
    data = {
        "title": "Orig",
        "title_i18n": {"en": "EnTitle", "cs": "CsTitle"},
        "other": "Keep"
    }
    loc = I18nHelper.localize_dict(data, "cs", ["title"])
    assert loc["title"] == "CsTitle"
    assert loc["other"] == "Keep"

def test_get_translation_function():
    """Test get_translation top-level function"""
    assert get_translation("cs", "tasks.create") == "Vytvořit úkol"
    assert get_translation("en", "tasks.create") == "Create Task"
    assert get_translation("en", "non.existent", "Def") == "Def"
    assert get_translation("en", "non.existent") == "non.existent"
