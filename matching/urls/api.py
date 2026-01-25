# matching/urls/api.py
from django.urls import path
from matching.views.api import MatchResumeJobsAPIView,MatchJobsResumeAPIView

urlpatterns = [
    path(
        "match/resume/<int:resume_id>/",
        MatchResumeJobsAPIView.as_view(),
        name="match-resume-jobs"
    ),
     path(
        "match/job/<int:job_id>/resumes/",
        MatchJobsResumeAPIView.as_view(),
        name="match-job-resumes"
    ),
]

