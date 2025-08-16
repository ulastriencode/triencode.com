# X:/.../directory/management/commands/sync_directory_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from clients.models import Client
from directory.models import DirectoryUser

User = get_user_model()

class Command(BaseCommand):
    help = "Tüm tenant'ların kullanıcılarını public.directory_directoryuser içine senkronize eder."

    def handle(self, *args, **options):
        tenants = Client.objects.all()
        created, updated = 0, 0
        for t in tenants:
            with schema_context(t.schema_name):
                for u in User.objects.all():
                    obj, is_created = DirectoryUser.objects.update_or_create(
                        client_id=t.id,
                        user_id=u.id,
                        defaults={
                            "tenant": t,
                            "owner_id": u.id,  # owner = kendisi
                            "title": f"Kullanıcı: {u.username}",
                            "client_schema": t.schema_name,
                            "client_name": t.name,
                            "username": u.username,
                            "email": u.email or "",
                            "is_active": u.is_active,
                            "is_superuser": u.is_superuser,
                            "last_login": u.last_login,
                            "date_joined": u.date_joined,
                            "first_name": getattr(u, "first_name", "") or "",
                            "last_name": getattr(u, "last_name", "") or "",
                        }
                    )
                    if is_created:
                        created += 1
                    else:
                        updated += 1
            self.stdout.write(self.style.SUCCESS(f"[{t.schema_name}] sync ok"))
        self.stdout.write(self.style.SUCCESS(f"Created: {created}, Updated: {updated}"))
