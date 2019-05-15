import requests

from urllib.parse import urlparse

from django.contrib.flatpages.views import flatpage
from django.http import Http404

try:
    from django.core.urlresolvers import resolve, Resolver404
except ImportError:
    from django.urls import resolve, Resolver404


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
            return response.content
        else:
            raise TargetNotFoundError("Source URL did not contain target URL")
    else:
        raise SourceFetchError("Could not fetch source URL")


class SourceFetchError(Exception):
    pass


class TargetNotFoundError(Exception):
    pass
