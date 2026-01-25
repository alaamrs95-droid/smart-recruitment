from django.urls import path, include

urlpatterns = [
    path("api/", include("accounts.urls.api")),
    path("", include("accounts.urls.web")),
]
