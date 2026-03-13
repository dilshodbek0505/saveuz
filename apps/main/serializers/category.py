from rest_framework import serializers

from apps.main.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Плоский список категорий с parent и order для построения дерева на клиенте."""

    parent = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "image",
            "parent",
            "order",
        )


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Вложенное дерево: каждая категория может содержать children."""

    parent = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "image",
            "parent",
            "order",
            "children",
        )

    def get_children(self, obj):
        # Используем prefetched children если есть, иначе запрос
        children = getattr(obj, "_prefetched_children", None)
        if children is None:
            children = obj.children.all().order_by("order", "name")
        return CategoryTreeSerializer(children, many=True, context=self.context).data
