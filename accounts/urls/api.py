# accounts/urls/api.py
from django.urls import path
from accounts.views.api import (
    CandidateOnlyView, RegisterAPIView, LoginAPIView, MeAPIView, EmployerOnlyView
)

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="api_register"),
    path("auth/login/", LoginAPIView.as_view(), name="api_login"),
    path("auth/me/", MeAPIView.as_view(), name="api_me"),
    path("employer-only/", EmployerOnlyView.as_view(), name="employer_only"),
    path("candidate-only/", CandidateOnlyView.as_view(), name="candidate_only"),

]