from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta
from resumes.models import Resume
from jobs.models import Job, Application
from matching.services.matcher import batch_match_jobs_to_resume
import json
from matching.services.matcher import calculate_match_score


@login_required
def analytics_dashboard(request):
    """لوحة التحليلات الشاملة للمرشح"""
    
    user = request.user
    
    if user.role != 'candidate':
        return redirect('dashboard')
    
    # البيانات الأساسية
    resumes = Resume.objects.filter(candidate=user, is_processed=True)
    
    jobs = Job.objects.filter(is_active=True)
    
    # 1. إحصائيات السير
    resume_stats = {
        'total': resumes.count(),
        'processed': resumes.filter(is_processed=True).count(),
        'average_completeness': calculate_resume_completeness(resumes),
    }
    

    
    # 2. حساب متوسط الاكتمال
    completeness_scores = []
    for resume in resumes:
        data = resume.parsed_data or {}
        score = 0
        if data.get('skills'): score += 20
        if data.get('education'): score += 20
        if data.get('experience'): score += 20
        if data.get('languages'): score += 20
        if data.get('certifications'): score += 20
        completeness_scores.append(score)
    
    resume_stats['average_completeness'] = (
        sum(completeness_scores) / len(completeness_scores)
        if completeness_scores else 0
    )
    
    # 3. تحليل المطابقات
    from matching.services.matcher import batch_match_jobs_to_resume
    all_matches = []
    monthly_matches = {}  # للرسم البياني الشهري
    
    for resume in resumes:
        matches = batch_match_jobs_to_resume(resume, jobs)
        for match in matches:
            score = match['match']['score']
            all_matches.extend([m['match']['score'] for m in matches])
    
    match_stats = {
        'excellent': len([m for m in all_match_scores if m >= 80]),
        'good': len([m for m in all_match_scores if 60 <= m < 80]),
        'fair': len([m for m in all_match_scores if 40 <= m < 60]),
        'low': len([m for m in all_match_scores if m < 40]),
        'average_score': (
            sum(all_match_scores) / len(all_match_scores) 
            if all_match_scores else 0
        ),
        'total_matches': len(all_match_scores),
    }
    
    # 4. تحليل المهارات
    all_skills = []
    market_demand = {}
    
    for resume in resumes:
        skills = resume.parsed_data.get('skills', [])
        all_skills.extend(skills)
    
    for job in jobs:
        for skill in job.required_skills or []:
            market_demand[skill] = market_demand.get(skill, 0) + 1
    
    top_skills = sorted(
        [(s, market_demand.get(s, 0)) for s in set(all_skills)],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # 5. التقديمات
    applications = Application.objects.filter(candidate=user).select_related('job')
    app_stats = {
        'total': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    # 6. للرسم البياني - بيانات JSON
    chart_data = {
        'match_distribution': {
            'labels': ['Excellent (80+)', 'Good (60-79)', 'Fair (40-59)', 'Low (<40)'],
            'data': [
                match_stats['excellent'],
                match_stats['good'],
                match_stats['fair'],
                match_stats['low'],
            ],
            'backgroundColor': ['#28a745', '#ffc107', '#fd7e14', '#dc3545'],
        },
        'application_status': {
            'labels': ['Pending', 'Accepted', 'Rejected'],
            'data': [app_stats['pending'], app_stats['accepted'], app_stats['rejected']],
            'backgroundColor': ['#ffc107', '#28a745', '#dc3545'],
        }
    }
     # 5. الاتجاهات الشهرية
    last_30_days = datetime.now() - timedelta(days=30)
    monthly_matches = []
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        # احسب المطابقات في هذا اليوم
        daily_matches = len([m for m in all_matches 
                           if m.created_at.date() == date.date()])
        monthly_matches.append(daily_matches)
    
    context = {
        'resume_stats': resume_stats,
        'top_skills': top_skills,
        'match_stats': match_stats,
        'app_stats': app_stats,
        'monthly_matches': monthly_matches,
    }
    
    
    context = {
        'resume_stats': resume_stats,
        'match_stats': match_stats,
        'app_stats': app_stats,
        'top_skills': top_skills,
        'chart_data': json.dumps(chart_data),
        'monthly_matches': monthly_matches,

    }
    
    return render(request, 'matching/analytics_dashboard.html', context)


def calculate_resume_completeness(resumes):
    """حساب متوسط اكتمال السير الذاتية"""
    total = 0
    for resume in resumes:
        data = resume.parsed_data
        completeness = 0
        if data.get('skills'): completeness += 20
        if data.get('education'): completeness += 20
        if data.get('experience'): completeness += 20
        if data.get('languages'): completeness += 20
        if data.get('certifications'): completeness += 20
        total += completeness
    
    return (total / len(resumes)) if resumes else 0


@login_required
def top_candidates_for_job(request, job_id):
    """عرض أفضل المرشحين لوظيفة محددة"""
    
    user = request.user
    job = get_object_or_404(Job, id=job_id, employer=user)
    
    # جميع السير المعالجة
    resumes = Resume.objects.filter(is_processed=True)
    
    # حساب المطابقة لكل سيرة
    candidates_matches = []
    
    for resume in resumes:
        match = calculate_match_score(resume.parsed_data, job)
        
        if match['score'] >= 30:  # حد أدنى معقول
            candidates_matches.append({
                'resume': resume,
                'candidate': resume.candidate,
                'match_score': match['score'],
                'match_level': match['level'],
                'details': match['details'],
                'applied': job.applications.filter(
                    candidate=resume.candidate
                ).exists(),
            })
    
    # ترتيب حسب درجة المطابقة
    candidates_matches.sort(
        key=lambda x: x['match_score'],
        reverse=True
    )
    
    # إحصائيات
    stats = {
        'total_potential': len(candidates_matches),
        'excellent': len([c for c in candidates_matches if c['match_score'] >= 80]),
        'good': len([c for c in candidates_matches if 60 <= c['match_score'] < 80]),
        'average_match': (
            sum(c['match_score'] for c in candidates_matches) / len(candidates_matches)
            if candidates_matches else 0
        ),
    }
    
    context = {
        'job': job,
        'candidates': candidates_matches[:50],  # حد 50
        'stats': stats,
    }
    
    return render(request, 'matching/top_candidates.html', context)
