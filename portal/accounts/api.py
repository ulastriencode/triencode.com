from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

def _current_tenant_id_from_request(request):
    if request and hasattr(request, "_current_tenant") and request._current_tenant:
        return request._current_tenant.id
    try:
        from tenancy.threadlocal import get_current_tenant_id
        return get_current_tenant_id()
    except Exception:
        return None

class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Token'a tenant id claim'i ekle
        token['tid'] = getattr(user, 'tenant_id', None)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get('request')
        current_tid = _current_tenant_id_from_request(request)
        user = self.user

        ok = False

        # Tek-tenant kullanıcı modeli
        if hasattr(user, 'tenant_id') and user.tenant_id == current_tid:
            ok = True
        else:
            # Çoklu üyelik varsa kontrol et
            try:
                from portal.memberships.models import TenantMembership
                ok = TenantMembership.objects.filter(
                    user=user, tenant_id=current_tid, is_active=True
                ).exists()
            except Exception:
                ok = False

        if not ok:
            raise AuthenticationFailed("Bu firmada oturum açma yetkiniz yok.")

        data['tid'] = current_tid
        return data

class TenantTokenObtainPairView(TokenObtainPairView):
    serializer_class = TenantTokenObtainPairSerializer
