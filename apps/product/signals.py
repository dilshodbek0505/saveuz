from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal

from apps.main.models import Discount, Product


@receiver(post_save, sender=Discount)
def discount_product(sender, instance, created, **kwargs):
    if not instance.is_active:
        try:
            product = instance.product
            product.discount_price = None
            product.discount_type = None
            product.discount_value = None
            product.save()
        except Exception as err:
            print("Xatolik: {}".format(str(err)))

        return
    
    try:
        product = instance.product
        product.discount_value = instance.value
        product.discount_type = instance.type
        if instance.type == Discount.DiscountType.PERCENTAGE:
            discount_amount = (product.price * instance.value) / Decimal("100")
            product.discount_price = product.price - discount_amount                
        else:
            product.discount_price = instance.value
        product.save()

    except Exception as err:
        print("Xatolik: {}".format(str(err)))


@receiver(post_delete, sender=Discount)
def delete_discount_product(sender, instance, **kwargs):
    try:
        product = instance.product
        product.discount_price = None
        product.discount_type = None
        product.discount_value = None
        product.save()
    except Exception as err:
        print("Xatolik: {}".format(str(err)))