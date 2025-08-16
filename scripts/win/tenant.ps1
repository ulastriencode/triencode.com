param(
  [Parameter(Mandatory=$true)][string]$Schema,
  [Parameter(Mandatory=$true)][string]$Domain
)

$ErrorActionPreference = "Stop"

python manage.py shell -c @"
from datetime import timedelta
from django.utils import timezone
from clients.models import Client, Domain

c, created = Client.objects.get_or_create(
    schema_name='$Schema',
    defaults={'name': '$Schema', 'paid_until': timezone.now().date()+timedelta(days=365), 'on_trial': True}
)

# Şemayı oluştur (varsa dokunmaz)
if not created:
    print('Tenant vardı; şema mevcut olabilir.')
c.create_schema(check_if_exists=True)

# Domain ekle/düzelt
Domain.objects.update_or_create(domain='$Domain', defaults={'tenant': c})
print('OK tenant:', c.schema_name)
"@
