# Настройка nginx для загрузки больших файлов

## Проблема
Ошибка `413 Request Entity Too Large` возникает, когда размер загружаемых файлов превышает лимит nginx (по умолчанию 1MB).

## Решение

### 1. Найдите конфигурационный файл nginx для admin.saveuz.uz

Обычно находится в:
- `/etc/nginx/sites-available/admin.saveuz.uz`
- `/etc/nginx/conf.d/admin.saveuz.uz.conf`
- или в основном конфиге `/etc/nginx/nginx.conf`

### 2. Добавьте/измените следующие настройки в блоке `server`:

```nginx
server {
    listen 80;
    server_name admin.saveuz.uz;

    # Увеличиваем лимит размера тела запроса до 20MB
    client_max_body_size 20M;
    
    # Увеличиваем таймауты для больших загрузок
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Буферизация для больших файлов
    client_body_buffer_size 128k;

    location / {
        proxy_pass http://127.0.0.1:8000;  # ваш порт Django
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличиваем таймауты прокси
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 3. Проверьте конфигурацию и перезапустите nginx:

```bash
# Проверка синтаксиса
sudo nginx -t

# Перезапуск nginx
sudo systemctl reload nginx
# или
sudo service nginx reload
```

### 4. Проверка

После настройки попробуйте загрузить изображение размером до 5MB (лимит в Django) или несколько изображений общим размером до 20MB.

## Примечания

- `client_max_body_size 20M` - позволяет загружать файлы до 20MB
- Если нужно больше, увеличьте значение (например, `50M` или `100M`)
- Убедитесь, что Django настройки `DATA_UPLOAD_MAX_MEMORY_SIZE` и `FILE_UPLOAD_MAX_MEMORY_SIZE` также увеличены (уже настроено в `settings.py`)
