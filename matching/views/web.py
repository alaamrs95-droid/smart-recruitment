# matching/views/web.py 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q
from resumes.models.uploaded import Resume
# تم استيراد نماذج السير الذاتية المبنية لدعم النظام الجديد
from resumes.models.builder import BuiltResume
from resumes.models.profile import CandidateResumeProfile
from jobs.models import Job
from matching.services.matcher import match_resume_to_job, calculate_match_score
from matching.services.built_resume_matcher import match_built_resume_to_jobs, calculate_built_resume_match
import json

# matching/views/web.py - تصحيح دالة my_matches_view
@login_required
def my_matches_view(request):
    """عرض جميع المطابقات الخاصة بالمستخدم"""
    user = request.user
    
    if user.role == 'candidate':
        # المرشح: مطابقات سيره الذاتية مع الوظائف
        from jobs.models import Job
        
        # الحصول على ملف تعريف المرشح
        try:
            profile = CandidateResumeProfile.objects.get(candidate=user)
            primary_resume = profile.get_primary_resume()
            
            if not primary_resume:
                context = {
                    'matches': [],
                    'total_matches': 0,
                    'high_matches': [],
                    'medium_matches': [],
                    'low_matches': [],
                    'has_resumes': False,
                }
                return render(request, 'matching/candidate_matches.html', context)
        except CandidateResumeProfile.DoesNotExist:
            context = {
                'matches': [],
                'total_matches': 0,
                'high_matches': [],
                'medium_matches': [],
                'low_matches': [],
                'has_resumes': False,
            }
            return render(request, 'matching/candidate_matches.html', context)
        
        all_matches = []
        
        # جلب الوظائف النشطة فقط
        jobs = Job.objects.filter(is_active=True).select_related('employer')
        
        # مطابقة السيرة الذاتية الرئيسية مع الوظائف
        if hasattr(primary_resume, 'title'):  # سيرة مبنية
            matches = match_built_resume_to_jobs(primary_resume, jobs)
            for match in matches:
                all_matches.append({
                    'resume': primary_resume,
                    'job': match['job'],
                    'match': match['match'],
                    'type': 'built',
                    'profile': profile
                })
        else:  # سيرة مرفوعة
            from matching.services.matcher import batch_match_jobs_to_resume
            matches = batch_match_jobs_to_resume(primary_resume, jobs)
            for match in matches:
                all_matches.append({
                    'resume': primary_resume,
                    'job': match['job'],
                    'match': match['match'],
                    'type': 'uploaded',
                    'profile': profile
                })
        
        # ترتيب حسب درجة المطابقة
        all_matches.sort(key=lambda x: x['match']['score'], reverse=True)
        
        # تقسيم المطابقات حسب النتيجة
        high_matches = [m for m in all_matches if m['match']['score'] >= 80]
        medium_matches = [m for m in all_matches if 50 <= m['match']['score'] < 80]
        low_matches = [m for m in all_matches if m['match']['score'] < 50]
        
        template = 'matching/candidate_matches.html'
        
    elif user.role == 'employer':
        # صاحب العمل: مطابقات المرشحين مع وظائفه
        from jobs.models import Job
        
        # جلب وظائف صاحب العمل النشطة
        jobs = Job.objects.filter(employer=user, is_active=True)
        
        if not jobs.exists():
            context = {
                'matches': [],
                'total_matches': 0,
                'high_matches': [],
                'medium_matches': [],
                'low_matches': [],
                'has_jobs': False,
            }
            return render(request, 'matching/employer_matches.html', context)
        
        all_matches = []
        
        # جلب ملفات تعريف المرشحين النشطين للمطابقة
        profiles = CandidateResumeProfile.objects.filter(
            is_active_for_matching=True,
            uploaded_resume__isnull=False
        ).select_related('candidate', 'uploaded_resume') | CandidateResumeProfile.objects.filter(
            is_active_for_matching=True,
            built_resume__isnull=False
        ).select_related('candidate', 'built_resume')
        
        # مطابقة كل ملف تعريف مع وظائف صاحب العمل
        for profile in profiles:
            primary_resume = profile.get_primary_resume()
            if not primary_resume:
                continue
                
            for job in jobs:
                if hasattr(primary_resume, 'title'):  # سيرة مبنية
                    match_result = calculate_built_resume_match(primary_resume, job)
                    resume_type = 'built'
                else:  # سيرة مرفوعة
                    match_result = match_resume_to_job(primary_resume, job)
                    resume_type = 'uploaded'
                
                if match_result["score"] > 10:
                    all_matches.append({
                        'resume': primary_resume,
                        'profile': profile,
                        'job': job,
                        'match': match_result,
                        'type': resume_type
                    })
        
        # ترتيب حسب درجة المطابقة
        all_matches.sort(key=lambda x: x['match']['score'], reverse=True)
        
        # تقسيم المطابقات حسب النتيجة
        high_matches = [m for m in all_matches if m['match']['score'] >= 80]
        medium_matches = [m for m in all_matches if 50 <= m['match']['score'] < 80]
        low_matches = [m for m in all_matches if m['match']['score'] < 50]
        
        template = 'matching/employer_matches.html'
    
    else:
        messages.error(request, _("Invalid user role."))
        return redirect('home')
    
    # السياق المشترك
    context = {
        'matches': all_matches,
        'total_matches': len(all_matches),
        'high_matches': high_matches,
        'medium_matches': medium_matches,
        'low_matches': low_matches,
        'high_count': len(high_matches),
        'medium_count': len(medium_matches),
        'low_count': len(low_matches),
    }
    
    if user.role == 'candidate':
        context['has_resumes'] = True
    else:
        context['has_jobs'] = True
    
    return render(request, template, context)

