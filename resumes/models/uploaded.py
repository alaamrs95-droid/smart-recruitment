# resumes/models/uploaded.py
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

User = settings.AUTH_USER_MODEL

class Resume(models.Model):
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'candidate'},
        related_name="resumes"
    )

    file = models.FileField(upload_to="resumes/%Y/%m/%d/", blank=True, null=True,
    validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
)
    original_filename = models.CharField(max_length=255, blank=True)
    raw_text = models.TextField(blank=True)

    parsed_data = models.JSONField(default=dict)

    is_processed = models.BooleanField(default=False)  # للتعامل مع الفشل
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.original_filename or 'Untitled'}"
    
    def get_absolute_url(self):
        """الحصول على الرابط المطلق للسيرة الذاتية"""
        return f"/resumes/{self.id}/"
    
    def save(self, *args, **kwargs):
        """
        عند حفظ السيرة الذاتية المرفوعة، تحديث ملف التعريف الخاص بالمرشح
        """
        super().save(*args, **kwargs)
        
        # تحديث أو إنشاء ملف تعريف المرشح فقط إذا كانت السيرة معالجة
        if self.is_processed:
            from .profile import CandidateResumeProfile
            profile, created = CandidateResumeProfile.objects.get_or_create(
                candidate=self.candidate
            )
            
            # إذا لم تكن هناك سيرة رئيسية أو كانت السيرة المرفوعة هي الرئيسية
            if profile.primary_resume_type == 'uploaded' or not profile.has_resume():
                profile.set_primary_resume('uploaded', self)
    
    def delete(self, *args, **kwargs):
        """
        عند حذف السيرة الذاتية المرفوعة، تحديث ملف التعريف
        """
        # تحديث ملف التعريف إذا كانت هذه هي السيرة الرئيسية
        from .profile import CandidateResumeProfile
        try:
            profile = CandidateResumeProfile.objects.get(candidate=self.candidate)
            if profile.uploaded_resume == self:
                profile.uploaded_resume = None
                # إذا لم يكن هناك سيرة مبنية، قم بتغيير النوع
                if not profile.built_resume:
                    profile.primary_resume_type = 'built'
                profile.save()
        except CandidateResumeProfile.DoesNotExist:
            pass
        
        super().delete(*args, **kwargs)
