# accounts/views/web.py
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _
from django.contrib import messages
from django.db.models import Count, Avg
from resumes.models import Resume
from matching.services.matcher import batch_match_jobs_to_resume
from ..forms import RegisterForm
from resumes.models import Resume
from jobs.models import Job, Application




@login_required
def dashboard_candidate_enhanced(request):
    """لوحة المرشح المحسّنة مع إحصائيات متقدمة"""
    
    user = request.user
    
    if user.role != 'candidate':
        return redirect('dashboard')
    
    # 1. إحصائيات السير الذاتية
    resumes = Resume.objects.filter(candidate=user)
    resume_stats = {
        'total': resumes.count(),
        'processed': resumes.filter(is_processed=True).count(),
    }
    
    # 2. حساب نسبة الاكتمال
    completeness_scores = []
    all_skills = set()
    
    for resume in resumes.filter(is_processed=True):
        data = resume.parsed_data or {}
        score = 0
        if data.get('skills'): 
            score += 20
            all_skills.update(data.get('skills', []))
        if data.get('education'): score += 20
        if data.get('experience'): score += 20
        if data.get('languages'): score += 20
        if data.get('certifications'): score += 20
        completeness_scores.append(score)
    
    average_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
    
    # 3. تحليل المطابقات
    jobs = Job.objects.filter(is_active=True)
    all_match_scores = []
    
    for resume in resumes.filter(is_processed=True):
        matches = batch_match_jobs_to_resume(resume, jobs)
        for match in matches:
            all_match_scores.append(match['match']['score'])
    
    # 4. حساب الإحصائيات
    match_stats = {
        'excellent': len([m for m in all_match_scores if m >= 80]),
        'good': len([m for m in all_match_scores if 60 <= m < 80]),
        'fair': len([m for m in all_match_scores if 40 <= m < 60]),
        'low': len([m for m in all_match_scores if m < 40]),
        'average_score': sum(all_match_scores) / len(all_match_scores) if all_match_scores else 0,
        'total_matches': len(all_match_scores),
    }
    
    # 5. التقديمات
    applications = Application.objects.filter(candidate=user)
    app_stats = {
        'total': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    # 6. أفضل المهارات المطلوبة
    all_market_skills = {}
    for job in jobs:
        for skill in job.required_skills or []:
            all_market_skills[skill] = all_market_skills.get(skill, 0) + 1
    
    top_demanded_skills = sorted(
        all_market_skills.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # 7. المهارات الناقصة الأكثر طلباً
    missing_skills = [
        (skill, count) for skill, count in top_demanded_skills
        if skill.lower() not in [s.lower() for s in all_skills]
    ][:3]
    
    context = {
        'resume_stats': resume_stats,
        'average_completeness': round(average_completeness),
        'match_stats': match_stats,
        'app_stats': app_stats,
        'top_demanded_skills': top_demanded_skills,
        'missing_skills': missing_skills,
        'resumes_count': resume_stats['total'],
        'processed_resumes_count': resume_stats['processed'],
        'matches_count': match_stats['total_matches'],
        'excellent_matches_count': match_stats['excellent'],
        'recent_jobs': jobs.order_by('-created_at')[:6],
    }
    
    return render(request, 'accounts/dashboard_candidate.html', context)


@login_required
def dashboard(request):
    user = request.user

    if user.role == "employer":   
        # جلب بيانات الشركة
        from jobs.models import Job
        from resumes.models import Resume
        
        # إحصائيات للشركات
        jobs_count = Job.objects.filter(employer=user).count()
        active_jobs = Job.objects.filter(employer=user, is_active=True).count()
        total_applications = 0  # يمكنك إضافته لاحقاً
        
        context = {
            'jobs_count': jobs_count,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
        }
        
        return render(request, "accounts/dashboard_employer.html", context)
    
    elif user.role == "candidate":
         # جلب بيانات المرشح
        from resumes.models import Resume
        from jobs.models import Job
        from matching.services.matcher import batch_match_jobs_to_resume
        from django.db.models import Count
       
        # إحصائيات السير الذاتية
        resumes = Resume.objects.filter(candidate=user)
        resumes_count = resumes.count()
        processed_resumes_count = resumes.filter(is_processed=True).count()
        
        # إحصائيات المطابقات
        from matching.views.web import my_matches_view
        # يمكنك استدعاء view أخرى أو حساب المطابقات هنا
        
        # الوظائف الحديثة
        recent_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:5]
        
        # الوظائف الموصى بها (مثال: حسب المهارات)
        recommended_jobs = Job.objects.filter(is_active=True)[:3]
        
        # تطبيقات المرشح (تخمين - تحتاج لتطبيق Applications)
        applications_count = 0
        pending_applications_count = 0
        matches_count = 0
        excellent_matches_count = 0
        
        context = {
            'resumes_count': resumes_count,
            'processed_resumes_count': processed_resumes_count,
            'applications_count': applications_count,
            'pending_applications_count': pending_applications_count,
            'profile_views': 156,  # يمكن جلبها من قاعدة البيانات
            'matches_count':  matches_count,    # يمكن جلبها من المطابقات
            'excellent_matches_count': excellent_matches_count,  # مطابقات ممتازة (>= 80%)
            'recent_jobs': recent_jobs,
            'recommended_jobs': recommended_jobs,
            # يمكنك تمرير recent_matches هنا إذا كان لديك
        }
        
        return render(request, "accounts/dashboard_candidate.html", context)
    return HttpResponse("Unknown role")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful!"))
            return redirect("dashboard")
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
        
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _("Welcome back, %(username)s!") % {'username': user.username})
            
            # التحقق من next parameter
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, _("Invalid username or password. Please try again."))
    else:
        form = AuthenticationForm()
    
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):

    logout(request)
    messages.info(request, _("You have been logged out successfully."))
    return redirect("login")
