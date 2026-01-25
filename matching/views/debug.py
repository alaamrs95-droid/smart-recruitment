# matching/views/debug.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from resumes.models import Resume
from jobs.models import Job
from matching.services.matcher import match_resume_to_job

@login_required
def debug_matches(request):
    """صفحة تصحيح للمطابقات"""
    user = request.user
    
    data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
        },
        'resumes': [],
        'jobs': [],
        'matches': [],
    }
    
    if user.role == 'candidate':
        # جلب سير المرشح
        resumes = Resume.objects.filter(candidate=user)
        data['resumes'] = [
            {
                'id': r.id,
                'filename': r.original_filename,
                'is_processed': r.is_processed,
                'has_parsed_data': bool(r.parsed_data),
            }
            for r in resumes
        ]
        
        # جلب الوظائف
        jobs = Job.objects.filter(is_active=True)[:5]
        data['jobs'] = [
            {
                'id': j.id,
                'title': j.title,
                'required_skills': j.required_skills,
            }
            for j in jobs
        ]
        
        # محاولة مطابقة
        if resumes.exists() and jobs.exists():
            resume = resumes.first()
            job = jobs.first()
            
            if resume.is_processed:
                match_result = match_resume_to_job(resume, job)
                data['matches'].append({
                    'resume_id': resume.id,
                    'job_id': job.id,
                    'match_result': match_result,
                })
    
    return JsonResponse(data)