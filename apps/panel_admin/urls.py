from django.urls import path

from apps.panel_admin.views.product import (
    AdminMarketListView,
    AdminCategoryListView,
    AdminBulkProductCreateView,
)


app_name = "panel_admin"


urlpatterns = [
    path("markets/", AdminMarketListView.as_view(), name="markets-list"),
    path("categories/", AdminCategoryListView.as_view(), name="categories-list"),
    path("products/bulk-create/", AdminBulkProductCreateView.as_view(), name="products-bulk-create"),
]
