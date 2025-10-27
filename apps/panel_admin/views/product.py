from django.db import transaction
from django.utils.crypto import constant_time_compare

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.main.models import Market, Product, Category
from apps.product.serializers import ProductSerializer
from apps.panel_admin.models import AdminDevice


class AdminMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ("id", "name")


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class BulkProductItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
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


class BulkProductCreatePayloadSerializer(serializers.Serializer):
    items = BulkProductItemSerializer(many=True, allow_empty=False)


class BulkProductCreateResponseSerializer(serializers.Serializer):
    created = serializers.IntegerField()
    items = ProductSerializer(many=True)


class AdminMarketListView(ListAPIView):
    queryset = Market.objects.all()
    serializer_class = AdminMarketSerializer
    # Public endpoint: no permissions


class AdminCategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    # Public endpoint: no permissions


class AdminBulkProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    """
    Bulk create products, restricted by a device token managed in Django admin.
    This endpoint does not require user authentication; instead callers must send
    the header `X-Panel-Device` with a token that matches an active
    `AdminDevice` record. Supports JSON payloads as well as multipart form data
    so product images can be uploaded directly.

    Payload format:
    {
      "items": [
        {"name": str, "price": number, "image": file/url, "description": str,
         "market": id, "category": id, "discount_price": number|null,
         "discount_type": str|null, "discount_value": number|null}
      ]
    }
    """

    @swagger_auto_schema(
        request_body=BulkProductCreatePayloadSerializer,
        manual_parameters=[
            openapi.Parameter(
                name="X-Panel-Device",
                in_=openapi.IN_HEADER,
                description="Device token issued from the admin panel",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            status.HTTP_201_CREATED: BulkProductCreateResponseSerializer,
            status.HTTP_403_FORBIDDEN: "Invalid or missing device token",
        },
        operation_description="Bulk create products. Requires an active device token "
                              "managed through the admin panel (no login needed)."
    )
    def post(self, request, *args, **kwargs):
        device_token = request.headers.get("X-Panel-Device", "")
        if not self._is_token_allowed(device_token):
            return Response({"detail": "Invalid or missing device token"}, status=status.HTTP_403_FORBIDDEN)

        payload_serializer = BulkProductCreatePayloadSerializer(data=request.data, context={"request": request})
        payload_serializer.is_valid(raise_exception=True)
        items = payload_serializer.validated_data.get("items")

        with transaction.atomic():
            products = []
            for validated in items:
                product = Product.objects.create(**validated)
                products.append(product)

        # Re-serialize created instances to return IDs and nested fields
        output = ProductSerializer(products, many=True, context={"request": request}).data
        return Response({"created": len(products), "items": output}, status=status.HTTP_201_CREATED)

    @staticmethod
    def _is_token_allowed(token: str) -> bool:
        if not token:
            return False

        allowed_tokens = AdminDevice.objects.filter(is_active=True).values_list("token", flat=True)
        for stored in allowed_tokens:
            if constant_time_compare(token, stored):
                return True
        return False
