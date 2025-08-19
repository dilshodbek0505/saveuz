from rest_framework.generics import ListAPIView

from apps.main.models import Banner
from apps.main.serializers import BannerSerializer


class BannerView(ListAPIView):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer