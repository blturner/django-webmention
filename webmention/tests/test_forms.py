import httpretty

from django.test import TestCase

from ..forms import SentWebMentionForm


class SentWebMentionFormTestCase(TestCase):
    def setUp(self):
        form_class = SentWebMentionForm

        target = "https://webmention-target.com/webmention"
        source = "https://webmention-source.com/content"

        data = {"response_to": target, "source": source}

        self.target = target
        self.form = form_class(data)

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

    @httpretty.activate
    def test_link_header_absolute_url(self):
        """
        https://webmention.rocks/test/2
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "Link": "<https://webmention-target.com/absolute/webmention>; rel='webmention'"
            },
        )
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/absolute/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

    @httpretty.activate
    def test_link_tag_absolute(self):
        """
        https://webmention.rocks/test/4
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='webmention' href='https://webmention.rocks/test/4'></head></html>",
        )
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention.rocks/test/4",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/test/5",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

    @httpretty.activate
    def test_anchor_tag_absolute(self):
        """
        https://webmention.rocks/test/6
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><a href='https://webmention.rocks/test/5' rel='webmention'>webmention</a></html>",
        )
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention.rocks/test/5",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

    @httpretty.activate
    def test_link_header_first(self):
        """
        https://webmention.rocks/test/11
        """
        httpretty.register_uri(
            httpretty.HEAD,
            self.target,
            adding_headers={
                "Link": "</relative/webmention>; rel='webmention'"
            },
        )
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            adding_headers={
                "Link": "</relative/webmention>; rel='webmention'"
            },
            body="<html><head><link rel='webmention' href='/nope'></head><body><a href='/nope' rel='webmention'>webmention</a></body></html>",
        )
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

    @httpretty.activate
    def test_naive_link_tag_rel_matching(self):
        """
        https://webmention.rocks/test/12
        """
        httpretty.register_uri(httpretty.HEAD, self.target)
        httpretty.register_uri(
            httpretty.GET,
            self.target,
            body="<html><head><link rel='not-webmention' href='/nope'></head><body><a href='https://webmention-target.com/relative/webmention' rel='webmention'>webmention</a></body></html>",
        )
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/relative/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/22/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")

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
        httpretty.register_uri(
            httpretty.POST,
            "https://webmention-target.com/redirected/webmention",
            body="you did it",
        )

        self.assertTrue(self.form.is_valid())

        saved = self.form.save()

        self.assertEqual(saved.response_body, "you did it")
