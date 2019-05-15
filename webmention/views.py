from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponse,
)
from django.views.generic import CreateView, DetailView

from .models import WebMentionResponse
from .forms import SentWebMentionForm, WebMentionForm
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

            response_body = fetch_and_validate_source(source, target)
            webmention.update(source, target, response_body)
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


class WebmentionStatus(DetailView):
    model = WebMentionResponse
    slug_field = "status_key"
    slug_url_kwarg = "status_key"
    template_name = "webmention/webmention_status.html"


class SendWebMentionView(CreateView):
    model = WebMentionResponse
    form_class = SentWebMentionForm
    template_name = "webmention/sentwebmention_form.html"
