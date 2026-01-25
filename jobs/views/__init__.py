# jobs/views/__init__.py
from .analytics import job_analytics
from .api import (
    JobListAPIView,
    JobDetailAPIView,
    CreateJobAPIView,
    UpdateJobAPIView,
    DeleteJobAPIView,
    EmployerJobsAPIView
)

from .web import (
    job_list_view,
    job_detail_view,
    create_job_view,
    update_job_view,
    delete_job_view,
    my_jobs_view
)

__all__ = [
    # API Views
    'JobListAPIView',
    'JobDetailAPIView',
    'CreateJobAPIView',
    'UpdateJobAPIView',
    'DeleteJobAPIView',
    'EmployerJobsAPIView',
    
    # Web Views
    'job_list_view',
    'job_detail_view',
    'create_job_view',
    'update_job_view',
    'delete_job_view',
    'my_jobs_view',
]