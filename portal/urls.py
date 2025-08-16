# portal/urls.py
from django.contrib import admin
from django.urls import path, include
from portal.accounts.views import CustomTokenObtainPairView
from django.views.generic import RedirectView
from tenancy.views import tenant_info
urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),  # kök -> admin
    path("admin/", admin.site.urls),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  # BİZİM VIEW
    path("api/cases/", include("portal.cases.urls")),  # <-- düzeltme
    path("api/tenant/", include("tenancy.urls")),
    path("tenant-info/", tenant_info, name="tenant-info")
]

# DİKKAT:
# - Burada veya başka yerde handler404/500 tanımlamayın.
# - include("portal.urls") gibi kendi kökünüzü include etmeyin.
