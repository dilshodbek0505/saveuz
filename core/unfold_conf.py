UNFOLD = {
    "SITE_TITLE": "SaveUz Admin",
    "SITE_HEADER": "SaveUz",
    "SITE_URL": "/",
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
    "THEME": "auto",  # 'light', 'dark', yoki 'auto'
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
        "show_all_applications": True,
        "navigation": [],
    },
    "TABS": [],
}

