import os
from .base import *
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- DJANGO-TENANTS'I TAMAMEN DEVRE DIŞI BIRAK ---
# Middleware'den temizle
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'django_tenants.middleware.main.TenantMainMiddleware']

# INSTALLED_APPS'ten temizle
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_tenants']

# Base.py içinde SHARED_APPS / TENANT_APPS tanımlıysa 'django_tenants'ı çıkar
if 'SHARED_APPS' in globals():
    SHARED_APPS = [a for a in SHARED_APPS if a != 'django_tenants']
if 'TENANT_APPS' in globals():
    TENANT_APPS = TENANT_APPS  # ekstra işlem gerekmiyor

# CurrentTenantMiddleware'i Security'den hemen sonra konumlandır
mw = 'tenancy.middleware.CurrentTenantMiddleware'
if mw not in MIDDLEWARE:
    try:
        idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1
    except ValueError:
        idx = 0
    MIDDLEWARE.insert(idx, mw)

DATABASE_ROUTERS = ['tenancy.db_router.HostDatabaseRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_DEFAULT_NAME', 'avp_default'),
        'USER': os.getenv('DB_DEFAULT_USER', os.getenv('POSTGRES_USER', 'postgres')),
        'PASSWORD': os.getenv('DB_DEFAULT_PASSWORD', os.getenv('POSTGRES_PASSWORD', '1')),
        'HOST': os.getenv('DB_DEFAULT_HOST', os.getenv('POSTGRES_HOST', '127.0.0.1')),
        'PORT': os.getenv('DB_DEFAULT_PORT', os.getenv('POSTGRES_PORT', '5432')),
    },
}

HOST_DB_MAP = {
    'deneme.localhost': 'deneme',}

DEFAULT_DB_ALIAS = 'default'

# '.localhost' wildcard tek başına alt domainlerin hepsini kapsar.

# ---- auto-added by create_tenant.py ----
DATABASES['deneme'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'avp_deneme',
    'USER': 'postgres',
    'PASSWORD': '1',
    'HOST': '127.0.0.1',
    'PORT': '5432',
}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'deneme.localhost']
