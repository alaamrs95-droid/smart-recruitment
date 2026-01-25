# matching/services/built_resume_matcher.py
# تم إنشاء هذا الملف لدعم مطابقة السير الذاتية المبنية داخل المنصة
from django.db.models import Q
from jobs.models import Job
from resumes.models.builder import BuiltResume, Experience, Education, Skill, Language
from matching.services.enhanced_matcher import EnhancedMatcher
import json

def match_built_resume_to_jobs(built_resume, jobs):
    """
    مطابقة سيرة ذاتية مبنية مع قائمة الوظائف
    """
    matches = []
    
    for job in jobs:
        match_result = calculate_built_resume_match(built_resume, job)
        if match_result['score'] > 0:
            matches.append({
                'job': job,
                'match': match_result
            })
    
    
    return sorted(matches, key=lambda x: x['match']['score'], reverse=True)

def calculate_built_resume_match(built_resume, job):
    """
    حساب درجة المطابقة بين سيرة ذاتية مبنية ووظيفة
    """
    matcher = EnhancedMatcher()
    
    # تحويل السيرة الذاتية المبنية إلى بيانات قابلة للمطابقة
    resume_data = extract_resume_data(built_resume)
    
    # استخدام المحسّن المحسّن للمطابقة
    result = matcher.calculate_match_score(resume_data, job)
    
    # إضافة معلومات إضافية خاصة بالسيرة المبنية
    result['built_resume_id'] = built_resume.id
    result['resume_title'] = built_resume.title
    
    return result

def extract_resume_data(built_resume):
    """
    استخراج البيانات من السيرة الذاتية المبنية بصيغة مناسبة للمطابقة
    """
    resume_data = {
        'title': built_resume.title,
        'summary': built_resume.summary,
        'skills': [],
        'experience': [],
        'education': [],
        'languages': [],
        'projects': [],
        'certifications': []
    }
    
    # استخراج المعلومات الشخصية
    if hasattr(built_resume, 'personal_info'):
        personal_info = built_resume.personal_info
        resume_data.update({
            'first_name': personal_info.first_name,
            'last_name': personal_info.last_name,
            'email': personal_info.email,
            'phone': personal_info.phone,
            'location': personal_info.location
        })
    
    # استخراج المهارات كنصوص للمطابقة الدلالية
    for skill in built_resume.skills.all():
        resume_data['skills'].append(skill.name)
    
    # استخراج الخبرات العملية كنصوص للمطابقة الدلالية
    for exp in built_resume.experiences.all():
        exp_text = f"{exp.position} {exp.company} {exp.description}"
        if exp.achievements:
            exp_text += f" {exp.achievements}"
        resume_data['experience'].append(exp_text)
        
        # حفظ البيانات المنظمة أيضاً
        resume_data.setdefault('structured_experience', []).append({
            'company': exp.company,
            'position': exp.position,
            'start_date': exp.start_date,
            'end_date': exp.end_date,
            'current_job': exp.current_job,
            'description': exp.description,
            'achievements': exp.achievements
        })
    
    # استخراج التعليم كنصوص للمطابقة الدلالية
    for edu in built_resume.education.all():
        edu_text = f"{edu.degree} {edu.field_of_study} {edu.institution}"
        resume_data['education'].append(edu_text)
        
        # حفظ البيانات المنظمة أيضاً
        resume_data.setdefault('structured_education', []).append({
            'institution': edu.institution,
            'degree': edu.degree,
            'degree_type': edu.degree_type,
            'field_of_study': edu.field_of_study,
            'start_date': edu.start_date,
            'end_date': edu.end_date,
            'current_study': edu.current_study,
            'gpa': edu.gpa
        })
    
    # استخراج اللغات كنصوص للمطابقة الدلالية
    for lang in built_resume.languages.all():
        resume_data['languages'].append(f"{lang.name} {lang.level}")
        
        # حفظ البيانات المنظمة أيضاً
        resume_data.setdefault('structured_languages', []).append({
            'name': lang.name,
            'level': lang.level
        })
    
    # استخراج المشاريع كنصوص للمطابقة الدلالية
    for project in built_resume.projects.all():
        project_text = f"{project.name} {project.description} {project.technologies}"
        resume_data['projects'].append(project_text)
        
        # حفظ البيانات المنظمة أيضاً
        resume_data.setdefault('structured_projects', []).append({
            'name': project.name,
            'description': project.description,
            'technologies': project.technologies,
            'start_date': project.start_date,
            'end_date': project.end_date
        })
    
    # استخراج الشهادات كنصوص للمطابقة الدلالية
    for cert in built_resume.certifications.all():
        cert_text = f"{cert.name} {cert.issuing_organization}"
        resume_data['certifications'].append(cert_text)
        
        # حفظ البيانات المنظمة أيضاً
        resume_data.setdefault('structured_certifications', []).append({
            'name': cert.name,
            'issuing_organization': cert.issuing_organization,
            'issue_date': cert.issue_date,
            'expiry_date': cert.expiry_date
        })
    
    return resume_data

