from rest_framework import serializers

from apps.main.models import CommonProductImage, Product, ProductImage
from apps.main.serializers import CategorySerializer, MarketSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "position")
        read_only_fields = fields


class CommonProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonProductImage
        fields = ("id", "image", "position")
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
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
        self.fields["market"] = MarketSerializer()
        return super().to_representation(instance)

    def get_name(self, instance):
        return instance.resolved_name

    def get_description(self, instance):
        return instance.resolved_description

    def get_category(self, instance):
        category = instance.resolved_category
        if not category:
            return None
        return CategorySerializer(category, context=self.context).data

    def get_images(self, instance):
        product_images = list(getattr(instance, "images").all())
        if product_images:
            return ProductImageSerializer(product_images, many=True, context=self.context).data
        if instance.common_product:
            common_images = list(instance.common_product.images.all())
            return CommonProductImageSerializer(common_images, many=True, context=self.context).data
        return []

    def get_image(self, instance):
        file_field = instance.primary_image_file
        if not file_field:
            return None
        request = self.context.get("request")
        url = file_field.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
