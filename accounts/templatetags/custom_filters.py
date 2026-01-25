# accounts/templatetags/custom_filters.py
# تم إنشاء هذا الملف لتجميع جميع الفلاتر المخصصة للنظام
from django import template

register = template.Library()

# === الفلاتر الحسابية ===

@register.filter
def multiply(value, arg):
    """ضرب القيمة في العامل"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """قسمة القيمة على العامل"""
    try:
        return float(value) / float(arg) if arg != 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """حساب النسبة المئوية"""
    try:
        return (float(value) / float(total)) * 100 if total != 0 else 0
    except (ValueError, TypeError):
        return 0

# === فلاتر السير الذاتية ===

@register.filter
def has_attr(obj, attr_name):
    """
    التحقق من وجود خاصية معينة في الكائن
    """
    return hasattr(obj, attr_name)

@register.filter
def get_resume_title(resume):
    """
    الحصول على عنوان السيرة الذاتية (للمبنية) أو اسم الملف (للمرفوعة)
    """
    if hasattr(resume, 'title'):
        return resume.title
    elif hasattr(resume, 'original_filename'):
        return resume.original_filename
    else:
        return "Unknown Resume"

@register.filter
def get_resume_type(resume):
    """
    الحصول على نوع السيرة الذاتية
    """
    if hasattr(resume, 'title'):
        return "built"
    elif hasattr(resume, 'original_filename'):
        return "uploaded"
    else:
        return "unknown"

@register.filter
def get_resume_icon(resume):
    """
    الحصول على أيقونة مناسبة لنوع السيرة الذاتية
    """
    if hasattr(resume, 'title'):
        return "fas fa-edit"
    elif hasattr(resume, 'original_filename'):
        return "fas fa-file-upload"
    else:
        return "fas fa-file"

@register.filter
def get_resume_color(resume):
    """
    الحصول على لون مناسب لنوع السيرة الذاتية
    """
    if hasattr(resume, 'title'):
        return "success"
    elif hasattr(resume, 'original_filename'):
        return "info"
    else:
        return "secondary"

@register.filter
def get_resume_url(resume):
    """
    الحصول على رابط السيرة الذاتية
    """
    if hasattr(resume, 'title'):
        # سيرة ذاتية مبنية
        return f"/resumes-builder/{resume.id}/"
    elif hasattr(resume, 'original_filename'):
        # سيرة ذاتية مرفوعة
        return f"/resumes/{resume.id}/"
    else:
        return "#"

@register.filter
def format_experience_years(years):
    """
    تنسيق سنوات الخبرة
    """
    if not years:
        return "No experience"
    if years == 1:
        return "1 year"
    elif years < 1:
        return f"< 1 year"
    else:
        return f"{int(years)}+ years"

# === فلاتر النصوص والتنسيق ===

@register.filter
def truncatechars_words(value, arg):
    """
    قص النص مع الحفاظ على الكلمات الكاملة
    """
    try:
        limit = int(arg)
        if len(value) <= limit:
            return value
        
        words = value.split()
        result = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= limit:
                result.append(word)
                current_length += len(word) + 1
            else:
                break
        
        return ' '.join(result) + '...'
    except (ValueError, TypeError):
        return value

@register.filter
def get_match_color_class(score):
    """
    الحصول على لون مناسب لدرجة المطابقة
    """
    if score >= 80:
        return "success"
    elif score >= 60:
        return "warning"
    else:
        return "secondary"

@register.filter
def get_match_level_text(score):
    """
    الحصول على نص مناسب لدرجة المطابقة
    """
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    else:
        return "Moderate"

@register.filter
def get_match_level_text_ar(score):
    """
    الحصول على نص عربي مناسب لدرجة المطابقة
    """
    if score >= 80:
        return "ممتاز"
    elif score >= 60:
        return "جيد"
    else:
        return "مقبول"

@register.filter
def arabic_number(value):
    """
    تحويل الأرقام إلى أرقام عربية
    """
    try:
        value = str(value)
        arabic_numbers = {
            '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
            '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
        }
        return ''.join(arabic_numbers.get(digit, digit) for digit in value)
    except (ValueError, TypeError):
        return value

# === فلاتر التواريخ ===

@register.filter
def time_ago(value):
    """
    عرض الوقت المنقضي بصورة سهلة
    """
    from datetime import datetime, timezone
    
    if not value:
        return ""
    
    now = datetime.now(timezone.utc)
    diff = now - value
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

@register.filter
def format_date_arabic(value):
    """
    تنسيق التاريخ بالصيغة العربية
    """
    if not value:
        return ""
    
    try:
        months = [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        return f"{value.day} {months[value.month - 1]} {value.year}"
    except (ValueError, TypeError, AttributeError):
        return str(value)

# === فلاتر الحالة والألوان ===

@register.filter
def status_badge_class(status):
    """
    الحصول على لون الشارة المناسب للحالة
    """
    status_colors = {
        'active': 'success',
        'inactive': 'secondary',
        'pending': 'warning',
        'rejected': 'danger',
        'approved': 'success',
        'completed': 'info',
        'cancelled': 'danger'
    }
    return status_colors.get(status.lower(), 'secondary')

@register.filter
def progress_bar_color(percentage):
    """
    الحصول على لون شريط التقدم المناسب
    """
    if percentage >= 80:
        return 'bg-success'
    elif percentage >= 60:
        return 'bg-warning'
    elif percentage >= 40:
        return 'bg-info'
    else:
        return 'bg-danger'

# === فلاتر القوائم والعد ===

@register.filter
def count_words(text):
    """
    عد الكلمات في النص
    """
    if not text:
        return 0
    return len(text.split())

@register.filter
def get_item(dictionary, key):
    """
    الحصول على قيمة من القاموس
    """
    return dictionary.get(key, '')

@register.filter
def list_length(items):
    """
    الحصول على طول القائمة
    """
    try:
        return len(items)
    except (TypeError, AttributeError):
        return 0

# === فلاتر الروابط والـ URL ===

@register.filter
def add_http(url):
    """
    إضافة http إذا لم يكن موجوداً
    """
    if url and not url.startswith(('http://', 'https://')):
        return f'http://{url}'
    return url

@register.filter
def domain_from_url(url):
    """
    استخراج اسم النطاق من الرابط
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return url

