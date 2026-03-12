#!/usr/bin/env python
"""Создать пользователя-владельца магазина и выдать только нужные права."""
import os
import sys
from datetime import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.core.files.base import ContentFile
from django.contrib.auth.models import Permission
from apps.user.models import User
from apps.main.models import Market

PHONE = "998901234567"
PASSWORD = "marketowner1"

# Только права, нужные владельцу магазина (свои магазины, товары, скидки, просмотр категорий)
MARKET_OWNER_PERMISSION_CODENAMES = [
    "main.view_market",
    "main.add_market",
    "main.change_market",
    "main.delete_market",
    "main.view_product",
    "main.add_product",
    "main.change_product",
    "main.delete_product",
    "main.view_discount",
    "main.add_discount",
    "main.change_discount",
    "main.delete_discount",
    "main.view_category",  # только просмотр — для выбора категории при создании товара
]

user, created = User.objects.get_or_create(
    phone_number=PHONE,
    defaults={"is_staff": True, "is_superuser": False},
)
user.is_staff = True
user.is_superuser = False
user.set_password(PASSWORD)
user.save()

# Убираем все группы и все старые права
user.groups.clear()
user.user_permissions.clear()

# Выдаём только нужные права (только main: магазины, товары, скидки, просмотр категорий)
perms = Permission.objects.filter(
    content_type__app_label="main",
    codename__in=["view_market", "add_market", "change_market", "delete_market",
                  "view_product", "add_product", "change_product", "delete_product",
                  "view_discount", "add_discount", "change_discount", "delete_discount",
                  "view_category"],
)
user.user_permissions.set(perms)
user.save()

markets = Market.objects.all()
if markets.exists():
    m = markets.first()
    m.owner = user
    m.save()
    print("Market assigned:", m.name, "(id=%s)" % m.id)
else:
    logo_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f"
        b"\x00\x00\x01\x01\x00\x05\x18\xd8n\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    m = Market(
        name="Mening do'konim",
        description="Demo do'kon",
        lon=69.2,
        lat=41.3,
        open_time=time(9, 0),
        end_time=time(18, 0),
        owner=user,
    )
    m.logo.save("logo.png", ContentFile(logo_png), save=False)
    m.save()
    print("Market created:", m.name, "(id=%s)" % m.id)

print("---")
print("Login (владелец магазина):")
print("  Telefon raqami:", PHONE)
print("  Parol:         ", PASSWORD)
print("  URL:            http://127.0.0.1:8000/admin/")
