# create_tenant.py
import os
import re
from pathlib import Path
import argparse
import sys

# Konsol/kaynaklarda unicode sorunlarını engelle
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import psycopg  # psycopg3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "avukatlik_portali.settings.rowlevel")
import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.contrib.auth import get_user_model


# ---------- DB helpers ----------

def ensure_db_exists(db_name, user, password, host, port):
    """
    Hedef DB yoksa UTF8 + template0 ile oluşturur.
    CREATE DATABASE işlemi autocommit=True ayrı bir bağlantıda yapılır.
    """
    # 1) Varlık kontrolü
    with psycopg.connect(dbname="postgres", user=user, password=password, host=host, port=port) as chk:
        exists = chk.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,)
        ).fetchone() is not None

    if exists:
        print(f"[i] Database already exists: {db_name} (skipping CREATE)")
        return

    # 2) Oluşturma: autocommit=True
    try:
        with psycopg.connect(
            dbname="postgres", user=user, password=password, host=host, port=port, autocommit=True
        ) as conn:
            conn.execute(f"""
                CREATE DATABASE "{db_name}"
                WITH TEMPLATE template0
                ENCODING 'UTF8'
                LC_COLLATE='C'
                LC_CTYPE='C';
            """)
            print(f"[+] Database created (UTF8, C-collate): {db_name}")
    except Exception as e1:
        # Alternatif: ICU (PG15+ ve ICU varsa). Windows'ta her zaman mevcut olmayabilir.
        try:
            with psycopg.connect(
                dbname="postgres", user=user, password=password, host=host, port=port, autocommit=True
            ) as conn:
                conn.execute(f"""
                    CREATE DATABASE "{db_name}"
                    LOCALE_PROVIDER = icu
                    ICU_LOCALE = 'tr-TR'
                    ENCODING 'UTF8'
                    TEMPLATE template0;
                """)
                print(f"[+] Database created (UTF8, ICU tr-TR): {db_name}")
        except Exception as e2:
            raise RuntimeError(f"DB create failed for {db_name}: {e2}") from e2


def add_alias_runtime(alias, db_name, user, password, host, port):
    if alias not in settings.DATABASES:
        base = settings.DATABASES.get("default", {}).copy()
        base.setdefault("ENGINE", "django.db.backends.postgresql")
        base.setdefault("AUTOCOMMIT", True)
        base.setdefault("CONN_MAX_AGE", 0)
        base.setdefault("CONN_HEALTH_CHECKS", False)
        base.setdefault("OPTIONS", {})
        base.setdefault("TIME_ZONE", None)

        base.update({
            "NAME": db_name,
            "USER": user,
            "PASSWORD": password,
            "HOST": host,
            "PORT": str(port),
        })
        settings.DATABASES[alias] = base
        print(f"[+] Added DATABASES['{alias}'] at runtime")
    else:
        print(f"[i] DATABASES['{alias}'] already defined")
    _ = connections[alias]  # lazy init


def patch_settings_databases(alias, db_name, user, password, host, port):
    """
    Settings dosyasına kalıcı bir satır ekler:
    DATABASES['alias'] = {...}
    """
    mod = __import__(os.environ["DJANGO_SETTINGS_MODULE"], fromlist=["*"])
    p = Path(mod.__file__)
    src = p.read_text(encoding="utf-8")

    # Zaten var mı?
    if re.search(rf"DATABASES\[['\"]{re.escape(alias)}['\"]\]", src):
        print(f"[i] Settings already has DATABASES['{alias}'] (skipping patch)")
        return

    block = f"""
# ---- auto-added by create_tenant.py ----
DATABASES['{alias}'] = {{
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': '{db_name}',
    'USER': '{user}',
    'PASSWORD': '{password}',
    'HOST': '{host}',
    'PORT': '{port}',
}}
"""
    p.write_text(src + "\n" + block, encoding="utf-8")
    print(f"[+] Patched settings: added DATABASES['{alias}']")


# ---------- App-level helpers ----------

def create_or_get_client_domain(alias, name, domains):
    from clients.models import Client, Domain
    client, _ = Client.objects.using(alias).get_or_create(
        name=name,
        defaults={"db_alias": alias} if hasattr(Client, "db_alias") else {},
    )
    print(f"[✓] Client: {client.id} ({client.name})")
    for i, d in enumerate(domains):
        dom, created = Domain.objects.using(alias).get_or_create(
            tenant=client,
            domain=d,
            defaults={"is_primary": True if i == 0 and hasattr(Domain, "is_primary") else False},
        )
        print(f"[{'+' if created else 'i'}] Domain: {dom.domain}")


