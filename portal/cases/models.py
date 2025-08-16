from django.db import models
from django.conf import settings
from django.utils import timezone

class Case(models.Model):
    STATUS_CHOICES = (("open", "open"), ("closed", "closed"))

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    tenant = models.ForeignKey("tenancy.Tenant", on_delete=models.CASCADE, related_name="cases")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_cases"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CaseStatusLog(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20, choices=Case.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Case.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case_id}: {self.old_status} -> {self.new_status} @ {self.changed_at:%Y-%m-%d %H:%M}"
