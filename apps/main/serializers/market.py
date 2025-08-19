from rest_framework import serializers

from apps.main.models import Market


class MarketSerializer(serializers.ModelSerializer):
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
        )