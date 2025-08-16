from django.conf import settings
from django.shortcuts import redirect

class RedirectPublicAdminMiddleware:
    """
    /admin/ isteği admin olmayan bir tenant’tan geliyorsa,
    yine kendi /admin/’inde kalsın; public’e gitmeye çalışırsa admin.localhost’a yönlendir.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_domain = getattr(settings, "ADMIN_PANEL_DOMAIN", "admin.localhost")

    def __call__(self, request):
        # public paneli doğrudan kullananı admin.localhost'a it
        if request.get_host().split(":")[0] in ("public.localhost", "localhost"):
            if request.path.startswith("/admin/"):
                return redirect(f"http://{self.admin_domain}:8000{request.path}")
        return self.get_response(request)
