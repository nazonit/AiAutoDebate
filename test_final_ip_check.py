#!/usr/bin/env python3
"""
Финальный тест для проверки правильности логики IP адресов
"""

import ipaddress

def test_ip_logic():
    """Тестирует логику IP адресов"""
    
    print("🎯 Финальная проверка логики IP адресов")
    print("=" * 50)
    
    # Тестовые данные
    bot1_url = "http://192.168.8.87:12345/v1/chat/completions"
    bot2_url = "http://192.168.8.89:1234/v1/chat/completions"
    
    # Извлекаем IP адреса
    def extract_ip(url):
        host_part = url.split('://')[1].split('/')[0]
        if ':' in host_part:
            return host_part.split(':')[0]
        return host_part
    
    def get_ip_numeric(ip_str):
        return int(ipaddress.ip_address(ip_str))
    
    bot1_ip = extract_ip(bot1_url)
    bot2_ip = extract_ip(bot2_url)
    
    bot1_numeric = get_ip_numeric(bot1_ip)
    bot2_numeric = get_ip_numeric(bot2_ip)
    
    print(f"📊 Данные ботов:")
    print(f"   Bot1: {bot1_ip} -> {bot1_numeric}")
    print(f"   Bot2: {bot2_ip} -> {bot2_numeric}")
    print()
    
    # Проверяем логику
    print(f"🔍 Проверка логики:")
    print(f"   Bot1 < Bot2: {bot1_numeric < bot2_numeric}")
    print(f"   Bot1 > Bot2: {bot1_numeric > bot2_numeric}")
    print()
    
    # Определяем первого говорящего
    first_speaker = "Bot1" if bot1_numeric < bot2_numeric else "Bot2"
    print(f"🎭 Результат:")
    print(f"   Первый говорящий: {first_speaker}")
    
    if first_speaker == "Bot1":
        print("   ✅ ПРАВИЛЬНО: Bot1 (IP 87) начинает первым")
        print("   ✅ Логика работает корректно")
    else:
        print("   ❌ НЕПРАВИЛЬНО: Bot2 (IP 89) не должен начинать первым")
        print("   ❌ Логика работает неправильно")
    
    print()
    print("📋 Порядок выступления:")
    print(f"   1. {first_speaker} (IP: {bot1_ip if first_speaker == 'Bot1' else bot2_ip})")
    print(f"   2. {'Bot2' if first_speaker == 'Bot1' else 'Bot1'} (IP: {bot2_ip if first_speaker == 'Bot1' else bot1_ip})")

if __name__ == "__main__":
    test_ip_logic()
