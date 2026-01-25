
# matching/services/enhanced_matcher.py
"""
محرك مطابقة محسّن مع دعم المرادفات والعربية
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .embedding_engine import get_embedding
from resumes.services.skill_synonyms import SkillSynonyms
from resumes.services.arabic_processor import ArabicProcessor


class EnhancedMatcher:
    """محرك مطابقة محسّن"""
    
    def __init__(self):
        self.weights = {
            'semantic': 0.25,
            'required_skills': 0.40,
            'preferred_skills': 0.15,
            'languages': 0.10,
            'experience': 0.10,
        }
    
    def calculate_semantic_score(self, resume_text: str, job_text: str) -> float:
        """حساب التشابه الدلالي"""
        if not resume_text or not job_text:
            return 0.0
        
        try:
            v1 = np.array(get_embedding(resume_text)).reshape(1, -1)
            v2 = np.array(get_embedding(job_text)).reshape(1, -1)
            similarity = float(cosine_similarity(v1, v2)[0][0])
            return similarity
        except Exception as e:
            print(f"خطأ في حساب التشابه: {e}")
            return 0.0
    
    def calculate_skills_match(
        self, 
        resume_skills: List[str], 
        job_skills: List[str],
        weight: float
    ) -> Dict[str, Any]:
        """مطابقة المهارات مع المرادفات"""
        
        if not job_skills:
            return {
                'score': 0,
                'percentage': 0,
                'matched': [],
                'missing': [],
            }
        
        # استخدام SkillSynonyms للمطابقة
        result = SkillSynonyms.match_skills(resume_skills, job_skills)
        
        matched_count = len(result['matched'])
        total_count = len(job_skills)
        percentage = matched_count / total_count if total_count > 0 else 0
        
        return {
            'score': percentage * weight * 100,
            'percentage': f"{percentage * 100:.1f}%",
            'matched': result['matched'],
            'missing': result['missing'],
            'matched_count': matched_count,
            'total_count': total_count,
        }
    
    def calculate_experience_score(
        self, 
        resume_years: int, 
        job_years: int,
        weight: float
    ) -> Dict[str, Any]:
        """حساب درجة الخبرة"""
        
        if not job_years or job_years <= 0:
            return {'score': 0, 'percentage': '0%', 'details': 'No requirement'}
        
        if not resume_years:
            resume_years = 0
        
        ratio = min(resume_years / job_years, 1.0)
        score = ratio * weight * 100
        
        return {
            'score': score,
            'percentage': f"{ratio * 100:.1f}%",
            'resume_years': resume_years,
            'job_years': job_years,
            'meets_requirement': resume_years >= job_years,
        }
    
    def calculate_languages_match(
        self, 
        resume_languages: List[str], 
        job_languages: List[str],
        weight: float
    ) -> Dict[str, Any]:
        """مطابقة اللغات"""
        
        if not job_languages:
            return {'score': 0, 'percentage': '0%', 'matched': [], 'missing': []}
        
        # توحيد اللغات
        resume_langs = {lang.lower() for lang in resume_languages}
        job_langs = {lang.lower() for lang in job_languages}
        
        matched = resume_langs & job_langs
        missing = job_langs - resume_langs
        
        percentage = len(matched) / len(job_langs) if job_langs else 0
        score = percentage * weight * 100
        
        return {
            'score': score,
            'percentage': f"{percentage * 100:.1f}%",
            'matched': list(matched),
            'missing': list(missing),
        }
    
    def calculate_match_score(self, resume_data: Dict, job: Any) -> Dict:
        """حساب درجة المطابقة الكاملة"""
        
        total_score = 0
        details = {}
        
        # 1. Semantic Matching
        resume_text = " ".join(resume_data.get("skills", []) + 
                              resume_data.get("experience", []))
        job_text = " ".join(job.required_skills or []) + " " + (job.title or "")
        
        semantic_similarity = self.calculate_semantic_score(resume_text, job_text)
        semantic_score = semantic_similarity * self.weights['semantic'] * 100
        details['semantic'] = {
            'score': semantic_score,
            'percentage': f"{semantic_similarity * 100:.1f}%",
            'similarity': semantic_similarity,
        }
        total_score += semantic_score
        
        # 2. Required Skills
        required_result = self.calculate_skills_match(
            resume_data.get("skills", []),
            job.required_skills or [],
            self.weights['required_skills']
        )
        details['required_skills'] = required_result
        total_score += required_result['score']
        
        # 3. Preferred Skills
        preferred_result = self.calculate_skills_match(
            resume_data.get("skills", []),
            job.preferred_skills or [],
            self.weights['preferred_skills']
        )
        details['preferred_skills'] = preferred_result
        total_score += preferred_result['score']
        
        # 4. Languages
        languages_result = self.calculate_languages_match(
            resume_data.get("languages", []),
            job.languages or [],
            self.weights['languages']
        )
        details['languages'] = languages_result
        total_score += languages_result['score']
        
        # 5. Experience
        experience_result = self.calculate_experience_score(
            resume_data.get("experience_years", 0) or 0,
            job.experience_years or 0,
            self.weights['experience']
        )
        details['experience'] = experience_result
        total_score += experience_result['score']
        
        return {
            'score': round(total_score, 2),
            'percentage': f"{round(total_score, 1)}%",
            'level': self._get_match_level(total_score),
            'details': details,
            'summary': self._generate_summary(details),
        }
    
    @staticmethod
    def _get_match_level(score: float) -> str:
        """تحديد مستوى المطابقة"""
        if score >= 80:
            return "Excellent Match! 🎉"
        elif score >= 60:
            return "Good Match! ✓"
        elif score >= 40:
            return "Fair Match ⚠️"
        else:
            return "Low Match ❌"
    
    @staticmethod
    def _generate_summary(details: Dict) -> str:
        """توليد ملخص نصي"""
        summary = []
        
        # مهارات متطابقة
        if details['required_skills']['matched']:
            summary.append(f"✓ Matched {len(details['required_skills']['matched'])} required skills")
        
        # مهارات ناقصة
        if details['required_skills']['missing']:
            summary.append(f"✗ Missing {len(details['required_skills']['missing'])} required skills")
        
        # لغات
        if details['languages']['matched']:
            summary.append(f"✓ Speaks required languages")
        
        # خبرة
        if details['experience']['meets_requirement']:
            summary.append(f"✓ Has sufficient experience")
        else:
            summary.append(f"⚠ Experience slightly below requirement")
        
        return " | ".join(summary)


# مثال الاستخدام:
if __name__ == "__main__":
    matcher = EnhancedMatcher()
    
    resume_data = {
        'skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
        'languages': ['English', 'Arabic'],
        'experience_years': 5,
    }
    
    # Object وهمي للوظيفة
    class Job:
        title = "Senior Python Developer"
        required_skills = ['Python', 'Django', 'PostgreSQL']
        preferred_skills = ['Docker', 'Kubernetes']
        languages = ['English']
        experience_years = 4
    
    job = Job()
    result = matcher.calculate_match_score(resume_data, job)
    print(result)