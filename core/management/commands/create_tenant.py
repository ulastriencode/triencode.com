# tenancy/management/commands/create_tenant.py
import os
import re
import getpass
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connections
from django.utils.module_loading import import_string

try:
    import psycopg
except Exception:
    psycopg = None  # CREATE DATABASE adımı yoksa psql ile de oluşturabilirsin


class Command(BaseCommand):
    help = "Yeni bir firma/tenant kur: Postgres DB oluştur, migrate et, Client & Domain ekle, admin oluştur, HOST_DB_MAP'e ekle."

    def add_arguments(self, parser):
        parser.add_argument("--alias", required=True, help="DB alias (örn. ulasdemirav)")
        parser.add_argument("--domain", required=True, help="Host (örn. ulasdemirav.localhost)")
        parser.add_argument("--name", required=True, help="Firma adı (örn. Ulas Demir AV)")

        parser.add_argument("--db-name", help="PostgreSQL veritabanı adı (vars: avp_<alias>)")
        parser.add_argument("--db-user", default=os.getenv("POSTGRES_USER", "postgres"))
        parser.add_argument("--db-password", default=os.getenv("POSTGRES_PASSWORD", "1"))
        parser.add_argument("--db-host", default=os.getenv("POSTGRES_HOST", "127.0.0.1"))
        parser.add_argument("--db-port", default=os.getenv("POSTGRES_PORT", "5432"))

        parser.add_argument("--admin-username", default="admin")
        parser.add_argument("--admin-email", default="admin@example.com")
        parser.add_argument("--admin-password", default=None)

        parser.add_argument("--no-admin", action="store_true", help="Superuser oluşturma")

    def handle(self, *args, **opts):
        # 0) Parametreler
        alias = opts["alias"].strip()
        domain = opts["domain"].strip().lower()
        name = opts["name"].strip()

        if not re.match(r"^[a-z0-9_]+$", alias):
            raise CommandError("alias yalnızca [a-z0-9_] karakterleri içermeli (örn. ulasdemirav).")

        db_name = (opts["db-name"] or f"avp_{alias}").strip()
        db_user = opts["db-user"]
        db_password = opts["db-password"]
        db_host = opts["db-host"]
        db_port = opts["db-port"]

        create_admin = not opts["no-admin"]
        admin_username = opts["admin-username"]
        admin_email = opts["admin-email"]
        admin_password = opts["admin-password"]

        if create_admin and not admin_password:
            self.stdout.write(self.style.WARNING("Admin şifresi (ekranda görünmez):"))
            admin_password = getpass.getpass("Password: ").strip()
            if not admin_password:
                raise CommandError("Admin şifresi boş olamaz.")

        # 1) DB oluştur (psycopg varsa)
        self.stdout.write(self.style.MIGRATE(f"[1/6] CREATE DATABASE {db_name}"))
        if psycopg:
            try:
                conninfo = f"host={db_host} port={db_port} dbname=postgres user={db_user} password={db_password}"
                with psycopg.connect(conninfo, autocommit=True) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
                        exists = cur.fetchone()
                        if not exists:
                            cur.execute(f'CREATE DATABASE "{db_name}";')
                            self.stdout.write(self.style.SUCCESS(f"  -> DB oluşturuldu: {db_name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"  -> DB zaten var: {db_name}"))
            except Exception as e:
                raise CommandError(f"CREATE DATABASE başarısız: {e}")
        else:
            self.stdout.write(self.style.WARNING("  -> psycopg yok, DB'yi önceden psql ile oluşturmuş olmalısın."))

        # 2) settings.DATABASES'e runtime alias ekle
        self.stdout.write(self.style.MIGRATE(f"[2/6] settings.DATABASES['{alias}'] ekleniyor"))
        if alias not in settings.DATABASES:
            settings.DATABASES[alias] = {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": db_name,
                "USER": db_user,
                "PASSWORD": db_password,
                "HOST": db_host,
                "PORT": db_port,
            }
            connections.databases = settings.DATABASES
        else:
            self.stdout.write(self.style.WARNING("  -> Alias zaten tanımlı"))

        # 3) migrate --database=<alias>
        self.stdout.write(self.style.MIGRATE(f"[3/6] migrate --database={alias}"))
        call_command("migrate", database=alias, interactive=False, verbosity=1)

        # 4) Client & Domain
        self.stdout.write(self.style.MIGRATE(f"[4/6] Client & Domain oluşturuluyor"))
        Client = import_string("clients.models.Client")
        Domain = import_string("clients.models.Domain")

        client_kwargs = {"name": name}
        if hasattr(Client, "db_alias"):
            client_kwargs["db_alias"] = alias

        client = Client.objects.using(alias).create(**client_kwargs)
        Domain.objects.using(alias).create(
            tenant=client,
            domain=domain,
            **({"is_primary": True} if "is_primary" in [f.name for f in Domain._meta.fields] else {}),
        )
        self.stdout.write(self.style.SUCCESS(f"  -> Client={client.id}, Domain={domain}"))

        # 5) Superuser
        if create_admin:
            self.stdout.write(self.style.MIGRATE(f"[5/6] Superuser oluşturuluyor"))
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.using(alias).create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
            )
            self.stdout.write(self.style.SUCCESS(f"  -> Admin: {admin_username} / {admin_email}"))

        # 6) HOST_DB_MAP patch (rowlevel.py'ı güncelle)
        self.stdout.write(self.style.MIGRATE(f"[6/6] HOST_DB_MAP güncelleniyor"))
        try:
            module = os.environ.get("DJANGO_SETTINGS_MODULE", "avukatlik_portali.settings.rowlevel")
            rowlevel = __import__(module, fromlist=["__file__"])
            rowlevel_path = Path(rowlevel.__file__)
            text = rowlevel_path.read_text(encoding="utf-8")

            if "HOST_DB_MAP" not in text:
                addition = (
                    "\n\nHOST_DB_MAP = {\n"
                    f"    '{domain}': '{alias}',\n"
                    "}\n"
                    "DEFAULT_DB_ALIAS = 'default'\n"
                )
                rowlevel_path.write_text(text + addition, encoding="utf-8")
                self.stdout.write(self.style.SUCCESS("  -> HOST_DB_MAP oluşturuldu"))
            else:
                import regex as rx
                m = rx.search(r"HOST_DB_MAP\s*=\s*\{(?P<body>.*?)\}", text, flags=rx.DOTALL)
                if m and f"'{domain}': '{alias}'" not in m.group("body"):
                    insert_at = m.end("body")
                    new_text = text[:insert_at] + f"\n    '{domain}': '{alias}'," + text[insert_at:]
                    rowlevel_path.write_text(new_text, encoding="utf-8")
                    self.stdout.write(self.style.SUCCESS(f"  -> HOST_DB_MAP eklendi: {domain} -> {alias}"))
                else:
                    self.stdout.write(self.style.WARNING("  -> HOST_DB_MAP zaten içeriyor veya bulunamadı"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"HOST_DB_MAP güncellemesi atlandı: {e}"))

        self.stdout.write(self.style.SUCCESS("\nTAMAMLANDI ✅"))
