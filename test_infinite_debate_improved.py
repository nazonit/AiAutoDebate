#!/usr/bin/env python3
"""
Тестовый скрипт для проверки улучшенной логики бесконечных дебатов
"""

import asyncio
import sys
import os

# Добавляем путь к src для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.debate_manager import DebateManager

async def test_infinite_debate():
    """Тестирует улучшенную логику бесконечных дебатов"""
    
    print("🚀 Запуск теста улучшенной логики бесконечных дебатов")
    print("=" * 60)
    
    # Создаем менеджер дебатов
    manager = DebateManager(mode=1)
    
    try:
        # Запускаем менеджер
        await manager.start()
        print("✅ Менеджер дебатов запущен")
        
        # Тестируем различные темы
        test_topics = [
            "Польза и вред социальных сетей",
            "Искусственный интеллект: угроза или возможность",
            "Дистанционное обучение vs традиционное образование"
        ]
        
        for i, topic in enumerate(test_topics, 1):
            print(f"\n📝 Тест {i}: {topic}")
            print("-" * 40)
            
            # Запускаем бесконечные дебаты
            await manager.start_infinite_debate(topic)
            print(f"✅ Дебаты запущены на тему: {topic}")
            
            # Выполняем несколько шагов дебатов
            step_count = 0
            max_steps = 10  # Ограничиваем количество шагов для теста
            
            while step_count < max_steps:
                step_count += 1
                print(f"\n🔄 Шаг {step_count}:")
                
                # Выполняем шаг дебатов
                continue_debate = await manager.step_infinite_debate()
                
                # Получаем текущее состояние
                state = manager.state_mode1
                
                if not continue_debate:
                    print("✅ Дебаты завершены!")
                    break
                
                # Показываем последний ответ
                if state.history:
                    last_message = state.history[-1]
                    if last_message.get("role") == "assistant":
                        speaker = last_message.get("name", "Unknown")
                        content = last_message.get("content", "")
                        print(f"💬 {speaker}: {content[:100]}...")
                        
                        # Показываем метрики качества
                        relevance = manager._check_topic_relevance(content)
                        print(f"📊 Релевантность: {relevance:.2f}")
                        
                        if len(state.history) > 1:
                            prev_message = state.history[-2]
                            if prev_message.get("role") == "assistant":
                                coherence = manager._check_conversation_coherence(
                                    content, prev_message.get("content", "")
                                )
                                print(f"📊 Связность: {coherence:.2f}")
                
                # Небольшая пауза между шагами
                await asyncio.sleep(1)
            
            # Останавливаем дебаты
            await manager.stop_infinite_debate()
            print(f"⏹️ Дебаты остановлены после {step_count} шагов")
            
            # Показываем статистику
            assistant_messages = [msg for msg in state.history if msg.get("role") == "assistant"]
            print(f"📈 Статистика:")
            print(f"   - Всего ответов: {len(assistant_messages)}")
            print(f"   - Согласие достигнуто: {state.agreement_reached}")
            print(f"   - Коэффициент связности: {state.conversation_coherence:.2f}")
            print(f"   - Ключевые слова темы: {list(state.topic_keywords)}")
            
            # Очищаем историю для следующего теста
            await manager.clear_history()
            print("🧹 История очищена")
            
            # Пауза между тестами
            await asyncio.sleep(2)
        
        print("\n🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Останавливаем менеджер
        await manager.stop()
        print("🛑 Менеджер дебатов остановлен")

async def test_agreement_detection():
    """Тестирует улучшенное определение согласия"""
    
    print("\n🔍 Тест определения согласия")
    print("=" * 40)
    
    manager = DebateManager(mode=1)
    
    # Тестовые пары ответов
    test_pairs = [
        # Согласие
        (
            "Я согласен с вашей точкой зрения. Ваши аргументы убедительны.",
            "Спасибо за поддержку. Мы пришли к общему мнению."
        ),
        # Несогласие
        (
            "Я не согласен с вашими доводами. У меня противоположное мнение.",
            "Я также не разделяю вашу позицию. Мы остаемся при своих мнениях."
        ),
        # Частичное согласие
        (
            "В целом я согласен, но есть некоторые нюансы.",
            "Да, вы правы в основном, но нужно учесть детали."
        ),
        # Завершение дебатов
        (
            "Пришли к согласию по основным вопросам.",
            "Да, мы достигли консенсуса. Дебаты можно завершать."
        )
    ]
    
    for i, (response1, response2) in enumerate(test_pairs, 1):
        agreement = manager._check_agreement(response1, response2)
        print(f"Тест {i}: {'✅ Согласие' if agreement else '❌ Несогласие'}")
        print(f"   Ответ 1: {response1}")
        print(f"   Ответ 2: {response2}")
        print()

if __name__ == "__main__":
    # Запускаем тесты
    asyncio.run(test_infinite_debate())
    asyncio.run(test_agreement_detection())
