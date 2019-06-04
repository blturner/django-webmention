from django import forms

from .models import WebMentionResponse


class WebMentionForm(forms.ModelForm):
    response_to = forms.URLField(widget=forms.HiddenInput)

    class Meta:
        model = WebMentionResponse
        fields = ("source", "response_to")


class ProcessWebMentionResponseForm(forms.ModelForm):
    response_to = forms.URLField(widget=forms.HiddenInput)
    source = forms.URLField(widget=forms.HiddenInput)

    class Meta:
        model = WebMentionResponse
        fields = ("source", "response_to")
