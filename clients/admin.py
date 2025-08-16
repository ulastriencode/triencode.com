# clients/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Client, Domain
from django.apps import apps
UserTenantMembership = apps.get_model('tenancy', 'UserTenantMembership')
User = get_user_model()

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 0
    verbose_name = "Alan Adı"
    verbose_name_plural = "Alan Adları"

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("ad", "sema", "db_alias_value", "son_odeme", "deneme_sureci", "kullanici_sayisi", "tenant_adminine_git")
    search_fields = ("name", "schema_name")
    inlines = [DomainInline]

    # --- mevcut methodlar ---
    def ad(self, obj): return obj.name
    ad.short_description = "Ad"

    def sema(self, obj): return obj.schema_name
    sema.short_description = "Şema"

    def son_odeme(self, obj): return obj.paid_until
    son_odeme.short_description = "Ücretli Bitiş"

    def deneme_sureci(self, obj): return obj.on_trial
    deneme_sureci.boolean = True
    deneme_sureci.short_description = "Deneme Süreci"

    def kullanici_sayisi(self, obj):
        return UserTenantMembership.objects.filter(tenant=obj).count()
    kullanici_sayisi.short_description = "Kullanıcı Sayısı"

    def tenant_adminine_git(self, obj):
        primary = obj.domains.filter(is_primary=True).first()
        host = (primary.domain if primary else f"{obj.schema_name}.localhost")
        return f"http://{host}:8000/admin/"
    tenant_adminine_git.short_description = "Tenant Admini"

    # --- eklenen güvenli sütun ---
    def db_alias_value(self, obj):
        return getattr(obj, "db_alias", "default")
    db_alias_value.short_description = "DB Alias"

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("domain", "tenant__name", "tenant__schema_name")
