# resumes/services/parsing.py
import re
from typing import List, Dict, Any
from .ai_fallback import ai_extract_skills


def simple_parse_resume(raw_text):
    """دالة بسيطة لتحليل النص واستخراج المعلومات الأساسية"""
    parsed_data = {
        'skills': [],
        'languages': [],
        'education': [],
        'experience': []
    }
    
    # استخراج المهارات
    skills_patterns = [
        r'(?:Skills?|المهارات)[:\n](.*?)(?:\n\n|\n[A-Z]|\Z)',
        r'(?:Technical Skills?|المهارات التقنية)[:\n](.*?)(?:\n\n|\n[A-Z]|\Z)',
        r'(?:Core Competencies|الكفاءات الأساسية)[:\n](.*?)(?:\n\n|\n[A-Z]|\Z)'
    ]
    
    for pattern in skills_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            skills = [skill.strip() for skill in re.split(r'[,;•\n]', match) if skill.strip()]
            parsed_data['skills'].extend(skills)
    
    # استخراج اللغات
    languages_patterns = [
        r'(?:Languages?|اللغات)[:\n](.*?)(?:\n\n|\n[A-Z]|\Z)',
        r'(?:Language Proficiency|إجادة اللغات)[:\n](.*?)(?:\n\n|\n[A-Z]|\Z)'
    ]
    
    for pattern in languages_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            languages = [lang.strip() for lang in re.split(r'[,;•\n]', match) if lang.strip()]
            parsed_data['languages'].extend(languages)
    
    # استخراج التعليم
    education_patterns = [
        r'(?:Education|التعليم|Educational Background|الخلفية التعليمية)[:\n](.*?)(?:\n\n|\nExperience|\nSkills|\n[A-Z]|\Z)',
        r'(?:Degree|درجة)[\s:](.*?)(?:\n\n|\nExperience|\nSkills|\n[A-Z]|\Z)'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            education = [edu.strip() for edu in re.split(r'[,;•\n]', match) if edu.strip()]
            parsed_data['education'].extend(education)
    
    # استخراج الخبرة
    experience_patterns = [
        r'(?:Experience|الخبرة|Work Experience|الخبرة العملية|Professional Experience|الخبرة المهنية)[:\n](.*?)(?:\n\n|\nEducation|\nSkills|\n[A-Z]|\Z)',
        r'(?:Employment History|سجل التوظيف)[:\n](.*?)(?:\n\n|\nEducation|\nSkills|\n[A-Z]|\Z)'
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            experience = [exp.strip() for exp in re.split(r'[,;•\n]', match) if exp.strip()]
            parsed_data['experience'].extend(experience)
    
    # إزالة التكرارات وتنظيف البيانات
    for key in parsed_data:
        parsed_data[key] = list(set(parsed_data[key]))  # إزالة التكرارات
        parsed_data[key] = [item for item in parsed_data[key] if len(item) > 2]  # إزالة العناصر القصيرة جداً
    
    return parsed_data


def parse_resume(text: str) -> Dict[str, Any]:
    """
    تحليل السيرة الذاتية بشكل متقدم باستخدام regex
    مع AI fallback ذكي عند فشل الاستخراج
    """
    if not text or len(text.strip()) < 10:
        return get_default_parsed_data()

    text_lower = text.lower()

    # 1️⃣ استخراج المهارات بالـ regex
    skills = extract_skills_advanced(text_lower)

    # 2️⃣ AI fallback إذا كانت المهارات قليلة (أقل من 3)
    if len(skills) < 3:
        skills = ai_extract_skills(text)

    return {
        "skills": skills,
        "languages": extract_languages_advanced(text_lower),
        "education": extract_education_advanced(text_lower),
        "experience": extract_experience_advanced(text_lower),
        "certifications": extract_certifications(text_lower),
        "summary": extract_summary(text),
    }


def get_default_parsed_data() -> Dict[str, Any]:
    """بيانات افتراضية عندما لا يمكن تحليل النص"""
    return {
        "skills": [],
        "languages": [],
        "education": [],
        "experience": [],
        "certifications": [],
        "summary": "",
    }


def extract_skills_advanced(text: str) -> List[str]:
    """استخراج المهارات بشكل متقدم (Regex)"""

    TECH_SKILLS = {
        "programming_languages": [
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust",
            "typescript", "swift", "kotlin", "scala", "r", "matlab", "perl", "shell"
        ],
        "web_frameworks": [
            "django", "flask", "fastapi", "react", "vue", "angular", "node.js", "express",
            "spring", "laravel", "ruby on rails", "asp.net", "jquery", "bootstrap"
        ],
        "databases": [
            "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "sql server",
            "cassandra", "elasticsearch", "dynamodb", "firebase"
        ],
        "devops_tools": [
            "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "aws",
            "azure", "gcp", "terraform", "ansible", "nginx", "apache"
        ],
        "data_science": [
            "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "keras",
            "opencv", "spark", "hadoop", "tableau", "power bi"
        ],
        "mobile": [
            "android", "ios", "react native", "flutter", "xamarin"
        ],
        "other_tech": [
            "rest api", "graphql", "websocket", "microservices", "agile", "scrum",
            "ci/cd", "tdd", "oop", "functional programming", "linux", "windows"
        ]
    }

    found_skills = []

    for skills in TECH_SKILLS.values():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                found_skills.append(skill.title())

    # إزالة التكرار مع الحفاظ على الترتيب
    unique_skills = list(dict.fromkeys(found_skills))

    # fallback بسيط داخل regex
    if not unique_skills:
        common_words = ["python", "django", "javascript", "sql", "html", "css"]
        for word in common_words:
            if word in text:
                unique_skills.append(word.title())

    # تنظيف كلمات غير مفيدة
    BLACKLIST = {"present", "optional", "additions"}
    unique_skills = [
        s for s in unique_skills if s.lower() not in BLACKLIST
    ]

    return unique_skills[:20]


def extract_languages_advanced(text: str) -> List[str]:
    """استخراج اللغات"""

    LANGUAGES = {
        "arabic": ["arabic", "العربية", "عربي"],
        "english": ["english", "الإنجليزية", "انجليزي", "إنجليزي"],
        "french": ["french", "الفرنسية", "فرنسي"],
        "spanish": ["spanish", "الإسبانية", "اسباني"],
        "german": ["german", "الألمانية", "الماني"],
        "chinese": ["chinese", "الصينية", "صيني", "mandarin"],
        "japanese": ["japanese", "اليابانية", "ياباني"],
        "russian": ["russian", "الروسية", "روسي"],
        "turkish": ["turkish", "التركية", "تركي"],
        "hindi": ["hindi", "الهندية", "هندي"],
    }

    found_languages = []

    for lang, keywords in LANGUAGES.items():
        for keyword in keywords:
            if keyword in text:
                found_languages.append(lang.title())
                break

    return list(dict.fromkeys(found_languages))


def extract_education_advanced(text: str) -> List[str]:
    """استخراج التعليم"""

    education_levels = []

    degrees = [
        ("Bachelor", ["bachelor", "bsc", "bs", "بكالوريوس"]),
        ("Master", ["master", "msc", "ms", "ماجستير"]),
        ("PhD", ["phd", "doctorate", "دكتوراه"]),
        ("Diploma", ["diploma", "دبلوم"]),
    ]

    for degree, keywords in degrees:
        for keyword in keywords:
            if keyword in text:
                education_levels.append(degree)
                break

    majors = [
        "computer science", "software engineering", "information technology",
        "architecture", "civil engineering", "business administration",
        "data science", "artificial intelligence"
    ]

    for major in majors:
        if major in text:
            education_levels.append(major.title())

    return list(dict.fromkeys(education_levels))[:5]


def extract_experience_advanced(text: str) -> List[str]:
    """استخراج الخبرة"""

    experience_info = []

    # استخراج سنوات الخبرة
    years_patterns = [
        r'(\d+)\s*(?:years?|سنوات?)(?:\s*of)?\s*experience',
        r'experience[:\s]*(\d+)\s*(?:years?|سنوات?)',
        r'(\d+)\s*(?:years?|سنوات?)\s*(?:of)?\s*(?:experience|خبرة)',
        r'(\d+)\s*years?\s*(?:of)?\s*(?:experience|work)',
    ]

    for pattern in years_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if int(match) > 0:
                experience_info.append(f"{match} Years Experience")

    # مستويات الخبرة
    levels = [
        ("Intern", ["intern", "internship", "متدرب"]),
        ("Junior", ["junior", "entry level", "مبتدئ"]),
        ("Mid-Level", ["mid-level", "mid level", "متوسط"]),
        ("Senior", ["senior", "كبير", "خبير"]),
        ("Lead", ["lead", "team lead", "قائد"]),
        ("Manager", ["manager", "مدير"]),
    ]

    for level, keywords in levels:
        for keyword in keywords:
            if keyword in text:
                experience_info.append(level.title())
                break

    year_patterns = [
        r'(\d+)\s*\+?\s*years?\s*(of)?\s*experience',
        r'خبرة\s*(\d+)\s*سنوات?',
    ]

    for pattern in year_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            years = int(match[0]) if isinstance(match, tuple) else int(match)
            experience_info.append(f"{years} Years Experience")

    return list(dict.fromkeys(experience_info))[:5]


def extract_certifications(text: str) -> List[str]:
    """استخراج الشهادات"""

    certifications = []

    known_certs = [
        "aws certified", "azure certified", "google cloud certified",
        "pmp", "scrum master", "six sigma", "ccna", "ccnp"
    ]

    for cert in known_certs:
        if cert in text:
            certifications.append(cert.title())

    return list(dict.fromkeys(certifications))[:5]


def extract_summary(text: str) -> str:
    """استخراج ملخص بسيط"""

    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:
            return sentence[:200] + "..." if len(sentence) > 200 else sentence
    return ""


# 🔁 دوال توافق خلفي
def extract_skills(text):
    return extract_skills_advanced(text.lower())


def extract_languages(text):
    return extract_languages_advanced(text.lower())


def extract_education(text):
    return extract_education_advanced(text.lower())


def extract_experience(text):
    return extract_experience_advanced(text.lower())
