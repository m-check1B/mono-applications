"""
Backend Internationalization (i18n) Module

Provides translation functionality for error messages, validation messages,
and other backend text that needs to be localized.
"""

from enum import Enum
from typing import Any


class SupportedLocale(str, Enum):
    """Supported locales"""
    EN = "en"
    ES = "es"
    CS = "cs"


# Translation dictionaries
TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Error messages
        "error.not_found": "Resource not found",
        "error.unauthorized": "Unauthorized access",
        "error.forbidden": "Forbidden",
        "error.bad_request": "Bad request",
        "error.internal_server": "Internal server error",
        "error.validation_failed": "Validation failed",
        "error.duplicate_entry": "Duplicate entry",
        "error.invalid_credentials": "Invalid credentials",

        # Validation messages
        "validation.required": "{field} is required",
        "validation.invalid_email": "Invalid email address",
        "validation.invalid_phone": "Invalid phone number",
        "validation.min_length": "{field} must be at least {min} characters",
        "validation.max_length": "{field} must be at most {max} characters",
        "validation.invalid_format": "Invalid format for {field}",

        # Success messages
        "success.created": "{resource} created successfully",
        "success.updated": "{resource} updated successfully",
        "success.deleted": "{resource} deleted successfully",

        # Campaign messages
        "campaign.started": "Campaign started",
        "campaign.paused": "Campaign paused",
        "campaign.completed": "Campaign completed",
        "campaign.no_contacts": "No contacts available for campaign",

        # Call messages
        "call.connected": "Call connected",
        "call.disconnected": "Call disconnected",
        "call.failed": "Call failed",
        "call.no_agents": "No agents available",

        # Recording messages
        "recording.started": "Recording started",
        "recording.stopped": "Recording stopped",
        "recording.not_found": "Recording not found",

        # IVR messages
        "ivr.flow_started": "IVR flow started",
        "ivr.invalid_input": "Invalid input received",
        "ivr.timeout": "Input timeout",

        # Agent messages
        "agent.status_changed": "Agent status changed to {status}",
        "agent.not_available": "Agent not available",
        "agent.assigned": "Agent assigned to call",
    },
    "es": {
        # Error messages
        "error.not_found": "Recurso no encontrado",
        "error.unauthorized": "Acceso no autorizado",
        "error.forbidden": "Prohibido",
        "error.bad_request": "Solicitud incorrecta",
        "error.internal_server": "Error interno del servidor",
        "error.validation_failed": "Validación fallida",
        "error.duplicate_entry": "Entrada duplicada",
        "error.invalid_credentials": "Credenciales inválidas",

        # Validation messages
        "validation.required": "{field} es obligatorio",
        "validation.invalid_email": "Dirección de correo electrónico inválida",
        "validation.invalid_phone": "Número de teléfono inválido",
        "validation.min_length": "{field} debe tener al menos {min} caracteres",
        "validation.max_length": "{field} debe tener como máximo {max} caracteres",
        "validation.invalid_format": "Formato inválido para {field}",

        # Success messages
        "success.created": "{resource} creado exitosamente",
        "success.updated": "{resource} actualizado exitosamente",
        "success.deleted": "{resource} eliminado exitosamente",

        # Campaign messages
        "campaign.started": "Campaña iniciada",
        "campaign.paused": "Campaña pausada",
        "campaign.completed": "Campaña completada",
        "campaign.no_contacts": "No hay contactos disponibles para la campaña",

        # Call messages
        "call.connected": "Llamada conectada",
        "call.disconnected": "Llamada desconectada",
        "call.failed": "Llamada fallida",
        "call.no_agents": "No hay agentes disponibles",

        # Recording messages
        "recording.started": "Grabación iniciada",
        "recording.stopped": "Grabación detenida",
        "recording.not_found": "Grabación no encontrada",

        # IVR messages
        "ivr.flow_started": "Flujo IVR iniciado",
        "ivr.invalid_input": "Entrada inválida recibida",
        "ivr.timeout": "Tiempo de espera agotado",

        # Agent messages
        "agent.status_changed": "Estado del agente cambiado a {status}",
        "agent.not_available": "Agente no disponible",
        "agent.assigned": "Agente asignado a la llamada",
    },
    "cs": {
        # Error messages
        "error.not_found": "Zdroj nenalezen",
        "error.unauthorized": "Neautorizovaný přístup",
        "error.forbidden": "Zakázáno",
        "error.bad_request": "Chybný požadavek",
        "error.internal_server": "Interní chyba serveru",
        "error.validation_failed": "Validace selhala",
        "error.duplicate_entry": "Duplicitní záznam",
        "error.invalid_credentials": "Neplatné přihlašovací údaje",

        # Validation messages
        "validation.required": "{field} je povinné",
        "validation.invalid_email": "Neplatná e-mailová adresa",
        "validation.invalid_phone": "Neplatné telefonní číslo",
        "validation.min_length": "{field} musí mít alespoň {min} znaků",
        "validation.max_length": "{field} může mít maximálně {max} znaků",
        "validation.invalid_format": "Neplatný formát pro {field}",

        # Success messages
        "success.created": "{resource} úspěšně vytvořen",
        "success.updated": "{resource} úspěšně aktualizován",
        "success.deleted": "{resource} úspěšně smazán",

        # Campaign messages
        "campaign.started": "Kampaň spuštěna",
        "campaign.paused": "Kampaň pozastavena",
        "campaign.completed": "Kampaň dokončena",
        "campaign.no_contacts": "Pro kampaň nejsou k dispozici žádné kontakty",

        # Call messages
        "call.connected": "Hovor připojen",
        "call.disconnected": "Hovor odpojen",
        "call.failed": "Hovor selhal",
        "call.no_agents": "Nejsou k dispozici žádní agenti",

        # Recording messages
        "recording.started": "Nahrávání zahájeno",
        "recording.stopped": "Nahrávání zastaveno",
        "recording.not_found": "Nahrávka nenalezena",

        # IVR messages
        "ivr.flow_started": "IVR tok spuštěn",
        "ivr.invalid_input": "Přijat neplatný vstup",
        "ivr.timeout": "Časový limit vypršel",

        # Agent messages
        "agent.status_changed": "Stav agenta změněn na {status}",
        "agent.not_available": "Agent není k dispozici",
        "agent.assigned": "Agent přiřazen k hovoru",
    }
}


