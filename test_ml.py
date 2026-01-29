import os
import sys
import django

# أضف هذه الأسطر في أعلى الملف (قبل أي import لـ Django)
# افترض أن اسم المشروع config (كما في wsgi.py: config.wsgi)
# و settings.py موجود في config/settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # ← غيّر 'config' إلى اسم مشروعك إذا مختلف

# إذا كان المسار غير مضاف (مثل إذا كان test_ml.py خارج المشروع)
# أضف هذا (اختياري إذا كان في نفس المجلد):
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# الآن قم بتهيئة Django
django.setup()

# بعد هذا يمكنك استيراد أي شيء من Django
from matching.services.ml_client import predict_similarity

# باقي الكود الخاص بك
print(predict_similarity(
    "Sample CV text: Experienced Python developer with Django and REST API skills",
    "Job: Need Python expert with web development experience"
))