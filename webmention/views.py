import logging

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

from .models import WebMentionResponse
from .forms import WebMentionForm, ProcessWebMentionResponseForm
from .resolution import (
    url_resolves,
    fetch_and_validate_source,
    SourceFetchError,
    TargetNotFoundError,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def receive(request):
    if "source" in request.POST and "target" in request.POST:
        source = request.POST.get("source")
        target = request.POST.get("target")

        form_data = {"source": source, "response_to": target}
        form = WebMentionForm(form_data)

        if not form.is_valid():
            error_string = [
                "{}".format(form.errors.get(key)[0])
                for key in form.errors.keys()
            ]
            try:
                webmention = WebMentionResponse.objects.get(
                    source=source, response_to=target
                )
                webmention.invalidate()
            except WebMentionResponse.DoesNotExist:
                pass
            return HttpResponseBadRequest("\n".join(error_string))

        webmention, _ = WebMentionResponse.objects.get_or_create(
            source=source, response_to=target
        )

        try:
            response = fetch_and_validate_source(source, target)
            webmention.update(source, target, response)
            return HttpResponse("The webmention was successfully received")
        except (SourceFetchError, TargetNotFoundError) as e:
            webmention.invalidate()
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            logger.error(str(e))
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


class WebmentionFormMixin(object):
    form_class = WebMentionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context


class WebmentionCreateView(CreateView):
    model = WebMentionResponse
    form_class = WebMentionForm
    template_name = "webmention/webmention_form.html"

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.model.objects.get(
                source=request.POST.get("source"),
                response_to=request.POST.get("response_to"),
            )
        except self.model.DoesNotExist:
            self.object = None

        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

        # return super().post(request, *args, **kwargs)


class WebmentionStatus(DetailView):
    model = WebMentionResponse
    pk_url_kwarg = "uuid"
    template_name = "webmention/webmention_status.html"
