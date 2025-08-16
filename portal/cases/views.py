from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from .models import Case
from .serializers import CaseSerializer
from .permissions import InSameTenantCanList, InSameTenantOwnerAdminCanWrite

class CaseListView(generics.ListCreateAPIView):
    serializer_class = CaseSerializer
    permission_classes = [InSameTenantCanList]  # yazma için owner/admin; GET’i de kapsar

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        user = self.request.user
        if not user.is_authenticated or not tenant or user.tenant_id != tenant.id:
            # authenticated ama yanlış tenant → 403
            raise PermissionDenied("Farklı tenant")
        # sadece bu tenanttaki davalar
        return Case.objects.filter(tenant=tenant).order_by("-updated_at")

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        user = self.request.user
        if not user.is_authenticated or not tenant or user.tenant_id != tenant.id:
            raise PermissionDenied("Farklı tenant")
        serializer.save(tenant=tenant, created_by=user)

class CaseDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CaseSerializer
    permission_classes = [InSameTenantOwnerAdminCanWrite]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        user = self.request.user
        if not user.is_authenticated or not tenant or user.tenant_id != tenant.id:
            raise PermissionDenied("Farklı tenant")
        return Case.objects.filter(tenant=tenant)

# (Varsa) status log listesi
from .models import CaseStatusLog
from .serializers import CaseStatusLogSerializer

class CaseStatusLogListView(generics.ListAPIView):
    serializer_class = CaseStatusLogSerializer
    permission_classes = [InSameTenantCanList]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        user = self.request.user
        if not user.is_authenticated or not tenant or user.tenant_id != tenant.id:
            raise PermissionDenied("Farklı tenant")
        case_id = self.kwargs["pk"]
        return CaseStatusLog.objects.filter(case_id=case_id, case__tenant=tenant).order_by("-changed_at")
