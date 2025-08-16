# portal/cases/serializers.py
from rest_framework import serializers
from .models import Case, CaseStatusLog

class CaseSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Case
        fields = [
            "id", "tenant", "title", "status",
            "created_at", "updated_at", "created_by",
        ]
        read_only_fields = ["tenant", "created_at", "updated_at", "created_by"]

    def get_created_by(self, obj):
        # kullanıcı adı dön; yoksa None
        u = getattr(obj, "created_by", None)
        return getattr(u, "username", None)

class CaseStatusLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CaseStatusLog
        fields = [
            "id", "case", "old_status", "new_status",
            "changed_by", "changed_at",
        ]
        read_only_fields = ["case", "old_status", "new_status", "changed_by", "changed_at"]

    def get_changed_by(self, obj):
        u = getattr(obj, "changed_by", None)
        return getattr(u, "username", None)
