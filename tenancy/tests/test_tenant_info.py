import uuid
from django.test import TestCase
from clients.models import Client as Tenant


class TenantInfoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tenant.objects.all().delete()
        Tenant.objects.create(
            name="firma2",
            domain=f"firma2-{uuid.uuid4()}.local"
        )

    def test_tenant_exists(self):
        self.assertTrue(Tenant.objects.filter(name="firma2").exists())
