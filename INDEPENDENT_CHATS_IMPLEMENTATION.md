# Реализация независимых чатов для каждого режима

## Обзор

Реализована система независимых чатов для каждого режима работы приложения:
- **Режим 1**: "Бесконечные дебаты" (sequential_mode = True)
- **Режим 5**: "Синхронный диалог" (sequential_mode = False)

Каждый режим теперь имеет:
- Свою независимую историю диалогов
- Отдельное окно чата в интерфейсе
- Собственное логирование
- Независимую очистку истории

## Изменения в файлах

### 1. HTML (src/web/templates/index.html)

**Добавлены вкладки чата:**
```html
<!-- Вкладки чата -->
<div class="chat-tabs">
  <button class="chat-tab active" data-mode="1">
    <span class="tab-title">Бесконечные дебаты</span>
    <span class="tab-indicator"></span>
  </button>
  <button class="chat-tab" data-mode="5">
    <span class="tab-title">Синхронный диалог</span>
    <span class="tab-indicator"></span>
  </button>
</div>

<!-- Контейнеры чата для каждого режима -->
<div class="chat-container">
  <div id="chat-mode1" class="chat active"></div>
  <div id="chat-mode5" class="chat"></div>
</div>
```

### 2. CSS (src/web/static/style.css)

**Добавлены стили для вкладок:**
```css
/* Стили для вкладок чата */
.chat-tabs { display: flex; border-bottom: 1px solid #222839; background: #0e1220; border-radius: 12px 12px 0 0; }
.chat-tab { flex: 1; background: transparent; color: var(--muted); border: none; padding: 12px 16px; cursor: pointer; position: relative; transition: all .2s ease; }
.chat-tab:hover { color: var(--text); background: rgba(255,255,255,0.02); }
.chat-tab.active { color: var(--accent); background: var(--panel); }
.chat-tab.active .tab-indicator { background: var(--accent); }

/* Контейнер чата */
.chat-container { flex: 1; position: relative; }
.chat { padding:12px; height:65vh; overflow:auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; opacity: 0; visibility: hidden; transition: opacity .3s ease, visibility .3s ease; }
.chat.active { opacity: 1; visibility: visible; }
```

### 3. JavaScript (src/web/static/app.js)

**Основные изменения:**

1. **Управление вкладками чата:**
```javascript
// Функция для переключения вкладок чата
function switchChatTab(mode) {
  // Обновляем активную вкладку
  chatTabButtons.forEach(btn => {
    btn.classList.remove('active');
    if (parseInt(btn.getAttribute('data-mode')) === mode) {
      btn.classList.add('active');
    }
  });
  
  // Обновляем активный чат
  chatMode1.classList.remove('active');
  chatMode5.classList.remove('active');
  
  if (mode === 1) {
    chatMode1.classList.add('active');
  } else {
    chatMode5.classList.add('active');
  }
  
  currentChatTab = mode;
}
```

2. **Отдельные API вызовы для каждого режима:**
```javascript
// Функция для загрузки состояния конкретного режима
async function pullStateForMode(mode) {
  try {
    const endpoint = mode === 1 ? '/api/state/mode1' : '/api/state/mode5';
    const data = await fetch(endpoint).then(r => r.json());
    const tail = data.history_tail || [];
    const targetChat = mode === 1 ? chatMode1 : chatMode5;
    
    // Очищаем чат для этого режима
    targetChat.innerHTML = '';
    
    for (const m of tail) {
      const baseRole = m.role === 'assistant' ? (m.name || 'bot') : m.role;
      let cssRole = baseRole;
      if (baseRole !== 'user') {
        cssRole = (m.name === 'Bot1') ? 'bot1' : 'bot2';
      }
      const label = baseRole === 'user' ? 'You' : (m.name || baseRole);
      addMsg(m.content, cssRole, label, targetChat);
    }
  } catch (e) { /* ignore */ }
}
```

3. **Независимая очистка чатов:**
```javascript
btnClear.addEventListener('click', async () => {
  // Очищаем только активный режим
  const endpoint = currentChatTab === 1 ? '/api/clear/mode1' : '/api/clear/mode5';
  await fetch(endpoint, { method: 'POST' });
  getActiveChat().innerHTML = '';
  logLine('[action] history cleared for current mode');
});
```

