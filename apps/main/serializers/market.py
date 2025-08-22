from rest_framework import serializers

from apps.main.models import Market


class MarketSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    class Meta:
        model = Market
        fields = (
            "id",
            "name",
            "description",
            "logo",
            "lon",
            "lat",
            "address",
            "open_time",
            "end_time",
            "owner",
            "is_favorited",
        )