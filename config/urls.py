from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.views.generic import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', set_language, name='set_language'),
    
    # API 
    path("api/accounts/", include("accounts.urls.api")),
    path("api/jobs/", include("jobs.urls.api")),
    path("api/resumes/", include("resumes.urls.api")),
    path("api/matching/", include("matching.urls.api")),
]


urlpatterns += i18n_patterns(
    path("", TemplateView.as_view(template_name="site/home.html"), name="home"),
    
    path("accounts/", include("accounts.urls.web")),
    path("jobs/", include("jobs.urls.web")),
    path("resumes/", include("resumes.urls.web")),
    path("resumes-builder/", include("resumes.urls_builder")),  # تم الإضافة: رابط مباشر لنظام بناء السير الذاتية
    path("matching/", include("matching.urls.web")),
    
    prefix_default_language=True, 
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # في الـ development نخدم الـ static من STATICFILES_DIRS (مجلد static الرئيسي)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])