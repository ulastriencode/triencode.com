
def current_tenant(request):
    return {'current_tenant': getattr(request, 'tenant', None)}
