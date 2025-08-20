from django.urls import path

from apps.product.views import ProductView, ProductDetailView


urlpatterns = [
    path("ProductList/", ProductView.as_view(), name="product-list"),
    path("ProductDetail/<int:pk>/", ProductDetailView.as_view(), name="product-detail")
]
