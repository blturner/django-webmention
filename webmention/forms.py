import requests

from django import forms
from django.urls import reverse

from .models import WebMentionResponse


class WebMentionForm(forms.ModelForm):
    response_to = forms.URLField(widget=forms.HiddenInput)

    class Meta:
        model = WebMentionResponse
        fields = ("source", "response_to")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get("source")
        target = cleaned_data.get("response_to")

        if source and target:
            url = self.request.build_absolute_uri(
                reverse("webmention:receive")
            )
            resp = requests.post(url, {"source": source, "target": target})

            if resp.status_code != 202:
                raise forms.ValidationError(resp.content.decode("utf-8"))
