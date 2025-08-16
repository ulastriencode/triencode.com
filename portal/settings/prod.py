from .base import *

DEBUG = False

# SADECE kendi domain(ler)in
ALLOWED_HOSTS = ["app.senin-domainin.com", ".senin-domainin.com"]

# HTTPS zorunluluğu
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Proxy/Nginx arkasındaysan:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CORS (gerekliyse kısıtlı tut)
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE
CORS_ALLOWED_ORIGINS = ["https://app.senin-domainin.com"]
CSRF_TRUSTED_ORIGINS = ["https://app.senin-domainin.com"]
