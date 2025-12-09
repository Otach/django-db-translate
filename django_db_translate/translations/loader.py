import logging
import pathlib
import polib

from django.conf import settings

logger = logging.getLogger(__name__)
_language_map = {x[0]: x[1] for x in settings.LANGUAGES}


class LocaleInfo:

    def __init__(self, locale: str, locale_file: pathlib.Path | None = None):
        self.locale = locale
        self.locale_files = [locale_file] if locale_file else list()
        self._po_files = {}
        self._entries = []

    def add_locale_file(self, locale_file: pathlib.Path) -> None:
        self.locale_files.append(locale_file)

    @property
    def entries(self) -> list[polib.POEntry]:
        if not self._entries:
            self._load()
            for _, po in self._po_files.items():
                self._entries.extend(iter(po))
        return self._entries

    @property
    def admin_url(self) -> str:
        return "dbtranslate/%s/" % self.locale

    @property
    def fullname(self) -> str:
        return _language_map.get(self.locale, self.locale)

    def _load(self):
        if not self._po_files:
            for lf in self.locale_files:
                po = polib.pofile(lf)
                self._po_files[lf] = po

        return

    def _save(self):
        for filepath, pofile in self._po_files.items():
            pofile.save(filepath)

        # Invalidate the currently loaded .po files
        self._po_files = {}
        self._entries = []


class TranslationRegistry:

    def __init__(self):
        self._registry = None
        if not isinstance(settings.LOCALE_PATHS, list) or len(settings.LOCALE_PATHS) == 0:
            logger.warning("'LOCALE_PATHS' django settings must be a list of " + \
                "directories containing your project's locale files.")

    @property
    def registry(self) -> dict[str, LocaleInfo]:
        if self._registry is None:
            self._registry = self._load_po_paths()

        return self._registry

    @property
    def available_locales_codes(self):
        defined_locales = sorted(self.registry.keys())
        if settings.LANGUAGE_CODE not in defined_locales:
            return [settings.LANGUAGE_CODE, *defined_locales]
        return defined_locales

    @property
    def available_locales(self):
        ...


    def _load_po_paths(self) -> dict[str, LocaleInfo]:
        project_locale_paths = []
        if not isinstance(settings.LOCALE_PATHS, list) or len(settings.LOCALE_PATHS) == 0:
            return {}

        for locale_dir in settings.LOCALE_PATHS:
            project_locale_paths.extend(sorted(locale_dir.rglob(f"**/*.po")))

        locale_map = {}
        for plp in project_locale_paths:
            # We assume filepaths will be in django's standard format:
            # `{settings.LOCAL_PATHS[i]}/<locale>/LC_MESSAGES/django.po`
            locale = plp.parts[-3]
            if locale not in locale_map:
                locale_map[locale] = LocaleInfo(locale)

            locale_map[locale].add_locale_file(plp)

        return locale_map
