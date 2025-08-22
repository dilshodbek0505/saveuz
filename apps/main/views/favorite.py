from rest_framework import viewsets, permissions
from rest_framework.generics import mixins
from apps.main.models import Favorite
from apps.main.serializers import FavoriteSerializer


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Favorite.objects.filter(is_active=True)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        qs = qs.order_by('-updated_at')
        return qs

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")
        market = serializer.validated_data.get("market")

        favorite = Favorite.objects.filter(
            user=self.request.user,
            product=product,
            market=market
        ).first()

        if favorite:
            favorite.is_active = not favorite.is_active
            favorite.save(update_fields=['is_active',])
        else:        
            serializer.save(user=self.request.user)
