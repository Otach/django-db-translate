import logging

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from django_db_translate.admin.forms import TranslationFormSet
from django_db_translate.translations import registry, EntryKeyIdentifier

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

@permission_required("dbtranslate.administrate_translations")
def refresh_registry(request, locale):
    locale_obj = registry.registry.get(locale)

    if not locale_obj:
        messages.add_message(
            request,
            messages.ERROR,
            f"No registry entry for locale '{locale}' found."
        )
    else:
        try:
            locale_obj._invalidate()
            if not locale_obj.entries:  # Calling this propery loads the entries
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Locale ({locale}) reload was successful, but there were no entries."
                )
            else:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Registry for locale ({locale}) refreshed successfully."
                )
        except Exception as e:
            logger.exception(f"Error refreshing registry for locale {locale}", exc_info=e)
            messages.add_message(
                request,
                messages.ERROR,
                f"Error occurred during locale ({locale}) refresh. Check logs for details."
            )

    return redirect(
        reverse(f"admin:locale_view_{locale}")
    )

