from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTenantOwner(BasePermission):
    """
    Objelerin sahibinin (owner) giriş yapmış kullanıcı olmasını
    ve objenin tenant'ının request.tenant ile aynı olmasını zorlar.
    List/Query seviyesinde filtreyi view içinde yapıyoruz; bu sınıf
    özellikle retrieve/update/delete gibi obje seviyesinde devreye girer.
    """
    def has_permission(self, request, view):
        # Genel erişim iznini burada sınırlamıyoruz (List için)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Okuma ve yazma için aynı kontrol
        same_owner = getattr(obj, "owner_id", None) == getattr(request.user, "id", None)
        same_tenant = getattr(obj, "tenant", None) == getattr(request, "tenant", None)
        return bool(same_owner and same_tenant)
