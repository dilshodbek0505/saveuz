from django.db.models import Count, Q, Exists, OuterRef

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import permissions

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.main.models import Favorite, Product
from apps.product.serializers import ProductSerializer


class ProductView(ListAPIView):
    queryset = Product.objects.select_related(
        "market",
        "category",
        "common_product",
        "common_product__category",
    ).prefetch_related("images", "common_product__images")
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "name",
        "name_ru",
        "name_uz",
        "name_en",
        "common_product__name",
        "common_product__name_ru",
        "common_product__name_uz",
        "common_product__name_en",
    ]
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['price']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name="market_id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter(name="category_id", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter(name="is_discount", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, default=False, required=False),
            openapi.Parameter(name="is_favorited", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        market_id = self.request.query_params.get("market_id")
        if market_id:
            qs = qs.filter(market_id=market_id)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(
                Q(category_id=category_id) | Q(common_product__category_id=category_id)
            )
        
        is_discount = self.request.query_params.get("is_discount")
        if is_discount and (is_discount == "True" or is_discount == "true"):
            qs = qs.filter(discount_type__isnull=False,
                           discount_price__isnull=False,
                           discount_value__isnull=False)

        qs = qs.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    product=OuterRef('pk'),
                    user=user,
                    is_active=True
                )
            )
        )

        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited and is_favorited.lower() == "true":
            qs = qs.filter(is_favorited=True)
        elif is_favorited and is_favorited.lower() == "false":
            qs = qs.filter(is_favorited=False)
        
        qs = qs.order_by('?')
        
        return qs

class ProductDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related(
        "market",
        "category",
        "common_product",
        "common_product__category",
    ).prefetch_related("images", "common_product__images")
    lookup_field = 'pk'


    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        qs = qs.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    product=OuterRef('pk'),
                    user=user,
                    is_active=True,
                )
            )
        )

        return qs
