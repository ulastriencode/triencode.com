
from django.contrib import admin
from .models import UserTenantMembership
@admin.register(UserTenantMembership)
class UserTenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tenant", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("user__username", "tenant__name")
