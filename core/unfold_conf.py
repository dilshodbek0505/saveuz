UNFOLD = {
    "SITE_TITLE": "SaveUz Admin",
    "SITE_HEADER": "SaveUz",
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
    "STYLES": [
        lambda request: "/static/css/unfold-custom.css",
    ],
    "SCRIPTS": [],
    "THEME": "auto",  # 'light', 'dark', yoki 'auto' - foydalanuvchi tizim sozlamalariga moslashadi
    "SHOW_THEME_TOGGLE": True,  # Theme toggle button'ni ko'rsatish
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
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                    },
                    {
                        "title": "Products",
                        "icon": "inventory_2",
                        "link": lambda request: "/admin/main/product/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": lambda request: "/admin/main/category/",
                    },
                    {
                        "title": "Markets",
                        "icon": "store",
                        "link": lambda request: "/admin/main/market/",
                    },
                    {
                        "title": "Banners",
                        "icon": "image",
                        "link": lambda request: "/admin/main/banner/",
                    },
                    {
                        "title": "Discounts",
                        "icon": "local_offer",
                        "link": lambda request: "/admin/main/discount/",
                    },
                    {
                        "title": "Favorites",
                        "icon": "bookmark",
                        "link": lambda request: "/admin/main/favorite/",
                    },
                    {
                        "title": "Notifications",
                        "icon": "notifications",
                        "link": lambda request: "/admin/main/notification/",
                    },
                    {
                        "title": "User Notifications",
                        "icon": "notifications_active",
                        "link": lambda request: "/admin/main/usernotification/",
                    },
                    {
                        "title": "Oferta",
                        "icon": "description",
                        "link": lambda request: "/admin/main/oferta/",
                    },
                ],
            },
            {
                "title": "Authentication",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": lambda request: "/admin/user/user/",
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": lambda request: "/admin/auth/group/",
                    },
                ],
            },
        ],
    },
    "TABS": [],
}

