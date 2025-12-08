from django.forms import formset_factory
from django import forms


class TranslationForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    raw_string = forms.CharField()
    comment = forms.CharField()
    msgctxt = forms.CharField()
    translated = forms.CharField(
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


TranslationFormSet = formset_factory(TranslationForm, extra=0)
