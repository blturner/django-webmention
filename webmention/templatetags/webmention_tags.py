from django import template
from django import forms

from ..models import WebMentionResponse
from ..forms import WebMentionForm, SentWebMentionForm

register = template.Library()


@register.inclusion_tag("webmention/webmention_form.html", takes_context=True)
def webmention_form(context, obj):
    request = context["request"]
    target = obj.get_absolute_url()

    data = {"response_to": request.build_absolute_uri(target)}
    form = WebMentionForm(initial=data)

    context["form"] = form

    return context


@register.inclusion_tag(
    "webmention/send_webmention_form.html", takes_context=True
)
def send_webmention_form(context, obj):
    request = context["request"]
    source = obj.get_absolute_url()

    data = {"source": request.build_absolute_uri(source)}

    form = SentWebMentionForm(initial=data)
    form.fields["source"] = forms.URLField(widget=forms.HiddenInput)

    context["form"] = form

    return context


@register.inclusion_tag("webmention/webmentions.html", takes_context=True)
def webmentions_for_object(context, obj):
    request = context["request"]
    target = request.build_absolute_uri(obj.get_absolute_url())
    webmentions = WebMentionResponse.objects.filter(
        response_to=target, reviewed=True
    )
    context["webmentions"] = [
        webmention.parse_response_body() for webmention in webmentions
    ]
    return context


@register.inclusion_tag("webmention/sent_webmentions.html", takes_context=True)
def sent_webmentions_for_object(context, obj):
    request = context["request"]
    source = request.build_absolute_uri(obj.get_absolute_url())
    context["webmentions"] = WebMentionResponse.objects.filter(source=source)
    return context
