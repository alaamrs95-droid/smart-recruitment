# matching/urls/web.py
from django.urls import path
from matching.views.web import (
    match_resume_jobs_view,
    match_job_resumes_view,
    my_matches_view,
    job_matches_view,
    match_detail_view,
)
from matching.views.debug import debug_matches
from matching.views.analytics import analytics_dashboard, top_candidates_for_job


app_name = "matching"

urlpatterns = [
    path("my-matches/", my_matches_view, name="my_matches"),
    path("resume/<int:resume_id>/jobs/", match_resume_jobs_view, name="resume_jobs"),
    path("job/<int:job_id>/candidates/", match_job_resumes_view, name="job_candidates"),
    path("job/<int:pk>/matches/", job_matches_view, name="job_matches"),
    path("detail/<int:resume_id>/<int:job_id>/", match_detail_view, name="match_detail"),
    path("debug/", debug_matches, name="debug"),
    path('analytics/', analytics_dashboard, name='analytics'),
    path('job/<int:job_id>/candidates/', top_candidates_for_job, name='top_candidates'),

]