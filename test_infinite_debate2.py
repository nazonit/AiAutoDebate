#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности бесконечных дебатов
"""

import asyncio
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.debate_manager import DebateManager


async def test_infinite_debate():
    """Тестирует функциональность бесконечных дебатов"""
    print("🚀 Запуск теста бесконечных дебатов...")
    
    # Создаем менеджер дебатов
    debate_manager = DebateManager(mode=1)
    
    try:
        # Запускаем менеджер
        await debate_manager.start()
        print("✅ Менеджер дебатов запущен")
        
        # Тестируем запуск бесконечных дебатов
        topic = "Искусственный интеллект: польза или вред для человечества?"
        print(f"📝 Запускаем дебаты на тему: {topic}")
        
        await debate_manager.start_infinite_debate(topic)
        print("✅ Бесконечные дебаты запущены")
        
        # Выполняем несколько шагов дебатов
        print("🔄 Выполняем шаги дебатов...")
        for i in range(5):
            print(f"   Шаг {i+1}...")
            continue_debate = await debate_manager.step_infinite_debate()
            
            if not continue_debate:
                print("✅ Дебаты завершены по согласию!")
                break
                
            # Небольшая пауза между шагами
            await asyncio.sleep(1)
        
        # Проверяем состояние
        state = debate_manager.get_state_snapshot()
        print(f"📊 Состояние дебатов:")
        print(f"   - Тема: {state.get('topic')}")
        print(f"   - Последний говорящий: {state.get('last_speaker')}")
        print(f"   - Количество сообщений: {len(state.get('history_tail', []))}")
        
        # Тестируем остановку дебатов
        print("🛑 Останавливаем дебаты...")
        await debate_manager.stop_infinite_debate()
        print("✅ Дебаты остановлены")
        
        # Проверяем, что дебаты действительно остановлены
        continue_debate = await debate_manager.step_infinite_debate()
        if not continue_debate:
            print("✅ Подтверждено: дебаты остановлены")
        
    except Exception as e:
        print(f"❌ Ошибка во время теста: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Останавливаем менеджер
        await debate_manager.stop()
        print("🔄 Менеджер дебатов остановлен")


async def test_agreement_detection():
    """Тестирует обнаружение согласия между ботами"""
    print("\n🔍 Тестирование обнаружения согласия...")
    
    debate_manager = DebateManager(mode=1)
    
    # Тестовые ответы
    response1 = "Я согласен с вашей точкой зрения. Вы правы в том, что это важный вопрос."
    response2 = "Согласен с вами полностью. Это действительно важная тема для обсуждения."
    
    # Проверяем обнаружение согласия
    agreement = debate_manager._check_agreement(response1, response2)
    print(f"   Ответ 1: {response1}")
    print(f"   Ответ 2: {response2}")
    print(f"   Согласие обнаружено: {agreement}")
    
    # Тест с несогласными ответами
    response3 = "Я не согласен с вашей позицией. Это спорный вопрос."
    response4 = "У меня противоположное мнение по этому поводу."
    
    agreement2 = debate_manager._check_agreement(response3, response4)
    print(f"   Ответ 3: {response3}")
    print(f"   Ответ 4: {response4}")
    print(f"   Согласие обнаружено: {agreement2}")


async def test_uniqueness_check():
    """Тестирует проверку уникальности ответов"""
    print("\n🔍 Тестирование проверки уникальности...")
    
    debate_manager = DebateManager(mode=1)
    
    # Тестовые ответы
    response1 = "Это очень важный вопрос для обсуждения."
    response2 = "Это очень важный вопрос для обсуждения."  # Дубликат
    response3 = "У меня есть другое мнение по этому поводу."
    
    recent_responses = set()
    
    # Проверяем уникальность
    unique1 = debate_manager._is_response_unique(response1, recent_responses)
    print(f"   Ответ 1 уникален: {unique1}")
    
    if unique1:
        recent_responses.add(debate_manager._normalize_text(response1))
    
    unique2 = debate_manager._is_response_unique(response2, recent_responses)
    print(f"   Ответ 2 (дубликат) уникален: {unique2}")
    
    unique3 = debate_manager._is_response_unique(response3, recent_responses)
    print(f"   Ответ 3 уникален: {unique3}")


async def main():
    """Основная функция тестирования"""
    print("🧪 Начинаем тестирование функциональности бесконечных дебатов\n")
    
    # Тестируем обнаружение согласия
    await test_agreement_detection()
    
    # Тестируем проверку уникальности
    await test_uniqueness_check()
    
    # Тестируем полный цикл дебатов (только если есть подключение к ботам)
    print("\n" + "="*50)
    print("⚠️  Следующий тест требует подключения к ботам LM Studio")
    print("   Если боты не запущены, тест может завершиться ошибкой")
    print("="*50)
    
    try:
        await test_infinite_debate()
    except Exception as e:
        print(f"❌ Тест дебатов не прошел (возможно, боты не подключены): {e}")
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main())
