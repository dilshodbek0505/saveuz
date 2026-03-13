#!/bin/bash
# Проверка статуса GitHub Actions runner на сервере
# Запуск: bash scripts/runner_status.sh (локально через SSH) или на сервере

RUNNER_DIR="/opt/actions-runner/runner"

echo "=== GitHub Actions Runner Status ==="
echo ""

if [ ! -d "$RUNNER_DIR" ]; then
    echo "❌ Runner NOT installed at $RUNNER_DIR"
    echo ""
    echo "Run: bash scripts/setup_github_runner.sh"
    exit 1
fi

echo "1. Service status:"
cd "$RUNNER_DIR"
./svc.sh status 2>/dev/null || echo "   (svc not configured)"
echo ""

echo "2. Systemd status:"
systemctl status actions.runner.* 2>/dev/null | head -15 || echo "   No systemd service"
echo ""

echo "3. Recent logs:"
journalctl -u "actions.runner.*" -n 20 --no-pager 2>/dev/null || echo "   No logs"
echo ""

echo "4. Runner process:"
ps aux | grep -E "Runner.Listener|actions-runner" | grep -v grep || echo "   No runner process"
echo ""

echo "5. Network (GitHub connectivity):"
curl -s -o /dev/null -w "   github.com: %{http_code} in %{time_total}s\n" --connect-timeout 5 https://github.com || echo "   Failed to reach GitHub"
