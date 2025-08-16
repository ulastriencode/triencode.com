# tenancy/db_router.py
from .middleware import get_current_db_alias

class HostDatabaseRouter:
    def db_for_read(self, model, **hints):
        return get_current_db_alias()

    def db_for_write(self, model, **hints):
        return get_current_db_alias()

    def allow_relation(self, obj1, obj2, **hints):
        return True

    # Tüm DB’lerde migrate’e izin veriyoruz; zaten sen üçüne de koştun.
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
