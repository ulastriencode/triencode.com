from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()
class TenantLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        tenant = getattr(request, 'tenant', None)

        if not tenant:
            return Response({"detail": "Tenant bulunamadı"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username, tenant=tenant)
        except User.DoesNotExist:
            return Response({"detail": "Kullanıcı bulunamadı"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"detail": "Şifre hatalı"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        refresh["tenant_id"] = tenant.id

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "tenant": tenant.name
            }
        })
    
