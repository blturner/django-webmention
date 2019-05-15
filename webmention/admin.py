from django.contrib import admin

from .models import WebMentionResponse


class WebMentionResponseAdmin(admin.ModelAdmin):
    model = WebMentionResponse

    fields = [
        "status_key",
        ("source_for_admin", "response_to_for_admin"),
        "response_body",
        ("date_created", "date_modified"),
        ("reviewed", "current"),
    ]

    readonly_fields = [
        "response_body",
        "source_for_admin",
        "response_to_for_admin",
        "date_created",
        "date_modified",
        "current",
        "status_key",
    ]

    list_display = [
        "status_key",
        "source_for_admin",
        "response_to_for_admin",
        "status_code",
        "date_created",
        "date_modified",
        "reviewed",
        "current",
    ]

    list_editable = ["reviewed"]

    list_filter = ["reviewed", "current"]

    date_hierarchy = "date_modified"


admin.site.register(WebMentionResponse, WebMentionResponseAdmin)
