from rest_framework import viewsets, permissions
from rest_framework.generics import mixins
from apps.main.models import Favorite
from apps.main.serializers import FavoriteSerializer


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # faqat login bo'lgan userning favoritlari
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
