import httpretty

from unittest.mock import Mock, patch

try:
    from django.core.urlresolvers import Resolver404
except ImportError:
    from django.urls import Resolver404

from django.test import TestCase

from ..resolution import (
    url_resolves,
    fetch_and_validate_source,
    get_webmention_endpoint,
    SourceFetchError,
    TargetNotFoundError,
)


class ResolutionTestCase(TestCase):
    def setUp(self):
        self.source = "http://example.com"
        self.target = "http://mysite.com"

    @patch("webmention.resolution.resolve")
    def test_url_resolves_when_resolves(self, mock_resolve):
        mock_resolve.return_value = "foo"
        self.assertTrue(url_resolves(self.target))

    @patch("webmention.resolution.resolve")
    def test_url_resolves_when_does_not_resolve(self, mock_resolve):
        mock_resolve.side_effect = Resolver404
        self.assertFalse(url_resolves("http://example.com/page"))

    @patch("requests.get")
    def test_fetch_and_validate_source_happy_path(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '<a href="{href}">{href}</a>'.format(
            href=self.target
        )
        mock_get.return_value = mock_response

        self.assertEqual(
            mock_response.content,
            fetch_and_validate_source(self.source, self.target),
        )

    @patch("requests.get")
    def test_fetch_and_validate_source_when_source_unavailable(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        self.assertRaises(
            SourceFetchError,
            fetch_and_validate_source,
            self.source,
            self.target,
        )

    @patch("requests.get")
    def test_fetch_and_validate_source_when_source_does_not_contain_target(
        self, mock_get
    ):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = "foo"
        mock_get.return_value = mock_response

        self.assertRaises(
            TargetNotFoundError,
            fetch_and_validate_source,
            self.source,
            self.target,
        )

    @httpretty.activate
    def test_link_header_relative_url(self):
        """
        https://webmention.rocks/test/1
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "Link": "</relative/webmention>; rel='webmention'"
            },
        )

        expected = "{}/relative/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_header_absolute_url(self):
        """
        https://webmention.rocks/test/2
        """
        link = "{}/absolute/webmention".format(self.target)
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={"Link": "<{}>; rel='webmention'".format(link)},
        )

        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, link)

    @httpretty.activate
    def test_link_tag_relative(self):
        """
        https://webmention.rocks/test/3
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='webmention' href='/webmention'></head></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_tag_absolute(self):
        """
        https://webmention.rocks/test/4
        """
        webmention_endpoint = "{}/test/4".format(self.target)
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='webmention' href='{}'></head></html>".format(
                webmention_endpoint
            ),
        )

        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, webmention_endpoint)

    @httpretty.activate
    def test_anchor_tag_relative(self):
        """
        https://webmention.rocks/test/5
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><a href='/test/5' rel='webmention'>webmention</a></html>",
        )

        expected = "{}/test/5".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_anchor_tag_absolute(self):
        """
        https://webmention.rocks/test/6
        """
        webmention_endpoint = "{}/test/6".format(self.target)
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><a href='{}' rel='webmention'>webmention</a></html>".format(
                webmention_endpoint
            ),
        )

        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, webmention_endpoint)

    @httpretty.activate
    def test_link_header_case_insensitive(self):
        """
        https://webmention.rocks/test/7
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "LinK": "</relative/webmention>; rel='webmention'"
            },
        )

        expected = "{}/relative/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_header_no_quotes(self):
        """
        https://webmention.rocks/test/8
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={"LinK": "</relative/webmention>; rel=webmention"},
        )

        expected = "{}/relative/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_tag_multiple_rel(self):
        """
        https://webmention.rocks/test/9
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='webmention somethingelse' href='/webmention'></head></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_header_multiple_rel(self):
        """
        https://webmention.rocks/test/10
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "LinK": "</relative/webmention>; rel=webmention somethingelse"
            },
        )

        expected = "{}/relative/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_header_first(self):
        """
        https://webmention.rocks/test/11
        """
        webmention_endpoint = "/relative/webmention"
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "Link": "<{}>; rel='webmention'".format(webmention_endpoint)
            },
        )
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            adding_headers={
                "Link": "<{}>; rel='webmention'".format(webmention_endpoint)
            },
            body="<html><head><link rel='webmention' href='/nope'></head><body><a href='/nope' rel='webmention'>webmention</a></body></html>",
        )

        expected = "{}{}".format(self.target, webmention_endpoint)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_naive_link_tag_rel_matching(self):
        """
        https://webmention.rocks/test/12
        """
        webmention_endpoint = "{}/relative/webmention".format(self.target)
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='not-webmention' href='/nope'></head><body><a href='{}' rel='webmention'>webmention</a></body></html>".format(
                webmention_endpoint
            ),
        )

        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, webmention_endpoint)

    @httpretty.activate
    def test_ignore_html_comment(self):
        """
        https://webmention.rocks/test/13
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head></head><body><!--<a href='/nope' rel='webmention'>webmention</a>--><a href='/webmention' rel='webmention'>webmention</a></body></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_ignore_escaped_html(self):
        """
        https://webmention.rocks/test/14
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><body>&lt;a href='/nope' rel='webmention'&gt;&lt;/a&gt;<a href='/webmention' rel='webmention'>webmention</a></body></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_empty_link_tag(self):
        """
        https://webmention.rocks/test/15
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='webmention' href></head></html>",
        )

        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, self.target)

    @httpretty.activate
    def test_document_order_anchor_before_link(self):
        """
        https://webmention.rocks/test/16
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><a href='/webmention' rel='webmention'>webmention</a><link href='/nope' rel='webmention'></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_document_order_link_before_anchor(self):
        """
        https://webmention.rocks/test/17
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><link href='/webmention' rel='webmention'><a href='/nope' rel='webmention'>webmention</a></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_multiple_link_headers(self):
        """
        https://webmention.rocks/test/18
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "Link": "</relative/error>; rel='other'",
                "Link": "</relative/webmention>; rel='webmention'",
            },
        )

        expected = "{}/relative/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_header_multiple_values(self):
        """
        https://webmention.rocks/test/19
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "Link": "</relative/error>; rel='other', </relative/webmention>; rel='webmention'"
            },
        )

        expected = "{}/relative/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_link_tag_no_href(self):
        """
        https://webmention.rocks/test/20
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><link rel='webmention'><a href='/webmention' rel='webmention'>webmention</a></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_preserve_query_string(self):
        """
        https://webmention.rocks/test/21
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><link rel='webmention' href='/webmention?query=yes'></html>",
        )

        expected = "{}/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_relative_to_page(self):
        """
        https://webmention.rocks/test/22
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><link rel='webmention' href='22/webmention'></html>",
        )

        expected = "{}/22/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)

    @httpretty.activate
    def test_follows_redirects(self):
        """
        https://webmention.rocks/test/23
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET, self.target, status=301, location=self.target
        )
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><link href='/redirected/webmention' rel='webmention'></html>",
        )

        expected = "{}/redirected/webmention".format(self.target)
        endpoint = get_webmention_endpoint(self.target)

        self.assertEqual(endpoint, expected)
