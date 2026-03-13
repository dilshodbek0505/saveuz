#!/bin/bash
# Запустить на сервере: bash scripts/check_deploy_speed.sh
# Показывает, что может тормозить деплой

echo "=== 1. Нагрузка и ресурсы ==="
uptime
echo ""
echo "CPU: $(nproc) cores"
free -h
echo ""
df -h /var/www/saveuz 2>/dev/null || df -h /

echo ""
echo "=== 2. Размер venv и кэша pip ==="
du -sh /var/www/saveuz/venv 2>/dev/null || echo "venv not found"
du -sh /var/www/saveuz/.pip-cache 2>/dev/null || echo ".pip-cache not found"
du -sh /var/www/saveuz/staticfiles 2>/dev/null || echo "staticfiles not found"

echo ""
echo "=== 3. Время ключевых операций (примерно) ==="
cd /var/www/saveuz || exit 1
source venv/bin/activate 2>/dev/null || true

echo -n "pip install (dry): "
time (pip install -r requirements.txt --dry-run 2>/dev/null | tail -1) 2>&1 || echo "skip"

echo -n "collectstatic: "
time (python manage.py collectstatic --noinput --dry-run 2>/dev/null | tail -3) 2>&1 || \
  time (python manage.py collectstatic --noinput 2>&1 | tail -3) 2>&1

echo ""
echo "=== 4. Количество статических файлов ==="
find /var/www/saveuz/staticfiles -type f 2>/dev/null | wc -l

echo ""
echo "=== 5. Последние логи runner (если есть) ==="
journalctl -u actions.runner.* -n 20 --no-pager 2>/dev/null || echo "No systemd runner logs"
# Или логи в домашней папке runner:
ls -la /var/www/saveuz/_diag 2>/dev/null || true
