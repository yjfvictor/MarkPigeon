"""
MarkPigeon Internationalization (i18n) Module

Provides multi-language support for the application.
"""

import json
import locale
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class I18n:
    """
    Internationalization manager for MarkPigeon.

    Supports loading translations from JSON files and provides
    a simple interface for translating strings.
    """

    # Supported locales
    SUPPORTED_LOCALES = ["en", "zh_CN"]
    DEFAULT_LOCALE = "en"

    def __init__(self, locales_dir: Path | None = None):
        """
        Initialize the i18n manager.

        Args:
            locales_dir: Directory containing locale JSON files.
                        If None, uses the default locales directory.
        """
        if locales_dir is None:
            # Default to locales directory relative to project root
            # src/core/i18n.py -> src/core -> src -> MarkPigeon
            self.locales_dir = Path(__file__).parent.parent.parent / "locales"
        else:
            self.locales_dir = Path(locales_dir)

        self._translations: dict = {}
        self._current_locale: str = self.DEFAULT_LOCALE
        self._fallback_translations: dict = {}

        # Auto-detect and load system locale
        self._detect_and_load_locale()

    def _detect_and_load_locale(self) -> None:
        """Detect system locale and load appropriate translations."""
        try:
            system_locale, _ = locale.getdefaultlocale()
            if system_locale:
                # Try to match system locale to supported locales
                for supported in self.SUPPORTED_LOCALES:
                    if system_locale.startswith(
                        supported.replace("_", "-")
                    ) or system_locale.startswith(supported):
                        self.load_locale(supported)
                        return

                # Try language code only (e.g., 'zh' from 'zh_CN')
                lang_code = system_locale.split("_")[0].split("-")[0]
                for supported in self.SUPPORTED_LOCALES:
                    if supported.startswith(lang_code):
                        self.load_locale(supported)
                        return
        except Exception as e:
            logger.warning(f"Failed to detect system locale: {e}")

        # Fall back to default
        self.load_locale(self.DEFAULT_LOCALE)

    def load_locale(self, locale_name: str) -> bool:
        """
        Load translations for a specific locale.

        Args:
            locale_name: Name of the locale (e.g., 'en', 'zh_CN')

        Returns:
            True if successfully loaded, False otherwise.
        """
        if locale_name not in self.SUPPORTED_LOCALES:
            logger.warning(f"Unsupported locale: {locale_name}")
            return False

        locale_file = self.locales_dir / f"{locale_name}.json"

        if not locale_file.exists():
            logger.warning(f"Locale file not found: {locale_file}")
            return False

        try:
            with open(locale_file, encoding="utf-8") as f:
                self._translations = json.load(f)
            self._current_locale = locale_name
            logger.info(f"Loaded locale: {locale_name}")

            # Load fallback (English) if not already English
            if locale_name != self.DEFAULT_LOCALE:
                fallback_file = self.locales_dir / f"{self.DEFAULT_LOCALE}.json"
                if fallback_file.exists():
                    with open(fallback_file, encoding="utf-8") as f:
                        self._fallback_translations = json.load(f)

            return True
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in locale file {locale_file}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load locale {locale_name}: {e}")
            return False

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current locale.

        Args:
            key: Dot-separated key path (e.g., 'app.title', 'messages.success')
            **kwargs: Format arguments for string interpolation

        Returns:
            Translated string, or the key itself if not found.
        """
        # Navigate through nested keys
        value = self._get_nested_value(self._translations, key)

        # Fallback to English if not found
        if value is None and self._fallback_translations:
            value = self._get_nested_value(self._fallback_translations, key)

        # Return key if still not found
        if value is None:
            logger.debug(f"Translation not found for key: {key}")
            return key

        # Apply format arguments if provided
        if kwargs:
            try:
                return value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format argument for key {key}: {e}")
                return value

        return value

    def _get_nested_value(self, data: dict, key: str) -> str | None:
        """
        Get a value from nested dict using dot-separated key.

        Args:
            data: Dictionary to search
            key: Dot-separated key path

        Returns:
            Value if found, None otherwise.
        """
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None

    @property
    def current_locale(self) -> str:
        """Get the current locale name."""
        return self._current_locale

    @property
    def available_locales(self) -> list:
        """Get list of available locales."""
        available = []
        for loc in self.SUPPORTED_LOCALES:
            locale_file = self.locales_dir / f"{loc}.json"
            if locale_file.exists():
                available.append(loc)
        return available

    def get_locale_display_name(self, locale_name: str) -> str:
        """
        Get human-readable display name for a locale.

        Args:
            locale_name: Locale code (e.g., 'en', 'zh_CN')

        Returns:
            Display name for the locale.
        """
        display_names = {
            "en": "English",
            "zh_CN": "简体中文",
        }
        return display_names.get(locale_name, locale_name)


# Global i18n instance for convenience
_global_i18n: I18n | None = None


def get_i18n() -> I18n:
    """Get the global i18n instance, creating it if necessary."""
    global _global_i18n
    if _global_i18n is None:
        _global_i18n = I18n()
    return _global_i18n


def t(key: str, **kwargs) -> str:
    """
    Convenience function to translate a key using the global i18n instance.

    Args:
        key: Dot-separated key path
        **kwargs: Format arguments

    Returns:
        Translated string.
    """
    return get_i18n().t(key, **kwargs)
