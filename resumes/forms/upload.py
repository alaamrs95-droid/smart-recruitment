# resumes/forms/upload.py
from django import forms
from django.utils.translation import gettext_lazy as _
from ..models.uploaded import Resume

class ResumeUploadForm(forms.ModelForm):
    """Form لرفع وتعديل السير الذاتية"""
    
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'required': True
            }),
        }
        labels = {
            'file': _("Resume File"),
        }
        help_texts = {
            'file': _("Upload your resume in PDF or DOCX format (Max 5MB)."),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # التحقق من حجم الملف
            max_size = 5 * 1024 * 1024  # 5MB
            if file.size > max_size:
                raise forms.ValidationError(_("File size must be less than 5MB."))
            
            # التحقق من نوع الملف
            allowed_extensions = ['.pdf', '.doc', '.docx']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(_("Only PDF, DOC, and DOCX files are allowed."))
        
        return file