from django.conf.urls import url

from . import views


app_name = "webmention"


urlpatterns = [
    url(
        r"^(?P<status_key>[-\w]+)/",
        views.WebmentionStatus.as_view(),
        name="status",
    ),
    url(r"^receive$", views.receive, name="receive"),
    url(r"^send/$", views.SendWebMentionView.as_view(), name="send"),
    url(r"^submit/$", views.WebmentionCreateView.as_view(), name="submit"),
]
