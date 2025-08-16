from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from clients.models import Client, Domain

class Command(BaseCommand):
    help = "Create or update a tenant and its domain."

    def add_arguments(self, parser):
        parser.add_argument("--schema", required=True)
        parser.add_argument("--domain", required=True)

    def handle(self, *args, **opts):
        schema = opts["schema"]
        domain = opts["domain"]

        c, created = Client.objects.get_or_create(
            schema_name=schema,
            defaults={"name": schema, "paid_until": timezone.now().date()+timedelta(days=365), "on_trial": True},
        )
        if created:
            c.create_schema(check_if_exists=True)
        Domain.objects.update_or_create(domain=domain, defaults={"tenant": c})
        self.stdout.write(self.style.SUCCESS(f"Tenant OK: {schema} -> {domain}"))
