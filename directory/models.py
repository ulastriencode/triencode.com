from django.db import models
from django.conf import settings
from clients.models import Client

class DirectoryUser(models.Model):
    # Bu iki alan tenant+owner filtrelemesi için
    tenant = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="directory_users", null=True, blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="directory_entries", null=True, blank=True
    )

    # Opsiyonel
    title = models.CharField(max_length=255, blank=True)

    # public.clients_client’e bağ
    client_id = models.IntegerField()              # clients_client.id
    client_schema = models.CharField(max_length=63)
    client_name = models.CharField(max_length=200)

    # tenant’taki users_user alanları (kopya veri)
    user_id = models.IntegerField()                # users_user.id
    username = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(null=True, blank=True)

    # görsel listeleme için opsiyonel
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)

    class Meta:
        unique_together = [("client_id", "user_id")]
        indexes = [
            models.Index(fields=["client_schema", "username"]),
        ]

    def __str__(self):
        return f"{self.client_schema}:{self.username}"
