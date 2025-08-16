# tenancy/utils.py
from __future__ import annotations

from typing import Optional
from django.conf import settings

from clients.models import Client, Domain
from .middleware import get_current_db_alias


def _resolve_current_tenant(host: Optional[str] = None) -> Optional[Client]:
    """
    Aktif DB alias'ına göre mevcut tenant'ı döner.
    - host verilirse önce Domain.domain == host arar.
    - yoksa ilgili alias'taki ilk Domain->tenant, o da yoksa ilk Client döner.
    """
    alias = get_current_db_alias()

    # 1) host'a doğrudan bağlı Domain -> tenant
    if host:
        dom = (
            Domain.objects.using(alias)
            .select_related("tenant")
            .filter(domain__iexact=host)
            .first()
        )
        if dom and dom.tenant_id:
            return dom.tenant

    # 2) alias'ta bir Domain varsa onun tenant'ı
    dom = (
        Domain.objects.using(alias)
        .select_related("tenant")
        .order_by("id")
        .first()
    )
    if dom and dom.tenant_id:
        return dom.tenant

    # 3) alias'taki ilk Client fallback
    return Client.objects.using(alias).order_by("id").first()


def get_current_tenant(host: Optional[str] = None) -> Optional[Client]:
    """
    Dışarıya açık fonksiyon: mevcut tenant (Client) objesini döner.
    """
    return _resolve_current_tenant(host=host)


def get_current_tenant_id(host: Optional[str] = None) -> Optional[int]:
    """
    Mevcut tenant ID'si; yoksa None.
    """
    t = _resolve_current_tenant(host=host)
    return t.id if t else None
