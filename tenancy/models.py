
from django.db import models
from django.conf import settings
from tenancy.utils import get_current_tenant

class UserTenantMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_memberships")
    tenant = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="user_memberships")
    is_primary = models.BooleanField(default=True)
    class Meta:
        unique_together = (("user","tenant"),)
        verbose_name = "Kullanıcı-Tenant Üyeliği"
        verbose_name_plural = "Kullanıcı-Tenant Üyelikleri"
    def __str__(self): return f"{self.user} @ {self.tenant}"

class TenantQuerySet(models.QuerySet):
    def for_current(self):
        t = get_current_tenant()
        return self.filter(tenant=t) if t else self.none()

class TenantManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        t = get_current_tenant()
        return qs.filter(tenant=t) if t else qs.none()

class TenantScopedModel(models.Model):
    tenant = models.ForeignKey("clients.Client", on_delete=models.CASCADE, editable=False, db_index=True)
    objects = TenantManager()
    all_objects = models.Manager()
    class Meta: abstract = True
    def save(self, *a, **k):
        if not self.tenant_id:
            t = get_current_tenant()
            if t is None:
                raise RuntimeError("Aktif tenant yok (CurrentTenantMiddleware?).")
            self.tenant = t
        return super().save(*a, **k)
