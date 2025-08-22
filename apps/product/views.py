from django.db.models import Count, Q, Exists, OuterRef

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from rest_framework import permissions

from apps.main.models import Product, Favorite
from apps.product.serializers import ProductSerializer


class ProductView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'name_ru', 'name_uz', 'name_en']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        market_id = self.request.query_params.get("market_id")
        if market_id:
            qs = qs.filter(market_id=market_id)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)
        
        qs = qs.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    product=OuterRef('pk'),
                    user=user,
                )
            )
        )
        return qs

class ProductDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = 'pk'


    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        qs = qs.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    product=OuterRef('pk'),
                    user=user,
                )
            )
        )

        return qs