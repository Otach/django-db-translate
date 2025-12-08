from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, reverse

from django_db_translate.admin.forms import TranslationFormSet

@permission_required("dbtranslate.manage_translations")
def locale_view(request, locale, context_func):
    fs = TranslationFormSet(
        request.POST if request.method == "POST" else None,
        initial=[
            {
                "id": i,
                "raw_string": x.msgid,
                "translated": x.msgstr
            } for i, x in enumerate(locale.entries)
        ]
    )

    if request.method == "POST":
        # TODO: Add proper validation and mapping for
        #  PO -> form entries
        if fs.is_valid():
            for e, f in zip(locale.entries, fs):
                e.msgstr = f.cleaned_data['translated']
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

