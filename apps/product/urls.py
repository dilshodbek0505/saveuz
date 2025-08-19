from django.urls import path

from apps.product.views import ProductView


urlpatterns = [
    path("ProductList/", ProductView.as_view(), name="product-list")
]
