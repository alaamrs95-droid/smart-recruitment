# resumes/urls/web.py
from django.urls import path, include
from ..views import web
from ..views.profile import resume_profile_view, set_primary_resume, toggle_matching_status

app_name = 'resumes'

urlpatterns = [
    # السير الذاتية المرفوعة
    path('', web.resume_list_view, name='list'),
    path('my/', web.my_resumes_view, name='my'),
    path('upload/', web.upload_resume_view, name='upload'),
    path('<int:pk>/', web.resume_detail_view, name='detail'),
    path('<int:pk>/update/', web.update_resume_view, name='update'),
    path('<int:pk>/delete/', web.delete_resume_view, name='delete'),
    
    # ملف تعريف السيرة الذاتية
    path('profile/', resume_profile_view, name='profile'),
    path('set-primary/<str:resume_type>/', set_primary_resume, name='set_primary'),
    path('toggle-matching/', toggle_matching_status, name='toggle_matching'),
    
    # نظام بناء السير الذاتية
    path('builder/', include('resumes.urls_builder')),
]