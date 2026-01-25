# jobs/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


User = settings.AUTH_USER_MODEL

class Job(models.Model):
    employer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jobs",
        limit_choices_to={'role': 'employer'},
        verbose_name=_("Employer")
    )
    title = models.CharField(max_length=255, verbose_name=_("Job Title"))
    description = models.TextField(verbose_name=_("Job Description"))
    
    # الحقول الهيكلية للمطابقة الذكية
    required_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Required Skills"),
        help_text=_("List of required skills, e.g.: ['Python', 'Django', 'PostgreSQL']")
    )
    
    preferred_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Preferred Skills"),
        help_text=_("Additional preferred skills (optional)")
    )
    
    languages = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Languages"),
        help_text=_("Required languages, e.g.: ['Arabic', 'English']")
    )
    
    education_level = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Education Level"),
        help_text=_("e.g.: Bachelor's Degree in Computer Science")
    )
    
    experience_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Experience Years"),
        help_text=_("Required years of experience")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.title} - {self.employer}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")
        
        
        
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'candidate'})
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        unique_together = ('job', 'candidate')  # يمنع التقديم المكرر

    def __str__(self):
        return f"{self.candidate} applied to {self.job}"