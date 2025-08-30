# Техническая архитектура AI Auto Debate

## Архитектурные принципы

### 1. Модульная архитектура
Проект построен по принципу модульной архитектуры с четким разделением ответственности:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Layer     │    │   API Layer     │    │  Business Logic │
│  (HTML/CSS/JS)  │◄──►│   (FastAPI)     │◄──►│  (DebateManager)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Bot Clients    │    │   Logging       │
                       │ (LMStudioClient)│    │   System        │
                       └─────────────────┘    └─────────────────┘
```

### 2. Асинхронная архитектура
Все операции выполняются асинхронно для обеспечения высокой производительности:

```python
# Пример асинхронного взаимодействия
async def step_sequence(self):
    speaker = self._pick_next_speaker()
    
    if not self.current_state.sequential_mode:
        # Параллельные запросы к ботам
        resp1_task = asyncio.create_task(self._ask_bot("Bot1"))
        resp2_task = asyncio.create_task(self._ask_bot("Bot2"))
        r1, r2 = await asyncio.gather(resp1_task, resp2_task)
    else:
        # Последовательный запрос
        msg = await self._ask_bot(speaker)
```

## Детали реализации

### 1. Управление состоянием

#### Независимые состояния для режимов
```python
class DebateManager:
    def __init__(self):
        # Отдельные состояния для каждого режима
        self.state_mode1 = DebateState(mode=1, sequential_mode=True)
        self.state_mode5 = DebateState(mode=5, sequential_mode=False)
        self.current_state = self.state_mode1  # Активное состояние
```

**Преимущества**:
- Изоляция данных между режимами
- Возможность переключения без потери контекста
- Независимое логирование

#### Переключение состояний
```python
async def set_mode(self, sequential: bool) -> None:
    async with self._lock:
        if sequential:
            self.current_state = self.state_mode1
        else:
            self.current_state = self.state_mode5
```

### 2. Система логирования

#### Многоуровневое логирование
```python
# Основной логгер
self.logger = build_logger("debate", mode=mode)

