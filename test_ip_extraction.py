#!/usr/bin/env python3
"""
Тестовый скрипт для проверки извлечения IP адресов из URL
"""

import sys
import os
import ipaddress

# Добавляем путь к src для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Импортируем напрямую из модуля
sys.path.insert(0, 'src')
from core.debate_manager import BotProfile

def test_ip_extraction():
    """Тестирует извлечение IP адресов из URL"""
    
    print("🔍 Тест извлечения IP адресов из URL")
    print("=" * 50)
    
    # Тестовые URL с IP адресами 87 и 89
    test_urls = [
        "http://192.168.8.87:12345/v1/chat/completions",  # Bot1 - IP 87
        "http://192.168.8.89:1234/v1/chat/completions",   # Bot2 - IP 89
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📝 Тест {i}: {url}")
        
        # Создаем профиль бота
        bot = BotProfile(name=f"Bot{i}", url=url)
        
        print(f"   Извлеченный IP: {bot.ip_address}")
        print(f"   Числовое значение: {bot.get_ip_numeric()}")
        
        # Проверяем, что IP извлечен правильно
        if bot.ip_address:
            try:
                ip_obj = ipaddress.ip_address(bot.ip_address)
                print(f"   Валидный IP: ✅")
                print(f"   IP версия: IPv{ip_obj.version}")
            except ValueError:
                print(f"   Валидный IP: ❌")
        else:
            print(f"   IP не извлечен: ❌")
    
    # Тестируем сравнение IP адресов
    print(f"\n🔍 Тест сравнения IP адресов:")
    print("-" * 30)
    
    bot1 = BotProfile(name="Bot1", url="http://192.168.8.87:12345/v1/chat/completions")
    bot2 = BotProfile(name="Bot2", url="http://192.168.8.89:1234/v1/chat/completions")
    
    bot1_ip = bot1.get_ip_numeric()
    bot2_ip = bot2.get_ip_numeric()
    
    print(f"Bot1 IP (87): {bot1_ip}")
    print(f"Bot2 IP (89): {bot2_ip}")
    print(f"Bot1 < Bot2: {bot1_ip < bot2_ip}")
    
    # Определяем первого говорящего
    first_speaker = "Bot1" if bot1_ip < bot2_ip else "Bot2"
    print(f"Первый говорящий: {first_speaker}")
    
    if first_speaker == "Bot1":
        print("✅ Логика правильная: Bot1 (IP 87) начинает первым")
    else:
        print("❌ Логика неправильная: Bot2 (IP 89) не должен начинать первым")

if __name__ == "__main__":
    test_ip_extraction()
