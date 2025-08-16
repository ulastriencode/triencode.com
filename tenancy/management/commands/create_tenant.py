from django.core.management.base import BaseCommand, CommandError
from clients.models import Client as Tenant

class Command(BaseCommand):
    help = "Create a single tenant. Usage: python manage.py create_tenant --name 'Firma 3' --domain firma3.localhost"

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--domain", required=True)

    def handle(self, *args, **opts):
        name = opts["name"]
        domain = opts["domain"]
        t, created = Tenant.objects.get_or_create(domain=domain, defaults={"name": name})
        if created:
            self.stdout.write(self.style.SUCCESS(f"Tenant created: {t.id} - {t.name} ({t.domain})"))
        else:
            raise CommandError(f"Tenant already exists for domain={domain}")
