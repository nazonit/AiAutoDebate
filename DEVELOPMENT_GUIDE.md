# Руководство по разработке AI Auto Debate

## Начало работы

### 1. Установка зависимостей
```powershell
# Создание виртуального окружения
python -m venv .venv

# Активация окружения
& .\.venv\Scripts\Activate.ps1

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Запуск проекта
```powershell
# Запуск сервера разработки
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Или использование скрипта
.\start_web.ps1
```

### 3. Проверка работоспособности
- Откройте http://localhost:8000 в браузере
- Проверьте подключение к ботам в боковой панели
- Протестируйте переключение между режимами

## Структура проекта для разработчиков

### Основные модули

#### `src/core/debate_manager.py`
**Центральный компонент системы**

**Ключевые классы для понимания**:
```python
@dataclass
class DebateState:
    mode: int = 1
    topic: Optional[str] = None
    history: List[Dict[str, str]] = field(default_factory=list)
    sequential_mode: bool = True
    last_speaker: Optional[str] = None

class DebateManager:
    def __init__(self):
        # Отдельные состояния для каждого режима
        self.state_mode1 = DebateState(mode=1, sequential_mode=True)
        self.state_mode5 = DebateState(mode=5, sequential_mode=False)
        self.current_state = self.state_mode1
```

**Основные методы для расширения**:
- `step_sequence()` - логика выполнения шага дебатов
- `_ask_bot()` - взаимодействие с ИИ-ботами
- `set_mode()` - переключение режимов
- `add_user_message()` - обработка пользовательских сообщений

#### `src/api/routes.py`
**API эндпоинты**

**Паттерн добавления новых эндпоинтов**:
```python
@router.get("/api/new-endpoint")
async def new_endpoint():
    """Описание эндпоинта"""
    return {"data": "value"}

@router.post("/api/new-action")
async def new_action(payload: dict):
    """Описание действия"""
    # Логика обработки
    return {"ok": True}
```

#### `src/web/static/app.js`
**Клиентская логика**

**Основные функции для понимания**:
```javascript
// Управление состоянием
let currentMode = 1;
let currentChatTab = 1;

// Переключение вкладок
function switchChatTab(mode) { /* ... */ }

// Загрузка состояния
async function pullStateForMode(mode) { /* ... */ }

// Обработка событий
sendBtn.addEventListener('click', () => { /* ... */ });
```

## Добавление новых функций

### 1. Добавление нового режима

#### Шаг 1: Обновление DebateManager
```python
# В src/core/debate_manager.py
class DebateManager:
    def __init__(self):
        # Добавить новое состояние
        self.state_mode3 = DebateState(mode=3, sequential_mode=False)
        # Обновить логику переключения
        self.mode3_logger = build_logger("mode3_new", mode=3)
```

#### Шаг 2: Добавление API эндпоинтов
```python
# В src/api/routes.py
@router.get("/state/mode3")
async def state_mode3():
    """Получить состояние для режима 3"""
    return {
        "mode": debate.state_mode3.mode,
        "topic": debate.state_mode3.topic,
        "history_tail": debate.state_mode3.history[-12:],
    }

@router.post("/clear/mode3")
async def clear_mode3():
    """Очистить историю режима 3"""
    debate.state_mode3.history.clear()
    return {"ok": True}
```

#### Шаг 3: Обновление фронтенда
```html
<!-- В src/web/templates/index.html -->
<button class="chat-tab" data-mode="3">
  <span class="tab-title">Новый режим</span>
  <span class="tab-indicator"></span>
</button>

<div id="chat-mode3" class="chat"></div>
```

```javascript
// В src/web/static/app.js
const chatMode3 = document.getElementById('chat-mode3');

// Обновить функцию getActiveChat
function getActiveChat() {
  if (currentChatTab === 1) return chatMode1;
  if (currentChatTab === 5) return chatMode5;
  if (currentChatTab === 3) return chatMode3;
}

// Обновить pullStateForMode
async function pullStateForMode(mode) {
  const endpoint = `/api/state/mode${mode}`;
  const targetChat = document.getElementById(`chat-mode${mode}`);
  // ... остальная логика
}
```

### 2. Добавление новых типов сообщений

#### Шаг 1: Обновление модели данных
```python
# В src/core/debate_manager.py
@dataclass
class DebateState:
    # Добавить новые поля
    system_messages: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Шаг 2: Обновление логики обработки
```python
async def add_system_message(self, message: str, message_type: str = "info"):
    async with self._lock:
        self.current_state.system_messages.append({
            "role": "system",
            "content": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        })
```

#### Шаг 3: Обновление API
```python
@router.post("/system-message")
async def add_system_message(payload: dict):
    message = payload.get("message", "")
    message_type = payload.get("type", "info")
    await debate.add_system_message(message, message_type)
    return {"ok": True}
```

### 3. Добавление новых настроек

#### Шаг 1: Обновление конфигурации
```python
# В src/core/config.py
class CONFIG:
    # Добавить новые настройки
    max_history_length: int = 50
    auto_save_interval: int = 300  # секунды
    enable_notifications: bool = True
```

#### Шаг 2: Добавление UI элементов
```html
<!-- В src/web/templates/index.html -->
<div class="settings">
  <h3>Настройки</h3>
  <label>
    Максимальная длина истории:
    <input type="number" id="maxHistoryLength" min="10" max="100" />
  </label>
  <label>
    <input type="checkbox" id="enableNotifications" />
    Включить уведомления
  </label>
</div>
```

