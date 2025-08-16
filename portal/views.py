# portal/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required  # istersen public bırakabilirsin; ben korumayı öneriyorum
def whoami(request):
    t = getattr(request, "_current_tenant", None) or getattr(request, "tenant", None)
    return JsonResponse({
        "user": request.user.username,
        "tenant_id": getattr(t, "id", None),
    })

def home(request):
    return JsonResponse({
        "message": "Avukatlık Portal API",
        "endpoints": ["/api/cases/", "/api/token/", "/api/token/refresh/", "/api/tenant/", "/api/whoami/", "/admin/"]
    })

def tenant_info(request):
    """
    Frontend RequireAuth: domain -> tenant eşleşmesini teyit eder.
    Bu endpoint anonim de olabilir.
    """
    t = getattr(request, "_current_tenant", None) or getattr(request, "tenant", None)
    return JsonResponse({
        "id": getattr(t, "id", None),
        "domain": getattr(t, "domain", None),
        "name": getattr(t, "name", None),
    })
