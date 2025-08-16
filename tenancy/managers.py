from django.db.models import Manager
from tenancy.utils import get_current_tenant_id
class EnforcedTenantManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        tid = get_current_tenant_id()
        return qs.filter(tenant_id=tid) if tid else qs.none()
