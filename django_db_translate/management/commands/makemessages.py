import logging
import tempfile
import os
import polib

from django.apps import apps
from django.core.management.commands.makemessages import (
    Command as MMCommand,
    check_programs
)

from django_db_translate.translations.query import DBTranslateQueryManager, DBTranslationString

logger = logging.getLogger(__name__)


class Command(MMCommand):
    _db_temp_file = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--include-db-strings",
            action="store_true",
            help="Include strings from database columns marked as translatable."
        )
        parser.add_argument(
            "--keep-db-strings",
            action="store_true",
            help="Keep generated temporary file used for database strings after making messages." +\
            " Useful for debugging"
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]

        # Check for all programs before pulling anything from the database.
        # `check_programs` raises `CommandError` when a program is not found.
        # The command caller handles this Exception, so we should not catch
        # it here.
        check_programs(
            "msguniq",
            "msgmerge",
            "msgattrib",
            "xgettext",
        )

        if options["include_db_strings"]:
            self._extract_db_strings()

        super().handle(*args, **options)

        if self._db_temp_file:
            if not options["keep_db_strings"]:
                os.unlink(self._db_temp_file.name)
            elif self.verbosity > 0:
                self.stdout.write(f"Keeping generated database string file: {self._db_temp_file.name}")

    def _extract_db_strings(self):

        # Get all models that have an actionable `translatable_fields` attribute defined
        models = {
            model: fields
            for app in apps.get_app_configs()
            for model in app.get_models()
            if ((fields := getattr(model, "translatable_fields", None)))
        }

        # Pull the values from each model and add to the list
        strings: list[str] = []
        for model, fields in models.items():

            manager_cls = getattr(model, "dbtranslate_query_manager", DBTranslateQueryManager)
            if not issubclass(manager_cls, DBTranslateQueryManager):
                logger.warning(
                    f"'dbtranslate_query_manager' for {model.__name__} must be a " +
                    "subclass of django_db_translate.translations.query.DBTranslateQueryManager. " +
                    "Falling back to default."
                )
                manager_cls = DBTranslateQueryManager

            model_strings = manager_cls(model, fields)._get_strings()
            # strings.extend(model_strings)

            # Should we do this in the QueryManager?
            for s in model_strings:
                # Wrap the string with the xgettext keywords
                if isinstance(s, str) and s:
                    strings.append(
                        'gettext(%r)' % polib.escape(s)
                    )
                elif isinstance(s, tuple) and len(s) == 2:
                    strings.append(
                        'pgettext(%r, %r)' % (polib.escape(s[1]), polib.escape(s[0]))
                    )
                else:
                    if self.verbosity > 1:
                        self.stderr.write(
                            f"database string value of {s} must be either a string or a two " +
                            "string value tuple"
                        )

        if len(strings) == 0:
            # Nothing to do, do return early
            if self.verbosity > 1:
                self.stdout.write("No strings marked for translation were found in the database.")
            return

        # Create a temporary `.py` file in this directory so `xgettext`
        #  will look through it for strings
        # TODO: (at a later time) figure out a custom extension. (i.e .dbstrings)
        self._db_temp_file = tempfile.NamedTemporaryFile(
            "w",
            suffix=".py",
            dir=".",
            delete_on_close=False,
            delete=False
        )
        self._db_temp_file.write('\n'.join(strings))
        self._db_temp_file.close()
