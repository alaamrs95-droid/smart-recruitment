# resumes/forms/builder.py
# تم إنشاء هذا الملف لدعم نظام بناء السيرة الذاتية داخل المنصة
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models.builder import (
    BuiltResume, PersonalInfo, Experience, Education, 
    Skill, Language, Project, Certification
)

class BuiltResumeForm(forms.ModelForm):
    """
    نموذج إنشاء/تعديل السيرة الذاتية
    """
    class Meta:
        model = BuiltResume
        fields = ['title', 'summary', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter resume title...')
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Write a brief professional summary...')
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = _('Resume Title')
        self.fields['summary'].label = _('Professional Summary')
        self.fields['is_default'].label = _('Set as default resume')

class PersonalInfoForm(forms.ModelForm):
    """
    نموذج المعلومات الشخصية
    """
    class Meta:
        model = PersonalInfo
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'location',
            'linkedin', 'github', 'website'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة ترجمة للحقول
        field_labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email Address'),
            'phone': _('Phone Number'),
            'location': _('Location'),
            'linkedin': _('LinkedIn Profile'),
            'github': _('GitHub Profile'),
            'website': _('Personal Website')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label
            self.fields[field_name].widget.attrs['placeholder'] = f'Enter {label.lower()}...'

class ExperienceForm(forms.ModelForm):
    """
    نموذج الخبرة العملية
    """
    class Meta:
        model = Experience
        fields = [
            'company', 'position', 'start_date', 'end_date', 
            'current_job', 'description', 'achievements'
        ]
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_job': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            'company': _('Company Name'),
            'position': _('Job Position'),
            'start_date': _('Start Date'),
            'end_date': _('End Date'),
            'current_job': _('I currently work here'),
            'description': _('Job Description'),
            'achievements': _('Key Achievements')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label

class EducationForm(forms.ModelForm):
    """
    نموذج التعليم
    """
    class Meta:
        model = Education
        fields = [
            'institution', 'degree', 'degree_type', 'field_of_study',
            'start_date', 'end_date', 'current_study', 'gpa', 'description'
        ]
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'degree_type': forms.Select(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_study': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '4'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            'institution': _('Institution Name'),
            'degree': _('Degree Title'),
            'degree_type': _('Degree Type'),
            'field_of_study': _('Field of Study'),
            'start_date': _('Start Date'),
            'end_date': _('End Date'),
            'current_study': _('Currently studying'),
            'gpa': _('GPA (out of 4.0)'),
            'description': _('Additional Information')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label

class SkillForm(forms.ModelForm):
    """
    نموذج المهارات
    """
    class Meta:
        model = Skill
        fields = ['name', 'level', 'years_of_experience']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '50'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            'name': _('Skill Name'),
            'level': _('Proficiency Level'),
            'years_of_experience': _('Years of Experience')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label

class LanguageForm(forms.ModelForm):
    """
    نموذج اللغات
    """
    class Meta:
        model = Language
        fields = ['name', 'level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            'name': _('Language Name'),
            'level': _('Proficiency Level')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label

class ProjectForm(forms.ModelForm):
    """
    نموذج المشاريع
    """
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'technologies', 
            'start_date', 'end_date', 'project_url', 'github_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'technologies': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'project_url': forms.URLInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            'name': _('Project Name'),
            'description': _('Project Description'),
            'technologies': _('Technologies Used'),
            'start_date': _('Start Date'),
            'end_date': _('End Date'),
            'project_url': _('Project URL'),
            'github_url': _('GitHub URL')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label
            if field_name in ['technologies']:
                self.fields[field_name].widget.attrs['placeholder'] = _('e.g., Python, Django, React')

class CertificationForm(forms.ModelForm):
    """
    نموذج الشهادات
    """
    class Meta:
        model = Certification
        fields = [
            'name', 'issuing_organization', 'issue_date', 
            'expiry_date', 'credential_id', 'credential_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_id': forms.TextInput(attrs={'class': 'form-control'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            'name': _('Certification Name'),
            'issuing_organization': _('Issuing Organization'),
            'issue_date': _('Issue Date'),
            'expiry_date': _('Expiry Date'),
            'credential_id': _('Credential ID'),
            'credential_url': _('Credential URL')
        }
        
        for field_name, label in field_labels.items():
            self.fields[field_name].label = label

# === Forms مخصصة للبحث والفلترة ===

class ResumeSearchForm(forms.Form):
    """
    نموذج البحث في السير الذاتية
    """
    query = forms.CharField(
        label=_('Search'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search resumes...')
        })
    )
    
    skill_level = forms.ChoiceField(
        label=_('Minimum Skill Level'),
        choices=[('', _('All Levels'))] + Skill._meta.get_field('level').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience_years = forms.IntegerField(
        label=_('Minimum Experience (years)'),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ResumeFilterForm(forms.Form):
    """
    نموذج فلترة السير الذاتية
    """
    has_education = forms.BooleanField(
        label=_('Has Education'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_experience = forms.BooleanField(
        label=_('Has Work Experience'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_projects = forms.BooleanField(
        label=_('Has Projects'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_certifications = forms.BooleanField(
        label=_('Has Certifications'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
