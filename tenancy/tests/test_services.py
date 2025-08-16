import pytest
from tenancy.services.create_tenant import create_tenant, TenantCreationError
from clients.models import Client, Domain

@pytest.mark.django_db
def test_create_tenant_basic_flow():
    client = create_tenant(name="Yeni Firma", schema_name="yenifirma", domain="sub.localhost")
    assert isinstance(client, Client)
    assert Domain.objects.filter(tenant=client, domain="sub.localhost").exists()

@pytest.mark.django_db
def test_create_tenant_duplicate_domain():
    create_tenant(name="A", schema_name="a", domain="dupe.localhost")
    with pytest.raises(TenantCreationError):
        create_tenant(name="B", schema_name="b", domain="DUPE.localhost")
