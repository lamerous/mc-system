# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
import paho.mqtt.client as mqtt
from room import Room
from user import User
from user import User
import sys
import io
import threading
from PyQt5.QtCore import pyqtSignal
from host_dialog import HostDialog
from port_dialog import PortDialog
from PyQt5.QtWidgets import QDialog



class MyWindow(QtWidgets.QMainWindow):
    update_room_signal = pyqtSignal(object)
    def on_pushButton_clicked(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)
    
    def setup_climate_controls(self):
        self.minHumSpinBox.setRange(0.0, 100.0)
        self.minHumSpinBox.setDecimals(1)
        self.minHumSpinBox.setSuffix(" %")
        
        self.maxHumSpinBox.setRange(0.0, 100.0)
        self.maxHumSpinBox.setDecimals(1)
        self.maxHumSpinBox.setSuffix(" %")
        
        self.minTempSpinBox.setRange(-20.0, 50.0)
        self.minTempSpinBox.setSingleStep(0.1)
        self.minTempSpinBox.setSuffix("°C")  
        
        self.maxTempSpinBox.setRange(-20.0, 50.0)
        self.maxTempSpinBox.setSingleStep(0.1)
        self.maxTempSpinBox.setSuffix("°C") 
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Обработка подключения к MQTT брокеру"""
        if rc == 0:
            print("Успешно подключено к MQTT брокеру")
        else:
            print(f"Ошибка подключения MQTT. Код: {rc}")

    def show_host_dialog(self):
        dialog = HostDialog(self.mqtt_broker_host, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_host = dialog.get_host().strip()
            
            if not new_host:
                QMessageBox.warning(self, "Ошибка", "Хост не может быть пустым")
                return
            
            if new_host == self.mqtt_broker_host:
                self.statusBar().showMessage("Хост не изменился", 2000)
                return
            
            # Сохраняем старое значение
            old_host = self.mqtt_broker_host
            
            # Обновляем значение
            self.mqtt_broker_host = new_host
            
            # Пытаемся сохранить
            if self.save_mqtt_config():
                self.statusBar().showMessage(
                    f"Хост изменен: {old_host} → {new_host}", 
                    3000
                )
                
                QMessageBox.information(
                    self,
                    "Успешно",
                    f"Хост MQTT брокера изменен:\n\n"
                    f"Было: {old_host}\n"
                    f"Стало: {new_host}\n\n"
                    f"Настройки сохранены в файл."
                )
                
                print(f"✅ Хост изменен: {old_host} → {new_host}")
            else:
                # Откатываем при ошибке
                self.mqtt_broker_host = old_host
                QMessageBox.warning(
                    self, 
                    "Ошибка сохранения", 
                    f"Не удалось сохранить хост {new_host} в файл.\n"
                    f"Восстановлен предыдущий хост: {old_host}"
                )
                print(f"❌ Ошибка сохранения, откат к {old_host}")

    
    def show_port_dialog(self):
        dialog = PortDialog(self.mqtt_broker_port, self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_port = dialog.get_port()
            
            if new_port == self.mqtt_broker_port:
                self.statusBar().showMessage("Порт не изменился", 2000)
                return
            
            # Сохраняем старое значение
            old_port = self.mqtt_broker_port
            
            # Обновляем значение
            self.mqtt_broker_port = new_port
            
            # Пытаемся сохранить
            if self.save_mqtt_config():
                self.statusBar().showMessage(
                    f"Порт изменен: {old_port} → {new_port}", 
                    3000
                )
                
                QMessageBox.information(
                    self,
                    "Успешно",
                    f"Порт MQTT брокера изменен:\n\n"
                    f"Было: {old_port}\n"
                    f"Стало: {new_port}\n\n"
                    f"Настройки сохранены в файл."
                )
                
                print(f"✅ Порт изменен: {old_port} → {new_port}")
            else:
                # Откатываем при ошибке
                self.mqtt_broker_port = old_port
                QMessageBox.warning(
                    self, 
                    "Ошибка сохранения", 
                    f"Не удалось сохранить порт {new_port} в файл.\n"
                    f"Восстановлен предыдущий порт: {old_port}"
                )
                print(f"❌ Ошибка сохранения, откат к {old_port}")

    def setup_mqtt(self):
        """Настройка MQTT клиента"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            self.mqtt_client.connect(self.mqtt_broker_host,self.mqtt_broker_port, 60)  
            self.mqtt_client.loop_start()
            self.mqtt_client.subscribe("connections")
            print("✅ Подписались на топик connections")
        except Exception as e:
            print(f"Ошибка подключения к MQTT: {str(e)}")


    def upload_rooms_from_file(self):
        file_path = "rooms.txt"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if ':' in line:
                        room_name = line.split(':', 1)[0].strip()
                        ip_address = line.split(':', 1)[1].strip()
                       
                        
                        # ВТОРОЕ: создаем комнату
                        self.create_and_register_room(room_name, ip_address)
                        print(f"Добавлена комната: '{room_name}' -> '{ip_address}'")
                        
                    else:
                        print(f"Пропущена строка без разделителя ':': {line}")
                        
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл rooms.txt не найден.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при чтении файла: {str(e)}")

    def create_and_register_room(self, room_name, ip_address):
        room = Room(room_name, ip_address)
        self.rooms.append(room)
        room.current_temperature = 23.5
        room.current_humidity = 40

        # Подписываемся на топики
        self.mqtt_client.subscribe(f"{room_name}/sensors/temperature")
        self.mqtt_client.subscribe(f"{room_name}/sensors/humidity")
        self.mqtt_client.subscribe(f"{room_name}/sensors/gases")
        print(f"Подписались на топики для комнаты: {room_name}")
        
        # Создаем запись с начальными значениями
        list_entry = f"Комната: {room.name} | Температура: {room.current_temperature}°C | Влажность: {room.current_humidity}% | Газы: {'Есть' if room.has_gas else 'Нет'}"
        self.listWidget.addItem(list_entry)
        
        # Сохраняем ссылку на элемент для обновления
        room.list_widget_item = self.listWidget.item(self.listWidget.count() - 1)
        
        self.roomsComboBox.addItem(room_name)
        self.deleteRoomcomboBox.addItem(room_name)
        
        if not self.toDeleteRoomButton.isVisible():
            self.toDeleteRoomButton.setVisible(True)

    def process_connection_message(self, payload):
        """Обработка сообщений из топика connections - связь IP и clock_id"""
        try:
            import json
            data = json.loads(payload)
            
            clock_id = data.get('clockId', '')
            room_name = data.get('room', '')
            ip = data.get('ip', '')
            
            if ip and clock_id and room_name:
                # Добавляем IP в историю
                self.connections_history.add(ip)
                print(f"✅ IP {ip} добавлен в историю подключений")
                
                # ✅ Создаем структуру для связи IP и clock_id
                device_info = {
                    'ip': ip,
                    'clock_id': clock_id,
                    'room': room_name
                }
                
                # ✅ Добавляем в список устройств
                self.connections_clock_id.append(device_info)
                
                # ✅ Добавляем в словарь: ключ = IP, значение = clock_id
                self.connections_devices[ip] = clock_id
                
                print(f"✅ Устройство добавлено: IP={ip}, ClockID={clock_id}, Room={room_name}")
                        
        except json.JSONDecodeError:
            print(f"❌ Ошибка парсинга JSON: {payload}")
        except Exception as e:
            print(f"❌ Ошибка обработки connection сообщения: {str(e)}")


    def check_ip_in_users(self, ip):
        """Проверяет IP в списке пользователей и возвращает 1 если известный, 0 если нет"""
        # Предполагая, что у вас есть список пользователей в self.users
        for user in getattr(self, 'users', []):
            # В зависимости от структуры вашего объекта пользователя
            if hasattr(user, 'ip_address') and user.ip_address == ip:
                return 1
            elif isinstance(user, dict) and user.get('ip') == ip:
                return 1
            elif isinstance(user, str) and user == ip:
                return 1
        return 0
    
    def send_alarm_to_room(self, room_name, alarm_type, message):
        """Публикация alarm сообщения в простом JSON формате"""
        try:
            import json
            from paho.mqtt import publish
            
            # ✅ Простой JSON с заголовком и текстом
            alarm_data = {
                "title": "ALARM",          # Заголовок ALARM
                "message": message         # Текст сообщения
            }
            
            # Публикуем JSON в топик room_name/alarm
            topic = f"{room_name}/alarm"
            publish.single(topic, json.dumps(alarm_data), hostname=self.mqtt_broker_host)
            
            print(f"✅ Alarm опубликован в топик {topic}: {message}")
            
        except Exception as e:
            print(f"❌ Ошибка публикации alarm: {e}")


    def on_mqtt_message(self, client, userdata, msg):
        """Обработка входящих MQTT сообщений"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            print(f"Получено MQTT: {topic} -> {payload}")
            
            if topic == "connections":
                self.process_connection_message(payload)
                return
            
            # Разбираем топик: room_name/sensors/temperature
            parts = topic.split('/')
            if len(parts) >= 3:
                room_name = parts[0]
                sensor_type = parts[2]  # temperature, humidity, gases
                
                # Находим комнату
                for room in self.rooms:
                    if room.name == room_name:
                        if sensor_type == "temperature":
                            room.current_temperature = float(payload)
                            print(f"Обновлена температура для {room_name}: {payload}°C")
                            
                            # ✅ ПРОВЕРКА ТЕМПЕРАТУРЫ И ОТПРАВКА ALARM
                            if not room.is_temperature_normal():
                                alarm_msg = f"Температура: {payload}°C (норма: {room.min_temperature}-{room.max_temperature}°C)"
                                self.send_alarm_to_room(room_name, "temperature", alarm_msg)
                            
                        elif sensor_type == "humidity":
                            room.current_humidity = float(payload)
                            print(f"Обновлена влажность для {room_name}: {payload}%")
                            
                            # ✅ ПРОВЕРКА ВЛАЖНОСТИ И ОТПРАВКА ALARM
                            if not room.is_humidity_normal():
                                alarm_msg = f"Влажность: {payload}% (норма: {room.min_humidity}-{room.max_humidity}%)"
                                self.send_alarm_to_room(room_name, "humidity", alarm_msg)
                            
                        elif sensor_type == "gases":
                            room.has_gas = (payload == "1")
                            gas_status = "Есть" if room.has_gas else "Нет"
                            print(f"Обновлены газы для {room_name}: {gas_status}")
                            
                            # ✅ ПРОВЕРКА ГАЗА И ОТПРАВКА ALARM
                            if room.has_gas:
                                alarm_msg = "Обнаружена утечка газа!"
                                self.send_alarm_to_room(room_name, "gas", alarm_msg)
                        
                        # Обновляем отображение
                        self.update_room_signal.emit(room) 
                        break
            else:
                print(f"Неизвестный формат топика: {topic}")
                        
        except Exception as e:
            print(f"Ошибка обработки MQTT сообщения: {str(e)}")


    def update_room_display(self, room):
        """Обновление отображения комнаты в listWidget"""
        if hasattr(room, 'list_widget_item') and room.list_widget_item:
            new_text = f"Комната: {room.name} | Температура: {room.current_temperature}°C | Влажность: {room.current_humidity}% | Газы: {'Есть' if room.has_gas else 'Нет'}"
            room.list_widget_item.setText(new_text)


    def setup_time_broadcast(self):
        """Настройка регулярной отправки времени каждую минуту"""
        from PyQt5.QtCore import QTimer
        
        # Создаем таймер
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.send_time_to_all_devices)
        
        # Запускаем каждую минуту (60000 мс)
        self.time_timer.start(3600000)
        
        # Сразу отправляем время при запуске
        self.send_time_to_all_devices()
        
        print("✅ Таймер отправки времени запущен (каждую секунду)")

    def send_message_to_device(self, clock_id, title, message, sender):
        """Отправка сообщения на конкретное устройство по clock_id"""
        try:
            import json
            from paho.mqtt import publish
            
            # Формируем JSON сообщение
            msg_data = {
                "sender": sender,
                "title": title, 
                "message": message
            }
            
            # Топик вида: clock_id/messages (например: "clock_001/messages")
            topic = f"{clock_id}/messages"
            
            # Отправка
            publish.single(topic, json.dumps(msg_data), hostname=self.mqtt_broker_host)
            print(f"✅ Сообщение отправлено на {clock_id}: {title}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")


    def send_time_to_all_devices(self):
        """Публикация времени в топик datetime для всех устройств"""
        import datetime
        from paho.mqtt import publish  # ← ИМПОРТ ТУТ
        
        now = datetime.datetime.now()
        time_str = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d} {now.day:02d}.{now.month:02d}.{now.year}"
        
        try:
            # ✅ ПРАВИЛЬНЫЙ ВЫЗОВ
            publish.single("datetime", time_str, hostname=self.mqtt_broker_host)
            print(f"✅ Время отправлено в топик datetime: {time_str}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки времени: {e}")


    def upload_users_from_file(self):
        file_path = "users.txt"
    
        try:
            with open(file_path, 'r',  encoding='utf-8') as file:  # Убрал encoding
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                
                    if ':' in line:
                        user_name = line.split(':', 1)[0].strip()
                        ip_address = line.split(':', 1)[1].strip()
                        self.add_user_from_file(user_name, ip_address)
                    
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл пользователей не найден.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при чтении файла: {str(e)}")
    
    
    
    def on_addRoomButton_pressed(self):
      self.stackedWidget.setCurrentWidget(self.addRoomPage)


    def add_user_from_file(self, user_name, ip_address):
        """Добавление пользователя при загрузке из файла (без проверки подключений)"""
        
        # 1. Проверяем, нет ли уже пользователя с таким IP в списке
        if self.is_ip_exists_in_users(ip_address):
            print(f"ℹ️ Пользователь с IP {ip_address} уже существует в списке (пропускаем)")
            return False
        
        # 2. Добавляем пользователя без проверки подключений
        new_user = User(user_name, ip_address)
        self.users.append(new_user)

        # Обновляем интерфейс
        if self.toDeleteEmpButton.isHidden():
            self.toDeleteEmpButton.setVisible(True)

        self.userComboBox.addItem(new_user.name)
        self.deleteEmployercomboBox.addItem(new_user.name)
        
        print(f"✓ Пользователь {user_name} с IP {ip_address} загружен из файла")
        return True
    

    def add_user_to_list(self, user_name, ip_address):
        """Добавление пользователя с проверкой существующего IP и наличия в топике connections"""
        
        # 1. Проверяем, нет ли уже пользователя с таким IP в списке
        if self.is_ip_exists_in_users(ip_address):
            print(f"Ошибка: Пользователь с IP {ip_address} уже существует в списке")
            QMessageBox.warning(self, "Ошибка", f"Пользователь с IP {ip_address} уже существует в списке!")
            return False
        
        # 2. Проверяем, есть ли такой IP в сообщениях из топика connections
        if not self.is_ip_in_connections(ip_address):
            print(f"Ошибка: IP {ip_address} не найден в топике connections")
            QMessageBox.warning(self, "Ошибка", 
                            f"IP {ip_address} не найден в подключениях!\n"
                            f"Сначала устройство должно отправить сообщение в топик connections.")
            return False
        
        # 3. Если обе проверки пройдены - добавляем пользователя
        new_user = User(user_name, ip_address)
        self.users.append(new_user)

        # Обновляем интерфейс
        if self.toDeleteEmpButton.isHidden():
            self.toDeleteEmpButton.setVisible(True)

        self.userComboBox.addItem(new_user.name)
        self.deleteEmployercomboBox.addItem(new_user.name)
        
        print(f"✓ Пользователь {user_name} с IP {ip_address} успешно добавлен")
        QMessageBox.information(self, "Успех", f"Пользователь {user_name} успешно добавлен")
        return True
 
    def update_delete_buttons_visibility(self):
        self.toDeleteRoomButton.setHidden(len(self.rooms) == 0)
        self.toDeleteEmpButton.setHidden(len(self.users) == 0)

    def is_ip_exists_in_users(self, ip):
        """Проверяет, есть ли IP в списке пользователей"""
        for user in self.users:
            if hasattr(user, 'ip_address') and user.ip_address == ip:
                return True
        return False

    def is_ip_in_connections(self, ip):
        """Проверяет, есть ли IP в истории подключений"""
        return ip in self.connections_history

    def write_room_to_text(self, file, room_name, ip_address):
        file.write(f"{room_name}: {ip_address}\n")

    def on_addRoomViewButton_pressed(self):
        import time
        
        
        self._adding_room = True
        
        try:
            room_name = self.roomNameLine.text().strip()
            ip_address = self.IPaddressLine.text().strip()
            print(f"Данные: комната='{room_name}', IP='{ip_address}'")

            # Проверка: не пустые ли поля
            if not room_name:
                print("Ошибка: пустое название комнаты")
                QMessageBox.warning(self, "Ошибка", "Поле 'Название комнаты' не может быть пустым")
                return
                
            if not ip_address:
                print("Ошибка: пустой IP-адрес")
                QMessageBox.warning(self, "Ошибка", "Поле 'IP-адрес' не может быть пустым")
                return

            try:
                with open("rooms.txt", 'a', encoding='utf-8') as file:
                    self.write_room_to_text(file, room_name, ip_address)
                    print("Файл записан успешно")
            except Exception as e:
                print(f"Ошибка записи в файл: {e}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось записать в файл: {str(e)}")
                return

            self.create_and_register_room(room_name, ip_address)
            self.update_delete_buttons_visibility()
            
            # Возврат на главную страницу
            self.stackedWidget.setCurrentWidget(self.infoRoomPage)
            print("Успешно завершено")
            
        finally:
            self._adding_room = False
            print(f"=== ВЫПОЛНЕНИЕ ЗАВЕРШЕНО в {time.time()} ===\n")
            
    def write_user_to_text(self, file, name, ip_address):
        file.write(f"{name}: {ip_address}\n")


    def on_addEmployer_pressed(self):
        ip_address = self.ipEmpLineEdit.text().strip()
        name = self.nameLineEdit.text().strip()
        
        # ПРОВЕРКА: НЕ ПУСТЫЕ ЛИ ПОЛЯ
        if not name:
            QMessageBox.warning(self, "Ошибка", "Поле 'Имя сотрудника' не может быть пустым")
            return
            
        if not ip_address:
            QMessageBox.warning(self, "Ошибка", "Поле 'IP-адрес' не может быть пустым")
            return
        
        try:
            with open("users.txt", 'a', encoding='utf-8') as file:
                self.write_user_to_text(file, name, ip_address)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось записать в файл: {str(e)}")
            return

        self.add_user_to_list(name, ip_address)
        # УБИРАЕМ ОЧИСТКУ ПОЛЕЙ
        # self.nameLineEdit.clear()
        # self.ipEmpLineEdit.clear()
        self.update_delete_buttons_visibility()
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)
    
        
    def rewrite_user_file(self):
        try:
            with open("users.txt", 'w',  encoding='utf-8') as file:  # Без encoding
                for user in self.users:
                    self.write_user_to_text(file, user.name, user.ip_address)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось перезаписать файл: {str(e)}")


    def on_pushButton_5_pressed(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_addEmployerButton_pressed(self):
        self.stackedWidget.setCurrentWidget(self.addEmpPage)

    def on_setButton_pressed(self):
        selected_room_name = self.roomsComboBox.currentText()
        if not selected_room_name:
            return

        for room in self.rooms:
            if room.name == selected_room_name:
                min_hum = self.minHumSpinBox.value()
                max_hum = self.maxHumSpinBox.value()
                min_temp = self.minTempSpinBox.value()
                max_temp = self.maxTempSpinBox.value()

                # Проверка: если оба значения влажности равны 0 — не сохраняем
                if min_hum == 0 and max_hum == 0:
                    QMessageBox.warning(self, "Некорректные значения",
                        "Минимальная и максимальная влажность равны 0.\nПожалуйста, введите корректные пороги.")
                    return

                # Сохраняем пороги
                room.min_humidity = min_hum
                room.max_humidity = max_hum
                room.min_temperature = min_temp
                room.max_temperature = max_temp

                QMessageBox.information(self, "Параметры сохранены",
                    f"Для комнаты \"{room.name}\" установлены пороги:\n"
                    f"Влажность: {min_hum}% – {max_hum}%\n"
                    f"Температура: {min_temp}°C – {max_temp}°C")
                break

        self.reset_threshold_fields()


    def rewrite_room_file(self):
        try:
            with open("rooms.txt", 'w',  encoding='utf-8') as file:  # Без encoding
                for room in self.rooms:
                    self.write_room_to_text(file, room.name, room.ip_address)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось перезаписать файл комнат: {str(e)}")

    def on_clearButton_pressed(self):
        self.reset_threshold_fields()

    def on_sendMessage_pressed(self):
        self.stackedWidget.setCurrentWidget(self.sendMessagePage)

    def on_sendMessageButton_pressed(self):
        # Получаем текст сообщения из поля ввода
        message_text = self.messageLineEdit.toPlainText().strip()
        if not message_text:
            QMessageBox.warning(self, "Ошибка", "Введите текст сообщения.")
            return
        
        title_of_message = self.messageLineEdit_2.toPlainText().strip()
        if not title_of_message:
            QMessageBox.warning(self, "Ошибка", "Введите название сообщения.")
            return
        
        # Получаем выбранного пользователя из комбобокса
        selected_name = self.userComboBox.currentText()
        
        # Находим IP адрес выбранного пользователя из self.users
        target_ip = None
        for user in self.users:
            if user.name == selected_name:
                target_ip = user.ip_address
                break
        
        if not target_ip:
            QMessageBox.warning(self, "Ошибка", "Не найден IP адрес для выбранного пользователя.")
            return
        
        # ✅ Находим clock_id из device_info по IP адресу
        target_clock_id = None
        for device in self.connections_clock_id:
            if device['ip'] == target_ip:  # Сравниваем IP адреса
                target_clock_id = device['clock_id']
                break
        
        if not target_clock_id:
            QMessageBox.warning(self, "Ошибка", "Не найден clock_id для устройства.")
            return
        
        try:
            # Отправляем сообщение на устройство
            self.send_message_to_device(
                clock_id=target_clock_id,  # ✅ Отправляем в топик clock_id
                title=title_of_message,
                message=message_text,
                sender=selected_name
            )
            
            # Очищаем поле ввода
            self.messageLineEdit.clear()
            self.messageLineEdit_2.clear()
            QMessageBox.information(self, "Успех", f"Сообщение отправлено на {selected_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение: {str(e)}")





    def reset_threshold_fields(self):
        self.minTempSpinBox.setValue(0)
        self.maxTempSpinBox.setValue(0)
        self.minHumSpinBox.setValue(0)
        self.maxHumSpinBox.setValue(0)


    def on_undoEmpButton_cpressed(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_undoRoomButton_pressed(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_exitButton_pressed(self):
        self.close()

    def on_undoEmpButton_pressed(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_pushButton_6_pressed(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_pushButton_2_pressed(self):
        # переключаем stackedWidget на страницу setLimitPage
        self.stackedWidget.setCurrentWidget(self.setLimitPage)

    def on_deleteRoomButton_pressed(self):
        selected_room_name = self.deleteRoomcomboBox.currentText()
        if not selected_room_name:
            return

        # Найти и удалить комнату из списка
        for i, room in enumerate(self.rooms):
            if room.name == selected_room_name:
                del self.rooms[i]
                break

        # Удалить из deleteRoomcomboBox
        current_index = self.deleteRoomcomboBox.currentIndex()
        if current_index != -1:
            self.deleteRoomcomboBox.removeItem(current_index)

        # Удалить из roomsComboBox
        index_rooms = self.roomsComboBox.findText(selected_room_name)
        if index_rooms != -1:
            self.roomsComboBox.removeItem(index_rooms)

        # Удалить из listWidget
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item_text = item.text()

            # Проверяем, начинается ли строка с "Комната: <selected_room_name>"
            if item_text.startswith(f"Комната: {selected_room_name}"):
                item = self.listWidget.takeItem(i)  # Удаляем из виджета
                del item  # Освобождаем память
                break

        self.rewrite_room_file()
        self.update_delete_buttons_visibility()
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_deleteEmployerButton_pressed(self):
        selected_user_name = self.deleteEmployercomboBox.currentText()
        if not selected_user_name:
            return

        # Найти и удалить пользователя из списка
        for i, user in enumerate(self.users):
            if user.name == selected_user_name:
                del self.users[i]
                break

        # Удалить из deleteEmployercomboBox
        index_delete = self.deleteEmployercomboBox.findText(selected_user_name)
        if index_delete != -1:
            self.deleteEmployercomboBox.removeItem(index_delete)

        # Удалить из userComboBox
        index_user = self.userComboBox.findText(selected_user_name)
        if index_user != -1:
            self.userComboBox.removeItem(index_user)

        # Перезаписать файл пользователей
        self.rewrite_user_file()

        self.update_delete_buttons_visibility()
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_pushButton_5_pressed(self):
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def on_toDeleteRoomButton_pressed(self):
        self.stackedWidget.setCurrentWidget(self.deleteRoomPage)

    def on_toDeleteEmpButton_pressed(self):
        self.stackedWidget.setCurrentWidget(self.deleteEmployerPage)

    def on_clearMessageButton_pressed(self):
        self.messageLineEdit.clear()
        self.messageLineEdit_2.clear()


    def closeEvent(self, event):
        
        self.mqtt_running = False
        if hasattr(self, 'mqtt_thread') and self.mqtt_thread.is_alive():
            self.mqtt_thread.join(timeout=1.0)
        super().closeEvent(event)


    def setup_mqtt_async(self):
    
        self.mqtt_running = True
        
        # Запускаем setup_mqtt в отдельном потоке
        self.mqtt_thread = threading.Thread(target=self.setup_mqtt)
        self.mqtt_thread.daemon = True
        self.mqtt_thread.start()


    def load_mqtt_config(self):
        try:  
            with open("mqtt_config.txt", 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('host='):
                        self.mqtt_broker_host = line[5:].strip()
                        print(f"✅ Загружен MQTT хост: {self.mqtt_broker_host}")
                    elif line.startswith('port='):
                        self.mqtt_broker_port = int(line[5:].strip())
                        print(f"✅ Загружен MQTT порт: {self.mqtt_broker_port}")
            
        except FileNotFoundError:
            print("❌ Файл mqtt_config.txt не найден!")
            raise
        except ValueError as e:
            print(f"❌ Ошибка в значении порта: {e}")
            raise
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            raise

    def save_mqtt_config(self):
        """Сохранить настройки MQTT в файл"""
        try:
            with open("mqtt_config.txt", 'w', encoding='utf-8') as f:
                f.write(f"host={self.mqtt_broker_host}\n")
                f.write(f"port={self.mqtt_broker_port}\n")
            
            print(f"✅ Файл успешно сохранен")
            return True  
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False 
        
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)
        
        self.update_room_signal.connect(self.update_room_display)

        self.actionMQTT_Broker.triggered.connect(self.show_host_dialog)
        self.actionMQTT_Port.triggered.connect(self.show_port_dialog)

        self.rooms = []
        self.users = []
        self.load_mqtt_config()
        self.connections_devices = {}
        self.connections_clock_id = []
        self.connections_history = set()
        self.setup_mqtt_async()
        self.setup_time_broadcast()
        self.setup_climate_controls()
        self.upload_rooms_from_file()
        self.upload_users_from_file()
        self.update_delete_buttons_visibility()
        self.stackedWidget.setCurrentWidget(self.infoRoomPage)

    def __del__(self):
        self.rooms.clear()
        self.users.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()