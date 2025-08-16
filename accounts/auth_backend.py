
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from clients.models import Client as Tenant

class TenantModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                tenant = getattr(request, "tenant", None) if request else None
                if tenant is not None:
                    if not UserTenantMembership.objects.filter(user=user, tenant=tenant).exists():
                        return None
                return user
        except UserModel.DoesNotExist:
            return None
        return None