@login_required
def match_resume_jobs_view(request, resume_id):
    """عرض مطابقات سيرة ذاتية محددة مع الوظائف"""
    resume = get_object_or_404(Resume, id=resume_id)
    
    # التحقق من الملكية للمرشحين
    if request.user.role == 'candidate' and resume.candidate != request.user:
        messages.error(request, _("You can only view matches for your own resumes."))
        return redirect('matching:my_matches')
    
    # جلب الوظائف النشطة
    jobs = Job.objects.filter(is_active=True).select_related('employer')
    
    matches = []
    for job in jobs:
        match_result = match_resume_to_job(resume, job)
        if match_result["score"] > 0:
            matches.append({
                'job': job,
                'match': match_result,
            })
    
    # ترتيب حسب درجة المطابقة
    matches.sort(key=lambda x: x['match']['score'], reverse=True)
    
    context = {
        'resume': resume,
        'matches': matches,
        'total_jobs': jobs.count(),
        'matched_jobs': len(matches),
        'top_matches': matches[:10],
    }
    return render(request, 'matching/resume_jobs_matches.html', context)

@login_required
def match_job_resumes_view(request, job_id):
    """عرض مطابقات وظيفة محددة مع السير الذاتية"""
    job = get_object_or_404(Job, id=job_id)
    
    # التحقق من الملكية للموظفين
    if request.user.role == 'employer' and job.employer != request.user:
        messages.error(request, _("You can only view matches for your own jobs."))
        return redirect('matching:my_matches')
    
    # جلب السير الذاتية المعالجة
    resumes = Resume.objects.filter(is_processed=True).select_related('candidate')
    
    matches = []
    for resume in resumes:
        match_result = match_resume_to_job(resume, job)
        if match_result["score"] > 10:
            matches.append({
                'resume': resume,
                'match': match_result,
            })
    
    # ترتيب حسب درجة المطابقة
    matches.sort(key=lambda x: x['match']['score'], reverse=True)
    
    context = {
        'job': job,
        'matches': matches,
        'total_resumes': resumes.count(),
        'matched_resumes': len(matches),
        'top_matches': matches[:10],
    }
    return render(request, 'matching/job_resumes_matches.html', context)

@login_required
def job_matches_view(request, pk):
    """عرض مختصر لمطابقات وظيفة (للموظفين)"""
    job = get_object_or_404(Job, id=pk)
    
    if request.user.role != 'employer' or job.employer != request.user:
        messages.error(request, _("Access denied."))
        return redirect('jobs:detail', pk=job.id)
    
    # جلب أفضل 10 مطابقات فقط للعرض السريع
    resumes = Resume.objects.filter(is_processed=True).select_related('candidate')
    top_matches = []
    
    for resume in resumes:
        match_result = match_resume_to_job(resume, job)
        if match_result["score"] >= 50:
            top_matches.append({
                'resume': resume,
                'match': match_result,
            })
    
    top_matches.sort(key=lambda x: x['match']['score'], reverse=True)
    top_matches = top_matches[:10]
    
    context = {
        'job': job,
        'top_matches': top_matches,
        'total_matches': len(top_matches),
    }
    return render(request, 'matching/job_matches_summary.html', context)

