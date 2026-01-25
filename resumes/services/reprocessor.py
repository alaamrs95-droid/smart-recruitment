# resumes/services/reprocessor.py
import os
from django.core.files.base import ContentFile
from ..models import Resume
from .nlp_parser import parse_resume

def create_test_resume(user, text_content, filename="test_resume.txt"):
    """إنشاء سيرة ذاتية اختبارية"""
    
    # إنشاء سيرة ذاتية جديدة
    resume = Resume.objects.create(
        candidate=user,
        original_filename=filename
    )
    
    # حفظ النص كملف
    resume.file.save(filename, ContentFile(text_content.encode('utf-8')))
    
    # معالجة السيرة الذاتية
    resume.raw_text = text_content
    resume.parsed_data = parse_resume(text_content)
    resume.is_processed = True
    resume.save()
    
    print(f"Created resume with {len(resume.parsed_data.get('skills', []))} skills")
    return resume

def reprocess_resume(resume):
    """إعادة معالجة سيرة ذاتية واحدة"""
    try:
        if resume.raw_text:
            # إعادة التحليل باستخدام parser الجديد
            resume.parsed_data = parse_resume(resume.raw_text)
            resume.is_processed = True
            resume.save()
            return True
    except Exception as e:
        print(f"Error processing resume {resume.id}: {str(e)}")
    return False

def reprocess_all_resumes():
    """إعادة معالجة جميع السير الذاتية"""
    resumes = Resume.objects.all()
    success_count = 0
    
    for resume in resumes:
        if reprocess_resume(resume):
            success_count += 1
    
    return f"Reprocessed {success_count} of {resumes.count()} resumes"