def get_resume_text_content(built_resume):
    """
    تجميع كل محتوى السيرة الذاتية المبنية كنص واحد للتحليل الدلالي
    """
    content_parts = []
    
    # إضافة الملخص
    if built_resume.summary:
        content_parts.append(built_resume.summary)
    
    # إضافة الخبرات
    for exp in built_resume.experiences.all():
        content_parts.extend([
            exp.position,
            exp.company,
            exp.description,
            exp.achievements or ''
        ])
    
    # إضافة التعليم
    for edu in built_resume.education.all():
        content_parts.extend([
            edu.degree,
            edu.field_of_study,
            edu.institution
        ])
    
    # إضافة المهارات
    for skill in built_resume.skills.all():
        content_parts.append(skill.name)
    
    # إضافة المشاريع
    for project in built_resume.projects.all():
        content_parts.extend([
            project.name,
            project.description,
            project.technologies
        ])
    
    return ' '.join(filter(None, content_parts))

def analyze_skills_match(built_resume, job):
    """
    تحليل مطابقة المهارات بشكل مفصل
    """
    resume_skills = set(skill.name.lower() for skill in built_resume.skills.all())
    job_required_skills = set(skill.lower() for skill in (job.required_skills or []))
    job_preferred_skills = set(skill.lower() for skill in (job.preferred_skills or []))
    
    # المهارات المطلوبة والمطابقة
    matched_required = resume_skills & job_required_skills
    missing_required = job_required_skills - resume_skills
    
    # المهارات المفضلة والمطابقة
    matched_preferred = resume_skills & job_preferred_skills
    
    return {
        'matched_required': list(matched_required),
        'missing_required': list(missing_required),
        'matched_preferred': list(matched_preferred),
        'required_match_percentage': len(matched_required) / len(job_required_skills) * 100 if job_required_skills else 0,
        'total_skills_match': len(matched_required) + len(matched_preferred)
    }

def analyze_experience_match(built_resume, job):
    """
    تحليل مطابقة الخبرة
    """
    total_experience = 0
    relevant_experience = 0
    
    for exp in built_resume.experiences.all():
        # حساب سنوات الخبرة
        from datetime import date
        end_date = exp.end_date or date.today()
        years = (end_date.year - exp.start_date.year)
        if end_date.month < exp.start_date.month or (end_date.month == exp.start_date.month and end_date.day < exp.start_date.day):
            years -= 1
        
        total_experience += years
        
        # التحقق من relevance للوظيفة
        if any(keyword.lower() in exp.description.lower() or keyword.lower() in exp.position.lower() 
               for keyword in (job.title.lower().split() + (job.required_skills or []))):
            relevant_experience += years
    
    return {
        'total_years': total_experience,
        'relevant_years': relevant_experience,
        'meets_requirement': total_experience >= (job.experience_years or 0)
    }

def generate_match_reasons(built_resume, job, match_score):
    """
    توليد أسباب المطابقة للسيرة الذاتية المبنية
    """
    reasons = []
    
    # تحليل المهارات
    skills_analysis = analyze_skills_match(built_resume, job)
    if skills_analysis['matched_required']:
        reasons.append(f"متطابق في {len(skills_analysis['matched_required'])} مهارات مطلوبة أساسية")
    
    # تحليل الخبرة
    exp_analysis = analyze_experience_match(built_resume, job)
    if exp_analysis['meets_requirement']:
        reasons.append(f"لديه {exp_analysis['total_years']} سنوات خبرة")
    
    # تحليل التعليم
    education_match = False
    for edu in built_resume.education.all():
        if edu.field_of_study.lower() in (job.title.lower() or ''):
            education_match = True
            break
    
    if education_match:
        reasons.append("خلفية تعليمية مناسبة للمجال")
    
    # إذا كانت النتيجة عالية
    if match_score >= 80:
        reasons.append("مطابقة ممتازة للمتطلبات")
    elif match_score >= 60:
        reasons.append("مطابقة جيدة للمتطلبات")
    
    return reasons[:3]  # إرجاع أفضل 3 أسباب
