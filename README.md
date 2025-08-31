# AI Auto Debate Web

Бэкенд-приложение на FastAPI для «бесконечных дебатов» между двумя локальными LLM (совместимыми с OpenAI Chat Completions API, напр. LM Studio). Веб‑интерфейс на Jinja2 + статика.

## Архитектура
- **FastAPI приложение** (`src/main.py`)
  - Подключает роуты из `src/api/routes.py`
  - Отдаёт статику и шаблоны из `src/web/`
- **Роуты API** (`src/api/routes.py`)
  - Жизненный цикл: `startup`/`shutdown` запускают/останавливают `DebateManager`
  - `GET /api/state` — состояние дебатов; `POST /api/topic` — задать тему
- **Диспетчер дебатов** (`src/core/debate_manager.py`)
  - Хранит тему, историю, определяет говорящего, запрашивает ответы у ботов
  - Фолбэк для Bot1: если не доступен основной URL, пробует `localhost` и `127.0.0.1`
- **HTTP клиент бота** (`src/bots/lmstudio_client.py`)
  - Совместим с OpenAI Chat Completions: `POST /v1/chat/completions`
- **Конфиг** (`src/core/config.py`)
  - Переменные окружения: `APP_HOST`, `APP_PORT`, `BOT1_URL`, `BOT1_ALT_URLS`, `BOT2_URL`, директории
- **Логирование** (`src/core/logger.py`)
  - Создание логгеров; папки логов в `logs/system` и `logs/modes`

Структура
```
src/
  api/routes.py           # FastAPI роуты
  bots/lmstudio_client.py # HTTP клиент для LLM
  core/
    config.py             # Конфиг
    debate_manager.py     # Логика дебатов
    logger.py             # Логи
  main.py                 # Точка входа FastAPI
  web/
    templates/index.html
    static/
```

## Требования
- Python 3.10+ (рекомендуется 3.11/3.12)
- Windows PowerShell (или другой терминал; ниже инструкции для PowerShell)

Зависимости: см. `requirements.txt` (FastAPI, Uvicorn, httpx, websockets, Jinja2, aiofiles и др.).

## Настройка ботов
Ожидаются два HTTP эндпоинта Chat Completions (LM Studio и аналоги):
- Bot1 (по умолчанию): `http://192.168.8.87:12345/v1/chat/completions`
- Bot2 (по умолчанию): `http://192.168.8.89:1234/v1/chat/completions`

Фолбэк для Bot1: если основной адрес недоступен, будут попытки на
- `http://localhost:12345/v1/chat/completions`
- `http://127.0.0.1:12345/v1/chat/completions`

Можно переопределить через переменные окружения:
```powershell
$env:BOT1_URL = "http://192.168.8.87:12345/v1/chat/completions"
$env:BOT1_ALT_URLS = "http://localhost:12345/v1/chat/completions,http://127.0.0.1:12345/v1/chat/completions"
$env:BOT2_URL = "http://192.168.8.89:1234/v1/chat/completions"
```

## Запуск (Windows PowerShell)
Вариант 1 — через скрипт:
```powershell
& C:/ai_auto_debate/run.ps1
```
Скрипт создаст venv (если нет), установит зависимости и запустит сервер на `0.0.0.0:8000`.

Вариант 2 — вручную по шагам:
```powershell
cd C:\ai_auto_debate
python -m venv .venv
& C:/ai_auto_debate/.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --disable-pip-version-check
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```
Откройте: `http://localhost:8000` (UI) и `http://localhost:8000/health` (проверка).

Примечания:
- В PowerShell НЕ используйте `&&`. Разделяйте команды `;` или переносом строки.
- Для смены хоста/порта приложения можно задать окружение:
```powershell
$env:APP_HOST = "0.0.0.0"
$env:APP_PORT = "8000"
```

## Быстрая проверка бота
```powershell
curl -Method POST -Uri $env:BOT1_URL -Body '{"messages":[{"role":"user","content":"ping"}]}' -ContentType 'application/json'
```

## Конфигурация (ENV)
- `APP_HOST` (default: `0.0.0.0`)
- `APP_PORT` (default: `8000`)
- `BOT1_URL` (default: `http://192.168.8.87:12345/v1/chat/completions`)
- `BOT1_ALT_URLS` (default: `http://localhost:12345/v1/chat/completions,http://127.0.0.1:12345/v1/chat/completions`)
- `BOT2_URL` (default: `http://192.168.8.89:1234/v1/chat/completions`)
- `LOGS_DIR` (default: `./logs`)
- `STORAGE_DIR` (default: `./storage`)

## Затык проекта
- Не могу заполнить чатом весь блок чата.
  


