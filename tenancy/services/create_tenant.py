from django.db import transaction, IntegrityError
from django.utils.text import slugify
from clients.models import Client, Domain

class TenantCreationError(Exception):
    pass

@transaction.atomic
def create_tenant(*, name: str, schema_name: str|None=None, domain: str|None=None,
                  on_trial: bool=True, primary_color:str|None=None,
                  secondary_color:str|None=None, logo=None) -> Client:
    if not name or not name.strip():
        raise TenantCreationError("name zorunludur")
    name = name.strip()

    schema = (schema_name or slugify(name)).replace("-", "")
    if not schema:
        raise TenantCreationError("schema_name uretilemedi")

    dom = (domain or f"{schema}.localhost").strip().lower()
    if not dom:
        raise TenantCreationError("domain zorunludur/uretilemedi")

    try:
        client = Client.objects.create(
            name=name,
            schema_name=schema,
            on_trial=on_trial,
            primary_color=primary_color or Client._meta.get_field('primary_color').default,
            secondary_color=secondary_color or Client._meta.get_field('secondary_color').default,
            logo=logo,
        )
        Domain.objects.create(tenant=client, domain=dom, is_primary=True)
    except IntegrityError as e:
        raise TenantCreationError(f"Tenant/Domain benzersizligi ihlali: {e}")

    return client
