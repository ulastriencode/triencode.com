from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from clients.models import Client
from django.contrib.auth import get_user_model
from directory.utils import upsert_directory_user

class Command(BaseCommand):
    help = "Tüm tenant'lardaki kullanıcıları public directory'ye aktarır."

    def handle(self, *args, **options):
        User = get_user_model()  # <-- burada da
        for client in Client.objects.all():
            self.stdout.write(self.style.WARNING(f"Scanning {client.schema_name}..."))
            with tenant_context(client):
                for u in User.objects.all():
                    upsert_directory_user(u)
        self.stdout.write(self.style.SUCCESS("Tamamlandı."))
