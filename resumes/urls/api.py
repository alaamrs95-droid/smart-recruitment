# resumes/urls/api.py
from django.urls import path
from resumes.views.api import (
    UploadResumeAPIView,
    MyResumesListAPIView,
    ResumeDetailAPIView,
    DeleteResumeAPIView,
    UpdateResumeAPIView
)

urlpatterns = [
    path("resumes/upload/", UploadResumeAPIView.as_view(), name="api_resume_upload"),
    path("resumes/my/", MyResumesListAPIView.as_view(), name="api_my_resumes"),
    path("resumes/<int:pk>/", ResumeDetailAPIView.as_view(), name="api_resume_detail"),
    path("resumes/<int:pk>/update/", UpdateResumeAPIView.as_view(), name="api_resume_update"),
    path("resumes/<int:pk>/delete/", DeleteResumeAPIView.as_view(), name="api_resume_delete"),
]