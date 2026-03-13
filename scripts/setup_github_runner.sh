#!/bin/bash
# =============================================================================
# GitHub Actions Self-Hosted Runner — установка на сервер Saveuz
# =============================================================================
# Запуск: скопируй на сервер и выполни:
#   chmod +x setup_github_runner.sh
#   ./setup_github_runner.sh
#
# Вариант 1 — с PAT (рекомендуется, автоматически):
#   export RUNNER_CFG_PAT="ghp_xxxxxxxxxxxx"   # GitHub Personal Access Token
#   ./setup_github_runner.sh
#
# Вариант 2 — без PAT (вручную):
#   ./setup_github_runner.sh
#   Затем выполни команды, которые выведет скрипт (токен возьми в GitHub)
# =============================================================================

set -e

# Требуется root для /opt и systemd
[ "$(id -u)" -eq 0 ] || { echo "Run as root: sudo $0"; exit 1; }

REPO="dilshodbek0505/saveuz"
RUNNER_DIR="/opt/actions-runner"
RUNNER_USER="root"   # или создай отдельного пользователя для безопасности

# -----------------------------------------------------------------------------
# 1. Проверка зависимостей
# -----------------------------------------------------------------------------
echo "[1/6] Checking dependencies..."
for cmd in curl jq; do
    if ! command -v $cmd &>/dev/null; then
        echo "Installing $cmd..."
        apt-get update -qq && apt-get install -y -qq $cmd || yum install -y $cmd 2>/dev/null || true
    fi
done

if ! command -v curl &>/dev/null || ! command -v jq &>/dev/null; then
    echo "ERROR: Install curl and jq: apt-get install curl jq"
    exit 1
fi

# -----------------------------------------------------------------------------
# 2. Создание директории
# -----------------------------------------------------------------------------
echo "[2/6] Creating runner directory..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Удаление старого runner (если переустановка)
if [ -d "./runner" ]; then
    echo "Removing old runner..."
    ./runner/svc.sh stop 2>/dev/null || true
    ./runner/svc.sh uninstall 2>/dev/null || true
    rm -rf ./runner
fi

# -----------------------------------------------------------------------------
# 3. Скачивание runner
# -----------------------------------------------------------------------------
echo "[3/6] Downloading GitHub Actions runner..."
RUNNER_PLAT="linux"
RUNNER_ARCH="x64"
[ "$(uname -m)" = "aarch64" ] && RUNNER_ARCH="arm64"

LATEST_TAG=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | jq -r '.tag_name')
LATEST_VER="${LATEST_TAG#v}"
RUNNER_FILE="actions-runner-${RUNNER_PLAT}-${RUNNER_ARCH}-${LATEST_VER}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/${LATEST_TAG}/${RUNNER_FILE}"

if [ ! -f "$RUNNER_FILE" ]; then
    curl -sL -o "$RUNNER_FILE" "$RUNNER_URL"
fi

# -----------------------------------------------------------------------------
# 4. Распаковка
# -----------------------------------------------------------------------------
echo "[4/6] Extracting..."
mkdir -p runner
tar xzf "$RUNNER_FILE" -C runner

# -----------------------------------------------------------------------------
# 5. Конфигурация (с токеном или без)
# -----------------------------------------------------------------------------
echo "[5/6] Configuring runner..."

cd runner

if [ -n "$RUNNER_CFG_PAT" ]; then
    # Автоматически получаем registration token через API
    echo "Getting registration token via PAT..."
    RUNNER_TOKEN=$(curl -s -X POST "https://api.github.com/repos/${REPO}/actions/runners/registration-token" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token ${RUNNER_CFG_PAT}" | jq -r '.token')
    
    if [ -z "$RUNNER_TOKEN" ] || [ "$RUNNER_TOKEN" = "null" ]; then
        echo "ERROR: Failed to get token. Check PAT permissions (repo scope)."
        exit 1
    fi
    
    ./config.sh --unattended --url "https://github.com/${REPO}" --token "$RUNNER_TOKEN" --name "saveuz-$(hostname)" --replace
else
    # Ручной режим — выводим инструкции
    echo ""
    echo "=============================================="
    echo "RUNNER_CFG_PAT not set. Manual configuration:"
    echo "=============================================="
    echo ""
    echo "1. Go to: https://github.com/${REPO}/settings/actions/runners/new"
    echo "2. Copy the token from the page"
    echo "3. Run:"
    echo "   cd $RUNNER_DIR/runner"
    echo "   ./config.sh --url https://github.com/${REPO} --token YOUR_TOKEN --name saveuz-\$(hostname) --replace"
    echo ""
    echo "4. Then install and start service:"
    echo "   sudo ./svc.sh install"
    echo "   sudo ./svc.sh start"
    echo ""
    exit 0
fi

# -----------------------------------------------------------------------------
# 6. Установка как systemd-сервис
# -----------------------------------------------------------------------------
echo "[6/6] Installing as systemd service..."
./svc.sh install
./svc.sh start

echo ""
echo "=============================================="
echo "✅ Runner installed and started!"
echo "=============================================="
echo ""
echo "Check status:  sudo ./svc.sh status"
echo "View logs:     journalctl -u actions.runner.* -f"
echo ""
echo "Verify on GitHub: https://github.com/${REPO}/settings/actions/runners"
echo ""
