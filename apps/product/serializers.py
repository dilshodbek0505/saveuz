from rest_framework import serializers

from apps.main.models import Product
from apps.main.serializers import CategorySerializer, MarketSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "image",
            "description",
            "market",
            "discount_price",
            "discount_type",
            "discount_value",
            "category",
        )

    def to_representation(self, instance):
        self.fields['category'] = CategorySerializer()
        self.fields['market'] = MarketSerializer()

        return super().to_representation(instance)
    
