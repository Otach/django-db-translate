from django.forms import formset_factory
from django import forms


class TranslationForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    raw_string = forms.CharField(widget=forms.Textarea({"rows": 2}), disabled=True)
    translated = forms.CharField(widget=forms.Textarea({"rows": 2}), required=False)


TranslationFormSet = formset_factory(TranslationForm, extra=0)
