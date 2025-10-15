from django.urls import path

from apps.panel_admin.views.product import (
    AdminMarketListView,
    AdminCategoryListView,
    AdminBulkProductCreateView,
)


urlpatterns = [
    path("markets/", AdminMarketListView.as_view(), name="admin-markets-list"),
    path("categories/", AdminCategoryListView.as_view(), name="admin-categories-list"),
    path("products/bulk-create/", AdminBulkProductCreateView.as_view(), name="admin-products-bulk-create"),
]
