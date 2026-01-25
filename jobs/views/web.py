# jobs/views/web.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import Http404
from django.db.models import Q
from ..models import Job
from ..forms import JobForm
from accounts.permissions import IsEmployer
from django.db import models

@login_required
def job_list_view(request):
    """عرض جميع الوظائف النشطة"""
    jobs = Job.objects.filter(is_active=True).select_related('employer')
    
    # فلترة حسب البحث
    search_query = request.GET.get('q', '')
    if search_query:
        jobs = jobs.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(required_skills__icontains=search_query)
        )
    
    # فلترة حسب المهارات
    skill_filter = request.GET.get('skill', '')
    if skill_filter:
        jobs = jobs.filter(required_skills__contains=[skill_filter])
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
        'skill_filter': skill_filter,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail_view(request, pk):
    """عرض تفاصيل وظيفة محددة"""
    job = get_object_or_404(Job, id=pk, is_active=True)
    
    # التحقق مما إذا كان المستخدم قد تقدم لهذه الوظيفة
    has_applied = False
    if request.user.is_authenticated and request.user.role == 'candidate':
        has_applied = job.applications.filter(candidate=request.user).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'can_edit': request.user == job.employer,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def create_job_view(request):
    """إنشاء وظيفة جديدة"""
    if request.user.role != 'employer':
        messages.error(request, _("Only employers can create jobs."))
        return redirect('jobs:list')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, _("Job created successfully!"))
            return redirect('jobs:detail', pk=job.id)
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = JobForm()
    
    context = {'form': form}
    return render(request, 'jobs/job_create.html', context)

@login_required
def update_job_view(request, pk):
    """تحديث وظيفة موجودة"""
    job = get_object_or_404(Job, id=pk)
    
    # التحقق من الصلاحيات
    if job.employer != request.user:
        messages.error(request, _("You don't have permission to edit this job."))
        return redirect('jobs:detail', pk=job.id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, _("Job updated successfully!"))
            return redirect('jobs:detail', pk=job.id)
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/job_update.html', context)

@login_required
def delete_job_view(request, pk):
    """حذف وظيفة"""
    job = get_object_or_404(Job, id=pk)
    
    # التحقق من الصلاحيات
    if job.employer != request.user:
        messages.error(request, _("You don't have permission to delete this job."))
        return redirect('jobs:detail', pk=job.id)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, _("Job deleted successfully!"))
        return redirect('jobs:list')
    
    context = {'job': job}
    return render(request, 'jobs/job_delete.html', context)

@login_required
def my_jobs_view(request):
    """عرض وظائف المستخدم (للموظفين)"""
    if request.user.role != 'employer':
        messages.error(request, _("Only employers can view their jobs."))
        return redirect('jobs:list')
    
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    
    context = {
        'jobs': jobs,
        'active_count': jobs.filter(is_active=True).count(),
        'inactive_count': jobs.filter(is_active=False).count(),
    }
    return render(request, 'jobs/my_jobs.html', context)