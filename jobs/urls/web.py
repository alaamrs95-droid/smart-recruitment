# jobs/urls/web.py
from django.urls import path
from jobs.views.analytics import job_analytics
from jobs.views.web import (
    job_list_view,
    job_detail_view,
    create_job_view,
    update_job_view,
    delete_job_view,
    my_jobs_view
)

app_name = "jobs"

urlpatterns = [
    path("", job_list_view, name="list"),
    path("<int:pk>/", job_detail_view, name="detail"),
    path("create/", create_job_view, name="create"),
    path("<int:pk>/update/", update_job_view, name="update"),
    path("<int:pk>/delete/", delete_job_view, name="delete"),
    path("my-jobs/", my_jobs_view, name="my_jobs"),
    path('analytics/', job_analytics, name='analytics'),

]