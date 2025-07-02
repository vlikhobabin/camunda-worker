#!/usr/bin/env python3
"""
Проверка состояния RabbitMQ очередей
"""

# Добавление родительского каталога в sys.path для импорта модулей проекта
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rabbitmq_client import RabbitMQClient

def main():
    """Проверить состояние всех очередей"""
    print("🐰 ПРОВЕРКА RABBITMQ ОЧЕРЕДЕЙ")
    print("=" * 40)
    
    client = RabbitMQClient()
    
    if client.connect():
        print("✅ Подключение к RabbitMQ успешно")
        
        queues_info = client.get_all_queues_info()
        
        if queues_info:
            print(f"\n📊 Найдено очередей: {len(queues_info)}")
            
            for queue_name, info in queues_info.items():
                msg_count = info.get("message_count", 0)
                consumer_count = info.get("consumer_count", 0)
                
                status_icon = "📬" if msg_count > 0 else "📭"
                consumer_icon = "👥" if consumer_count > 0 else "🚫"
                
                print(f"\n{status_icon} {queue_name}:")
                print(f"   📨 Сообщений: {msg_count}")
                print(f"   {consumer_icon} Потребителей: {consumer_count}")
                
                if msg_count > 0:
                    print(f"   ⚠️ В очереди есть необработанные сообщения!")
        else:
            print("❌ Не удалось получить информацию об очередях")
        
        client.disconnect()
    else:
        print("❌ Не удалось подключиться к RabbitMQ")

if __name__ == "__main__":
    main() 