#### Шаг 3: Обработка в JavaScript
```javascript
// В src/web/static/app.js
document.getElementById('maxHistoryLength').addEventListener('change', async (e) => {
  const value = parseInt(e.target.value);
  await fetch('/api/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ max_history_length: value })
  });
});
```

## Отладка и тестирование

### 1. Логирование

#### Добавление логов
```python
# В любом файле
import logging
logger = logging.getLogger(__name__)

logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.debug("Отладочная информация")
```

#### Просмотр логов
```bash
# Просмотр логов в реальном времени
tail -f logs/debate.log

# Просмотр логов конкретного режима
tail -f logs/mode1_debates.log
```

### 2. Отладка API

#### Тестирование эндпоинтов
```bash
# Проверка состояния
curl http://localhost:8000/api/state/mode1

# Отправка сообщения
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{"text": "Тестовое сообщение"}'

# Очистка истории
curl -X POST http://localhost:8000/api/clear/mode1
```

#### Использование FastAPI docs
- Откройте http://localhost:8000/docs
- Интерактивная документация API
- Тестирование эндпоинтов прямо в браузере

### 3. Отладка фронтенда

#### Консоль браузера
```javascript
// Добавление отладочной информации
console.log('Текущий режим:', currentMode);
console.log('Активная вкладка:', currentChatTab);

// Проверка состояния
console.log('Состояние режима 1:', await fetch('/api/state/mode1').then(r => r.json()));
```

#### Инструменты разработчика
- F12 → Console - для отладки JavaScript
- F12 → Network - для мониторинга API запросов
- F12 → Elements - для инспекции DOM

## Оптимизация производительности

### 1. Ограничение истории
```python
# Ограничение размера истории для предотвращения утечек памяти
def trim_history(self, max_length: int = 50):
    if len(self.current_state.history) > max_length:
        self.current_state.history = self.current_state.history[-max_length:]
```

### 2. Кэширование
```python
# Кэширование часто используемых данных
from functools import lru_cache

@lru_cache(maxsize=128)
def get_bot_info(bot_name: str):
    # Кэшированная информация о боте
    pass
```

### 3. Асинхронные операции
```python
# Использование asyncio.gather для параллельных операций
async def parallel_operations(self):
    tasks = [
        self.operation1(),
        self.operation2(),
        self.operation3()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

## Безопасность

### 1. Валидация входных данных
```python
from pydantic import BaseModel, validator

class MessagePayload(BaseModel):
    text: str
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Текст не может быть пустым')
        if len(v) > 1000:
            raise ValueError('Текст слишком длинный')
        return v.strip()
```

### 2. Ограничение доступа
```python
# Проверка прав доступа
def check_permission(user_id: str, action: str) -> bool:
    # Логика проверки прав
    pass

@router.post("/admin/action")
async def admin_action(payload: dict, user_id: str):
    if not check_permission(user_id, "admin"):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
```

### 3. Санитизация данных
```python
import html

def sanitize_text(text: str) -> str:
    """Очистка текста от потенциально опасных символов"""
    return html.escape(text.strip())
```

## Развертывание

### 1. Продакшн конфигурация
```python
# config/production.py
class ProductionConfig:
    debug = False
    log_level = "INFO"
    max_workers = 4
    host = "0.0.0.0"
    port = 8000
```

### 2. Docker контейнеризация
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY storage/ ./storage/

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Мониторинг
```python
# Добавление метрик
from prometheus_client import Counter, Histogram

request_counter = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    request_counter.inc()
    start_time = time.time()
    response = await call_next(request)
    request_duration.observe(time.time() - start_time)
    return response
```

## Советы по разработке

### 1. Следование принципам
- **DRY** (Don't Repeat Yourself) - избегайте дублирования кода
- **SOLID** - следуйте принципам SOLID
- **KISS** (Keep It Simple, Stupid) - делайте код простым

### 2. Комментирование кода
```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Краткое описание функции.
    
    Args:
        param1: Описание первого параметра
        param2: Описание второго параметра
        
    Returns:
        Описание возвращаемого значения
        
    Raises:
        ValueError: Когда что-то идет не так
    """
    # Логика функции
    pass
```

### 3. Тестирование
```python
import pytest

def test_debate_manager_initialization():
    manager = DebateManager()
    assert manager.current_state.mode == 1
    assert manager.current_state.sequential_mode == True

@pytest.mark.asyncio
async def test_mode_switching():
    manager = DebateManager()
    await manager.set_mode(sequential=False)
    assert manager.current_state == manager.state_mode5
```

### 4. Git workflow
```bash
# Создание новой ветки для функции
git checkout -b feature/new-mode

# Регулярные коммиты
git add .
git commit -m "feat: add new debate mode"

# Создание pull request
git push origin feature/new-mode
```

## Полезные ресурсы

### Документация
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [JavaScript ES6+](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

### Инструменты
- [Postman](https://www.postman.com/) - тестирование API
- [VS Code](https://code.visualstudio.com/) - редактор кода
- [Git](https://git-scm.com/) - система контроля версий

### Сообщество
- [FastAPI Discord](https://discord.gg/VQjKpSwpJB)
- [Python Discord](https://discord.gg/python)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi)
