from django.forms import formset_factory
from django import forms


class TranslationForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    raw_string = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    msgctxt = forms.CharField(required=False)
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
