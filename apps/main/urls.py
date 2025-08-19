from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.main.views import BannerView, CategoryView, MarketView \
                            ,FavoriteViewSet


router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorites')


urlpatterns = [
    path("banner/BannerList/", BannerView.as_view(), name="banner-list"),
    path("category/CategoryList/", CategoryView.as_view(), name="category-list"),
    path("market/MarketList/", MarketView.as_view(), name="market-list"),

    *router.urls,

]
