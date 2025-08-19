JAZZMIN_SETTINGS = {
    "site_title": "SaveUz Admin",
    "site_header": "SaveUz",
    "site_brand": "SaveUz",
    "site_logo": "logo.png",
    "login_logo": "logo.png",
    "site_logo_classes": "img-circle",
    "welcome_sign": "Welcome to SaveUz Admin",
    "copyright": "SaveUz Ltd",
    "search_model": ["auth.User", "main.Product"],

    ############
    # Top Menu #
    ############
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://t.me/saveuz_support", "new_window": True},
    ],

    #############
    # User Menu #
    #############
    "usermenu_links": [
        {"name": "Support", "url": "https://t.me/saveuz_support", "new_window": True},
        {"model": "auth.user"},
    ],

    #############
    # Side Menu #
    #############
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "auth",
        "main.banner",
        "main.category",
        "main.product",
        "main.discount",
        "main.market",
        "main.favorite",
    ],

    # Custom links qo'shish mumkin bo'lsa
    # "custom_links": {
    #     "main": [{
    #         "name": "Generate Report",
    #         "url": "generate_report",
    #         "icon": "fas fa-file-alt",
    #         "permissions": ["main.view_product"]
    #     }]
    # },

    # Side menu iconlar
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",

        "main.banner": "fas fa-image",
        "main.category": "fas fa-list",
        "main.product": "fas fa-box",
        "main.discount": "fas fa-percent",
        "main.market": "fas fa-store",
        "main.favorite": "fas fa-bookmark"
    },

    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs"
    },
    "language_chooser": True,
}
