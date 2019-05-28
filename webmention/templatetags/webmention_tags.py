import mf2py

from django import template
from django import forms
from django.forms import modelformset_factory

from ..models import WebMentionResponse
from ..forms import (
    WebMentionForm,
    SentWebMentionForm,
    ProcessWebMentionResponseForm,
)

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
def send_webmention_form(context, absolute_url, content):
    request = context["request"]
    source = request.build_absolute_uri(absolute_url)
    mf2data = mf2py.parse(doc=content)

    queryset = WebMentionResponse.objects.filter(source=source)

    try:
        targets = mf2data["rels"]["webmention"]
    except KeyError:
        targets = []

    initial = [
        {"source": source, "response_to": target}
        for target in targets
        if not queryset.filter(response_to=target).exists()
    ]

    WebMentionResponseFormSet = modelformset_factory(
        WebMentionResponse,
        form=ProcessWebMentionResponseForm,
        extra=len(initial),
    )

    context["formset"] = WebMentionResponseFormSet(
        initial=initial, queryset=queryset
    )

    context["webmentions"] = [
        {
            "target": target,
            "webmention": WebMentionResponse.objects.filter(
                source=source, response_to=target
            ).first(),
        }
        for target in targets
    ]

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