### 4. Backend (src/core/debate_manager.py)

**Основные изменения:**

1. **Отдельные состояния для каждого режима:**
```python
# Отдельные состояния для каждого режима
self.state_mode1 = DebateState(mode=1, sequential_mode=True)
self.state_mode5 = DebateState(mode=5, sequential_mode=False)
self.current_state = self.state_mode1  # По умолчанию режим 1
```

2. **Переключение между состояниями:**
```python
async def set_mode(self, sequential: bool) -> None:
    async with self._lock:
        # Переключаемся между состояниями режимов
        if sequential:
            self.current_state = self.state_mode1
            self.mode1_logger.info("Switched to infinite debates mode")
        else:
            self.current_state = self.state_mode5
            self.mode5_logger.info("Switched to sync dialog mode")
    self.logger.info(f"Mode set: {'sequential' if sequential else 'sync'}")
```

3. **Отдельные логгеры:**
```python
# Отдельные логгеры для каждого режима
self.mode1_logger = build_logger("mode1_debates", mode=1)
self.mode5_logger = build_logger("mode5_sync", mode=5)
```

### 5. API (src/api/routes.py)

**Новые эндпоинты:**

1. **Получение состояния для каждого режима:**
```python
@router.get("/state/mode1")
async def state_mode1():
    """Получить состояние для режима 1 (Бесконечные дебаты)"""
    return {
        "mode": debate.state_mode1.mode,
        "topic": debate.state_mode1.topic,
        "last_speaker": debate.state_mode1.last_speaker,
        "history_tail": debate.state_mode1.history[-12:],
        "sequential_mode": debate.state_mode1.sequential_mode,
    }

@router.get("/state/mode5")
async def state_mode5():
    """Получить состояние для режима 5 (Синхронный диалог)"""
    return {
        "mode": debate.state_mode5.mode,
        "topic": debate.state_mode5.topic,
        "last_speaker": debate.state_mode5.last_speaker,
        "history_tail": debate.state_mode5.history[-12:],
        "sequential_mode": debate.state_mode5.sequential_mode,
    }
```

2. **Очистка отдельных режимов:**
```python
@router.post("/clear/mode1")
async def clear_mode1():
    """Очистить историю только для режима 1"""
    debate.state_mode1.history.clear()
    debate.state_mode1.last_speaker = None
    debate.state_mode1.topic = None
    return {"ok": True}

@router.post("/clear/mode5")
async def clear_mode5():
    """Очистить историю только для режима 5"""
    debate.state_mode5.history.clear()
    debate.state_mode5.last_speaker = None
    debate.state_mode5.topic = None
    return {"ok": True}
```

## Функциональность

### 1. Независимые чаты
- Каждый режим имеет свой собственный чат
- Переключение между режимами не влияет на историю другого режима
- Сообщения сохраняются отдельно для каждого режима

### 2. Визуальное переключение
- Вкладки чата с плавными переходами
- Индикация активной вкладки
- Автоматическое переключение при смене режима

### 3. Независимое управление
- Очистка истории только для активного режима
- Отдельные логи для каждого режима
- Независимые настройки и состояния

### 4. Сохранение дизайна
- Все существующие стили сохранены
- Добавлены новые стили для вкладок
- Плавные анимации переходов

## Тестирование

Создан тестовый скрипт `test_independent_chats.py` для проверки:
- Независимости историй режимов
- Корректности переключения между режимами
- Независимой очистки чатов
- Работы API эндпоинтов

## Использование

1. **Переключение между режимами:**
   - Нажмите кнопку "Бесконечные дебаты" или "Синхронный диалог" в верхнем меню
   - Или используйте вкладки чата для быстрого переключения

2. **Очистка чата:**
   - Кнопка "Очистить чат" очищает только активный режим
   - История другого режима остается нетронутой

3. **Отправка сообщений:**
   - Сообщения отправляются в активный режим
   - Каждый режим сохраняет свою историю независимо

## Преимущества реализации

1. **Изоляция данных** - каждый режим работает независимо
2. **Улучшенный UX** - четкое разделение между режимами
3. **Масштабируемость** - легко добавить новые режимы
4. **Сохранение контекста** - можно переключаться между режимами без потери данных
5. **Отдельное логирование** - каждый режим имеет свои логи для отладки
