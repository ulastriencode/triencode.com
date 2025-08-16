import uuid
from django.test import TestCase
from clients.models import Client as Tenant


class LoginTenantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Var olan tüm Tenant kayıtlarını sil
        Tenant.objects.all().delete()

        # Benzersiz domain üret
        cls.t1 = Tenant.objects.create(
            name="firma1",
            domain=f"firma1-{uuid.uuid4()}.local"
        )
        cls.t2 = Tenant.objects.create(
            name="firma2",
            domain=f"firma2-{uuid.uuid4()}.local"
        )

    def test_tenant_count(self):
        self.assertEqual(Tenant.objects.count(), 2)
