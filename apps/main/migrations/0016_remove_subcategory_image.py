# Remove image field from Subcategory

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0015_subcategory_product_subcategory_commonproduct_subcategory"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subcategory",
            name="image",
        ),
    ]
