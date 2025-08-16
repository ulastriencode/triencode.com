# portal/middleware/tenant.py
from django.conf import settings
from clients.models import Client as Tenant
from tenancy.threadlocal import set_current_tenant_id

class TenantMiddleware:
    ADMIN_PREFIXES = ("/admin/", "/static/", "/media/", "/__debug__/")

    def __init__(self, get_response):
        self.get_response = get_response

    def _is_bypass_path(self, path: str) -> bool:
        return bool(path and path.startswith(self.ADMIN_PREFIXES))

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get("HTTP_HOST") or request.get_host() or ""
        # PORTU AT, sadece hostname ile eşle
        hostname = host.split(":")[0].lower()

        # DEBUG: ne geliyor görelim
        print(f"[TENANT MW] HTTP_HOST={host} -> hostname={hostname}")

        try:
            request.tenant = Tenant.objects.get(domain=hostname)
        except Tenant.DoesNotExist:
            request.tenant = None

        return self.get_response(request)

        # 0) admin/static/media/debug => tenant yok
        if self._is_bypass_path(path):
            set_current_tenant_id(None)
            request.tenant = None
            request._current_tenant = None
            return self.get_response(request)

        # 1) host
        host_header = request.META.get("HTTP_X_FORWARDED_HOST") or request.get_host()
        host = (host_header or "").split(":")[0]

        t = None

        # 2) birebir domain
        if host:
            t = Tenant.objects.filter(domain=host).only("id", "domain", "name").first()

        # 3) dev'de otomatik oluştur (sub.localhost)
        if not t and settings.DEBUG and host.endswith(".localhost"):
            sub = host.split(".localhost")[0]
            if sub:
                t = Tenant.objects.filter(domain=host).only("id", "domain", "name").first()
                if not t:
                    t = Tenant.objects.create(name=sub.capitalize(), domain=host)

        # 4) fallback (opsiyonel)
        if not t:
            fallback = getattr(settings, "DEFAULT_TENANT_DOMAIN", None)
            if fallback:
                t = Tenant.objects.filter(domain=fallback).only("id", "domain", "name").first()

        # 5) thread-local + request
        set_current_tenant_id(t.id if t else None)
        request.tenant = t
        request._current_tenant = t

        return self.get_response(request)
