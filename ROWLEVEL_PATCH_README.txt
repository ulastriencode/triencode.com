
Bu paket SADECE ekle/degistir dosyaları içerir.
Uygulama adımları:

1) ZIP'i proje köküne (manage.py ile aynı dizine) açın. Ağaç şöyle olmalı:
   avukatlik_portali/
     manage.py
     accounts/
     clients/
     tenancy/             <-- yeni
     avukatlik_portali/
       settings/
         rowlevel.py      <-- yeni

2) Ortam değişkeni ve migrasyonlar:
   PowerShell:
     $env:DJANGO_SETTINGS_MODULE="avukatlik_portali.settings.rowlevel"
     python manage.py makemigrations clients tenancy
     python manage.py migrate

3) İlk tenant/domain ve kullanıcı-üyelik:
   python manage.py shell
   from clients.models import Client, Domain
   from django.contrib.auth import get_user_model
   from tenancy.models import UserTenantMembership
   c = Client.objects.create(name="Default", schema_name="default")
   Domain.objects.create(tenant=c, domain="admin.localhost", is_primary=True)
   User = get_user_model()
   u = User.objects.create_user(username="admin", password="admin123")
   UserTenantMembership.objects.create(user=u, tenant=c, is_primary=True)

4) Çalıştır:
   python manage.py runserver
