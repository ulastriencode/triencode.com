from django.db import connection
from contextlib import nullcontext as schema_context
from clients.models import Client
from .models import DirectoryUser

def upsert_directory_user(u):
    """
    Tenant şemasındaki users.User instance'ını alır,
    public.directory_directoryuser içine upsert eder.
    """
    tenant = connection.get_tenant()                 # aktif tenant
    # tenant'ı public tablosundan bul
    client = Client.objects.get(schema_name=tenant.schema_name)

    payload = {
        "client_id": client.id,
        "client_schema": client.schema_name,
        "client_name": client.name,
        "user_id": u.id,
        "username": u.username,
        "email": u.email or "",
        "is_active": u.is_active,
        "is_superuser": u.is_superuser,
        "last_login": u.last_login,
        "date_joined": getattr(u, "date_joined", None),
        "first_name": getattr(u, "first_name", ""),
        "last_name": getattr(u, "last_name", ""),
    }

    # public şemaya geçip upsert
    with schema_context("public"):
        obj, _created = DirectoryUser.objects.update_or_create(
            client_id=client.id, user_id=u.id, defaults=payload
        )
        return obj

def delete_directory_user(u):
    tenant = connection.get_tenant()
    client = Client.objects.get(schema_name=tenant.schema_name)
    with schema_context("public"):
        DirectoryUser.objects.filter(client_id=client.id, user_id=u.id).delete()
