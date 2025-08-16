import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    f"avukatlik_portali.settings.{os.getenv('DJANGO_ENV', 'dev')}"
)

application = get_wsgi_application()