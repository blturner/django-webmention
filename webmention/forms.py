import requests

from urllib.parse import urljoin, urlparse

from django import forms
from django.urls import reverse

from bs4 import BeautifulSoup

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
            if source == target:
                raise forms.ValidationError(
                    "source and target cannot be the same"
                )
            url = self.request.build_absolute_uri(
                reverse("webmention:receive")
            )
            resp = requests.post(url, {"source": source, "target": target})

            if resp.status_code != 200:
                raise forms.ValidationError(resp.content.decode("utf-8"))


class SentWebMentionForm(forms.ModelForm):
    class Meta:
        model = WebMentionResponse
        fields = ("source", "response_to")

    def clean_response_to(self):
        target = self.cleaned_data["response_to"]
        endpoint = None

        resp = requests.head(url=target)

        if resp.links.get("webmention"):
            endpoint = resp.links["webmention"]["url"]

        if not endpoint:
            for key in resp.links.keys():
                if "webmention" in key.split():
                    endpoint = resp.links.get(key)["url"]

        if not endpoint:
            resp = requests.get(url=target)

            parsed_html = BeautifulSoup(resp.content, features="html5lib")

            webmention = parsed_html.find_all(
                ["link", "a"], attrs={"rel": "webmention"}
            )

            filtered = [
                element for element in webmention if element.has_attr("href")
            ]

            endpoint = filtered[0].attrs.get("href") or target

        if not endpoint:
            raise forms.ValidationError(
                "No webmention endpoint could be found for the target URL."
            )

        parsed_endpoint = urlparse(endpoint)

        if not parsed_endpoint.netloc:
            endpoint = urljoin(target, endpoint)

        self.endpoint = endpoint

        return target

    def save(self, commit=True):
        instance = super().save(commit=False)

        resp = requests.post(
            self.endpoint,
            {"target": instance.response_to, "source": instance.source},
        )

        instance.status_code = resp.status_code
        instance.response_body = resp.content.decode("utf-8")

        if commit:
            instance.save()
        return instance
