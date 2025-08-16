#!/usr/bin/env bash
set -e

# DB hazır olana kadar bekle
python - <<'PY'
import os, time, psycopg
host=os.getenv("DB_HOST","db"); port=int(os.getenv("DB_PORT","5432"))
user=os.getenv("DB_USER","postgres"); pwd=os.getenv("DB_PASSWORD","postgres")
name=os.getenv("DB_NAME","postgres")
while True:
    try:
        psycopg.connect(host=host, port=port, user=user, password=pwd, dbname=name).close()
        break
    except Exception as e:
        print("DB bekleniyor...", e)
        time.sleep(1)
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn avukatlik_portali.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 60
