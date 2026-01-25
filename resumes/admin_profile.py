# resumes/admin_profile.py
# تم إنشاء هذا الملف لإدارة ملفات تعريف السير الذاتية في لوحة التحكم
from django.contrib import admin
from .models_profile import CandidateResumeProfile

@admin.register(CandidateResumeProfile)
class CandidateResumeProfileAdmin(admin.ModelAdmin):
    """
    إدارة ملفات تعريف السير الذاتية في لوحة التحكم
    """
    list_display = [
        'candidate', 
        'primary_resume_type', 
        'has_uploaded_resume', 
        'has_built_resume', 
        'has_both_resumes_display',
        'is_active_for_matching',
        'last_updated'
    ]
    list_filter = [
        'primary_resume_type',
        'is_active_for_matching',
        'last_updated'
    ]
    search_fields = [
        'candidate__username',
        'candidate__first_name',
        'candidate__last_name',
        'candidate__email'
    ]
    readonly_fields = [
        'last_updated',
        'has_both_resumes_display'
    ]
    
    fieldsets = (
        ('معلومات المرشح', {
            'fields': ('candidate',)
        }),
        ('السير الذاتية', {
            'fields': (
                'uploaded_resume',
                'built_resume',
                'primary_resume_type'
            )
        }),
        ('إعدادات المطابقة', {
            'fields': ('is_active_for_matching',)
        }),
        ('معلومات النظام', {
            'fields': ('last_updated', 'has_both_resumes_display'),
            'classes': ('collapse',)
        })
    )
    
    def has_uploaded_resume(self, obj):
        """عرض ما إذا كان لديه سيرة مرفوعة"""
        return obj.uploaded_resume is not None
    has_uploaded_resume.boolean = True
    has_uploaded_resume.short_description = "سيرة مرفوعة"
    
    def has_built_resume(self, obj):
        """عرض ما إذا كان لديه سيرة مبنية"""
        return obj.built_resume is not None
    has_built_resume.boolean = True
    has_built_resume.short_description = "سيرة مبنية"
    
    def has_both_resumes_display(self, obj):
        """عرض ما إذا كان لديه كلا النوعين"""
        return obj.has_both_resumes()
    has_both_resumes_display.boolean = True
    has_both_resumes_display.short_description = "كلا النوعين"
    
    def get_queryset(self, request):
        """تحسين الاستعلامات"""
        return super().get_queryset(request).select_related(
            'candidate',
            'uploaded_resume',
            'built_resume'
        )
