from rest_framework.permissions import BasePermission, SAFE_METHODS

class InSameTenantCanList(BasePermission):
    """
    Aynı tenanta ait kullanıcı ise:
      - SAFE_METHODS (GET/HEAD/OPTIONS) → izin ver
    """
    def has_permission(self, request, view):
        user = request.user
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated or not tenant:
            return False
        return getattr(user, "tenant_id", None) == getattr(tenant, "id", None)

class InSameTenantOwnerAdminCanWrite(BasePermission):
    """
    Aynı tenant + rol owner/admin ise yazma izni.
    Eğer memberships kullanmıyorsan basitçe is_staff / is_superuser ile kısıtlayabilirsin.
    """
    def has_permission(self, request, view):
        user = request.user
        tenant = getattr(request, "tenant", None)
        if not user or not user.is_authenticated or not tenant:
            return False
        if getattr(user, "tenant_id", None) != getattr(tenant, "id", None):
            return False

        if request.method in SAFE_METHODS:
            return True

        # ---- ROL KONTROLÜ ----
        # Eğer TenantMembership modelini aktif kullanıyorsan burada kontrol et.
        # Şimdilik basit: is_staff veya is_superuser yazmaya yetkili olsun.
        return bool(user.is_staff or user.is_superuser)
