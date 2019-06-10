import requests

from django import forms

from .models import WebMentionResponse


class WebMentionForm(forms.ModelForm):
    response_to = forms.URLField(widget=forms.HiddenInput)

    class Meta:
        model = WebMentionResponse
        fields = ("source", "response_to")

    def clean(self):
        cleaned_data = super().clean()

        response_to = cleaned_data.get("response_to")
        source = cleaned_data.get("source")

        if response_to and source:
            resp = requests.get(source)

            if response_to not in str(resp.content):
                raise forms.ValidationError(
                    "Source URL did not contain target URL"
                )

    def clean_response_to(self):
        response_to = self.cleaned_data.get("response_to")

        resp = requests.get(response_to)

        if resp.status_code != requests.codes.ok:
            raise forms.ValidationError(
                "Target URL did not resolve to a resource on the server"
            )

        return response_to

    def clean_source(self):
        source = self.cleaned_data.get("source")

        resp = requests.get(source)

        if resp.status_code != requests.codes.ok:
            raise forms.ValidationError("Could not fetch source URL")

        return source


class ProcessWebMentionResponseForm(forms.ModelForm):
    response_to = forms.URLField(widget=forms.HiddenInput)
    source = forms.URLField(widget=forms.HiddenInput)

    class Meta:
        model = WebMentionResponse
        fields = ("source", "response_to")
