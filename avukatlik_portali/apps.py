# avukatlik_portali/apps.py
from django.apps import AppConfig
from django.contrib import admin
from django.conf import settings


class AvukatlikPortaliConfig(AppConfig):
    name = "avukatlik_portali"
    verbose_name = "Yönetim"

    def ready(self):
        # Admin başlıklarını apps yüklendikten sonra ayarla
       
        admin.site.site_header = getattr(settings, "ADMIN_SITE_HEADER", "Yönetim Paneli")
        admin.site.site_title  = getattr(settings, "ADMIN_SITE_TITLE",  "Yönetim")
        admin.site.index_title = getattr(settings, "ADMIN_INDEX_TITLE", "Kontrol Paneli")
