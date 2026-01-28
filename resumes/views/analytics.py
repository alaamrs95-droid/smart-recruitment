# resumes/views/analytics.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from resumes.models import Resume
from jobs.models import Job
from collections import Counter
import json

@login_required
def skills_gap_analysis(request):
    """تحليل الفجوة بين المهارات الحالية والمطلوبة"""
    
    user = request.user
    
    if user.role != 'candidate':
        return redirect('dashboard')
    
    # جمع المهارات الحالية
    resumes = Resume.objects.filter(candidate=user, is_processed=True)
    current_skills = set()
    
    for resume in resumes:
        skills = resume.parsed_data.get('skills', [])
        current_skills.update([s.lower() for s in skills])
    
    # جمع المهارات المطلوبة
    jobs = Job.objects.filter(is_active=True)
    market_skills = Counter()
    skill_frequency = Counter()

    
    for job in jobs:
        required = [s.lower() for s in (job.required_skills or [])]
        preferred = [s.lower() for s in (job.preferred_skills or [])]
        all_job_skills = required + preferred
        
        for skill in all_job_skills:
            market_skills[skill] += 1
            if skill in required:
                skill_frequency[skill] += 2  # وزن أكثر للمهارات المطلوبة
    
    # تحليل الفجوة
    total_jobs = jobs.count()
    gap_analysis = {
        'mastered': [],
        'learn': [],
        'optional': [],
    }
    
    for skill, frequency in market_skills.most_common(50):
        if skill in current_skills:
            gap_analysis['mastered'].append({
                'skill': skill,
                'market_demand': frequency,
                'percentage': (frequency / total_jobs * 100) if total_jobs > 0 else 0,
                'advantage': 'High Demand'
            })
        else:
            if frequency > total_jobs * 0.3:  # 30%+
                gap_analysis['learn'].append({
                    'skill': skill,
                    'market_demand': frequency,
                    'percentage': (frequency / total_jobs * 100) if total_jobs > 0 else 0,
                    'difficulty': estimate_difficulty(skill),
                    'salary_impact': estimate_salary_impact(skill),
                    'learning_time': estimate_learning_time(skill)
                })
            else:
                gap_analysis['optional'].append({
                    'skill': skill,
                    'market_demand': frequency,
                })
    
    # حساب التغطية
    coverage = (
        (len(current_skills) / len(market_skills) * 100) 
        if market_skills else 0
    )
    
    context = {
        'current_skills': sorted(current_skills),
        'gap_analysis': gap_analysis,
        'total_market_skills': len(market_skills),
        'coverage': (len(current_skills) / len(market_skills) * 100) if market_skills else 0,
        'learn_count': len(gap_analysis['learn']),
        'mastered_count': len(gap_analysis['mastered']),
    }
    
    return render(request, 'resumes/skills_gap_analysis.html', context)





def estimate_difficulty(skill):
    """تقدير مستوى الصعوبة"""
    easy_skills = ['git', 'sql', 'html', 'css', 'linux']
    hard_skills = ['kubernetes', 'machine learning', 'deep learning']
    
    if any(s in skill for s in easy_skills):
        return 'Easy'
    elif any(s in skill for s in hard_skills):
        return 'Hard'
    else:
        return 'Medium'

def estimate_salary_impact(skill):
    """تقدير تأثير المهارة على الراتب"""
    high_impact = {
        'kubernetes': '+25%',
        'machine learning': '+30%',
        'docker': '+15%',
    }
    return high_impact.get(skill.lower(), '+10%')

def estimate_learning_time(skill):
    """تقدير وقت التعلم"""
    times = {
        'easy': '2-4 weeks',
        'medium': '1-3 months',
        'hard': '3-6 months'
    }
    difficulty = estimate_difficulty(skill)
    return times.get(difficulty, '1-3 months')

