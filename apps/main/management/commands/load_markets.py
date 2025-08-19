import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.main.models import Market


class Command(BaseCommand):
    help = "Import categories from category.json and file.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category_file", type=str, default="db_files/market.json",
            help="Path to category.json"
        )
        parser.add_argument(
            "--file_file", type=str, default="db_files/file.json",
            help="Path to file.json"
        )

    def handle(self, *args, **options):
        category_path = options["category_file"]
        file_path = options["file_file"]

        if not os.path.exists(category_path):
            self.stderr.write(self.style.ERROR(f"{category_path} not found"))
            return
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"{file_path} not found"))
            return

        # fayllarni o‘qish
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = {item["id"]: item for item in json.load(f)}

        with open(category_path, "r", encoding="utf-8") as f:
            categories = json.load(f)

        self.stdout.write(self.style.NOTICE(f"{len(categories)} categories found."))

        for cat in categories:
            image_id = cat.get("logo_id")
            file_obj = file_data.get(image_id)
            if not file_obj:
                self.stderr.write(
                    self.style.WARNING(f"No image found for category {cat['name']} (image_id={image_id})")
                )
                continue

            image_path = os.path.join(file_obj["file"])

            category, created = Market.objects.update_or_create(
                id=cat["id"],
                name=cat["name"],
                lon=cat["lon"],
                lat=cat["lat"],
                open_time=cat["start_time"],
                end_time=cat["end_time"],
                owner_id=1,
                description=cat["description"],
                defaults={
                    "logo": image_path,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated category: {category.name}"))

        self.stdout.write(self.style.SUCCESS("Import finished."))
