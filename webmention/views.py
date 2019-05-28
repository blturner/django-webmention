from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponse,
    HttpResponseRedirect,
)
from django.views.generic import CreateView, DetailView
from django.forms import modelformset_factory
from django.shortcuts import render
from django.urls import reverse

from .models import WebMentionResponse
from .forms import WebMentionForm, ProcessWebMentionResponseForm
from .resolution import (
    url_resolves,
    fetch_and_validate_source,
    SourceFetchError,
    TargetNotFoundError,
)


@csrf_exempt
@require_POST
def receive(request):
    if "source" in request.POST and "target" in request.POST:
        source = request.POST.get("source")
        target = request.POST.get("target")
        webmention = None

        if not url_resolves(target, request=request):
            return HttpResponseBadRequest(
                "Target URL did not resolve to a resource on the server"
            )

        try:
            try:
                webmention = WebMentionResponse.objects.get(
                    source=source, response_to=target
                )
            except WebMentionResponse.DoesNotExist:
                webmention = WebMentionResponse()

            response = fetch_and_validate_source(source, target)
            webmention.update(source, target, response)
            return HttpResponse("The webmention was successfully received")
        except (SourceFetchError, TargetNotFoundError) as e:
            webmention.invalidate()
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            return HttpResponseServerError(str(e))
    else:
        return HttpResponseBadRequest(
            "webmention source and/or target not in request"
        )


def process_webmentions(request):
    redirect_to = request.META.get("HTTP_REFERER")
    WebMentionResponseFormSet = modelformset_factory(
        WebMentionResponse, form=ProcessWebMentionResponseForm
    )

    if request.method == "POST":
        formset = WebMentionResponseFormSet(request.POST)

        if formset.is_valid():
            instances = formset.save()

            if not instances:
                instances = [form.instance for form in formset.forms]

            for instance in instances:
                instance.send_webmention()

    return HttpResponseRedirect(redirect_to)

    # formset = WebMentionResponseFormSet()
    # return render(
    #     request, "webmention/process_webmentions.html", {"formset": formset}
    # )


class WebmentionCreateView(CreateView):
    model = WebMentionResponse
    form_class = WebMentionForm
    template_name = "webmention/webmention_form.html"

    def get_form_kwargs(self):
        """
        Sets the request on the form in order to use request.build_absolute_uri.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(
            source=request.POST.get("source"),
            response_to=request.POST.get("response_to"),
        )

        return super().post(request, *args, **kwargs)


class WebmentionStatus(DetailView):
    model = WebMentionResponse
    pk_url_kwarg = "uuid"
    template_name = "webmention/webmention_status.html"
