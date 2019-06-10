import mf2py
import requests
import uuid

from dateutil.parser import parse

from django.db import models
from django.urls import reverse

from .resolution import get_webmention_endpoint


class WebMentionResponse(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=6
    )
    response_body = models.TextField()
    response_to = models.URLField()
    source = models.URLField()
    reviewed = models.BooleanField(default=False)
    current = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    status_code = models.CharField(max_length=3)

    class Meta:
        unique_together = ["response_to", "source"]
        verbose_name = "webmention"
        verbose_name_plural = "webmentions"

    def __str__(self):
        return self.source

    def get_absolute_url(self):
        return reverse("webmention:status", kwargs={"uuid": self.id})

    def source_for_admin(self):
        return '<a href="{href}">{href}</a>'.format(href=self.source)

    source_for_admin.allow_tags = True
    source_for_admin.short_description = "source"

    def response_to_for_admin(self):
        return '<a href="{href}">{href}</a>'.format(href=self.response_to)

    response_to_for_admin.allow_tags = True
    response_to_for_admin.short_description = "response to"

    def invalidate(self):
        if self.date_created:
            self.current = False
            self.save()

    def update(self, source, target, response):
        self.status_code = response.status_code
        self.response_body = response.content.decode("utf-8")
        self.source = source
        self.response_to = target
        self.current = True
        self.save()

    def parse_response_body(self):
        data = mf2py.parse(doc=self.response_body)
        webmention = {}

        items = data.get("items")

        if len(items) > 0:
            item = items[0]
            item_props = item.get("properties")

            webmention["type"] = item["type"][0]
            webmention["name"] = item_props["name"]

            author = item_props["author"][0]
            author_props = author.get("properties")

            webmention["author"] = {"type": author.get("type")[-1]}

            for key in author_props.keys():
                webmention["author"][key] = author_props.get(key)[-1]

            for key in item_props.keys():
                value = item_props.get(key)[-1]
                if key == "published":
                    value = parse(value)
                if key == "content":
                    value = value["html"]
                webmention[key] = value

        return webmention

    def save(self, *args, **kwargs):
        resp = requests.get(self.source)

        self.status_code = resp.status_code
        self.response_body = resp.content.decode("utf-8")

        super().save(*args, **kwargs)

    def send_webmention(self):
        url = get_webmention_endpoint(self.response_to)

        if not url:
            return

        resp = requests.post(
            url, {"target": self.response_to, "source": self.source}
        )

        self.update(self.source, self.response_to, resp)

        return resp
