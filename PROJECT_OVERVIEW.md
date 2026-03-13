# Saveuz — обзор проекта (бэкенд + мобильное приложение)

Единый проект: **бэкенд** (SaveuzBackend) и **мобильное приложение** (Save uz, Flutter). Каталог магазинов и товаров для Узбекистана (saveuz.uz), с авторизацией по телефону, избранным и уведомлениями.

---

## 1. Бэкенд (SaveuzBackend)

### 1.1 Технологии

| Компонент | Технология |
|-----------|------------|
| Фреймворк | Django 5.2 |
| API | Django REST Framework |
| БД | SQLite (по умолчанию) |
| Кэш/очереди | Redis, Celery |
| Админка | django-unfold |
| Документация API | drf-yasg (Swagger) — `/swagger/` |
| Локализация | django-modeltranslation (uz/ru/en) |
| Push-уведомления | Firebase (fcm-django), firebase_admin |
| SMS OTP | Eskiz (см. `apps/user/utils.py`) |
| Доп. | CORS, import_export, Pillow, python-environ |

### 1.2 Структура приложений

| Приложение | Путь | Назначение |
|------------|------|------------|
| **user** | `apps/user/` | Пользователи: авторизация по телефону (OTP), профиль, смена номера, удаление аккаунта. |
| **main** | `apps/main/` | Ядро: рынки, категории, товары, баннеры, избранное, уведомления, оферта. |
| **product** | `apps/product/` | Публичное API товаров: список, детали, поиск, фильтры. |
| **panel_admin** | `apps/panel_admin/` | Админское API: списки рынков/категорий, массовое создание товаров (по device token). |
| **bot** | `apps/bot/` | Telegram-бот (aiogram). |

### 1.3 Маршрутизация API (префикс `api/v1/`)

| Префикс | Приложение | Основные эндпоинты |
|---------|------------|--------------------|
| `api/v1/user/` | user | `auth/OTPSend/`, `auth/Login/`, `auth/Register/`, `auth/Logout/`, `profile/`, `profile/delete/`, `profile/PhoneNumberChangeSendOTP/`, `profile/PhoneNumberChangeVerify/` |
| `api/v1/main/` | main | `banner/BannerList/`, `category/CategoryList/`, `market/MarketList/`, `market/MarketDetail/<id>/`, `favorites/` (CRUD), `notifications/NotificationList/`, `notifications/ToggleNotificationAllowed/`, `oferta/` |
| `api/v1/product/` | product | `ProductList/`, `ProductDetail/<id>/` (query: `page`, `search`, `category_id`, `market_id`) |
| `api/v1/admin/` | panel_admin | `markets/`, `categories/`, `products/bulk-create/` (POST, по device token) |

Дополнительно: `admin/` — Django Unfold, `panel-admin/bulk-products/` — страница массового добавления товаров (HTML).

### 1.4 Аутентификация

- **REST API:** `SessionAuthentication` + **TokenAuthentication** (DRF).
- Токен создаётся при Login/Register, хранится на клиенте и передаётся в заголовке: `Authorization: Token <token>`.
- Пользователь: **phone_number** как USERNAME_FIELD; пароль не используется для входа (только OTP).

### 1.5 Основные модели (main)

| Модель | Ключевые поля |
|--------|----------------|
| **User** (user) | `phone_number`, `logo`, `notification_allowed`, `test_user`, `fcm_token`, `lang` |
| **Market** | `name`, `description`, `logo`, `lon`, `lat`, `address`, `open_time`, `end_time`, `owner` (FK → User) |
| **Category** | `name`, `image`, `parent` (self FK) |
| **Product** | `common_product` (FK, опционально), `name`, `price`, `description`, `market`, `category`, скидки (`discount_*`) |
| **ProductImage** | `product`, `image`, `position` |
| **Banner** | `name`, `image`, `position`, `is_active` |
| **Favorite** | `user`, `product` (опционально), `market` (опционально), `is_active`; уникальность (user, product) |
| **Notification** / **UserNotification** | Push: заголовок, тело, получатели, статус, связь с FCM |
| **Oferta** | `title`, `file`, `is_active` |

Моделей заказов/корзины/оплаты в проекте **нет** — только каталог и избранное.

### 1.6 Пагинация

- Класс: `core.pagination.StandardResultsSetPagination`.
- Размер страницы по умолчанию: 20, параметр `page_size` (макс. 100).

---

## 2. Мобильное приложение (Save uz — Flutter)

### 2.1 Технологии

- **Flutter** (Dart 3.x), Material 3, Google Fonts (Montserrat).
- **Хранение:** SharedPreferences (токен, онбординг, язык).
- **Сеть:** пакет `http`, один сервис — `ApiService` (baseUrl: `https://admin.saveuz.uz/api/v1`).
- **Локализация:** встроенная (l10n), языки uz/ru; заголовок `Accept-Language`: `uz-UZ` / `ru-RU`.
- **Карты:** Yandex MapKit.
- **Прочее:** deep links (app_links), маска ввода (mask_text_input_formatter), кэш картинок (cached_network_image), shimmer, share_plus.

### 2.2 Структура (lib/)

