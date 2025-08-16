from rest_framework import generics, permissions
from .models import DirectoryUser
from .serializers import DirectoryUserSerializer
from .permissions import IsTenantOwner  # <-- EKLENDİ
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

class MyDirectoryUsersView(generics.ListAPIView):
    serializer_class = DirectoryUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # listeleme için yeterli

    def get_queryset(self):
        qs = DirectoryUser.objects.all()
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            qs = qs.filter(tenant=tenant)
        return qs.filter(owner=self.request.user).order_by("-id")


class DirectoryUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DirectoryUser.objects.all()
    serializer_class = DirectoryUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantOwner]  # <-- obje seviyesinde kontrol

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            qs = qs.filter(tenant=tenant)
        return qs.filter(owner=self.request.user)
@api_view(["GET"])
@permission_classes([AllowAny])
def tenant_info(request):
    t = getattr(request, "tenant", None)

    def build_logo_url(obj):
        try:
            if obj and getattr(obj, "logo", None):
                f = getattr(obj.logo, "url", None)
                if f:
                    return request.build_absolute_uri(f)
        except Exception:
            pass
        return None

    data = {
        "host": request.get_host(),
        "authenticated": bool(request.user and request.user.is_authenticated),
        "tenant": None if not t else {
            "id": getattr(t, "id", None),
            "name": getattr(t, "name", None),
            "db_alias": getattr(t, "db_alias", None),
            "logo": build_logo_url(t),
            # İsteğe bağlı alanlar; varsa döner
            "primary_color": getattr(t, "primary_color", None),
            "secondary_color": getattr(t, "secondary_color", None),
        },
    }
    return Response(data)