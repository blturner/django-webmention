from django.conf.urls import url

from . import views


app_name = "webmention"


urlpatterns = [
    url(r"^$", views.receive, name="receive"),
    url(r"^send/$", views.process_webmentions, name="send"),
    url(r"^submit/$", views.WebmentionCreateView.as_view(), name="submit"),
    url(
        r"^(?P<uuid>[-\w]+)/$", views.WebmentionStatus.as_view(), name="status"
    ),
]
