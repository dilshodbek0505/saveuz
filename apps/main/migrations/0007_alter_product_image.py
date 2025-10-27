from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_notification_usernotification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="product_images/",
                verbose_name="Image",
            ),
        ),
    ]

