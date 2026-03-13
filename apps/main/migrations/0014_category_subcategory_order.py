# Generated manually for subcategories (order field + Meta ordering)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0013_market_cascade_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="O'zaro tartib (kichik raqam birinchi).",
                verbose_name="Tartib",
            ),
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ["parent_id", "order", "name"],
                "verbose_name": "Kategoriya",
                "verbose_name_plural": "Kategoriyalar",
            },
        ),
    ]
