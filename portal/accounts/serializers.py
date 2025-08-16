# portal/accounts/serializers.py
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 1) önce kullanıcı doğrulansın (self.user set olur)
        data = super().validate(attrs)

        # 2) tek-tenant kuralı
        request = self.context.get('request')
        req_tid = getattr(getattr(request, 'tenant', None), 'id', None)
        user_tid = getattr(getattr(self.user, 'tenant', None), 'id', None)

        # DEBUG: Sunucu konsoluna düşer (test için; çalışınca silebilirsin)
        print(f"[JWT VALIDATE] req_tid={req_tid} user_tid={user_tid} user={getattr(self.user,'username',None)}")

        if not req_tid or not user_tid or req_tid != user_tid:
            raise AuthenticationFailed("Tenant mismatch", code="tenant_mismatch")

        # 3) claim
        token = self.get_token(self.user)
        token['tenant_id'] = user_tid
        data['refresh'] = str(token)
        data['access']  = str(token.access_token)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
