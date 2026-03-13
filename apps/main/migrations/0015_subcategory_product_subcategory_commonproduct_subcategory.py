# Generated manually for Subcategory model and subcategory FK on Product/CommonProduct

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0014_category_subcategory_order"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subcategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=128, verbose_name="Nomi")),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="subcategory_images/", verbose_name="Rasm"),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="O'zaro tartib (kichik raqam birinchi).",
                        verbose_name="Tartib",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="subcategories",
                        to="main.category",
                        verbose_name="Kategoriya",
                    ),
                ),
            ],
            options={
                "verbose_name": "Subkategoriya",
                "verbose_name_plural": "Subkategoriyalar",
                "ordering": ["category", "order", "name"],
            },
        ),
        migrations.AddField(
            model_name="commonproduct",
            name="subcategory",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="common_products",
                to="main.subcategory",
                verbose_name="Subkategoriya",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="subcategory",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="main.subcategory",
                verbose_name="Subkategoriya",
            ),
        ),
    ]
