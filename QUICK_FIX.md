# Быстрое решение ошибки 413 Request Entity Too Large

## Автоматическое решение (рекомендуется)

Запустите скрипт на сервере:

```bash
cd /var/www/saveuz
sudo bash scripts/setup_nginx_upload_limit.sh
```

Скрипт автоматически:
- Найдет конфиг nginx
- Создаст резервную копию
- Добавит необходимые настройки
- Проверит синтаксис
- Перезагрузит nginx

## Ручное решение

Если скрипт не работает, выполните вручную:

### 1. Найдите конфиг nginx:
```bash
sudo find /etc/nginx -name "*admin.saveuz*" -o -name "*saveuz*"
```

### 2. Откройте конфиг:
```bash
sudo nano /etc/nginx/sites-available/admin.saveuz.uz
# или
sudo nano /etc/nginx/conf.d/admin.saveuz.uz.conf
```

### 3. Добавьте в блок `server` (после `server_name` или `listen`):
```nginx
client_max_body_size 20M;
client_body_timeout 60s;
client_header_timeout 60s;
client_body_buffer_size 128k;
```

### 4. В блоке `location /` добавьте (если их нет):
```nginx
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

### 5. Проверьте и перезагрузите:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Проверка

После настройки попробуйте загрузить изображение в админке. Ошибка 413 должна исчезнуть.
