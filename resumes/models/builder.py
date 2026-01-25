# resumes/models/builder.py
# تم إنشاء هذا الملف لدعم نظام بناء السيرة الذاتية داخل المنصة
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class BuiltResume(models.Model):
    """
    نموذج السيرة الذاتية المبنية داخل المنصة
    بديل للسير الذاتية المرفوعة كملفات
    """
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='built_resumes')
    title = models.CharField(max_length=200, verbose_name=_("Resume Title"))
    summary = models.TextField(verbose_name=_("Professional Summary"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_default = models.BooleanField(default=False, verbose_name=_("Default Resume"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Built Resume")
        verbose_name_plural = _("Built Resumes")
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.candidate.username} - {self.title}"
    
    def get_full_name(self):
        """الحصول على الاسم الكامل للمرشح"""
        return f"{self.candidate.first_name} {self.candidate.last_name}".strip()
    
    def get_absolute_url(self):
        """الحصول على الرابط المطلق للسيرة الذاتية"""
        return f"/resumes-builder/{self.id}/"
    
    def save(self, *args, **kwargs):
        """
        عند حفظ السيرة الذاتية المبنية، تحديث ملف التعريف الخاص بالمرشح
        """
        super().save(*args, **kwargs)
        
        # تحديث أو إنشاء ملف تعريف المرشح
        from .profile import CandidateResumeProfile
        profile, created = CandidateResumeProfile.objects.get_or_create(
            candidate=self.candidate
        )
        
        # إذا كانت هذه هي السيرة الذاتية الافتراضية أو لا توجد سيرة رئيسية
        if self.is_default or not profile.has_resume():
            profile.set_primary_resume('built', self)
    
    def delete(self, *args, **kwargs):
        """
        عند حذف السيرة الذاتية المبنية، تحديث ملف التعريف
        """
        # تحديث ملف التعريف إذا كانت هذه هي السيرة الرئيسية
        from .profile import CandidateResumeProfile
        try:
            profile = CandidateResumeProfile.objects.get(candidate=self.candidate)
            if profile.built_resume == self:
                profile.built_resume = None
                # إذا لم يكن هناك سيرة مرفوعة، قم بتغيير النوع
                if not profile.uploaded_resume:
                    profile.primary_resume_type = 'uploaded'
                profile.save()
        except CandidateResumeProfile.DoesNotExist:
            pass
        
        super().delete(*args, **kwargs)
    
    def get_email(self):
        """الحصول على البريد الإلكتروني"""
        return self.candidate.email
    
    def get_phone(self):
        """الحصول على رقم الهاتف"""
        return getattr(self.candidate, 'phone', '')
    
    def get_location(self):
        """الحصول على الموقع"""
        return getattr(self.candidate, 'location', '')

class PersonalInfo(models.Model):
    """
    المعلومات الشخصية للسيرة الذاتية
    """
    resume = models.OneToOneField(BuiltResume, on_delete=models.CASCADE, related_name='personal_info')
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    linkedin = models.URLField(blank=True, verbose_name=_("LinkedIn Profile"))
    github = models.URLField(blank=True, verbose_name=_("GitHub Profile"))
    website = models.URLField(blank=True, verbose_name=_("Personal Website"))
    
    class Meta:
        verbose_name = _("Personal Information")
        verbose_name_plural = _("Personal Information")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Experience(models.Model):
    """
    نموذج الخبرات العملية
    """
    resume = models.ForeignKey(BuiltResume, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200, verbose_name=_("Company"))
    position = models.CharField(max_length=200, verbose_name=_("Position"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    current_job = models.BooleanField(default=False, verbose_name=_("Current Job"))
    description = models.TextField(verbose_name=_("Job Description"))
    achievements = models.TextField(blank=True, verbose_name=_("Key Achievements"))
    
    class Meta:
        verbose_name = _("Work Experience")
        verbose_name_plural = _("Work Experiences")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    def get_duration(self):
        """حساب مدة الخبرة"""
        from datetime import date
        end = self.end_date or date.today()
        start = self.start_date
        years = end.year - start.year
        if end.month < start.month or (end.month == start.month and end.day < start.day):
            years -= 1
        return f"{years}+ years"

class Education(models.Model):
    """
    نموذج التعليم
    """
    DEGREE_TYPES = [
        ('high_school', _('High School')),
        ('bachelor', _('Bachelor\'s Degree')),
        ('master', _('Master\'s Degree')),
        ('phd', _('PhD')),
        ('diploma', _('Diploma')),
        ('certificate', _('Certificate')),
    ]
    
    resume = models.ForeignKey(BuiltResume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200, verbose_name=_("Institution"))
    degree = models.CharField(max_length=100, verbose_name=_("Degree"))
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES, verbose_name=_("Degree Type"))
    field_of_study = models.CharField(max_length=200, verbose_name=_("Field of Study"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    current_study = models.BooleanField(default=False, verbose_name=_("Currently Studying"))
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name=_("GPA"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Education")
        ordering = ['-end_date']
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study}"

class Skill(models.Model):
    """
    نموذج المهارات
    """
    SKILL_LEVELS = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
        ('expert', _('Expert')),
    ]
    
    resume = models.ForeignKey(BuiltResume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100, verbose_name=_("Skill Name"))
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, verbose_name=_("Skill Level"))
    years_of_experience = models.IntegerField(null=True, blank=True, verbose_name=_("Years of Experience"))
    
    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
        ordering = ['-years_of_experience', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

class Language(models.Model):
    """
    نموذج اللغات
    """
    LANGUAGE_LEVELS = [
        ('basic', _('Basic')),
        ('intermediate', _('Intermediate')),
        ('fluent', _('Fluent')),
        ('native', _('Native')),
    ]
    
    resume = models.ForeignKey(BuiltResume, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=50, verbose_name=_("Language"))
    level = models.CharField(max_length=20, choices=LANGUAGE_LEVELS, verbose_name=_("Proficiency Level"))
    
    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['-level', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

class Project(models.Model):
    """
    نموذج المشاريع الشخصية
    """
    resume = models.ForeignKey(BuiltResume, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200, verbose_name=_("Project Name"))
    description = models.TextField(verbose_name=_("Project Description"))
    technologies = models.CharField(max_length=500, verbose_name=_("Technologies Used"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    project_url = models.URLField(blank=True, verbose_name=_("Project URL"))
    github_url = models.URLField(blank=True, verbose_name=_("GitHub URL"))
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name

class Certification(models.Model):
    """
    نموذج الشهادات
    """
    resume = models.ForeignKey(BuiltResume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200, verbose_name=_("Certification Name"))
    issuing_organization = models.CharField(max_length=200, verbose_name=_("Issuing Organization"))
    issue_date = models.DateField(verbose_name=_("Issue Date"))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_("Expiry Date"))
    credential_id = models.CharField(max_length=100, blank=True, verbose_name=_("Credential ID"))
    credential_url = models.URLField(blank=True, verbose_name=_("Credential URL"))
    
    class Meta:
        verbose_name = _("Certification")
        verbose_name_plural = _("Certifications")
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.name} from {self.issuing_organization}"
