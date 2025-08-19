from import_export import resources
from apps.main.models import Product


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'discount_price', 'discount_type', 'discount_value', 'category', 'market')
        export_order = ('id', 'name', 'price', 'discount_price', 'discount_type', 'discount_value', 'category', 'market')
