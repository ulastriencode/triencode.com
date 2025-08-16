import uuid
from django.test import TestCase
from clients.models import Client as Tenant

class LoginTenantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Tenant.objects.all().delete()
        Tenant.objects.create(
            name="firma2",
            domain=f"firma2-{uuid.uuid4()}.local"
        )

    def test_dummy(self):
        self.assertEqual(Tenant.objects.count(), 1)
