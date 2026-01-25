# resumes/services/arabic_processor.py
"""
معالجة خاصة للنصوص العربية
"""

import re
from typing import List, Dict

class ArabicProcessor:
    """معالج النصوص العربية"""
    
    # الأرقام العربية إلى الإنجليزية
    ARABIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    
    # الحروف المتشابهة العربية
    SIMILAR_CHARS = {
        'ا': 'ا',  # ألف مختلفة
        'ى': 'ي',  # ألف مقصورة
        'ة': 'ه',  # تاء مربوطة
    }
    
    @staticmethod
    def is_arabic(text: str) -> bool:
        """التحقق من وجود أحرف عربية"""
        return bool(re.search(r'[\u0600-\u06FF]', text))
    
    @staticmethod
    def clean_arabic(text: str) -> str:
        """تنظيف النص العربي"""
        # حذف الحركات
        text = re.sub(r'[\u064B-\u0652]', '', text)
        
        # تحويل الأرقام العربية
        text = text.translate(ArabicProcessor.ARABIC_DIGITS)
        
        # توحيد الحروف المتشابهة
        for old, new in ArabicProcessor.SIMILAR_CHARS.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    @staticmethod
    def split_arabic_text(text: str) -> List[str]:
        """تقسيم النص العربي إلى كلمات"""
        # إزالة العلامات والفواصل
        text = re.sub(r'[،؛:؟!()""«»]', ' ', text)
        # تقسيم بالفراغات
        words = text.split()
        # إزالة الكلمات القصيرة جداً
        return [w for w in words if len(w) > 2]
    
    @staticmethod
    def normalize_arabic_text(text: str) -> str:
        """توحيد النص العربي للمقارنة"""
        text = ArabicProcessor.clean_arabic(text)
        text = text.lower()
        return text

# مثال الاستخدام:
if __name__ == "__main__":
    text = "مرحباً، أنا أعمل في شركة تقنية! الرقم: ١٢٣"
    
    print("الأصلي:", text)
    print("نظيف:", ArabicProcessor.clean_arabic(text))
    print("موحد:", ArabicProcessor.normalize_arabic_text(text))
    print("مقسم:", ArabicProcessor.split_arabic_text(text))
