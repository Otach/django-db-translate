import logging

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from django_db_translate.admin.forms import TranslationFormSet
from django_db_translate.translations import EntryKeyIdentifier

logger = logging.getLogger(__name__)


@permission_required("dbtranslate.manage_translations")
def locale_view(request, locale, context_func):

    fs = TranslationFormSet(
        request.POST if request.method == "POST" else None,
        initial=[
            {
                "id": i,
                "msgid": v.msgid,
                "msgstr": v.msgstr,
                "tcomment": v.tcomment,
                "comment": v.comment,
                "msgctxt": v.msgctxt,
            } for i, (_, v) in enumerate(locale.entries.items())
        ]
    )

    if request.method == "POST":
        if fs.is_valid():
            for f in fs:

                # Extract locale entry from the registry
                # If the `entry_key` is None after validation,
                #  then this is an invalid entry (something went
                #  terribly wrong, or arbitrary data was provided
                #  to the form). In this case we don't want to
                #  include it in the .po file
                mapped = True
                if not f.cleaned_data["entry_key"]:
                    mapped = False
                e = locale.entries.get(f.cleaned_data["entry_key"])
                if mapped and e is None:
                    mapped = False

                if not mapped:
                    logger.warning(
                        f"Entry with msgid '{f.cleaned_data.get("msgid")}' could not" +
                        " be mapped to an existing entry in the .po files. Skipping."
                    )
                    continue

                # `e` here is an entry pulled from the registry.
                e.msgstr = f.cleaned_data['msgstr']
                e.tcomment = f.cleaned_data['tcomment']

            locale._save()
            return redirect(
                reverse(f"admin:locale_view_{locale.locale}")
            )

    return render(
        request,
        "db_translate/locale.html",
        {
            "locale": locale,
            "title": f"{locale.fullname} Translation Editing",
            "formset": fs,
            **context_func(request)
        }
    )

