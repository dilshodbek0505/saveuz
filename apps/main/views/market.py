from django.db.models import OuterRef, Exists

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import permissions

from apps.main.serializers import MarketSerializer
from apps.main.models import Market, Favorite


class MarketView(ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        
        owner_id = self.request.query_params.get("owner_id")
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        
        qs = qs.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    market=OuterRef('pk'),
                    user=user,
                    is_active=True,
                )
            )
        )

        return qs

class MarketDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MarketSerializer
    queryset = Market.objects.all()
    lookup_field = 'pk'


    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        qs = qs.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    market=OuterRef('pk'),
                    user=user,
                    is_active=True
                )
            )
        )

        return qs