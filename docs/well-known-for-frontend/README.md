# Файлы для фронтенда (saveuz.org)

Скопируйте эти два файла в проект фронтенда так, чтобы они отдавались по адресам:

- `https://www.saveuz.org/.well-known/apple-app-site-association`
- `https://www.saveuz.org/.well-known/assetlinks.json`

## Куда класть

- **Next.js:** в папку `public/.well-known/` (создайте `.well-known`, положите туда оба файла).
- **Vite / Create React App:** в `public/.well-known/`.
- **Другой статический хостинг:** загрузите папку `.well-known` в корень сайта.

Итоговая структура на фронте:

```
public/
  .well-known/
    apple-app-site-association   ← без расширения .json
    assetlinks.json
```

## Android: заменить SHA256 в assetlinks.json

В файле `assetlinks.json` замените значение в `sha256_cert_fingerprints` (сейчас там нули) на реальный SHA-256 отпечаток вашего release-ключа **без двоеточий**, 64 символа, в нижнем регистре.

Как получить:

```bash
keytool -list -v -keystore your-release-key.keystore -alias your-alias
```

Скопируйте строку **SHA256** (например `AB:CD:EF:12:...`) и вставьте в JSON **без двоеточий**, маленькими буквами: `abcdef12...`.

После замены ссылки вида `https://www.saveuz.org/product/123` будут открывать приложение на устройстве.
