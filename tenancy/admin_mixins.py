from django.contrib import admin
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from django.db.models import QuerySet
class TenantScopedAdminMixin:
    tenant_field_name = "tenant"  # modellerdeki FK alan adı

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if isinstance(qs, QuerySet) and tenant:
            qs = qs.filter(tenant=tenant, owner=self.request.user)
        return qs

    def has_module_permission(self, request):
        if getattr(request, "is_global_admin", False):
            return True
        tenant = getattr(request, "tenant", None)
        if not tenant or not request.user.is_authenticated:
            return False
        # istersen membership kontrolü
        return True

    def save_model(self, request, obj, form, change):
        if not getattr(request, "is_global_admin", False):
            tenant = getattr(request, "tenant", None)
            if tenant is None:
                raise PermissionDenied("Tenant bulunamadı.")
            if hasattr(obj, self.tenant_field_name):
                setattr(obj, self.tenant_field_name, tenant)
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not getattr(request, "is_global_admin", False):
            tenant = getattr(request, "tenant", None)
            if tenant and self.tenant_field_name in form.base_fields:
                bf = form.base_fields[self.tenant_field_name]
                bf.initial = tenant
                bf.disabled = True
        return form
    
    
class TenantOwnerScopedViewSetMixin:
    permission_classes = [IsAuthenticated]

    tenant_field_name = "tenant"  # modeldeki tenant FK adı
    owner_field_name  = "owner"   # modeldeki owner/user FK adı

    def _get_tenant(self):
        return getattr(self.request, "tenant", None)

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self._get_tenant()
        user = self.request.user
        # SÜPERUSER BİLE OLSA SADECE KENDİNİ GÖRSÜN istiyorsan, bypass YOK!
        filters = {}
        if tenant is not None:
            filters[self.tenant_field_name] = tenant
        filters[self.owner_field_name] = user
        return qs.filter(**filters)

    def perform_create(self, serializer):
        data = {}
        tenant = self._get_tenant()
        if tenant is not None:
            data[self.tenant_field_name] = tenant
        data[self.owner_field_name] = self.request.user
        serializer.save(**data)
        
class IsTenantOwner(BasePermission):
    """
    Sadece kendi tenant'ındaki ve kendi "owner"ı olduğu kayıtları görsün.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj.tenant.schema_name ve obj.owner kullanıcıya ait olmalı
        return (
            getattr(obj, "tenant", None) and
            getattr(obj.tenant, "schema_name", None) == getattr(request, "tenant", None).schema_name and
            getattr(obj, "owner_id", None) == request.user.id
        )