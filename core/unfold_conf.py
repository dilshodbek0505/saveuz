UNFOLD = {
    "SITE_TITLE": "SaveUz Boshqaruv",
    "SITE_HEADER": "SaveUz",
    "SITE_NAME": "SaveUz",
    "SITE_URL": "https://saveuz.org/",
    "SITE_ICON": "speed",
    "SITE_LOGO": {
        "light": "/static/logo.png",
        "dark": "/static/logo.png",
    },
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": None,
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
        "redirect_after": None,
    },
    # "STYLES": [
    #     lambda request: "/static/css/unfold-custom.css",
    # ], # commentdan olinmasin
    "SCRIPTS": [],
    # THEME parametri bo'lmasa, Unfold default theme toggle button'ni ko'rsatadi
    # Foydalanuvchi header'dagi button orqali light/dark mode o'rtasida o'zgartirishi mumkin
    "COLORS": {
        "primary": {
            "50": "255 247 237",   # Very light orange
            "100": "255 237 213",  # Light orange
            "200": "255 220 177",  # Lighter orange
            "300": "255 195 130",  # Light-medium orange
            "400": "255 165 79",   # Medium orange
            "500": "255 140 0",    # Main orange (logo color)
            "600": "255 120 0",    # Darker orange
            "700": "255 100 0",    # Dark orange
            "800": "230 80 0",     # Very dark orange
            "900": "200 60 0",     # Darkest orange
            "950": "150 40 0",     # Almost black orange
        },
    },
    "DARK": {
        "primary": {
            "50": "150 40 0",      # Dark mode uchun
            "100": "200 60 0",
            "200": "230 80 0",
            "300": "255 100 0",
            "400": "255 120 0",
            "500": "255 140 0",    # Main orange (logo color)
            "600": "255 165 79",
            "700": "255 195 130",
            "800": "255 220 177",
            "900": "255 237 213",
            "950": "255 247 237",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "ru": "🇷🇺",
                "uz": "🇺🇿",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,  # Custom navigation ishlatamiz
        "navigation": [
            {
                "title": "Navigatsiya",
                "separator": True,
                "items": [
                    {
                        "title": "Bosh sahifa",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                        "permission": lambda request: request.user.is_staff,
                    },
                    {
                        "title": "Umumiy mahsulotlar",
                        "icon": "inventory",
                        "link": lambda request: "/admin/main/commonproduct/",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": "Mahsulotlar",
                        "icon": "inventory_2",
                        "link": lambda request: "/admin/main/product/",
                        "permission": lambda request: request.user.has_perm("main.view_product"),
                    },
                    {
                        "title": "Kategoriyalar",
                        "icon": "category",
                        "link": lambda request: "/admin/main/category/",
                        "permission": lambda request: request.user.has_perm("main.view_category"),
                    },
                    {
                        "title": "Do'konlar",
                        "icon": "store",
                        "link": lambda request: "/admin/main/market/",
                        "permission": lambda request: request.user.has_perm("main.view_market"),
                    },
                    {
                        "title": "Bannerlar",
                        "icon": "image",
                        "link": lambda request: "/admin/main/banner/",
                        "permission": lambda request: request.user.has_perm("main.view_banner"),
                    },
                    {
                        "title": "Chegirmalar",
                        "icon": "local_offer",
                        "link": lambda request: "/admin/main/discount/",
                        "permission": lambda request: request.user.has_perm("main.view_discount"),
                    },
                    {
                        "title": "Sevimlilar",
                        "icon": "bookmark",
                        "link": lambda request: "/admin/main/favorite/",
                        "permission": lambda request: request.user.has_perm("main.view_favorite"),
                    },
                    {
                        "title": "Bildirishnomalar",
                        "icon": "notifications",
                        "link": lambda request: "/admin/main/notification/",
                        "permission": lambda request: request.user.has_perm("main.view_notification"),
                    },
                    {
                        "title": "Foydalanuvchi bildirishnomalari",
                        "icon": "notifications_active",
                        "link": lambda request: "/admin/main/usernotification/",
                        "permission": lambda request: request.user.has_perm("main.view_usernotification"),
                    },
                    {
                        "title": "Oferta",
                        "icon": "description",
                        "link": lambda request: "/admin/main/oferta/",
                        "permission": lambda request: request.user.has_perm("main.view_oferta"),
                    },
                ],
            },
            {
                "title": "Autentifikatsiya",
                "separator": True,
                "items": [
                    {
                        "title": "Foydalanuvchilar",
                        "icon": "person",
                        "link": lambda request: "/admin/user/user/",
                        "permission": lambda request: request.user.has_perm("user.view_user"),
                    },
                    {
                        "title": "Guruhlar",
                        "icon": "group",
                        "link": lambda request: "/admin/auth/group/",
                        "permission": lambda request: request.user.has_perm("auth.view_group"),
                    },
                ],
            },
        ],
    },
    "TABS": [],
}

