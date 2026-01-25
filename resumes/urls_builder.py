# resumes/urls_builder.py
# تم إنشاء هذا الملف لدعم نظام بناء السيرة الذاتية داخل المنصة
from django.urls import path
from .views.builder import *

app_name = 'resumes_builder'

urlpatterns = [
    # === URLs الرئيسية للسير الذاتية ===
    path('', ResumeBuilderView.as_view(), name='resume_list'),
    path('create/', CreateResumeView.as_view(), name='resume_create'),
    path('<int:pk>/', ResumeDetailView.as_view(), name='resume_detail'),
    path('<int:pk>/edit/', EditResumeView.as_view(), name='resume_edit'),
    
    # === URLs للمعلومات الشخصية ===
    path('<int:resume_id>/personal-info/', edit_personal_info, name='edit_personal_info'),
    
    # === URLs للخبرات العملية ===
    path('<int:resume_id>/experience/add/', add_experience, name='add_experience'),
    path('<int:resume_id>/experience/<int:experience_id>/edit/', edit_experience, name='edit_experience'),
    path('<int:resume_id>/experience/<int:experience_id>/delete/', delete_experience, name='delete_experience'),
    
    # === URLs للأقسام الأخرى ===
    path('<int:resume_id>/education/add/', add_education, name='add_education'),
    path('<int:resume_id>/skills/add/', add_skill, name='add_skill'),
    path('<int:resume_id>/languages/add/', add_language, name='add_language'),
    path('<int:resume_id>/projects/add/', add_project, name='add_project'),
    path('<int:resume_id>/certifications/add/', add_certification, name='add_certification'),
    
    # === URLs للعمليات المتقدمة ===
    path('<int:resume_id>/set-default/', set_default_resume, name='set_default'),
    path('<int:resume_id>/delete/', delete_resume, name='delete_resume'),
    path('<int:resume_id>/duplicate/', duplicate_resume, name='duplicate_resume'),
]
