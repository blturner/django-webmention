import requests

from urllib.parse import urljoin, urlparse

from django.contrib.flatpages.views import flatpage
from django.http import Http404

try:
    from django.core.urlresolvers import resolve, Resolver404
except ImportError:
    from django.urls import resolve, Resolver404

from bs4 import BeautifulSoup


def url_resolves(url, request=None):
    path = urlparse(url).path
    try:
        resolve(path)
    except Resolver404:
        try:
            flatpage(request, path)
        except Http404:
            return False
    return True


def fetch_and_validate_source(source, target):
    response = requests.get(source)
    if response.status_code == 200:
        if target in str(response.content):
            return response
        else:
            raise TargetNotFoundError("Source URL did not contain target URL")
    else:
        raise SourceFetchError("Could not fetch source URL")


def get_webmention_endpoint(target):
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
        raise WebmentionEndpointNotFoundError(
            "No webmention endpoint could be found for the target URL."
        )

    parsed_endpoint = urlparse(endpoint)

    if not parsed_endpoint.netloc:
        endpoint = urljoin(target, endpoint)

    return endpoint


class SourceFetchError(Exception):
    pass


class TargetNotFoundError(Exception):
    pass


class WebmentionEndpointNotFoundError(Exception):
    pass
