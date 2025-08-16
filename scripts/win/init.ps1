param(
  [string]$DbName = "avukatlik_portali_dev",
  [string]$PgUser = "postgres",
  [string]$PgPass = "1",
  [string]$PgHost = "localhost",
  [int]   $PgPort = 5432
)

$ErrorActionPreference = "Stop"

# 1) DB var mı? yoksa oluştur
psql -U $PgUser -h $PgHost -p $PgPort -tc "SELECT 1 FROM pg_database WHERE datname='$DbName';" | Out-String | Select-String -Pattern 1 | Out-Null
if (!$?) {
  psql -U $PgUser -h $PgHost -p $PgPort -c "CREATE DATABASE $DbName;"
}

# 2) public (shared) migrasyonları
python manage.py migrate_schemas --shared

# 3) public domain güvence
python manage.py shell -c "
from clients.models import Client, Domain
c, _ = Client.objects.get_or_create(schema_name='sonerdicanav', defaults={'name':'sonerdicanav','paid_until':'2099-01-01','on_trial':True})
Domain.objects.get_or_create(domain='sonerdicanav.localhost', defaults={'tenant': c})
print('public ok')
"
