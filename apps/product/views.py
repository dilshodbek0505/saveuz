from django.shortcuts import render

from rest_framework.generics import ListAPIView

from apps.main.models import Product
from apps.product.serializers import ProductSerializer


class ProductView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        market_id = self.request.query_params.get("market_id")
        if market_id:
            qs = qs.filter(market_id=market_id)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)
        
        return qs
