from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions

class TenantAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)  # self.user set edilir
        request = self.context.get("request")
        # Tenant zorunluluğu:
        if not request or not getattr(request, "tenant", None):
            raise exceptions.AuthenticationFailed("Tenant bulunamadı (host geçersiz).", code="tenant_missing")

        user = self.user
        if not getattr(user, "tenant_id", None):
            raise exceptions.AuthenticationFailed("Kullanıcıya tanımlı tenant yok.", code="user_no_tenant")

        if not request.tenant or user.tenant_id != request.tenant.id:
            raise exceptions.AuthenticationFailed("Tenant uyuşmuyor.", code="tenant_mismatch")

        return data
