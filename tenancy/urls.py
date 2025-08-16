from django.urls import path
from .api import TenantInfoView

urlpatterns = [
    path("tenant-info/", TenantInfoView.as_view(), name="tenant-info"),
]
