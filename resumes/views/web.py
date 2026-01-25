# resumes/views/web.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import Http404
from ..models.uploaded import Resume
from ..forms import ResumeUploadForm
from ..permissions import IsCandidate
import os
from datetime import datetime
from django.db.models import Count, Q
from matching.services.matcher import batch_match_jobs_to_resume
from jobs.models import Job

from ..services.file_extractor import extract_text
from ..services.parsing import simple_parse_resume

# استيراد views_profile
from .profile import resume_profile_view, set_primary_resume, toggle_matching_status


@login_required
def resume_list_view(request):
    """عرض السير الذاتية (للموظفين فقط)"""
    if request.user.role != 'employer':
        messages.error(request, _("Only employers can view resumes."))
        return redirect('dashboard')
    
    resumes = Resume.objects.filter(
        parsed_data__isnull=False,
        candidate__is_active=True
    ).select_related('candidate')
    
    # فلترة حسب المهارات
    skill_filter = request.GET.get('skill', '')
    if skill_filter:
        resumes = resumes.filter(parsed_data__skills__contains=[skill_filter])
    
    # فلترة حسب التعليم
    education_filter = request.GET.get('education', '')
    if education_filter:
        resumes = resumes.filter(parsed_data__education__contains=[education_filter])
    
    context = {
        'resumes': resumes,
        'skill_filter': skill_filter,
        'education_filter': education_filter,
        'total_count': resumes.count(),
    }
    return render(request, 'resumes/resume_list.html', context)

@login_required
def resume_detail_view(request, pk):
    """عرض تفاصيل سيرة ذاتية"""
    resume = get_object_or_404(Resume, id=pk)

    # التحقق من الصلاحيات
    if request.user != resume.candidate and request.user.role != 'employer':
        messages.error(request, _("You don't have permission to view this resume."))
        return redirect('dashboard')

    # استخراج البيانات المحللة
    parsed_data = resume.parsed_data or {}
    skills = parsed_data.get('skills', [])
    languages = parsed_data.get('languages', [])
    education = parsed_data.get('education', [])
    experience = parsed_data.get('experience', [])

    # معلومات الملف مع التحقق من وجوده
    if resume.file and resume.file.name:
        file_info = {
            'name': os.path.basename(resume.file.name),
            'size': f"{resume.file.size / 1024:.1f} KB",
            'type': os.path.splitext(resume.file.name)[1].upper().replace('.', ''),
            'uploaded': resume.created_at.strftime("%B %d, %Y"),
        }
    else:
        file_info = None

    context = {
        'resume': resume,
        'skills': skills,
        'languages': languages,
        'education': education,
        'experience': experience,
        'file_info': file_info,
        'can_edit': request.user == resume.candidate,
        'is_employer': request.user.role == 'employer',
    }
    return render(request, 'resumes/resume_detail.html', context)


@login_required
def upload_resume_view(request):
    """رفع سيرة ذاتية جديدة"""
    if request.user.role != 'candidate':
        messages.error(request, _("Only candidates can upload resumes."))
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # التحقق من وجود الملف
            if 'file' not in request.FILES or not request.FILES['file']:
                messages.error(request, _("Please select a file to upload."))
                return render(request, 'resumes/resume_upload.html', {'form': form})
            
            resume = form.save(commit=False)
            resume.candidate = request.user
            resume.original_filename = request.FILES['file'].name
            resume.save()
            
            try:
                raw_text = extract_text(resume.file.path)
                resume.raw_text = raw_text
                resume.parsed_data = simple_parse_resume(raw_text)
                resume.is_processed = True
                resume.processed_at = datetime.now()
                resume.save()
                messages.success(request, _("Resume uploaded and processed successfully!"))
            except Exception as e:
                print(f"Processing error: {e}")
                resume.is_processed = False
                resume.save()
                messages.warning(request, _("Resume uploaded but processing failed. Please try again later."))
            
            return redirect('resumes:my')
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = ResumeUploadForm()
    
    return render(request, 'resumes/resume_upload.html', {'form': form})

@login_required
def update_resume_view(request, pk):
    """تحديث سيرة ذاتية"""
    resume = get_object_or_404(Resume, id=pk)
    
    # التحقق من الصلاحيات
    if resume.candidate != request.user:
        messages.error(request, _("You don't have permission to edit this resume."))
        return redirect('resumes:detail', pk=resume.id)
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            if 'file' in request.FILES:
                resume.original_filename = request.FILES['file'].name
                # إعادة المعالجة
                resume.is_processed = False
                resume.processed_at = None
            form.save()
            if 'file' in request.FILES:
                try:
                    raw_text = extract_text(resume.file.path)
                    resume.raw_text = raw_text
                    resume.parsed_data = simple_parse_resume(raw_text)
                    resume.is_processed = True
                    resume.processed_at = datetime.now()
                    resume.save()
                    messages.success(request, _("Resume updated and processed successfully!"))
                except Exception as e:
                    print(f"Processing error: {e}")
                    resume.is_processed = False
                    resume.save()
                    messages.warning(request, _("Resume updated, but processing failed."))
            else:
                messages.success(request, _("Resume updated successfully!"))
            
            return redirect('resumes:detail', pk=resume.id)
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = ResumeUploadForm(instance=resume)
    
    context = {
        'form': form,
        'resume': resume,
    }
    return render(request, 'resumes/resume_update.html', context)

@login_required
def delete_resume_view(request, pk):
    """حذف سيرة ذاتية"""
    resume = get_object_or_404(Resume, id=pk)
    
    # التحقق من الصلاحيات
    if resume.candidate != request.user:
        messages.error(request, _("You don't have permission to delete this resume."))
        return redirect('resumes:detail', pk=resume.id)
    
    if request.method == 'POST':
        resume.delete()
        messages.success(request, _("Resume deleted successfully!"))
        return redirect('resumes:my')
    
    context = {'resume': resume}
    return render(request, 'resumes/resume_delete.html', context)

@login_required
def my_resumes_view(request):
    """عرض سير المستخدم الذاتية"""
    if request.user.role != 'candidate':
        messages.error(request, _("Only candidates can view their resumes."))
        return redirect('dashboard')
    
    # جلب السير الذاتية للمستخدم
    resumes = Resume.objects.filter(candidate=request.user).order_by('-created_at')
    
    # حساب الإحصائيات
    processed_count = resumes.filter(is_processed=True).count()
    
    # حساب عدد المطابقات لكل سيرة ذاتية
    for resume in resumes:
        if resume.is_processed:
            jobs = Job.objects.filter(is_active=True)
            matches = batch_match_jobs_to_resume(resume, jobs)
            resume.match_count = len([m for m in matches if m['match']['score'] > 50])
        else:
            resume.match_count = 0
    
    # إحصائيات إضافية
    total_matches = sum(resume.match_count for resume in resumes)
    
    # فلترة حسب الحالة
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'processed':
        resumes = resumes.filter(is_processed=True)
    elif status_filter == 'processing':
        resumes = resumes.filter(is_processed=False)
    
    context = {
        'resumes': resumes,
        'processed_count': processed_count,
        'total_matches': total_matches,
        'status_filter': status_filter,
    }
    return render(request, 'resumes/my_resumes.html', context)