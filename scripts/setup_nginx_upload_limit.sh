#!/bin/bash
# Скрипт для автоматической настройки nginx для загрузки больших файлов
# Использование: sudo bash scripts/setup_nginx_upload_limit.sh

set -e

echo "🔧 Настройка nginx для загрузки больших файлов..."

# Находим конфигурационный файл nginx для admin.saveuz.uz
NGINX_CONFIGS=(
    "/etc/nginx/sites-available/admin.saveuz.uz"
    "/etc/nginx/conf.d/admin.saveuz.uz.conf"
    "/etc/nginx/sites-enabled/admin.saveuz.uz"
)

NGINX_CONFIG=""
for config in "${NGINX_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        NGINX_CONFIG="$config"
        echo "✅ Найден конфиг: $config"
        break
    fi
done

if [ -z "$NGINX_CONFIG" ]; then
    echo "❌ Конфигурационный файл nginx не найден!"
    echo "Проверьте наличие файла в одном из мест:"
    for config in "${NGINX_CONFIGS[@]}"; do
        echo "  - $config"
    done
    exit 1
fi

# Создаем резервную копию
BACKUP_FILE="${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$NGINX_CONFIG" "$BACKUP_FILE"
echo "💾 Создана резервная копия: $BACKUP_FILE"

# Проверяем, есть ли уже настройка client_max_body_size
if grep -q "client_max_body_size" "$NGINX_CONFIG"; then
    echo "⚠️  Настройка client_max_body_size уже существует, обновляем..."
    # Обновляем существующую настройку до 20M
    sed -i 's/client_max_body_size[^;]*;/client_max_body_size 20M;/' "$NGINX_CONFIG"
else
    echo "➕ Добавляем настройки в блок server..."
    # Ищем строку с server_name admin.saveuz.uz или просто server_name
    if grep -q "server_name.*admin.saveuz.uz" "$NGINX_CONFIG"; then
        # Добавляем после server_name
        sed -i '/server_name.*admin.saveuz.uz/a\    client_max_body_size 20M;\n    client_body_timeout 60s;\n    client_header_timeout 60s;\n    client_body_buffer_size 128k;' "$NGINX_CONFIG"
    elif grep -q "^[[:space:]]*server_name" "$NGINX_CONFIG"; then
        # Добавляем после первого server_name
        sed -i '0,/^[[:space:]]*server_name/s//    client_max_body_size 20M;\n    client_body_timeout 60s;\n    client_header_timeout 60s;\n    client_body_buffer_size 128k;\n&/' "$NGINX_CONFIG"
    elif grep -q "^[[:space:]]*listen" "$NGINX_CONFIG"; then
        # Добавляем после первого listen
        sed -i '0,/^[[:space:]]*listen/s//    client_max_body_size 20M;\n    client_body_timeout 60s;\n    client_header_timeout 60s;\n    client_body_buffer_size 128k;\n&/' "$NGINX_CONFIG"
    else
        echo "❌ Не удалось найти место для вставки настроек в блоке server"
        echo "Пожалуйста, добавьте вручную в блок server:"
        echo "    client_max_body_size 20M;"
        echo "    client_body_timeout 60s;"
        echo "    client_header_timeout 60s;"
        echo "    client_body_buffer_size 128k;"
        exit 1
    fi
fi

# Проверяем и добавляем настройки прокси таймаутов в location /
if grep -q "location[[:space:]]\+/" "$NGINX_CONFIG"; then
    if ! grep -q "proxy_read_timeout" "$NGINX_CONFIG"; then
        echo "➕ Добавляем настройки таймаутов прокси в location /..."
        # Добавляем после proxy_set_header или proxy_pass в location /
        if grep -q "proxy_pass" "$NGINX_CONFIG"; then
            sed -i '/proxy_pass/a\        proxy_connect_timeout 60s;\n        proxy_send_timeout 60s;\n        proxy_read_timeout 60s;' "$NGINX_CONFIG"
        elif grep -q "proxy_set_header" "$NGINX_CONFIG"; then
            # Добавляем после последнего proxy_set_header в location /
            sed -i '/location[[:space:]]\+\//,/^[[:space:]]*}/ { /proxy_set_header[^}]*$/a\        proxy_connect_timeout 60s;\n        proxy_send_timeout 60s;\n        proxy_read_timeout 60s; }' "$NGINX_CONFIG" || \
            sed -i '/proxy_set_header Host/a\        proxy_connect_timeout 60s;\n        proxy_send_timeout 60s;\n        proxy_read_timeout 60s;' "$NGINX_CONFIG"
        fi
    else
        echo "✅ Настройки таймаутов прокси уже существуют"
    fi
fi

# Проверяем синтаксис nginx
echo "🔍 Проверка синтаксиса nginx..."
if nginx -t; then
    echo "✅ Синтаксис nginx корректен"
    
    # Перезагружаем nginx
    echo "🔄 Перезагрузка nginx..."
    if systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null; then
        echo "✅ Nginx успешно перезагружен"
        echo ""
        echo "🎉 Настройка завершена успешно!"
        echo "Теперь можно загружать файлы до 20MB"
    else
        echo "⚠️  Не удалось перезагрузить nginx автоматически"
        echo "Выполните вручную: sudo systemctl reload nginx"
    fi
else
    echo "❌ Ошибка в синтаксисе nginx!"
    echo "Восстанавливаем резервную копию..."
    cp "$BACKUP_FILE" "$NGINX_CONFIG"
    exit 1
fi
