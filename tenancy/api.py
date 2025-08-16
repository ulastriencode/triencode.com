# portal/tenancy/api.py
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class TenantInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tenant = getattr(request, "tenant", None)
        data = {
            "host": request.get_host(),
            "authenticated": request.user.is_authenticated,
            "tenant": None,
        }
        if tenant:
            data["tenant"] = {
                "id": tenant.id,
                "name": tenant.name,
                "logo_url": request.build_absolute_uri(tenant.logo.url) if tenant.logo else None,
            }
        if request.user.is_authenticated:
            data["user"] = {"id": request.user.id, "username": request.user.username}
        return Response(data)
