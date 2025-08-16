# tenancy/threadlocal.py
from .middleware import get_current_db_alias
from .utils import get_current_tenant_id  # permissions.py bu fonksiyonu buradan import ediyor

__all__ = ["get_current_db_alias", "get_current_tenant_id"]
