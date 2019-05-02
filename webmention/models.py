import mf2py

from dateutil.parser import parse

from django.db import models


# make rendering a method instead of template tag
class WebMentionResponse(models.Model):
    response_body = models.TextField()
    response_to = models.URLField()
    source = models.URLField()
    reviewed = models.BooleanField(default=False)
    current = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "webmention"
        verbose_name_plural = "webmentions"

    def __str__(self):
        return self.source

    def source_for_admin(self):
        return '<a href="{href}">{href}</a>'.format(href=self.source)

    source_for_admin.allow_tags = True
    source_for_admin.short_description = "source"

    def response_to_for_admin(self):
        return '<a href="{href}">{href}</a>'.format(href=self.response_to)

    response_to_for_admin.allow_tags = True
    response_to_for_admin.short_description = "response to"

    def invalidate(self):
        if self.id:
            self.current = False
            self.save()

    def update(self, source, target, response_body):
        self.response_body = response_body
        self.source = source
        self.response_to = target
        self.current = True
        self.save()

    def parse_response_body(self):
        data = mf2py.parse(doc=self.response_body)
        webmention = {}

        item = data["items"][0]
        item_props = item["properties"]

        webmention["type"] = item["type"][0]
        webmention["name"] = item_props["name"]

        author = item_props["author"][0]

        webmention["author"] = {
            "type": author["type"][0],
            "name": author["properties"]["name"][0],
            "url": author["properties"]["url"][0],
        }

        webmention["summary"] = item_props["summary"][0]
        webmention["published"] = parse(item_props["published"][0])
        webmention["content"] = item_props["content"][0]["html"]

        return webmention
