# clients/models.py
from django.db import models
from datetime import date, timedelta
from django.utils import timezone

def one_year_later():
    return date.today() + timedelta(days=365)

DEFAULT_PRIMARY = "#0ea5e9"
DEFAULT_SECONDARY = "#1e293b"

class Client(models.Model):
    

    db_alias = models.CharField("DB Alias", max_length=50, null=True, blank=True, db_index=True ,default="default",
                                help_text="Bu tenant'ın verilerinin bulunduğu Django DATABASES alias'ı")
    name = models.CharField("Ad", max_length=100, unique=True)
    schema_name = models.CharField("Şema Adı", max_length=63, unique=True)
    paid_until = models.DateField("Ücretli Bitiş", default=one_year_later)
    on_trial = models.BooleanField("Deneme Sürecinde", default=True)
    logo = models.ImageField("Logo", upload_to="logos/", blank=True, null=True)
    primary_color = models.CharField("Birincil Renk", max_length=7, default=DEFAULT_PRIMARY)
    secondary_color = models.CharField("İkincil Renk", max_length=7, default=DEFAULT_SECONDARY)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Müşteri (Tenant)"
        verbose_name_plural = "Müşteriler (Tenantlar)"
    def __str__(self): return self.name

class Domain(models.Model):
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="domains")
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domainler"
    def __str__(self): return self.domain
