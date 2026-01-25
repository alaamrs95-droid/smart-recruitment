# accounts/urls/web.py
from django.urls import path
from accounts.views.web import dashboard, register_view, login_view, logout_view
urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"), 
]