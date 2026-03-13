from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.main.models import Subcategory
from apps.main.serializers.subcategory import SubcategorySerializer


class SubcategoryListView(ListAPIView):
    """Список субкатегорий по category_id. Без category_id — пустой список."""

    permission_classes = [AllowAny]
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        category_id = self.request.query_params.get("category_id")
        if not category_id:
            return Subcategory.objects.none()
        try:
            return Subcategory.objects.filter(category_id=int(category_id)).order_by(
                "order", "name"
            )
        except (ValueError, TypeError):
            return Subcategory.objects.none()
