from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tenant_info(request):
    tenant = getattr(request, "tenant", None)
    if not tenant:
        return Response({"error": "Tenant bulunamadı"}, status=400)

    return Response({
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "logo": tenant.logo.url if tenant.logo else None,
            "theme_color": tenant.theme_color,
            "domain": tenant.domain_url,
            "schema": tenant.schema_name
        }
    })
