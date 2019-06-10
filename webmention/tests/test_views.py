import httpretty

from unittest.mock import Mock, patch

from django.test import TestCase
from django.http import (
    HttpResponseBadRequest,
    HttpResponse,
    HttpResponseServerError,
)

from ..models import WebMentionResponse
from ..views import receive
from ..resolution import SourceFetchError, TargetNotFoundError


class ReceiveTestCase(TestCase):
    def setUp(self):
        self.source = "http://example.com"
        self.target = "http://mysite.com"

    def test_receive_when_source_not_in_post_data(self):
        request = Mock()
        request.method = "POST"
        request.POST = {"target": self.target}

        response = receive(request)

        self.assertTrue(isinstance(response, HttpResponseBadRequest))

    def test_receive_when_target_not_in_post_data(self):
        request = Mock()
        request.method = "POST"
        request.POST = {"source": self.source}

        response = receive(request)

        self.assertTrue(isinstance(response, HttpResponseBadRequest))

    @httpretty.activate
    def test_receive_when_target_does_not_resolve(self):
        httpretty.register_uri(httpretty.GET, self.target, status=404)
        httpretty.register_uri(httpretty.GET, self.source, status=200)

        request = Mock()
        request.method = "POST"
        request.POST = {"source": self.source, "target": self.target}

        response = receive(request)

        self.assertTrue(isinstance(response, HttpResponseBadRequest))
        self.assertEqual(
            response.content.decode("utf-8"),
            "Target URL did not resolve to a resource on the server",
        )

    @httpretty.activate
    def test_receive_happy_path(self):
        httpretty.register_uri(httpretty.GET, self.target, status=200)

        body = '<a href="{}" rel="webmention">webmention</a>'.format(
            self.target
        )

        httpretty.register_uri(
            httpretty.GET, self.source, status=200, body=body
        )

        request = Mock()
        request.method = "POST"
        request.POST = {"source": self.source, "target": self.target}

        response = receive(request)

        self.assertTrue(isinstance(response, HttpResponse))

        webmention = WebMentionResponse.objects.get(
            source=self.source, response_to=self.target
        )

        self.assertEqual(webmention.status_code, "200")
        self.assertEqual(webmention.response_body, body)

    @httpretty.activate
    def test_receive_when_source_unavailable(self,):
        httpretty.register_uri(httpretty.GET, self.source, status=400)
        httpretty.register_uri(httpretty.GET, self.target, status=200)

        request = Mock()
        request.method = "POST"
        request.POST = {"source": self.source, "target": self.target}

        WebMentionResponse.objects.create(
            source=self.source, response_to=self.target, current=True
        )

        response = receive(request)

        webmention = WebMentionResponse.objects.get(
            source=self.source, response_to=self.target
        )

        self.assertTrue(isinstance(response, HttpResponseBadRequest))
        self.assertFalse(webmention.current)

    @httpretty.activate
    def test_receive_when_source_does_not_contain_target(self):
        httpretty.register_uri(httpretty.GET, self.source, status=200)
        httpretty.register_uri(httpretty.GET, self.target, status=200)

        request = Mock()
        request.method = "POST"
        request.POST = {"source": self.source, "target": self.target}

        response = receive(request)

        self.assertTrue(isinstance(response, HttpResponseBadRequest))
        self.assertEqual(
            response.content.decode("utf-8"),
            "Source URL did not contain target URL",
        )

    @patch("webmention.views.fetch_and_validate_source")
    @httpretty.activate
    def test_receive_when_general_exception_occurs(
        self, mock_fetch_and_validate_source
    ):
        body = '<a href="{}" rel="webmention">webmention</a>'.format(
            self.target
        )
        httpretty.register_uri(
            httpretty.GET, self.source, status=200, body=body
        )
        httpretty.register_uri(httpretty.GET, self.target, status=200)

        request = Mock()
        request.method = "POST"
        request.POST = {"source": self.source, "target": self.target}

        mock_fetch_and_validate_source.side_effect = Exception
        response = receive(request)

        mock_fetch_and_validate_source.assert_called_once_with(
            self.source, self.target
        )
        self.assertTrue(isinstance(response, HttpResponseServerError))

    def test_receive_when_source_is_invalid(self):
        source = "kaboom"
        request = Mock()
        request.method = "POST"
        request.POST = {"source": source, "target": self.target}

        response = receive(request)

        self.assertTrue(isinstance(response, HttpResponseBadRequest))