def ensure_superuser(alias, username, email, password):
    User = get_user_model()
    mgr = User._default_manager.db_manager(alias)
    u = mgr.filter(username=username).first()
    if u:
        print(f"[i] Superuser already exists: {username}")
        return
    u = User(username=username, email=email, is_active=True, is_staff=True, is_superuser=True)
    u.set_password(password)
    u.save(using=alias)
    print(f"[+] Superuser created: {username}")


def patch_hosts_and_map(domain, alias):
    mod = __import__(os.environ["DJANGO_SETTINGS_MODULE"], fromlist=["*"])
    p = Path(mod.__file__)
    text = p.read_text(encoding="utf-8")

    # ALLOWED_HOSTS patch
    if "ALLOWED_HOSTS" in text:
        pat = r"ALLOWED_HOSTS\s*=\s*\[(?P<body>.*?)\]"
        m = re.search(pat, text, flags=re.S)
        if m and (f"'{domain}'" not in m.group("body") and f'"{domain}"' not in m.group("body")):
            insert_at = m.end("body")
            text = text[:insert_at] + f"\n '{domain}'," + text[insert_at:]
            print(f"[+] Patched ALLOWED_HOSTS with '{domain}'")
        else:
            print("[i] ALLOWED_HOSTS already contains domain")
    else:
        text += f"\nALLOWED_HOSTS = ['127.0.0.1', 'localhost', '{domain}']\n"
        print("[+] Created ALLOWED_HOSTS")

    # HOST_DB_MAP patch
    if "HOST_DB_MAP" not in text:
        text += f"\nHOST_DB_MAP = {{\n    '{domain}': '{alias}',\n}}\n"
        print("[+] Created HOST_DB_MAP")
    else:
        m = re.search(r"HOST_DB_MAP\s*=\s*\{(?P<body>.*?)\}", text, flags=re.S)
        if m and f"'{domain}': '{alias}'" not in m.group("body"):
            insert_at = m.end("body")
            text = text[:insert_at] + f"\n    '{domain}': '{alias}'," + text[insert_at:]
            print(f"[+] Patched HOST_DB_MAP: {domain} -> {alias}")
        else:
            print("[i] HOST_DB_MAP already contains mapping")

    p.write_text(text, encoding="utf-8")


# ---------- Orchestrator ----------

def create_tenant(alias, domain, name, admin_username, admin_email, admin_password, persist_db_alias):
    db_name = f"avp_{alias}"
    db_user = os.getenv("POSTGRES_USER", getattr(settings, "DB_USER", "postgres"))
    db_pass = os.getenv("POSTGRES_PASSWORD", getattr(settings, "DB_PASSWORD", "postgres"))
    db_host = os.getenv("POSTGRES_HOST", getattr(settings, "DB_HOST", "127.0.0.1"))
    db_port = os.getenv("POSTGRES_PORT", getattr(settings, "DB_PORT", "5432"))

    # 1) DB oluştur/yoksa
    ensure_db_exists(db_name, db_user, db_pass, db_host, db_port)

    # 2) DATABASES alias (runtime)
    add_alias_runtime(alias, db_name, db_user, db_pass, db_host, db_port)

    # (opsiyonel) 2b) Kalıcı patch
    if persist_db_alias:
        patch_settings_databases(alias, db_name, db_user, db_pass, db_host, db_port)

    # 3) migrate
    print(f"[->] migrate --database={alias}")
    call_command("migrate", database=alias, interactive=False, verbosity=1)

    # 4) client + domain
    create_or_get_client_domain(alias, name, [domain])

    # 5) superuser
    ensure_superuser(alias, admin_username, admin_email, admin_password)

    # 6) host eşleşmeleri
    patch_hosts_and_map(domain, alias)

    print("\nTAMAMLANDI ✅")


# ---------- CLI ----------

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--alias", required=True, help="Veritabanı alias'ı (örn: firma1)")
    ap.add_argument("--domain", required=True, help="Tenant domain (örn: firma1.localhost)")
    ap.add_argument("--name", required=True, help="Client adı (örn: Firma 1)")
    ap.add_argument("--admin-username", default="admin")
    ap.add_argument("--admin-email", default="admin@local")
    ap.add_argument("--admin-password", default="1")
    ap.add_argument("--persist", action="store_true", help="DATABASES aliasını settings'e kalıcı yaz")
    args = ap.parse_args()

    create_tenant(
        alias=args.alias,
        domain=args.domain,
        name=args.name,
        admin_username=args.admin_username,
        admin_email=args.admin_email,
        admin_password=args.admin_password,
        persist_db_alias=args.persist,
    )
