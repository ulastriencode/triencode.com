from rest_framework import serializers
from .models import DirectoryUser

class DirectoryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectoryUser
        fields = [
            "id", "title",
            "client_id","client_schema","client_name",
            "user_id","username","email","first_name","last_name",
            "is_active","is_superuser","last_login","date_joined",
        ]