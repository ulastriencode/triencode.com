import pytest
from django.test import RequestFactory
from tenancy.middleware import CurrentTenantMiddleware
from clients.models import Client, Domain

@pytest.mark.django_db
def test_current_tenant_middleware_resolves_domain_case_insensitively():
    c = Client.objects.create(name="Firma", schema_name="firma")
    Domain.objects.create(tenant=c, domain="Firma1.LOCALHOST", is_primary=True)

    rf = RequestFactory()
    req = rf.get("/", HTTP_HOST="firmA1.localhost:8000")
    mw = CurrentTenantMiddleware(lambda r: r)
    resp = mw(req)
    assert getattr(resp, "tenant", None) == c
