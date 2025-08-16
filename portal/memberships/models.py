from django.conf import settings
from django.db import models
from clients.models import Client as Tenant

class TenantMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("user", "User"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_memberships")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "tenant")
        verbose_name = "Tenant Membership"
        verbose_name_plural = "Tenant Memberships"

    def __str__(self):
        return f"{self.user} @ {self.tenant} ({self.role})"
