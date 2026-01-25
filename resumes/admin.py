# resumes/admin.py
from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "candidate",
        "created_at",
    )

    readonly_fields = (
        "raw_text",
        "parsed_data",
        "created_at",
    )

    search_fields = (
        "candidate__username",
        "candidate__email",
    )

    list_filter = ("created_at",)

    fieldsets = (
        ("Owner", {
            "fields": ("candidate",),
        }),
        ("File", {
            "fields": ("file",),
        }),
        ("Extracted Text", {
            "fields": ("raw_text",),
        }),
        ("Parsed Data (AI)", {
            "fields": ("parsed_data",),
        }),
        ("Metadata", {
            "fields": ("created_at",),
        }),
    )
