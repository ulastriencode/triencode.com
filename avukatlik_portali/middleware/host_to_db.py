from utils.current_db import set_current_db

class HostToDBAliasMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        alias = "default"
        if host.startswith("sonerdicanav"): alias = "sonerdicanav"
        elif host.startswith("emirkevserav"): alias = "emirkevserav"
        set_current_db(alias)
        return self.get_response(request)
