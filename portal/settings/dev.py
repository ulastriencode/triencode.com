from .base import *
from datetime import timedelta

# Debug & Hosts
DEBUG = True

# Apps Configuration
ADDITIONAL_APPS = [
    "rest_framework_simplejwt",
    "corsheaders",
]
INSTALLED_APPS += ADDITIONAL_APPS + [
    "portal.memberships",
    "accounts",
]

# Middleware Configuration
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CorsMiddleware should be at the top
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "tenancy.middleware.TenantMiddleware",  # Tenant middleware after common
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS & CSRF Configuration
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ALLOW_ALL_ORIGINS = True  # Note: This contradicts with ALLOWED_ORIGINS, you might want to choose one
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000","http://admin.localhost:8000"]

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Authentication Configuration
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    'portal.accounts.backends.TenantAwareBackend',
    'django.contrib.auth.backends.ModelBackend',
]