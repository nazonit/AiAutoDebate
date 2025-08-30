#!/usr/bin/env python3
"""
Простой тест для проверки IP адресов
"""

import ipaddress

def extract_ip_from_url(url):
    """Извлекает IP адрес из URL"""
    try:
        if '://' in url:
            host_part = url.split('://')[1].split('/')[0]
            if ':' in host_part:
                host = host_part.split(':')[0]
            else:
                host = host_part
            
            # Проверяем, является ли это IP адресом
            try:
                ipaddress.ip_address(host)
                return host
            except ValueError:
                return None
    except Exception:
        return None
    return None

def get_ip_numeric(ip_address):
    """Возвращает числовое представление IP для сравнения"""
    if not ip_address:
        return 0
    try:
        return int(ipaddress.ip_address(ip_address))
    except ValueError:
        return 0

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
        
        # Извлекаем IP адрес
        ip_address = extract_ip_from_url(url)
        numeric_value = get_ip_numeric(ip_address)
        
        print(f"   Извлеченный IP: {ip_address}")
        print(f"   Числовое значение: {numeric_value}")
        
        # Проверяем, что IP извлечен правильно
        if ip_address:
            try:
                ip_obj = ipaddress.ip_address(ip_address)
                print(f"   Валидный IP: ✅")
                print(f"   IP версия: IPv{ip_obj.version}")
            except ValueError:
                print(f"   Валидный IP: ❌")
        else:
            print(f"   IP не извлечен: ❌")
    
    # Тестируем сравнение IP адресов
    print(f"\n🔍 Тест сравнения IP адресов:")
    print("-" * 30)
    
    bot1_url = "http://192.168.8.87:12345/v1/chat/completions"
    bot2_url = "http://192.168.8.89:1234/v1/chat/completions"
    
    bot1_ip = extract_ip_from_url(bot1_url)
    bot2_ip = extract_ip_from_url(bot2_url)
    
    bot1_numeric = get_ip_numeric(bot1_ip)
    bot2_numeric = get_ip_numeric(bot2_ip)
    
    print(f"Bot1 IP (87): {bot1_ip} -> {bot1_numeric}")
    print(f"Bot2 IP (89): {bot2_ip} -> {bot2_numeric}")
    print(f"Bot1 < Bot2: {bot1_numeric < bot2_numeric}")
    
    # Определяем первого говорящего
    first_speaker = "Bot1" if bot1_numeric < bot2_numeric else "Bot2"
    print(f"Первый говорящий: {first_speaker}")
    
    if first_speaker == "Bot1":
        print("✅ Логика правильная: Bot1 (IP 87) начинает первым")
    else:
        print("❌ Логика неправильная: Bot2 (IP 89) не должен начинать первым")

if __name__ == "__main__":
    test_ip_extraction()
