from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.main.views import BannerView, CategoryView, MarketView \
                            ,FavoriteViewSet, MarketDetailView, NotificationListView \
                            ,ToggleNotificationAllowedView, OfertaView


router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorites')


urlpatterns = [
    path("banner/BannerList/", BannerView.as_view(), name="banner-list"),
    path("category/CategoryList/", CategoryView.as_view(), name="category-list"),
    path("market/MarketList/", MarketView.as_view(), name="market-list"),
    path("market/MarketDetail/<int:pk>/", MarketDetailView.as_view(), name="market-detail"),

    path("notifications/NotificationList/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/ToggleNotificationAllowed/", ToggleNotificationAllowedView.as_view(), name="notifications-toggle-allowed"),

    path("oferta/", OfertaView.as_view(), name="oferta-detail"),

    *router.urls,

]
