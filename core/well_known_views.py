"""
Views для Universal Links / App Links верификации.
Отдаёт apple-app-site-association (iOS) и assetlinks.json (Android),
чтобы ссылки https://saveuz.uz/product/{id} и /market/{id} открывали приложение.
"""
import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings


def _setting(name: str, default: str) -> str:
    return os.environ.get(name) or getattr(settings, name, default) or default


# iOS: Bundle ID из мобильного приложения (uz.saveuz.saveUz)
IOS_APP_BUNDLE_ID = _setting("DEEP_LINK_IOS_BUNDLE_ID", "uz.saveuz.saveUz")
# iOS: Team ID из Apple Developer (775STZ7YSD — из Xcode проекта)
IOS_TEAM_ID = _setting("DEEP_LINK_IOS_TEAM_ID", "775STZ7YSD")

# Android: package name (uz.saveuz.app)
ANDROID_PACKAGE = _setting("DEEP_LINK_ANDROID_PACKAGE", "uz.saveuz.app")
# Android: SHA-256 отпечаток signing certificate (заменить на свой из keytool -list -v -keystore ...)
ANDROID_SHA256_FINGERPRINT = _setting(
    "DEEP_LINK_ANDROID_SHA256",
    "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00",
)


@require_GET
@csrf_exempt
@xframe_options_exempt
def apple_app_site_association(request):
    """
    https://saveuz.uz/.well-known/apple-app-site-association
    Без расширения .json — так требует Apple.
    """
    content = {
        "applinks": {
            "apps": [],
            "details": [
                {
                    "appID": f"{IOS_TEAM_ID}.{IOS_APP_BUNDLE_ID}",
                    "paths": [
                        "/product/*",
                        "/market/*",
                    ],
                },
            ],
        },
    }
    return HttpResponse(
        json.dumps(content, separators=(",", ":")),
        content_type="application/json",
    )


@require_GET
@csrf_exempt
@xframe_options_exempt
def asset_links_json(request):
    """
    https://saveuz.uz/.well-known/assetlinks.json
    Для Android App Links. SHA256 отпечаток нужно заменить на реальный.
    """
    # Убираем двоеточия из отпечатка для формата assetlinks
    sha256 = ANDROID_SHA256_FINGERPRINT.replace(":", "").lower()

    content = [
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": ANDROID_PACKAGE,
                "sha256_cert_fingerprints": [sha256],
            },
        },
    ]
    return JsonResponse(content, safe=False)
