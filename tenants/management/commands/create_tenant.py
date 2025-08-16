from django.core.management.base import BaseCommand
from tenants.models import Client, Domain

class Command(BaseCommand):
    help = "Yeni tenant oluşturur"

    def handle(self, *args, **options):
        tenant = Client(schema_name='firma1', name='Firma 1', theme_color="#ff0000")
        tenant.save()

        domain = Domain(domain='firma1.localhost', tenant=tenant, is_primary=True)
        domain.save()

        self.stdout.write(self.style.SUCCESS('Tenant başarıyla oluşturuldu'))
