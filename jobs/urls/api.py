# jobs/urls/api.py
from django.urls import path 
from jobs.views.api import (
    JobListAPIView,
    JobDetailAPIView,
    CreateJobAPIView,
    UpdateJobAPIView,
    DeleteJobAPIView,
    EmployerJobsAPIView
)

urlpatterns = [
    path("jobs/", JobListAPIView.as_view(), name="api_job_list"),
    path("jobs/<int:pk>/", JobDetailAPIView.as_view(), name="api_job_detail"),
    path("jobs/create/", CreateJobAPIView.as_view(), name="api_job_create"),
    path("jobs/<int:pk>/update/", UpdateJobAPIView.as_view(), name="api_job_update"),
    path("jobs/<int:pk>/delete/", DeleteJobAPIView.as_view(), name="api_job_delete"),
    path("employer/jobs/", EmployerJobsAPIView.as_view(), name="api_employer_jobs"),
]