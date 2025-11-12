import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.main.models import Product, ProductImage


class Command(BaseCommand):
    help = "Import Products from product.json and file.json and market_product.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--product_file", type=str, default="db_files/product.json",
            help="Path to product.json"
        )
        parser.add_argument(
            "--file_file", type=str, default="db_files/file.json",
            help="Path to file.json"
        )
        parser.add_argument(
            "--market_product_file", type=str, default="db_files/market_product.json",
            help="Path to market_product.json"
        )
        parser.add_argument(
            "--product_images_file", type=str, default="db_files/product_images.json",
            help="Path to product_images.json"
        )

    def handle(self, *args, **options):
        product_path = options["product_file"]
        file_path = options["file_file"]
        market_product_path = options["market_product_file"]
        product_images_path = options["product_images_file"]

        if not os.path.exists(product_path):
            self.stderr.write(self.style.ERROR(f"{product_path} not found"))
            return
        
        if not os.path.exists(product_images_path):
            self.stderr.write(self.style.ERROR(f"{product_images_path} not found"))
            return

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"{file_path} not found"))
            return
        
        if not os.path.exists(market_product_path):
            self.stderr.write(self.style.ERROR(f"{market_product_path} not found"))
            return

        # fayllarni o‘qish
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = {item["id"]: item for item in json.load(f)}

        with open(product_path, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        with open(market_product_path, "r", encoding="utf-8") as f:
            market_products = json.load(f)
        
        with open(product_images_path, "r", encoding="utf-8") as f:
            product_images = json.load(f)

        self.stdout.write(self.style.NOTICE(f"{len(products)} products found."))
        self.stdout.write(self.style.NOTICE(f"{len(market_products)} market products found."))

        for product in products:
            product_image_id = None
            for image in product_images:
                if product['id'] == image.get("product_id"):
                    product_image_id = image.get("file_id")
                    break
    
    
            file_obj = file_data.get(product_image_id)
            if not file_obj:
                self.stderr.write(
                    self.style.WARNING(f"No image found for category {product['name']} (image_id={product_image_id})")
                )
                continue

            image_path = os.path.join(file_obj["file"])
            
            
            market_product = None
    
            for market_product_item in market_products:
                if int(market_product_item["product_id"]) == int(product['id']):
                    market_product = market_product_item
                    break
        
            if not market_product:
                continue
                
            try:
                product_instance = Product.objects.create(
                    id=product['id'],
                    name=product['name'],
                    description="description",
                    price=market_product["base_price"],
                    market_id=market_product["market_id"],
                    category_id=product["category_id"],

                )
                ProductImage.objects.create(
                    product=product_instance,
                    image=image_path,
                    position=0,
                )
                self.stdout.write(self.style.SUCCESS(f"Created category: {product_instance.name}"))
            except Exception as err:
                pass
            

        self.stdout.write(self.style.SUCCESS("Import finished."))
