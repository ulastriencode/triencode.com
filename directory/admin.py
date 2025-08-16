from django.contrib import admin
from .models import DirectoryUser

@admin.register(DirectoryUser)
class DirectoryUserAdmin(admin.ModelAdmin):
    list_display = ("username", "client_schema", "tenant", "owner", "is_active")
    search_fields = ("username", "client_schema", "client_name", "email")
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request, "tenant", None)
        filters = {"owner": request.user}
        if tenant is not None:
            filters["tenant"] = tenant
        return qs.filter(**filters)

    def save_model(self, request, obj, form, change):
        if not change:
            if getattr(obj, "tenant_id", None) is None:
                obj.tenant = getattr(request, "tenant", None)
            if getattr(obj, "owner_id", None) is None:
                obj.owner = request.user
        super().save_model(request, obj, form, change)