class Translator:
    """Translator class for backend i18n"""

    def __init__(self, locale: SupportedLocale = SupportedLocale.EN):
        self.locale = locale

    def set_locale(self, locale: SupportedLocale):
        """Set the current locale"""
        self.locale = locale

    def translate(self, key: str, **params: Any) -> str:
        """
        Translate a key to the current locale

        Args:
            key: Translation key (e.g., "error.not_found")
            **params: Parameters to interpolate into the translation

        Returns:
            Translated string
        """
        translations = TRANSLATIONS.get(self.locale.value, TRANSLATIONS["en"])
        text = translations.get(key, key)

        # Replace parameters
        if params:
            try:
                text = text.format(**params)
            except KeyError:
                # If parameter not found, return text as-is
                pass

        return text

    def t(self, key: str, **params: Any) -> str:
        """Shorthand for translate"""
        return self.translate(key, **params)


# Global translator instance
_translator = Translator()


def get_translator() -> Translator:
    """Get the global translator instance"""
    return _translator


def set_locale(locale: SupportedLocale):
    """Set the global locale"""
    _translator.set_locale(locale)


def translate(key: str, locale: SupportedLocale | None = None, **params: Any) -> str:
    """
    Translate a key

    Args:
        key: Translation key
        locale: Optional locale override
        **params: Parameters to interpolate

    Returns:
        Translated string
    """
    if locale:
        # Create temporary translator with specific locale
        temp_translator = Translator(locale)
        return temp_translator.translate(key, **params)

    return _translator.translate(key, **params)


def t(key: str, locale: SupportedLocale | None = None, **params: Any) -> str:
    """Shorthand for translate"""
    return translate(key, locale, **params)
