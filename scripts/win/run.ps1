param([string]$HostEntry = "127.0.0.1  sonerdicanav.localhost")

$hosts = "C:\Windows\System32\drivers\etc\hosts"
if (-not (Select-String -Path $hosts -Pattern "sonerdicanav\.localhost" -Quiet)) {
  Add-Content -Path $hosts -Value $HostEntry
}

# Bekleyen (app) migrasyonları varsa (tenantlar için)
python manage.py migrate_schemas --tenant

python manage.py runserver
