
from django.apps import AppConfig
class TenancyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenancy"
    verbose_name = "Tenancy (Row-level)"
