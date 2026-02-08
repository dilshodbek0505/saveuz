from django.db.models import OuterRef, Exists, Count

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import permissions

from apps.main.serializers import MarketSerializer
from apps.main.models import Market, Favorite


class MarketView(ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        
        owner_id = self.request.query_params.get("owner_id")
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        
        if user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        market=OuterRef('pk'),
                        user=user,
                        is_active=True,
                    )
                )
            )
        else:
            qs = qs.annotate(is_favorited=Count("id") * 0)

        return qs

class MarketDetailView(RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MarketSerializer
    queryset = Market.objects.all()
    lookup_field = 'pk'


    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        market=OuterRef('pk'),
                        user=user,
                        is_active=True
                    )
                )
            )
        else:
            qs = qs.annotate(is_favorited=Count("id") * 0)

        return qs
