# resumes/services/ai_fallback.py
import re
from matching.services.embedding_engine import get_embedding, similarity

STOPWORDS = {
    "and", "or", "with", "using", "experience",
    "skills", "knowledge", "ability", "abilities",
    "basic", "advanced"
}

def ai_extract_skills(text: str) -> list:
    skills = set()

    SECTION_TITLES = {
        "education", "experience", "work experience", "skills",
        "languages", "certifications", "summary",
        "professional summary", "profile"
    }

    lines = re.split(r'[\n•\-|]', text)

    for line in lines:
        clean = line.strip().lower()

        # ❌ تجاهل الفارغ
        if not clean or len(clean) < 3:
            continue

        # ❌ تجاهل العناوين
        if clean in SECTION_TITLES:
            continue

        # ❌ تجاهل الإيميل
        if re.search(r'\S+@\S+\.\S+', clean):
            continue

        # ❌ تجاهل الروابط
        if "http" in clean or "www" in clean:
            continue

        # ❌ تجاهل العناوين والأرقام
        if re.search(r'\d{2,}', clean):
            continue

        # ❌ تجاهل الأسماء (اسمين فقط بدون كلمات مهنية)
        if len(clean.split()) == 2 and clean.replace(" ", "").isalpha():
            continue

        # ❌ تجاهل الجمل
        if len(clean.split()) > 5:
            continue

        skills.add(clean.title())

    # استخدام النموذج المدمج للتحليل الدلالي إذا كانت المهارات قليلة
    skills_list = sorted(skills)
    
    if len(skills_list) < 3:
        # استخدام النموذج المدمج لاستخراج مهارات إضافية
        return extract_skills_with_embedding(text)
    
    return skills_list


def extract_skills_with_embedding(text: str) -> list:
    """
    استخراج المهارات باستخدام النموذج المدمج (paraphrase-multilingual-MiniLM-L12-v2)
    """
    # قائمة المهارات الشائعة في الموارد البشرية والتقنية
    common_skills = [
        "recruitment", "talent acquisition", "performance management", "hr policies",
        "ats systems", "candidate screening", "interview coordination", "onboarding",
        "employee relations", "compensation and benefits", "training and development",
        "hr analytics", "workforce planning", "employee engagement", "hr compliance",
        "python", "javascript", "java", "react", "django", "sql", "html", "css",
        "docker", "kubernetes", "aws", "git", "agile", "scrum"
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        # حساب التشابه الدلالي بين النص والمهارة
        similarity_score = similarity(text_lower, skill)
        
        # إذا كان التشابه عالٍ (> 0.3)، أضف المهارة
        if similarity_score > 0.3:
            found_skills.append((skill.title(), similarity_score))
    
    # ترتيب المهارات حسب درجة التشابه
    found_skills.sort(key=lambda x: x[1], reverse=True)
    
    # إرجاع أفضل 10 مهارات
    return [skill[0] for skill in found_skills[:10]]
