void handleMQTT() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
  // oled.clear();
  // oled.println("Сообщение получено в топике: ");
  // oled.println(topic);

  Serial.print("Сообщение получено в топике: ");
  Serial.print(topic);
  Serial.print(". Сообщение: ");
  String messageTemp;

  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
    // oled.print((char)payload[i]);
    messageTemp += (char)payload[i];
  }
  Serial.println();

  if (String(topic) == room_name+"/sensors/temperature") {
    temperature = String(messageTemp).toInt();
  }
  if (String(topic) == room_name+"/sensors/humidity") {
    humidity = String(messageTemp).toInt();
  }
  if (String(topic) == room_name+"/sensors/pressure"){
    pressure = String(messageTemp).toInt();
  }
  if (String(topic) == "datetime"){
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, messageTemp);
  
    if (error) {
      Serial.print("Ошибка парсинга: ");
      Serial.println(error.c_str());
      return;
    }

    hours = doc["time"];
    minutes = doc["minutes"];
    seconds = doc["seconds"];
    day = doc["day"];
    month = doc["month"];
    year = doc["year"];

    client.unsubscribe("datetime");
    timeUpdated = false;
  }
  if (String(topic) == clock_id+"/messages"){
    String takenMessage, messageSender, messageTitle;
    int i = 0;
    while (messageTemp[i] != '^') {
      messageSender += messageTemp[i];
      i++;
    }
    i++;
    while (messageTemp[i] != '^') {
      messageTitle += messageTemp[i];
      i++;
    }
    i++;
    for (int j = i; j < length; j++) {
      takenMessage += messageTemp[j];
    }
    messageMenu.addItem(messageSender+": "+messageTitle, takenMessage);
  }
  // oled.update();
}

void reconnect() {
  oled.clear();
  if (!previousMqttConnectError || startMqttReconnect){
    oled.println("Попытка подключения");
    oled.println("к MQTT-брокеру...");
    if (client.connect("ESP8266Client")) {
      mqttErr = false;
      String topic = room_name+"/sensors";
      subscribeToTopics();
    } else {
      mqttErr = true;
      previousMqttConnectError = true;
    }

    if (mqttErr == true){
      oled.println("MQTT не доступен");

      startMqttReconnect = false;
      oled.update();
      delay(3000);
    }
    else {
      // oled.println("Соединение востановлено");
    }
  }
}

void subscribeToTopics() {
  String topics[] = {
    room_name + "/sensors/temperature",
    room_name + "/sensors/humidity",
    room_name + "/sensors/pressure",
    clock_id + "/messages"
  };
  
  for (String topic : topics) {
    if (client.subscribe(topic.c_str())) {
      Serial.println("Subscribed to: " + topic);
    }
  }
  if (!timeUpdated) {
    client.subscribe("datetime");
  }
}

void sendFirstConnectionMessage() {
  String message = "{";
  message += "\"device\": \"clock\",";
  message += "\"chipId\": \"" + String(ESP.getChipId()) + "\",";
  message += "\"clockId\": \"" + clock_id + "\",";
  message += "\"room\": \"" + room_name + "\",";
  message += "\"ip\": \"" + WiFi.localIP().toString() + "\",";
  message += "\"version\": \"1.0\",";
  message += "\"status\": \"connected\",";
  message += "\"firstBoot\": " + String(config.first_start ? "true" : "false");
  message += "}";
  
  String statusTopic = "connections";
  
  if (client.publish(statusTopic.c_str(), message.c_str())) {
    Serial.println("First connection message sent to: " + statusTopic);
    Serial.println("Message: " + message);
  } else {
    Serial.println("Failed to send first connection message");
  }
  
  // Также можно отправить простые сообщения в сенсорные топики
  String initTempTopic = room_name + "/sensors/initial";
  String initMessage = "Device initialized in room: " + room_name;
  client.publish(initTempTopic.c_str(), initMessage.c_str());
}