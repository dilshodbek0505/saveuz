from rest_framework import serializers

from apps.main.models import Product, ProductImage
from apps.main.serializers import CategorySerializer, MarketSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "position")
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "image",
            "images",
            "description",
            "market",
            "discount_price",
            "discount_type",
            "discount_value",
            "category",
            "is_favorited",
        )

    def to_representation(self, instance):
        self.fields["category"] = CategorySerializer()
        self.fields["market"] = MarketSerializer()
        return super().to_representation(instance)

    def get_image(self, instance):
        file_field = instance.primary_image_file
        if not file_field:
            return None
        request = self.context.get("request")
        url = file_field.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