# === فلاتر الأمان والتنظيف ===

@register.filter
def safe_email(email):
    """
    إخفاء جزء من البريد الإلكتروني للأمان
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) > 2:
        local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{local}@{domain}"

@register.filter
def escape_csv(value):
    """
    الهروب من الأحرف الخاصة في CSV
    """
    if not value:
        return ""
    
    value = str(value)
    if any(char in value for char in [',', '"', '\n', '\r']):
        value = value.replace('"', '""')
        value = f'"{value}"'
    
    return value

# === فلاتر متقدمة ===

@register.simple_tag
def query_transform(request, **kwargs):
    """
    تعديل معاملات الـ URL الحالية
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            updated.pop(key, None)
        else:
            updated[key] = value
    return updated.urlencode()

@register.filter
def humanize_file_size(size):
    """
    تحويل حجم الملف إلى صيغة مقروءة
    """
    if not size:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

@register.filter
def get_initials(name, count=2):
    """
    الحصول على الأحرف الأولى من الاسم
    """
    if not name:
        return ""
    
    words = name.split()
    initials = [word[0].upper() for word in words[:count] if word]
    return ''.join(initials)

# === فلاتر خاصة بالمنصة ===

@register.filter
def job_type_ar(job_type):
    """
    ترجمة نوع الوظيفة إلى العربية
    """
    types = {
        'full_time': 'دوام كامل',
        'part_time': 'دوام جزئي',
        'contract': 'عقد',
        'internship': 'تدريب',
        'remote': 'عن بعد',
        'hybrid': 'مختلط'
    }
    return types.get(job_type.lower(), job_type)

@register.filter
def experience_level_ar(level):
    """
    ترجمة مستوى الخبرة إلى العربية
    """
    levels = {
        'entry': 'مبتدئ',
        'junior': 'مبتدئ',
        'mid': 'متوسط',
        'senior': 'خبير',
        'lead': 'قائد فريق',
        'manager': 'مدير'
    }
    return levels.get(level.lower(), level)

@register.filter
def skill_level_ar(level):
    """
    ترجمة مستوى المهارة إلى العربية
    """
    levels = {
        'beginner': 'مبتدئ',
        'intermediate': 'متوسط',
        'advanced': 'متقدم',
        'expert': 'خبير'
    }
    return levels.get(level.lower(), level)

@register.filter
def language_level_ar(level):
    """
    ترجمة مستوى اللغة إلى العربية
    """
    levels = {
        'basic': 'أساسي',
        'intermediate': 'متوسط',
        'fluent': 'متمكن',
        'native': 'الأم'
    }
    return levels.get(level.lower(), level)

# === فلاتر إضافية للنماذج ===

@register.filter
def get_class_name(obj):
    """
    الحصول على اسم الكلاس للكائن
    """
    return obj.__class__.__name__
