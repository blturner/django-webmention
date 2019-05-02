from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def render_webmention(webmention):
    context = {"webmention": webmention.parse_response_body()}
    return render_to_string("webmention/render_webmention.html", context)
