# resumes/models/profile.py
# تم إنشاء هذا الملف لربط السير الذاتية المرفوعة والمبنية معاً
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CandidateResumeProfile(models.Model):
    """
    نموذج يربط السير الذاتية المرفوعة والمبنية للمرشح
    كل مرشح لديه ملف تعريف واحد فقط يمكن أن يحتوي على سير ذاتية مرفوعة ومبنية
    """
    candidate = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='resume_profile',
        limit_choices_to={'role': 'candidate'},
        verbose_name=_("Candidate")
    )
    
    # السيرة الذاتية المرفوعة (اختياري)
    uploaded_resume = models.ForeignKey(
        'resumes.Resume',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profile_primary',
        verbose_name=_("Uploaded Resume")
    )
    
    # السيرة الذاتية المبنية (اختياري)
    built_resume = models.ForeignKey(
        'resumes.BuiltResume',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profile_primary',
        verbose_name=_("Built Resume")
    )
    
    # نوع السيرة الذاتية الرئيسية (التي ستظهر للمطابقة)
    primary_resume_type = models.CharField(
        max_length=10,
        choices=[
            ('uploaded', _('Uploaded Resume')),
            ('built', _('Built Resume')),
            ('both', _('Both - Prioritize Built')),
        ],
        default='uploaded',
        verbose_name=_("Primary Resume Type"),
        help_text=_("Which resume type to prioritize for matching")
    )
    
    # هل السيرة الذاتية نشطة للمطابقة
    is_active_for_matching = models.BooleanField(
        default=True,
        verbose_name=_("Active for Matching")
    )
    
    # تاريخ آخر تحديث
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))
    
    class Meta:
        verbose_name = _("Candidate Resume Profile")
        verbose_name_plural = _("Candidate Resume Profiles")
        
    def __str__(self):
        return f"{self.candidate.username} - Resume Profile"
    
    def get_primary_resume(self):
        """
        الحصول على السيرة الذاتية الرئيسية للمطابقة
        """
        if self.primary_resume_type == 'built' and self.built_resume:
            return self.built_resume
        elif self.primary_resume_type == 'uploaded' and self.uploaded_resume:
            return self.uploaded_resume
        elif self.primary_resume_type == 'both':
            # إعطاء الأولوية للسيرة المبنية إذا وجدت
            if self.built_resume:
                return self.built_resume
            elif self.uploaded_resume:
                return self.uploaded_resume
        
        # الرجوع إلى أي سيرة ذاتية متاحة
        if self.built_resume:
            return self.built_resume
        elif self.uploaded_resume:
            return self.uploaded_resume
        
        return None
    
    def get_all_resumes(self):
        """
        الحصول على جميع السير الذاتية للمرشح
        """
        resumes = []
        if self.uploaded_resume:
            resumes.append({
                'type': 'uploaded',
                'resume': self.uploaded_resume,
                'title': self.uploaded_resume.original_filename or _("Uploaded Resume"),
                'is_primary': self.primary_resume_type in ['uploaded', 'both']
            })
        
        if self.built_resume:
            resumes.append({
                'type': 'built',
                'resume': self.built_resume,
                'title': self.built_resume.title or _("Built Resume"),
                'is_primary': self.primary_resume_type in ['built', 'both']
            })
        
        return resumes
    
    def get_resume_title(self):
        """
        الحصول على عنوان السيرة الذاتية الرئيسية
        """
        resume = self.get_primary_resume()
        if not resume:
            return _("No Resume")
        
        if hasattr(resume, 'title'):
            return resume.title
        elif hasattr(resume, 'original_filename'):
            return resume.original_filename
        else:
            return _("Untitled Resume")
    
    def get_resume_type_display(self):
        """
        الحصول على عرض نوع السيرة الذاتية
        """
        if self.primary_resume_type == 'built':
            return _("Built Resume")
        elif self.primary_resume_type == 'both':
            return _("Both Resumes")
        else:
            return _("Uploaded Resume")
    
    def set_primary_resume(self, resume_type, resume_instance=None):
        """
        تعيين السيرة الذاتية الرئيسية
        """
        if resume_type == 'built':
            if resume_instance:
                self.built_resume = resume_instance
            self.primary_resume_type = 'built'
        elif resume_type == 'uploaded':
            if resume_instance:
                self.uploaded_resume = resume_instance
            self.primary_resume_type = 'uploaded'
        elif resume_type == 'both':
            self.primary_resume_type = 'both'
        
        self.save()
    
    def has_resume(self):
        """
        التحقق من وجود سيرة ذاتية
        """
        return self.uploaded_resume is not None or self.built_resume is not None
    
    def has_both_resumes(self):
        """
        التحقق من وجود السير الذاتية المرفوعة والمبنية معاً
        """
        return self.uploaded_resume is not None and self.built_resume is not None
    
    def get_resume_url(self):
        """
        الحصول على رابط السيرة الذاتية الرئيسية
        """
        resume = self.get_primary_resume()
        if not resume:
            return "#"
        
        if hasattr(resume, 'get_absolute_url'):
            return resume.get_absolute_url()
        elif hasattr(resume, 'id') and self.primary_resume_type in ['built', 'both'] and self.built_resume:
            return f"/resumes-builder/{resume.id}/"
        elif hasattr(resume, 'id') and self.primary_resume_type in ['uploaded', 'both'] and self.uploaded_resume:
            return f"/resumes/{resume.id}/"
        else:
            return "#"
    
    def get_uploaded_resume_url(self):
        """
        الحصول على رابط السيرة الذاتية المرفوعة
        """
        if self.uploaded_resume:
            return f"/resumes/{self.uploaded_resume.id}/"
        return "#"
    
    def get_built_resume_url(self):
        """
        الحصول على رابط السيرة الذاتية المبنية
        """
        if self.built_resume:
            return f"/resumes-builder/{self.built_resume.id}/"
        return "#"
