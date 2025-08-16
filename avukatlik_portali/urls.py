# avukatlik_portali/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from directory.views import MyDirectoryUsersView
from django.views.generic import RedirectView


schema_view = get_schema_view(
    openapi.Info(
        title="Avukatlık Portalı API",
        default_version="v1",
        description="Çoklu kiracı API",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", RedirectView.as_view(url="/api/docs/", permanent=False), name="api-root"),
    path("api/", include("tenancy.urls")),
    path("api/my-users/", MyDirectoryUsersView.as_view(), name="my-users"),
    path("api/auth/", include("accounts.api_urls")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/tenant-info/", TokenRefreshView.as_view(), name="tenant_info"),


    # Tenant endpoints

    # Docs
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    

] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)