# jobs/admin.py
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "employer", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "experience_years")
    search_fields = ("title", "description", "employer__username")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("معلومات أساسية", {
            'fields': ('title', 'description', 'is_active')
        }),
        ("متطلبات الوظيفة", {
            'fields': ('required_skills', 'preferred_skills', 'languages', 'education_level', 'experience_years')
        }),
        ("معلومات النظام", {
            'fields': ('employer', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )