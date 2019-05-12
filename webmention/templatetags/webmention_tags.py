from django import template
from django.template.loader import render_to_string

from ..forms import WebMentionForm

register = template.Library()


@register.inclusion_tag("webmention/webmention_form.html", takes_context=True)
def webmention_form(context, obj):
    request = context["request"]
    target = obj.get_absolute_url()

    data = {"response_to": request.build_absolute_uri(target)}
    form = WebMentionForm(initial=data)

    context["form"] = form

    return context


@register.simple_tag
def render_webmention(webmention):
    context = {"webmention": webmention.parse_response_body()}
    return render_to_string("webmention/render_webmention.html", context)
