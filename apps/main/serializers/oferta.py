from rest_framework import serializers

from apps.main.models import Oferta


class OfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oferta
        fields = (
            "id",
            "title",
            "file",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

