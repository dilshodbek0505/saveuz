from rest_framework.generics import ListAPIView

from apps.main.serializers import MarketSerializer
from apps.main.models import Market


class MarketView(ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        
        owner_id = self.request.query_params.get("owner_id")
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        
        return qs
    