# Отдельные логгеры для режимов
self.mode1_logger = build_logger("mode1_debates", mode=1)
self.mode5_logger = build_logger("mode5_sync", mode=5)
```

#### Ротация логов
```python
def build_logger(name: str, mode: int = None):
    # Настройка ротации по размеру и времени
    handler = RotatingFileHandler(
        filename,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
```

### 3. Клиент-серверное взаимодействие

#### REST API
```python
# Получение состояния режима
@router.get("/state/mode1")
async def state_mode1():
    return {
        "mode": debate.state_mode1.mode,
        "topic": debate.state_mode1.topic,
        "history_tail": debate.state_mode1.history[-12:],
    }
```

#### WebSocket для real-time логов
```python
@app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_text("[system] WebSocket готов")
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        pass
```

### 4. Обработка ошибок и отказоустойчивость

#### Fallback механизм для URL ботов
```python
async def _ask_bot(self, bot_name: str) -> Optional[str]:
    # Список URL для попыток подключения
    urls_to_try: List[str]
    if bot_name == "Bot1":
        urls_to_try = [self.bot1.url] + list(CONFIG.bot1_alt_urls)
    else:
        urls_to_try = [self.bot2.url, base, base2]
    
    for attempt in range(3):
        try:
            # Попытка подключения
            resp = await client.chat(history_slice)
            return msg
        except Exception as e:
            # Логирование ошибки и повторная попытка
            self.logger.error(f"{bot_name} request error: {e}")
            await asyncio.sleep(2)
    return None
```

#### Автоопределение модели
```python
try:
    resp = await client.chat(history_slice)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        await client._fetch_and_cache_model()
        resp = await client.chat(history_slice)
```

### 5. Frontend архитектура

#### Компонентная структура
```javascript
// Управление состоянием
let currentMode = 1;
let currentChatTab = 1;

// Функции для работы с UI
function switchChatTab(mode) { /* ... */ }
function getActiveChat() { /* ... */ }
function addMsg(text, role, labelText, targetChat) { /* ... */ }
```

#### Асинхронные операции
```javascript
// Загрузка состояния для всех режимов
async function pullAllStates() {
    await Promise.all([
        pullStateForMode(1),
        pullStateForMode(5)
    ]);
}

// Периодическое обновление
setInterval(pullAllStates, 2000);
```

### 6. Стилизация и UX

#### CSS переменные для темизации
```css
:root {
    --bg: #0d0f14;
    --panel: #141824;
    --text: #e6e6e6;
    --accent: #6aa9ff;
    --bot1: #7bd88f;
    --bot2: #ff7ab2;
}
```

#### Плавные переходы
```css
.chat {
    opacity: 0;
    visibility: hidden;
    transition: opacity .3s ease, visibility .3s ease;
}
.chat.active {
    opacity: 1;
    visibility: visible;
}
```

## Производительность и оптимизация

### 1. Ограничение истории
```python
# Ограничение истории для API запросов
history_slice = LMStudioClient.make_history_slice(
    self.current_state.history, 
    limit=12
)

# Ограничение в UI
"history_tail": self.state_mode1.history[-12:]
```

### 2. Кэширование
```python
# Кэширование информации о модели
@property
def _detected_model(self) -> Optional[str]:
    if not hasattr(self, '_cached_model'):
        self._cached_model = None
    return self._cached_model
```

### 3. Асинхронные операции
```python
# Параллельные запросы к ботам
resp1_task = asyncio.create_task(self._ask_bot("Bot1"))
resp2_task = asyncio.create_task(self._ask_bot("Bot2"))
r1, r2 = await asyncio.gather(resp1_task, resp2_task)
```

## Безопасность

### 1. Валидация входных данных
```python
@router.post("/message")
async def post_message(payload: dict):
    text = payload.get("text", "").strip()
    if not text:
        return {"ok": False, "error": "empty"}
```

### 2. Ограничение доступа к файлам
```python
def get_logs_path(self) -> str:
    # Возвращает только путь к директории логов
    return CONFIG.logs_dir
```

### 3. Обработка исключений
```python
try:
    # Операции с файлами
    with open(self.roles_file, "r", encoding="utf-8") as f:
        self.roles = json.load(f)
except Exception as e:
    self.logger.error(f"Roles load error: {e}")
```

## Масштабируемость

### 1. Легкое добавление новых режимов
```python
# Для добавления нового режима достаточно:
self.state_mode3 = DebateState(mode=3, sequential_mode=False)
```

### 2. Модульная структура API
```python
# Новые эндпоинты легко добавляются
@router.get("/state/mode3")
async def state_mode3():
    return {"mode": debate.state_mode3.mode, ...}
```

### 3. Конфигурируемость
```python
# Все настройки вынесены в конфигурацию
class CONFIG:
    bot1_url = "http://192.168.8.87:1234/v1/chat/completions"
    bot2_url = "http://192.168.8.89:1234/v1/chat/completions"
    logs_dir = "logs"
    prompts_dir = "storage/prompts"
```

## Мониторинг и отладка

### 1. Подробное логирование
```python
# Логирование всех важных событий
self.mode1_logger.info(f"Topic set for infinite debates: {topic}")
self.mode5_logger.info(f"Next speaker in sync dialog: {speaker}")
```

### 2. Индикаторы состояния
```javascript
// Индикация подключения ботов
async function refreshIndicators() {
    const conn = await fetch('/api/connectivity').then(r => r.json());
    bot1Led.classList.toggle('off', !conn.bot1);
    bot2Led.classList.toggle('off', !conn.bot2);
}
```

### 3. Отслеживание ошибок
```python
# Сбор и отображение ошибок
def get_errors(self, tail: int = 50) -> List[str]:
    return self.last_errors[-tail:]
```

## Тестирование

### 1. Структура тестов
```python
async def test_independent_chats():
    # Тестирование независимости режимов
    # Тестирование переключения состояний
    # Тестирование очистки истории
```

### 2. API тестирование
```python
# Тестирование всех эндпоинтов
async with session.get(f"{base_url}/api/state/mode1") as resp:
    state1 = await resp.json()
```

## Развертывание

### 1. Скрипты автоматизации
```powershell
# start_web.ps1
$ErrorActionPreference = "Stop"
& .\.venv\Scripts\Activate.ps1
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 2. Виртуальное окружение
```powershell
# install.ps1
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Заключение

Архитектура проекта обеспечивает:
- **Модульность** - четкое разделение ответственности
- **Масштабируемость** - легко добавлять новые функции
- **Отказоустойчивость** - обработка ошибок и fallback механизмы
- **Производительность** - асинхронная архитектура
- **Удобство использования** - интуитивный интерфейс
- **Мониторинг** - подробное логирование и индикаторы состояния