| Папка/файл | Содержимое |
|------------|------------|
| **main.dart** | Точка входа, инициализация локализации и токена, SplashScreen, обработка deep links (saveuz://product/id, saveuz.uz/product/id, market/id). |
| **services/api_service.dart** | Все запросы к API: OTP, Login, Register, профиль, баннеры, категории, рынки, товары, избранное, смена телефона. Fallback на IP при ошибках DNS/таймаута. Демо-токен для Apple Review. |
| **models/** | product.dart, market.dart, category.dart, banner.dart — fromJson/toJson под ответы API. |
| **screens/** | onboarding_screen, login/register/otp, main_screen (табы), home_page, categories_page, favourites_page, profile_page, product_single_page, market_single_page, map_page, notifications_page, edit_profile_page, change_phone_number_page и др. |
| **services/** | banner_store, category_store, market_store, market_list_store, product_list_store, favorites_store, register_service, localization_service, onboarding_service, city_service. |
| **widgets/** | bottom_nav_bar, banner_swiper, categories_block, markets_block, products_block, search_results_widget, home_header, language_selector, notification_button, custom_toast и др. |

### 2.3 Связь с бэкендом (какие эндпоинты использует приложение)

| Действие в приложении | Метод ApiService | Эндпоинт бэкенда |
|-----------------------|------------------|-------------------|
| Отправка OTP | `sendOTP(phone)` | `POST /user/auth/OTPSend/` |
| Вход | `login(phone, code)` | `POST /user/auth/Login/` |
| Регистрация | `register(firstName, phoneNumber, code, lastName?)` | `POST /user/auth/Register/` |
| Профиль | `getUserProfile()`, `updateUserProfile(...)` | `GET/PUT /user/profile/` |
| Смена телефона | `sendPhoneNumberChangeOTP`, `verifyPhoneNumberChange` | `POST /user/profile/PhoneNumberChangeSendOTP/`, `.../PhoneNumberChangeVerify/` |
| Баннеры | `getBannerList()` | `GET /main/banner/BannerList/` |
| Категории | `getCategoryList()` | `GET /main/category/CategoryList/` |
| Список магазинов (админский) | `getMarketList()` | `GET /admin/markets/` |
| Список магазинов (публичный) | `getMainMarketList(page, search)` | `GET /main/market/MarketList/` |
| Детали магазина | `getMarketDetail(id)` | `GET /main/market/MarketDetail/<id>/` |
| Список товаров | `getProductList(page, search, categoryId, marketId)` | `GET /product/ProductList/` |
| Детали товара | `getProductDetail(id)` | `GET /product/ProductDetail/<id>/` |
| Избранное | `getFavorites()`, `addToFavorites(productId/marketId)`, `removeFromFavorites(favoriteId)` | `GET/POST/DELETE /main/favorites/` |
| Категории (админ, если используется) | `getAdminCategoryList()` | `GET /admin/categories/` |

Токен после логина/регистрации сохраняется в ApiService и SharedPreferences и передаётся в заголовке `Authorization: Token <token>` для всех запросов, где нужна авторизация.

### 2.4 Особенности приложения

- **Демо для Apple:** тестовый телефон `+998 00 100-10-01`, OTP `1111`, захардкоженный токен для ревью.
- **Fallback на IP:** при DNS/таймауте запросы дублируются на `https://185.191.141.148/api/v1` с заголовком `Host: admin.saveuz.uz`.
- **Deep links:** открытие товара/магазина по ссылкам saveuz.uz/product/id, saveuz.uz/market/id и saveuz://product/id.
- **Стартовый экран:** если есть сохранённый токен — сразу MainScreen; иначе онбординг → MainScreen.

---

## 3. Общая схема взаимодействия

```
[Flutter App]  ←→  https://admin.saveuz.uz/api/v1  ←→  [Django]
                        Token в заголовке
                        Accept-Language: uz-UZ / ru-RU
```

- Пользователь вводит телефон → OTP через Eskiz → Login/Register → токен.
- Каталог: баннеры, категории, рынки, товары — с пагинацией и поиском/фильтрами.
- Избранное и профиль требуют токена; смена телефона — через OTP с бэкенда.
- Админ: Unfold в браузере; массовое добавление товаров — через panel_admin (device token) и страницу bulk-products.

---

## 4. Важные файлы для правок

**Бэкенд:**

- `core/settings.py` — настройки, CORS, DRF, пагинация, Firebase.
- `core/urls.py` — корневые маршруты и Swagger.
- `apps/user/views.py`, `apps/user/serializers` — авторизация и профиль.
- `apps/main/views/`, `apps/main/serializers/` — баннеры, категории, рынки, избранное, уведомления, оферта.
- `apps/product/views.py`, `apps/product/serializers.py` — список/детали товаров.
- `apps/panel_admin/views/` — админские списки и bulk-create.

**Приложение:**

- `lib/services/api_service.dart` — базовый URL и все вызовы API.
- `lib/main.dart` — инициализация, deep links, Splash.
- `lib/models/` — соответствие полей ответам API.

Этот файл можно использовать как единую точку входа при изучении и доработке проекта от А до Я.
