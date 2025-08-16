from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    tenant = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        default=None,
        related_name='users',
        db_constraint=False,   # tenant şemasında public tabloya FK kurmaya çalışma
    )
class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"