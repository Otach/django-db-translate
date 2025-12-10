from django.forms import formset_factory
from django import forms

import polib

from django_db_translate.translations import EntryKeyIdentifier


class TranslationForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())

    # We use hidden inputs here on the form to retain data on failed form POSTS
    msgid = forms.CharField(required=False, widget=forms.HiddenInput())
    comment = forms.CharField(required=False, widget=forms.HiddenInput())
    msgctxt = forms.CharField(required=False, widget=forms.HiddenInput())

    msgstr = forms.CharField(
        widget=forms.Textarea({
            "rows": 3,
            "placeholder": "Enter Translation Here..."
        }),
        required=False
    )

    tcomment = forms.CharField(
        widget=forms.Textarea({
            "rows": 2,
            "placeholder": "Translator Comment"
        }),
        required=False
    )

    def _escape_string(self, _input: str | None) -> str:
        if _input is None:
            return ""

        return polib.escape(_input)

    def clean(self):
        cleaned_data = super().clean()

        for field_name in ("translated", "tcomment"):
            self.cleaned_data[field_name] = self._escape_string(self.cleaned_data.get(field_name))
        self.cleaned_data["entry_key"] = EntryKeyIdentifier.from_cleaned_data(self.cleaned_data)

        return cleaned_data


TranslationFormSet = formset_factory(TranslationForm, extra=0)
