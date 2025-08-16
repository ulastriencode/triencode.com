# tenancy/middleware.py
import threading
from django.conf import settings

_local = threading.local()

def set_current_db_alias(alias: str):
    _local.DB_ALIAS = alias

def get_current_db_alias() -> str:
    return getattr(_local, "DB_ALIAS", getattr(settings, "DEFAULT_DB_ALIAS", "default"))

class CurrentTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1) Host'u çöz (portu at)
        host = request.get_host().split(":")[0].lower()

        # 2) Host -> DB alias
        alias = settings.HOST_DB_MAP.get(host, settings.DEFAULT_DB_ALIAS)
        set_current_db_alias(alias)

        # 3) İsteğe tenant'ı iliştir
        request.tenant = None
        try:
            from clients.models import Domain, Client

            # Önce host'a birebir uyan Domain'ı dene
            domain_obj = (
                Domain.objects.using(alias)
                .select_related("tenant")
                .filter(domain__iexact=host)
                .first()
            )
            if domain_obj and domain_obj.tenant_id:
                request.tenant = domain_obj.tenant
            else:
                # Yoksa o alias'taki ilk Client'ı ver (tek kiracı senaryosu için güvenli fallback)
                request.tenant = Client.objects.using(alias).order_by("id").first()
        except Exception:
            # Sessizce geç; tenant None kalır
            pass

        return self.get_response(request)