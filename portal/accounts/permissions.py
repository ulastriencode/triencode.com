# portal/tenancy/permissions.py
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from portal.memberships.models import TenantMembership

def must_be_tenant_member(view):
    def _wrapped(request, *args, **kwargs):
        if getattr(request, "is_global_admin", False):
            return view(request, *args, **kwargs)
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            raise PermissionDenied("Tenant bulunamadı.")
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        is_member = TenantMembership.objects.filter(user=request.user, tenant=tenant, is_active=True).exists()
        if not is_member:
            raise PermissionDenied("Bu tenant'a erişiminiz yok.")
        return view(request, *args, **kwargs)
    return _wrapped
