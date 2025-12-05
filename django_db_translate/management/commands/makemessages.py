import tempfile
import os

from django.apps import apps
from django.core.management.commands.makemessages import Command as MMCommand


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

        # Pull the values from each model and add to the set to prevent duplicates
        strings = set()
        for model, fields in models.items():
            row_strings = list(model.objects.values_list(*fields).distinct())
            for row_string in row_strings:
                for s in row_string:
                    strings.add(f'gettext("{str(s)}")')  # Wrap the string with the xgettext keyword

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
