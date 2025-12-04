void loadConfig() {
  EEPROM.begin(EEPROM_SIZE);
  EEPROM.get(0, config);
  EEPROM.end();

  if (String(config.version) != CONFIG_VERSION) {
    Serial.println("Invalid config version, resetting to defaults");
    resetConfig();
  }
  if (strlen(config.room_name) > 0) {
    room_name = String(config.room_name);
  }
}

void saveConfig() {
  strcpy(config.version, CONFIG_VERSION);
  
  EEPROM.begin(EEPROM_SIZE);
  EEPROM.put(0, config);
  EEPROM.commit();
  EEPROM.end();
  
  Serial.println("Configuration saved");
}

void resetConfig() {
  strcpy(config.version, CONFIG_VERSION);
  strcpy(config.wifi_ssid, "");
  strcpy(config.wifi_pass, "");
  strcpy(config.room_name, "room1");
  strcpy(config.mqtt_broker, "");
  config.mqtt_port = 0;
  config.first_start = true;
  
  saveConfig();
}

void connectToStoredWifi() {
  if (strlen(config.wifi_ssid) == 0) {
    Serial.println("No WiFi credentials stored");
    return;
  }
  
  Serial.print("Connecting to ");
  Serial.println(config.wifi_ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(config.wifi_ssid, config.wifi_pass);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi");
  }
}