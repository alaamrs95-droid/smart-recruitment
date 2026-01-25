# jobs/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Job

class JobForm(forms.ModelForm):
    """Form لإنشاء وتعديل الوظائف"""
    
    # حقول JSON كـ textarea للسهولة
    required_skills_text = forms.CharField(
        label=_("Required Skills"),
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': _("Enter skills separated by commas\ne.g. Python, Django, PostgreSQL, JavaScript")
        }),
        required=True,
        help_text=_("Separate skills with commas")
    )
    
    preferred_skills_text = forms.CharField(
        label=_("Preferred Skills"),
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': _("Optional preferred skills\n e.g. Docker, AWS, React")
        }),
        required=False,
        help_text=_("Separate skills with commas")
    )
    
    languages_text = forms.CharField(
        label=_("Required Languages"),
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': _("e.g. Arabic, English, French")
        }),
        required=True,
        help_text=_("Separate languages with commas")
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'education_level',
            'experience_years', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g. Senior Django Developer')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('Describe the job responsibilities, requirements, and benefits...')
            }),
            'education_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("e.g. Bachelor's Degree in Computer Science")
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': _('Years of experience required')
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'is_active': _("Active (visible to candidates)"),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تحويل JSON إلى text للعرض
        if self.instance and self.instance.pk:
            self.fields['required_skills_text'].initial = ', '.join(self.instance.required_skills)
            self.fields['preferred_skills_text'].initial = ', '.join(self.instance.preferred_skills)
            self.fields['languages_text'].initial = ', '.join(self.instance.languages)
        else:
            # قيم افتراضية عند الإنشاء
            self.fields['languages_text'].initial = 'Arabic, English'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # تحويل النص إلى قوائم
        required_skills_text = cleaned_data.get('required_skills_text', '')
        preferred_skills_text = cleaned_data.get('preferred_skills_text', '')
        languages_text = cleaned_data.get('languages_text', '')
        
        # تحويل إلى قوائم وإزالة الفراغات
        required_skills = [skill.strip() for skill in required_skills_text.split(',') if skill.strip()]
        preferred_skills = [skill.strip() for skill in preferred_skills_text.split(',') if skill.strip()]
        languages = [lang.strip() for lang in languages_text.split(',') if lang.strip()]
        
        # التحقق من المهارات المطلوبة
        if not required_skills:
            self.add_error('required_skills_text', _("At least one required skill is needed."))
        
        # التحقق من اللغات
        if not languages:
            self.add_error('languages_text', _("At least one language is required."))
        
        # حفظ القوائم في البيانات النظيفة
        cleaned_data['required_skills'] = required_skills
        cleaned_data['preferred_skills'] = preferred_skills
        cleaned_data['languages'] = languages
        
        return cleaned_data
    
    def save(self, commit=True):
        job = super().save(commit=False)
        
        # استخدام البيانات النظيفة بعد التحويل
        job.required_skills = self.cleaned_data.get('required_skills', [])
        job.preferred_skills = self.cleaned_data.get('preferred_skills', [])
        job.languages = self.cleaned_data.get('languages', [])
        
        if commit:
            job.save()
        
        return job