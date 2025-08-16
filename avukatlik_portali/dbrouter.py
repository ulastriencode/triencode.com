from utils.current_db import get_current_db

class RowLevelRouter:
    def db_for_read(self, model, **hints): return get_current_db()
    def db_for_write(self, model, **hints): return get_current_db()
    def allow_migrate(self, db, app_label, model_name=None, **hints): return True
