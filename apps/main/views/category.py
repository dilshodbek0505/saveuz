from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.main.models import Category
from apps.main.serializers import CategorySerializer
from apps.main.serializers.category import CategoryTreeSerializer


class CategoryView(ListAPIView):
    """Список категорий. parent_id — фильтр по родителю; tree=1 — дерево с вложенными children."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        parent_id = self.request.query_params.get("parent_id")
        if parent_id is not None:
            if parent_id == "" or parent_id == "null":
                qs = qs.filter(parent__isnull=True)
            else:
                qs = qs.filter(parent_id=parent_id)
        else:
            qs = qs.filter(parent__isnull=True)
        return qs.order_by("order", "name")

    def get_serializer_class(self):
        if self.request.query_params.get("tree") == "1":
            return CategoryTreeSerializer
        return CategorySerializer

    def list(self, request, *args, **kwargs):
        if request.query_params.get("tree") != "1":
            return super().list(request, *args, **kwargs)
        # Полное дерево: один запрос, собираем в памяти, отдаём корни с вложенными children
        qs = Category.objects.order_by("parent_id", "order", "name")
        all_cats = list(qs)
        by_parent = {}
        for c in all_cats:
            pid = c.parent_id if c.parent_id is not None else 0
            if pid not in by_parent:
                by_parent[pid] = []
            by_parent[pid].append(c)
        for c in all_cats:
            c._prefetched_children = by_parent.get(c.pk, [])
        roots = by_parent.get(0, [])
        serializer = CategoryTreeSerializer(roots, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
