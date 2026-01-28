
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from jobs.models import Job, Application
from resumes.models import Resume,redirect
from matching.services.matcher import calculate_match_score
from django.db.models import Count, Avg

@login_required
def job_analytics(request):
    """تحليل أداء الوظائف"""
    
    user = request.user
    
    if user.role != 'employer':
        return redirect('dashboard')
    
    # الوظائف الخاصة بصاحب العمل
    jobs = Job.objects.filter(employer=user)
    
    jobs_performance = []
    
    for job in jobs:
        # عدد التقديمات
        applications = job.applications.all()
        app_count = applications.count()
        
        # حساب جودة التقديمات
        excellent_apps = 0
        good_apps = 0
        
        for app in applications:
            resume = app.candidate.resumes.filter(is_processed=True).first()
            if resume:
                match = calculate_match_score(resume.parsed_data, job)
                if match['score'] >= 80:
                    excellent_apps += 1
                elif match['score'] >= 60:
                    good_apps += 1
        
        # معدل التحويل
        accepted = applications.filter(status='accepted').count()
        conversion_rate = (accepted / app_count * 100) if app_count > 0 else 0
        
        jobs_performance.append({
            'job': job,
            'applications': app_count,
            'excellent': excellent_apps,
            'good': good_apps,
            'conversion_rate': round(conversion_rate, 1),
            'accepted': accepted,
            'status': 'Open' if job.is_active else 'Closed',
        })
    
    # إحصائيات عامة
    all_applications = Application.objects.filter(
        job__employer=user
    )
    
    total_stats = {
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_applications': all_applications.count(),
        'avg_apps_per_job': (
            all_applications.count() / jobs.count() 
            if jobs.count() > 0 else 0
        ),
        'avg_conversion': (
            all_applications.filter(status='accepted').count() / 
            all_applications.count() * 100
            if all_applications.count() > 0 else 0
        ),
    }
    
    context = {
        'jobs_performance': jobs_performance,
        'total_stats': total_stats,
    }
    
    return render(request, 'jobs/analytics_dashboard.html', context)
