# resumes/services/skill_synonyms.py
"""
قاموس المرادفات للمهارات التقنية
يدعم العربية والإنجليزية
"""

from typing import Dict, Set, List

class SkillSynonyms:
    """إدارة المرادفات والمهارات المتشابهة"""
    
    # قاموس المرادفات الرئيسي
    SYNONYMS_MAP = {
        # Programming Languages
        'python': {'py', 'python3', 'python 3', 'python3.x'},
        'javascript': {'js', 'node.js', 'nodejs', 'node', 'javascript/typescript'},
        'java': {'java programming', 'java development'},
        'csharp': {'c#', 'c-sharp', 'dotnet'},
        'cpp': {'c++', 'c plus plus'},
        
        # Web Frameworks
        'django': {'django framework', 'django rest'},
        'react': {'reactjs', 'react.js', 'react frontend'},
        'angular': {'angularjs', 'angular.js'},
        'vue': {'vue.js', 'vuejs'},
        'fastapi': {'fastapi framework'},
        
        # Databases
        'postgresql': {'postgres', 'psql', 'postgresql database'},
        'mysql': {'mysql database', 'mariadb'},
        'mongodb': {'mongo', 'mongodb database', 'nosql'},
        'redis': {'redis cache', 'redis database'},
        'sqlserver': {'sql server', 'mssql', 'ms sql', 't-sql'},
        
        # DevOps & Cloud
        'docker': {'containerization', 'docker containers', 'dockerization'},
        'kubernetes': {'k8s', 'kube', 'container orchestration'},
        'aws': {'amazon web services', 'amazon cloud'},
        'gcp': {'google cloud platform', 'google cloud'},
        'azure': {'microsoft azure', 'azure cloud'},
        'jenkins': {'ci/cd', 'continuous integration'},
        'git': {'github', 'gitlab', 'bitbucket', 'version control'},
        
        # Data Science
        'machinelearning': {'ml', 'machine learning', 'ai', 'artificial intelligence'},
        'deeplearning': {'deep learning', 'neural networks', 'tensorflow', 'pytorch'},
        'pandas': {'pandas library', 'data manipulation'},
        'numpy': {'numerical python', 'array processing'},
        'scikit-learn': {'sklearn', 'scikit learn', 'machine learning library'},
        
        # Other
        'restapi': {'rest', 'rest web services', 'web api'},
        'graphql': {'graph ql', 'graphql api'},
        'microservices': {'micro services', 'service oriented'},
        'agile': {'scrum', 'agile methodology'},
        'devops': {'dev ops', 'deployment operations'},
        'linux': {'unix', 'linux operating system'},
        'docker': {'container', 'containerization'},
    }
    
    # العربية -> الإنجليزية
    ARABIC_TRANSLATION = {
        'بايثون': 'python',
        'جافاسكريبت': 'javascript',
        'جافا': 'java',
        'جنقو': 'django',
        'ريأكت': 'react',
        'ڤو': 'vue',
        'ديانجو': 'django',
        'قاعدة بيانات': 'database',
        'قاعدة البيانات': 'database',
        'تطوير': 'development',
        'تطوير الويب': 'web development',
        'تطوير الخادم': 'backend development',
        'تطوير الواجهة': 'frontend development',
        'الذكاء الاصطناعي': 'artificial intelligence',
        'تعلم آلي': 'machine learning',
        'تعلم عميق': 'deep learning',
        'معالجة البيانات': 'data processing',
        'الأمن السيبراني': 'cybersecurity',
        'الشبكات': 'networking',
        'إدارة الخوادم': 'server administration',
        'خوادم': 'servers',
        'سحابة': 'cloud',
        'حوسبة سحابية': 'cloud computing',
        'حاويات': 'containers',
        'أوركسترا': 'orchestration',
    }
    
    @classmethod
    def get_normalized_skill(cls, skill: str) -> str:
        """
        توحيد المهارة إلى شكل موحد
        مثال: "python3" → "python"
        """
        skill = skill.strip().lower()
        
        # ترجمة العربية أولاً
        if any('\u0600' <= c <= '\u06FF' for c in skill):
            skill = cls.ARABIC_TRANSLATION.get(skill, skill)
        
        # البحث عن المهارة في الخريطة
        for main_skill, synonyms in cls.SYNONYMS_MAP.items():
            if skill in synonyms or skill == main_skill:
                return main_skill
        
        return skill
    
    @classmethod
    def get_all_forms(cls, skill: str) -> Set[str]:
        """
        الحصول على جميع صيغ المهارة
        مثال: "django" → {'django', 'django framework', 'django rest', ...}
        """
        normalized = cls.get_normalized_skill(skill)
        return cls.SYNONYMS_MAP.get(normalized, {normalized})
    
    @classmethod
    def match_skills(cls, resume_skills: List[str], job_skills: List[str]):
        """
        مطابقة المهارات مع الأخذ بالمرادفات
        يرجع: (matched_skills, missing_skills, partial_match)
        """
        # توحيد المهارات
        resume_normalized = {cls.get_normalized_skill(s) for s in resume_skills}
        job_normalized = {cls.get_normalized_skill(s) for s in job_skills}
        
        # المطابقة
        matched = resume_normalized & job_normalized
        missing = job_normalized - resume_normalized
        
        return {
            'matched': list(matched),
            'missing': list(missing),
            'match_percentage': len(matched) / len(job_normalized) * 100 if job_normalized else 0,
        }


# الاستخدام:
if __name__ == "__main__":
    # مثال 1: توحيد مهارة واحدة
    print(SkillSynonyms.get_normalized_skill("python3"))  # → "python"
    print(SkillSynonyms.get_normalized_skill("js"))       # → "javascript"
    print(SkillSynonyms.get_normalized_skill("بايثون"))   # → "python"
    
    # مثال 2: مطابقة مهارات
    resume = ["Python", "JavaScript", "Django"]
    job = ["python3", "nodejs", "react", "docker"]
    result = SkillSynonyms.match_skills(resume, job)
    print(result)
    # {
    #   'matched': ['python', 'javascript'],
    #   'missing': ['react', 'docker'],
    #   'match_percentage': 50.0
    # }