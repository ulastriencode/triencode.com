import os
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _


LANGUAGE_CODE = "tr"         # Türkçe arayüz
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# (Opsiyonel ama hoş) Admin başlıkları


ADMIN_SITE_HEADER = "Avukatlık Portalı Yönetim Paneli"
ADMIN_SITE_TITLE = "Avukatlık Portalı Yönetimi"
ADMIN_INDEX_TITLE = "Yönetim Paneli"
TENANT_ADMIN_ACCESS_ALL = True 
# ------------ Paths / ENV ------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../avukatlik_portali
PROJECT_ROOT = BASE_DIR.parent                     # repo kökü

# DJANGO_ENV=dev|prod gibi dosyayı seç: .env.dev, .env.prod
DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")
ENV_FILE = PROJECT_ROOT / f".env.{DJANGO_ENV}"

# python-dotenv ile yükle (yoksa .env fallback)
try:
    from dotenv import load_dotenv
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        # ayni kökte düz .env varsa onu da dene
        fallback = PROJECT_ROOT / ".env"
        if fallback.exists():
            load_dotenv(fallback)
except Exception:
    pass

def env_bool(name: str, default=False):
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on")

def env_list(name: str, default=None):
    v = os.getenv(name)
    if v is None:
        return default or []
    return [item.strip() for item in v.split(",") if item.strip()]

# ------------ Core ------------
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    # dev için düşmeyelim; prod'da mutlaka .env ver
    SECRET_KEY = "dev-" + ("x" * 48)

DEBUG = env_bool("DEBUG", default=True)

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    default=[
        "127.0.0.1", "localhost",
        "emirkevserav.localhost", "sonerdicanav.localhost","ulasdemirav.localhost","deneme.localhost",
    ],
)

SHARED_APPS = [
    'django_tenants',     # her zaman ilk
    'clients',            # tenants listesi
    'directory',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
]

TENANT_APPS = [
    "avukatlik_portali.apps.AvukatlikPortaliConfig",
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.auth',
    'users',
    'accounts',
    
    # tenant’a özel diğer app’ler
]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS

# Bu projede lazım olan app'leri garanti ekle
for app in ['tenancy', 'clients']:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

DATABASE_ROUTERS = ['tenancy.db_router.HostDatabaseRouter', 'avukatlik_portali.dbrouter.RowLevelRouter', 
]

# ------------ Database (PostgreSQL + django-tenants engine) ------------


DB_NAME = os.getenv("DB_NAME", "avukatlik_portali_dev")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")


import os
from pathlib import Path

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "avukatlik_portali"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": {"connect_timeout": 10},
    }
}
DATABASE_ROUTERS = ['tenancy.db_router.HostDatabaseRouter', 'avukatlik_portali.dbrouter.RowLevelRouter']

AUTH_USER_MODEL = "users.User"
ADMIN_PANEL_DOMAIN = os.getenv("ADMIN_PANEL_DOMAIN", "admin.localhost")
# ------------ Middleware ------------
MIDDLEWARE = [
    'tenancy.middleware.CurrentTenantMiddleware',
    "avukatlik_portali.middleware.RedirectPublicAdminMiddleware",# ① en üstte
    "corsheaders.middleware.CorsMiddleware",                # ② CORS (yükseklerde)
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "avukatlik_portali.urls"
WSGI_APPLICATION = "avukatlik_portali.wsgi.application"

# ------------ DRF / JWT ------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("SIMPLEJWT_ACCESS_TTL_MIN", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("SIMPLEJWT_REFRESH_TTL_DAY", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ------------ CORS / CSRF ------------
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://firma1.localhost:3000",
        "http://firma2.localhost:3000",
        "http://firma3.localhost:3000",
        "http://emirkevserav.localhost:3000",
        "http://sonerdicanav.localhost:3000",
        "http://public.localhost:3000",
        "http://client1.localhost:3000",
        "http://admin.localhost:3000",
    ],
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-tenant-domain",
    "authorization",
    "content-type",
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS[:]  # aynısını kullan

# ------------ Templates / Static / Media ------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
