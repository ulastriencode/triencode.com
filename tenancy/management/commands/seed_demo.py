from django.core.management.base import BaseCommand
from clients.models import Client as Tenant
from portal.cases.models import Case

class Command(BaseCommand):
    help = "Create demo tenants and sample cases"

    def handle(self, *args, **kwargs):
        t1, _ = Tenant.objects.get_or_create(name="Firma 1", domain="firma1.localhost")
        t2, _ = Tenant.objects.get_or_create(name="Firma 2", domain="firma2.localhost")
        for t in (t1, t2):
            Case.objects.get_or_create(tenant=t, title=f"{t.name} - Dava 1")
            Case.objects.get_or_create(tenant=t, title=f"{t.name} - Dava 2", status="closed")
        self.stdout.write(self.style.SUCCESS("Demo tenants & cases created."))
