# resumes/urls_profile.py
# تم إنشاء هذا الملف لروابط ملفات تعريف السير الذاتية
from django.urls import path
from . import views_profile

app_name = 'resumes_profile'

urlpatterns = [
    path('profile/', views_profile.resume_profile_view, name='profile'),
    path('set-primary/<str:resume_type>/', views_profile.set_primary_resume, name='set_primary'),
    path('toggle-matching/', views_profile.toggle_matching_status, name='toggle_matching'),
]
