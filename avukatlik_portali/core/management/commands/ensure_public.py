from django.core.management.base import BaseCommand
from clients.models import Client, Domain

class Command(BaseCommand):
    help = "Ensure public tenant and domain exist."

    def handle(self, *args, **opts):
        c, _ = Client.objects.get_or_create(
            schema_name="public",
            defaults={"name": "Public", "paid_until": "2099-01-01", "on_trial": True},
        )
        Domain.objects.get_or_create(domain="admin.localhost", defaults={"tenant": c})
        self.stdout.write(self.style.SUCCESS("Public OK"))
