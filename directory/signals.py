from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .utils import upsert_directory_user, delete_directory_user

User = get_user_model()  # <-- import_string yerine

@receiver(post_save, sender=User)
def user_saved(sender, instance, **kwargs):
    try:
        upsert_directory_user(instance)
    except Exception:
        pass

@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    try:
        delete_directory_user(instance)
    except Exception:
        pass
