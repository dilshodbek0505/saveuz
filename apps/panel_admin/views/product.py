from django.db import transaction

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from drf_yasg.utils import swagger_auto_schema

from apps.main.models import Market, Product, Category
from apps.product.serializers import ProductSerializer


class IsSuperUser(BasePermission):
    message = "You must be logged in as a superuser."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)


class AdminMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = ("id", "name")


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class BulkProductItemSerializer(serializers.ModelSerializer):
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
    items = BulkProductItemSerializer(many=True)


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
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsSuperUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    """
    Bulk create products, restricted to authenticated Django sessions belonging
    to superusers. Any request that is not backed by a logged-in superuser
    session is rejected. Supports JSON payloads as well as multipart form data
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
        responses={status.HTTP_201_CREATED: BulkProductCreateResponseSerializer},
        operation_description="Bulk create products. Requires an active session "
                              "for a logged-in superuser."
    )
    def post(self, request, *args, **kwargs):
        payload_serializer = BulkProductCreatePayloadSerializer(data=request.data, context={"request": request})
        payload_serializer.is_valid(raise_exception=True)
        items = payload_serializer.validated_data.get("items")
        if not items:
            return Response({"detail": "`items` must be a non-empty list"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            products = []
            for validated in items:
                product = Product.objects.create(**validated)
                products.append(product)

        # Re-serialize created instances to return IDs and nested fields
        output = ProductSerializer(products, many=True, context={"request": request}).data
        return Response({"created": len(products), "items": output}, status=status.HTTP_201_CREATED)
