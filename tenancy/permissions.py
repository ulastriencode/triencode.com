from rest_framework import permissions
from tenancy.threadlocal import get_current_tenant_id
from rest_framework.permissions import BasePermission, SAFE_METHODS
from portal.memberships.models import TenantMembership

class IsSameTenant(permissions.BasePermission):
    def has_permission(self, request, view):
        current_tid = get_current_tenant_id()
        # SimpleJWT doğrulanmış token DRF’de request.auth içinde claims olarak erişilebilir
        token_tid = None
        if request.auth and isinstance(request.auth, dict):
            token_tid = request.auth.get("tenant_id")
        else:
            # bazı versiyonlarda request.auth bir Token objesi olur
            try:
                token_tid = request.auth.get("tenant_id")
            except Exception:
                token_tid = None
        return current_tid and token_tid and int(current_tid) == int(token_tid)
    
class IsTenantWriterOrReadOnly(BasePermission):
    """
    GET/HEAD/OPTIONS serbest.
    Yazma (POST/PUT/PATCH/DELETE) sadece role in ('owner','admin')
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        # Yazma isteği -> kullanıcı login mi ve aynı tenant mı?
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        current_tid = get_current_tenant_id()
        if not current_tid:
            return False

        # Üyelik bul ve rolü kontrol et
        try:
            memb = TenantMembership.objects.get(user=user, tenant_id=current_tid, is_active=True)
        except TenantMembership.DoesNotExist:
            return False

        return memb.role in ("owner", "admin")