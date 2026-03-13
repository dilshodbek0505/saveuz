# GitHub Actions Self-Hosted Runner — настройка

Pipeline зависает, потому что workflow использует `runs-on: self-hosted`, но на сервере **нет установленного runner'а**. GitHub ждёт, пока появится свободный self-hosted runner, и в итоге таймаут.

## Быстрая установка (5 минут)

### Шаг 1: Создай Personal Access Token (PAT)

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. **Generate new token (classic)**
3. Выбери scope: **repo** (полный доступ к репозиториям)
4. Сгенерируй и скопируй токен (начинается с `ghp_`)

### Шаг 2: Подключись к серверу

```bash
ssh root@185.191.141.148
```

### Шаг 3: Скопируй и запусти скрипт

**Вариант A — одной командой (с локальной машины):**

```bash
# С твоей машины (где лежит SaveuzBackend)
# Замени ghp_ТВОЙ_ТОКЕН на реальный PAT
scp scripts/setup_github_runner.sh root@185.191.141.148:/root/ && \
ssh root@185.191.141.148 "chmod +x /root/setup_github_runner.sh && RUNNER_CFG_PAT='ghp_ТВОЙ_ТОКЕН' /root/setup_github_runner.sh"
```

**Вариант B — вручную на сервере:**

```bash
# На сервере
cd /root
# Скачай скрипт или создай его (см. scripts/setup_github_runner.sh)
export RUNNER_CFG_PAT="ghp_xxxxxxxxxxxxxxxx"
chmod +x setup_github_runner.sh
./setup_github_runner.sh
```

**Вариант C — без PAT (полностью вручную):**

1. Открой: https://github.com/dilshodbek0505/saveuz/settings/actions/runners/new
2. Выбери **Linux** и **x64**
3. Скопируй команды с страницы и выполни их на сервере
4. После `./config.sh` выполни:
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

### Шаг 4: Проверка

```bash
# На сервере
/opt/actions-runner/runner/svc.sh status
```

Или открой: https://github.com/dilshodbek0505/saveuz/settings/actions/runners — runner должен быть зелёным (Idle).

---

## Если pipeline всё ещё зависает

### 1. Runner не запущен

```bash
cd /opt/actions-runner/runner
sudo ./svc.sh start
sudo ./svc.sh status
```

### 2. Runner не подключается к GitHub (firewall / сеть)

```bash
# Проверка доступа
curl -I https://github.com
```

Runner нужен только **исходящий** HTTPS (443) к `github.com` и `api.github.com`. Входящие порты не нужны.

### 3. Логи

```bash
journalctl -u actions.runner.* -f
```

### 4. Перезапуск runner

```bash
cd /opt/actions-runner/runner
sudo ./svc.sh stop
sudo ./svc.sh start
```

---

## Структура после установки

| Путь | Назначение |
|------|------------|
| `/opt/actions-runner/` | Директория runner'а |
| `/opt/actions-runner/runner/` | Бинарники и конфиг |
| `actions.runner.*` | Systemd-сервис |

Runner работает как демон, подключается к GitHub и ждёт джобы. При пуше в `main` workflow запускается на этом сервере.
