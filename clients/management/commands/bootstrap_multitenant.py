# clients/management/commands/bootstrap_multitenant.py
import os
from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model, get_tenant_domain_model, schema_context
from django.contrib.auth import get_user_model


defaults={
  "paid_until": date.today() + timedelta(days=365),
  "on_trial": False,
  "primary_color": "#1f2937",
  "secondary_color": "#2563eb",
}
class Command(BaseCommand):
    help = "DEFAULT_TENANTS ve DEFAULT_SUPERUSER_* env'lerine göre tenant/domain ve superuser oluşturur."

    def handle(self, *args, **options):
        Tenant = get_tenant_model()
        Domain = get_tenant_domain_model()
        User = get_user_model()

        # Ör: DEFAULT_TENANTS="admin:admin.localhost,soner:soner.localhost"
        raw = os.getenv("DEFAULT_TENANTS", "").strip()
        if not raw:
            self.stdout.write(self.style.WARNING("DEFAULT_TENANTS boş. İşlem yapılmadı."))
            return

        admin_panel_domain = os.getenv("ADMIN_PANEL_DOMAIN", "admin.localhost")
        su_username = os.getenv("DEFAULT_SUPERUSER_USERNAME", "admin")
        su_email = os.getenv("DEFAULT_SUPERUSER_EMAIL", "admin@example.com")
        su_password = os.getenv("DEFAULT_SUPERUSER_PASSWORD", "admin123")

        items = [p.strip() for p in raw.split(",") if p.strip()]
        created_any = False

        for item in items:
            if ":" not in item:
                self.stdout.write(self.style.WARNING(f"Atlandı (format schema:domain olmalı): {item}"))
                continue
            schema_name, domain = [x.strip() for x in item.split(":", 1)]
            name = schema_name

            tenant, t_created = Tenant.objects.get_or_create(
                schema_name=schema_name,
                defaults={
                    "name": name,
                    "paid_until": date.today() + timedelta(days=365),  # 1 yıl geçerli
                },
            )
            if t_created:
                self.stdout.write(self.style.SUCCESS(f"Tenant oluşturuldu: {schema_name}"))

            # domain
            Domain.objects.get_or_create(
                domain=domain,
                defaults={
                    "tenant": tenant,
                    "is_primary": True,
                },
            )

            # Her tenant için süperuser oluştur
            with schema_context(schema_name):
                if not User.objects.filter(username=su_username).exists():
                    User.objects.create_superuser(
                        username=su_username,
                        email=su_email,
                        password=su_password,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"[{schema_name}] superuser oluşturuldu: {su_username}"
                    ))
                    created_any = True

        # Public için de süperuser (opsiyonel)
        with schema_context("public"):
            if not User.objects.filter(username=su_username).exists():
                User.objects.create_superuser(
                    username=su_username,
                    email=su_email,
                    password=su_password,
                )
                self.stdout.write(self.style.SUCCESS(
                    f"[public] superuser oluşturuldu: {su_username}"
                ))
                created_any = True

        if not created_any:
            self.stdout.write("Yeni superuser oluşturulmadı (mevcut olabilir).")
        self.stdout.write(self.style.SUCCESS("bootstrap_multitenant tamamlandı."))
