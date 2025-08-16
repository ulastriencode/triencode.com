from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        # Test kullanıcı oluştur
        self.username = "testuser"
        self.password = "123456"
        User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        response = self.client.post("/api/login/", {
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_fail(self):
        response = self.client.post("/api/login/", {
            "username": "wrong",
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
