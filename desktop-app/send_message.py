import paho.mqtt.publish as publish
import json

# Данные для отправки
message = {
    "device": "clock",
    "chipId": "1535762", 
    "clockId": "176f12",
    "room": "Room314",
    "ip": "1222333",
    "version": "1.0",
    "status": "connected",
    "firstBoot": False
}

# Отправка сообщения
try:
    publish.single("connections", 
                   json.dumps(message), 
                   hostname="172.20.193.73")
    print("✅ Сообщение успешно отправлено!")
    print(f"📨 IP {message['ip']} отправлен в топик connections")
except Exception as e:
    print(f"❌ Ошибка отправки: {e}")