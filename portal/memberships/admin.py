from django.contrib import admin
from .models import TenantMembership

@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ('user','tenant','role','is_active')
    list_filter = ('role','is_active','tenant')
    search_fields = ('user__username','tenant__name')
