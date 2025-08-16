from rest_framework.permissions import BasePermission

def _current_tenant_id_from_request(request):
    if request and hasattr(request, "_current_tenant") and request._current_tenant:
        return request._current_tenant.id
    try:
        from tenancy.threadlocal import get_current_tenant_id
        return get_current_tenant_id()
    except Exception:
        return None

class TokenTenantMatchesHost(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True  # auth başka yerde engeller
        token = getattr(request, 'auth', None)
        if not token:
            return True
        token_tid = token.get('tid', None)
        current_tid = _current_tenant_id_from_request(request)
        if token_tid and current_tid and int(token_tid) != int(current_tid):
            return False
        return True
