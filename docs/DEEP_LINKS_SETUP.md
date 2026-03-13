# Настройка Deep Links («Поделиться» → открытие приложения)

Чтобы ссылки из «Поделиться» (Telegram и др.) открывали приложение и вели на нужный товар/магазин, нужны Universal Links (iOS) и App Links (Android).

## Домены

| Назначение | Домен |
|------------|--------|
| **Фронтенд (сайт, ссылки для шаринга)** | https://www.saveuz.org/ |
| **Бэкенд (API, админка)** | https://admin.saveuz.uz/ |

В приложении при «Поделиться» отправляются ссылки вида:
- `https://www.saveuz.org/product/{id}`
- `https://www.saveuz.org/market/{id}`

Чтобы по ним открывалось приложение (а не только сайт), файлы верификации **должны отдаваться с домена saveuz.org** (фронтенд), т.к. именно этот домен указан в ссылках.

## Что уже сделано

- **Приложение (Save uz):** шаринг использует `https://www.saveuz.org/product/{id}` и `.../market/{id}`. В приложении настроены Associated Domains (iOS) и App Links (Android) для **saveuz.org** и **www.saveuz.org**.
- **Бэкенд (admin.saveuz.uz):** отдаёт файлы верификации по путям:
  - `/.well-known/apple-app-site-association` (iOS)
  - `/.well-known/assetlinks.json` (Android)

Их можно использовать как источник содержимого для фронтенда (см. ниже).

## Что нужно сделать

### 1. Раздача .well-known с домена saveuz.org (фронтенд)

Файлы верификации должны быть доступны по адресам:

- `https://saveuz.org/.well-known/apple-app-site-association`
- `https://saveuz.org/.well-known/assetlinks.json`
- `https://www.saveuz.org/.well-known/apple-app-site-association`
- `https://www.saveuz.org/.well-known/assetlinks.json`

**Готовые файлы:** в репозитории есть папка `docs/well-known-for-frontend/` с файлами `apple-app-site-association` и `assetlinks.json`. Скопируйте их в проект фронтенда в папку `public/.well-known/` (см. README в той папке).

**Другие варианты:**

1. **Прокси с фронта на бэкенд**  
   На сервере/хостинге, где крутится **saveuz.org**, настроить проксирование:
   - запросы к `/.well-known/apple-app-site-association` → `https://admin.saveuz.uz/.well-known/apple-app-site-association`
   - запросы к `/.well-known/assetlinks.json` → `https://admin.saveuz.uz/.well-known/assetlinks.json`

2. **Статика на фронте**  
   Сгенерировать два файла (один раз взять содержимое по ссылкам с admin.saveuz.uz ниже) и раздавать их на saveuz.org как статику по путям `/.well-known/...`.

После этого iOS и Android смогут верифицировать домен saveuz.org для приложения.

### 2. Android: SHA-256 отпечаток

В бэкенде в `core/well_known_views.py` по умолчанию подставлена заглушка для SHA256. Нужно указать отпечаток **release** keystore приложения:

```bash
keytool -list -v -keystore your-release-key.keystore -alias your-key-alias
```

Скопировать **SHA256** и задать в настройках бэкенда или в переменных окружения:

```python
# В settings.py
DEEP_LINK_ANDROID_SHA256 = "AB:CD:EF:..."
```

или

```env
DEEP_LINK_ANDROID_SHA256=AB:CD:EF:...
```

Тогда бэкенд (и прокси/статика на saveuz.org) будут отдавать правильный `assetlinks.json`.

### 3. Опционально: настройки в Django

При отличии bundle id / team id / package переопределите в `settings.py` или через env:

```python
DEEP_LINK_IOS_BUNDLE_ID = "uz.saveuz.saveUz"
DEEP_LINK_IOS_TEAM_ID = "775STZ7YSD"
DEEP_LINK_ANDROID_PACKAGE = "uz.saveuz.app"
DEEP_LINK_ANDROID_SHA256 = "..."  # см. выше
```

## Проверка

- **С бэкенда:** открыть в браузере  
  `https://admin.saveuz.uz/.well-known/apple-app-site-association` и  
  `https://admin.saveuz.uz/.well-known/assetlinks.json` — должны вернуться нужные JSON.
- **С фронта (после настройки):** то же содержимое по  
  `https://www.saveuz.org/.well-known/apple-app-site-association` и  
  `https://www.saveuz.org/.well-known/assetlinks.json`.
- **В приложении:** поделиться товаром/магазином в Telegram, перейти по ссылке — должно открыться приложение на нужном экране.