@login_required
def match_detail_view(request, resume_id, job_id):
    """عرض تفاصيل مطابقة محددة"""
    
    # محاولة الحصول على السيرة المبنية أولاً
    try:
        from resumes.models_builder import BuiltResume
        resume = get_object_or_404(BuiltResume, id=resume_id)
        resume_type = 'built'
    except:
        # إذا لم تكن سيرة مبنية، جرب السيرة المرفوعة
        resume = get_object_or_404(Resume, id=resume_id)
        resume_type = 'uploaded'
    
    job = get_object_or_404(Job, id=job_id)
    
    # التحقق من الصلاحيات
    if request.user.role == 'candidate' and resume.candidate != request.user:
        messages.error(request, _("Access denied."))
        return redirect('matching:my_matches')
    
    if request.user.role == 'employer' and job.employer != request.user:
        messages.error(request, _("Access denied."))
        return redirect('matching:my_matches')
    
    # حساب المطابقة حسب نوع السيرة
    if resume_type == 'built':
        from matching.services.built_resume_matcher import calculate_built_resume_match
        match_result = calculate_built_resume_match(resume, job)
    else:
        match_result = match_resume_to_job(resume, job)
    
    # تحليل مفصل
    analysis = {}
    
    if resume_type == 'built':
        # تحليل خاص بالسيرة المبنية
        from matching.services.built_resume_matcher import analyze_skills_match as analyze_built_skills_match
        from matching.services.built_resume_matcher import analyze_experience_match as analyze_built_experience_match
        analysis = {
            'skills_analysis': analyze_built_skills_match(resume, job),
            'experience_analysis': analyze_built_experience_match(resume, job),
            'recommendations': get_recommendations(match_result),
        }
    else:
        # تحليل السيرة المرفوعة
        analysis = {
            'skills_analysis': analyze_skills_match(resume, job),
            'languages_analysis': analyze_languages_match(resume, job),
            'recommendations': get_recommendations(match_result),
        }
    
    context = {
        'resume': resume,
        'job': job,
        'match': match_result,
        'analysis': analysis,
        'resume_type': resume_type,
        'can_apply': request.user.role == 'candidate' and resume.candidate == request.user,
        'can_contact': request.user.role == 'employer' and job.employer == request.user,
    }
    return render(request, 'matching/match_detail.html', context)

# دوال مساعدة
def analyze_skills_match(resume, job):
    """تحليل مطابقة المهارات"""
    resume_skills = set(s.lower() for s in resume.parsed_data.get('skills', []))
    required_skills = set(s.lower() for s in (job.required_skills or []))
    preferred_skills = set(s.lower() for s in (job.preferred_skills or []))
    
    return {
        'required_matched': list(required_skills & resume_skills),
        'required_missing': list(required_skills - resume_skills),
        'preferred_matched': list(preferred_skills & resume_skills),
        'preferred_missing': list(preferred_skills - resume_skills),
        'extra_skills': list(resume_skills - (required_skills | preferred_skills)),
    }

def analyze_languages_match(resume, job):
    """تحليل مطابقة اللغات"""
    resume_langs = set(l.lower() for l in resume.parsed_data.get('languages', []))
    job_langs = set(l.lower() for l in (job.languages or []))
    
    return {
        'matched': list(job_langs & resume_langs),
        'missing': list(job_langs - resume_langs),
    }

def get_recommendations(match_result):
    """توليد توصيات بناءً على نتيجة المطابقة"""
    recommendations = []
    score = match_result['score']
    
    if score >= 80:
        recommendations.append(_("Excellent match! You're highly qualified for this position."))
        recommendations.append(_("Consider applying immediately."))
    elif score >= 50:
        recommendations.append(_("Good match. You meet most requirements."))
        recommendations.append(_("Consider highlighting your relevant skills in your application."))
    else:
        recommendations.append(_("There's room for improvement."))
        
        if match_result['details'].get('missing', {}).get('required_skills'):
            missing = match_result['details']['missing']['required_skills'][:3]
            recommendations.append(_("Consider learning: {}").format(', '.join(missing)))
    
    return recommendations