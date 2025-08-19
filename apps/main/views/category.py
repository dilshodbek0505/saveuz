from rest_framework.generics import ListAPIView

from apps.main.models import Category
from apps.main.serializers import CategorySerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer    

    def get_queryset(self):
        qs = super().get_queryset()
        
        parent_id = self.request.query_params.get("parent_id")
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
        else:
            qs = qs.filter(parent__isnull=True)
            
        return qs
        