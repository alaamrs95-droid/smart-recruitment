# matching/services/matcher.py

from typing import Dict, Any, List
from django.utils.translation import gettext as _
from .embedding_engine import similarity
from .enhanced_matcher import EnhancedMatcher


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def normalize_list(values: List[str]) -> set:
    return set(v.lower().strip() for v in values or [] if v)


def build_resume_text(resume_parsed: Dict) -> str:
    return " ".join(
        resume_parsed.get("skills", []) +
        resume_parsed.get("education", []) +
        resume_parsed.get("experience", [])
    )


def build_job_text(job: Any) -> str:
    return " ".join(
        (job.required_skills or []) +
        (job.preferred_skills or []) +
        [job.title or "", job.description or ""]
    )


def extract_experience_years(experience_list: List[str]) -> int:
    """استخراج سنوات الخبرة من نصوص الخبرة"""
    import re

    for exp in experience_list:
        match = re.search(r'(\d+)\s*(?:years?|سنوات?|سنة)', exp, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return 0


# ------------------------------------------------------------------
# Semantic Matching
# ------------------------------------------------------------------

def calculate_semantic_score(resume_parsed: Dict, job: Any) -> float:
    """
    حساب التشابه الدلالي (Semantic Similarity) باستخدام embeddings
    """
    resume_text = build_resume_text(resume_parsed)
    job_text = build_job_text(job)

    if not resume_text or not job_text:
        return 0.0

    return similarity(resume_text, job_text)


# ------------------------------------------------------------------
# Enhanced Match Score (NEW)
# ------------------------------------------------------------------

def calculate_match_score(resume_parsed: Dict, job: Any) -> Dict:
    """
    حساب درجة المطابقة النهائية (نسخة محسّنة باستخدام EnhancedMatcher)
    """

    matcher = EnhancedMatcher()

    resume_data = {
        "skills": resume_parsed.get("skills", []),
        "languages": resume_parsed.get("languages", []),
        "experience_years": extract_experience_years(
            resume_parsed.get("experience", [])
        ),
    }

    result = matcher.calculate_match_score(resume_data, job)

    # تهيئة المفاتيح إن لم تكن موجودة
    if "strengths" not in result:
        result["strengths"] = []
    if "weaknesses" not in result:
        result["weaknesses"] = []
    if "recommendations" not in result:
        result["recommendations"] = []

    # إضافة التشابه الدلالي كعامل داعم (غير مكسِر)
    semantic_similarity = calculate_semantic_score(resume_parsed, job)
    result["details"]["semantic"] = round(semantic_similarity * 100, 1)

    if semantic_similarity >= 0.7:
        result["strengths"].append(_("Strong semantic alignment with job description"))
    elif semantic_similarity < 0.4:
        result["weaknesses"].append(_("Low semantic similarity with job description"))

    # إضافة التوصيات
    result["recommendations"] = generate_recommendations(result, job)

    # إضافة اللون والتصنيف
    result["color_class"] = get_score_color_class(result["score"])
    result["label"] = get_score_label(result["score"])

    return result


def generate_recommendations(result: Dict, job: Any) -> List[str]:
    """توليد توصيات تحسينية ذكية"""
    recommendations = []

    details = result.get("details", {})

    # المهارات المطلوبة
    missing_skills = details.get("required_skills", {}).get("missing", [])
    if missing_skills:
        if len(missing_skills) == 1:
            recommendations.append(
                _("Learn {} to improve your match score").format(missing_skills[0])
            )
        else:
            recommendations.append(
                _("Improve these skills: {}").format(", ".join(missing_skills[:3]))
            )

    # الخبرة
    exp_details = details.get("experience", {})
    if exp_details and not exp_details.get("meets_requirement", True):
        diff = exp_details.get("job_years", 0) - exp_details.get("resume_years", 0)
        if diff > 0:
            recommendations.append(
                _("Gain {} more year(s) of experience").format(diff)
            )

    # اللغات
    missing_langs = details.get("languages", {}).get("missing", [])
    if missing_langs:
        recommendations.append(
            _("Consider learning: {}").format(", ".join(missing_langs))
        )

    return recommendations


# ------------------------------------------------------------------
# UI Helpers
# ------------------------------------------------------------------



def get_score_color(score: float) -> str:
    """
    لون HEX للاستخدام في charts أو inline styles
    """
    if score >= 80:
        return "#28a745"   # Bootstrap green
    if score >= 60:
        return "#ffc107"   # Bootstrap yellow
    return "#dc3545"       # Bootstrap red


def get_score_color_class(score: float) -> str:
    """
    Bootstrap color class للاستخدام في UI
    (badge / progress-bar / borders)
    """
    if score >= 80:
        return "success"
    if score >= 60:
        return "warning"
    return "danger"


def get_score_label(score: float) -> str:
    """
    وصف نصي لمستوى المطابقة
    """
    if score >= 90:
        return _("Perfect")
    if score >= 80:
        return _("Excellent")
    if score >= 70:
        return _("Very Good")
    if score >= 60:
        return _("Good")
    if score >= 50:
        return _("Moderate")
    if score >= 40:
        return _("Fair")
    if score >= 30:
        return _("Poor")
    return _("Very Poor")

# ------------------------------------------------------------------
# Public APIs
# ------------------------------------------------------------------

def match_resume_to_job(resume, job) -> Dict:
    return calculate_match_score(resume.parsed_data, job)


def batch_match_resumes_to_job(job, resumes):
    matches = []
    for resume in resumes:
        if resume.is_processed:
            matches.append({
                "resume": resume,
                "match": match_resume_to_job(resume, job),
            })

    return sorted(matches, key=lambda x: x["match"]["score"], reverse=True)


def batch_match_jobs_to_resume(resume, jobs):
    matches = []
    for job in jobs:
        if job.is_active:
            result = match_resume_to_job(resume, job)
            if result["score"] > 10:
                matches.append({
                    "job": job,
                    "match": result,
                })

    return sorted(matches, key=lambda x: x["match"]["score"], reverse=True)
# End of matching/services/matcher.py
