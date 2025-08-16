from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tenancy.threadlocal import get_current_tenant_id
from portal.memberships.models import TenantMembership

class TenantAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        t = super().get_token(user)
        t["tenant_id"] = get_current_tenant_id()
        return t

    def validate(self, attrs):
        data = super().validate(attrs)
        tid = get_current_tenant_id()
        if not tid:
            raise serializers.ValidationError("Tenant belirlenemedi.")
        ok = TenantMembership.objects.filter(user=self.user, tenant_id=tid, is_active=True).exists()
        if not ok:
            raise serializers.ValidationError("Bu firmada aktif hesabınız yok.")
        data["tenant_id"] = tid
        return data
