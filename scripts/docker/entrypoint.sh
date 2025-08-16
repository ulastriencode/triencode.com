#!/usr/bin/env bash
set -e

# DB hazır mı?
echo "Waiting for Postgres ${DB_HOST}:${DB_PORT} ..."
python - <<'PY'
import os, time, psycopg2
host=os.getenv("DB_HOST","db"); port=int(os.getenv("DB_PORT","5432"))
user=os.getenv("DB_USER","postgres"); pwd=os.getenv("DB_PASSWORD",""); name=os.getenv("DB_NAME","postgres")
for i in range(60):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=name).close()
        break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB not ready")
PY

# Public migrasyonları
python manage.py migrate_schemas --shared

# Public tenant/domain garanti
python manage.py shell -c "
from clients.models import Client, Domain
c,_=Client.objects.get_or_create(schema_name='public', defaults={'name':'Public','paid_until':'2099-01-01','on_trial':True})
Domain.objects.get_or_create(domain='public.localhost', defaults={'tenant':c})
print('Public OK')
"

# (Opsiyonel) ENV ile default tenant’lar (virgülle ayır)
# Ör: DEFAULT_TENANTS=sonerdicanav:sonerdicanav.localhost,emirkevserav:emirkevserav.localhost
if [ -n "${DEFAULT_TENANTS}" ]; then
python manage.py shell - <<PY
from datetime import timedelta
from django.utils import timezone
from clients.models import Client, Domain
raw="${DEFAULT_TENANTS}"
for item in [x.strip() for x in raw.split(",") if x.strip()]:
    sch, dom = item.split(":")
    c,created=Client.objects.get_or_create(schema_name=sch,
        defaults={'name':sch,'paid_until':timezone.now().date()+timedelta(days=365),'on_trial':True})
    if created:
        c.create_schema(check_if_exists=True)
    Domain.objects.update_or_create(domain=dom, defaults={'tenant':c})
    print("Tenant OK:", sch, "->", dom)
PY
fi

# Tenant app migrasyonları
python manage.py migrate_schemas --tenant

# Geliştirme sunucusu
python manage.py runserver 0.0.0.0:8000
