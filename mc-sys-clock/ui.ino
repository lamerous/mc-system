void initMessageMenu() {
  messageMenu.addItem("    --- ДАЛЬШЕ ---", "");
}

void checkBatteryCharge() {
  if (batteryCheckTimer >= 5000){
    batMv = ESP.getVcc();
    batteryCheckTimer = 0;
  }
}

void drawHeader() {
  const int bat_pos_x = 110;
  const int bat_pos_y = 1;
  const int bat_width = 10;
  const int bat_height = 5;

  oled.home();
  oled.print(F("BIMO"));

  // Рисуем индикатор заряда
  float capacity = BAT_FULL - BAT_EMPTY;
  float cur_capacity = batMv - BAT_EMPTY;
  float charge = cur_capacity / capacity;

  oled.setCursorXY(30, 0);
  // left for debug info
  if (mqttErr){
    oled.print(F("MQTT ERR"));
  }

  int percent_charge = charge*100;

  oled.setCursorXY(94, 0);
  if (percent_charge < 10){
    oled.setCursorXY(102, 0);
  }
  if (percent_charge == 100) {
    oled.setCursorXY(86, 0);
  }
  oled.print(percent_charge);

  oled.rect(bat_pos_x, bat_pos_y, bat_pos_x + bat_width, bat_pos_y + bat_height, OLED_STROKE);
  oled.rect(bat_pos_x, bat_pos_y, bat_pos_x+bat_width*charge, bat_pos_y + bat_height, OLED_FILL);

  oled.fastLineV(bat_pos_x + bat_width + 1, bat_pos_y + 1, bat_pos_y + bat_height - 2);

  oled.fastLineH(8, 0, 128);
}

void firstStartUpMenu() {
  if (!config.first_start) return;
  
  oled.clear();

  oled.setCursorXY(0, 16);
  oled.setScale(1);

  oled.print("SSID: "); oled.println(ap_ssid);
  oled.print("PASS: "); oled.println(AP_DEFAULT_PASS);
  oled.print("IP: "); oled.println(WiFi.softAPIP());

  oled.autoPrintln(1);
  oled.println("Web config available");
  oled.autoPrintln(0);

  drawHeader();

  oled.update();
}

void showDebugInfoMenu() {
  oled.clear();
  drawHeader();
  oled.setCursorXY(0, 16);

  oled.println("INFO MENU");
  oled.print("IP: "); oled.println(WiFi.localIP());
  oled.print("MQTT: "); oled.println(String(config.mqtt_broker));

  oled.update();
}

void drawDateTimeMenu() {
  // Время
  if (colonTimer >= 500) {
    showColon = !showColon;
    colonTimer = 0;
  }

  oled.setScale(2);
  oled.setCursorXY(35, 22);
  
  if (hours < 10) {
    oled.print("0");
  }
  oled.print(hours);
  oled.print(showColon ? ":" : " ");
  
  if (minutes < 10) {
    oled.print("0");
  }
  oled.print(minutes);

  // Дата
  oled.setScale(1);
  oled.setCursorXY(34, 40);
  
  if (day < 10) {
    oled.print("0");
  }
  oled.print(day);
  oled.print(".");
  
  if (month < 10) {
    oled.print("0");
  }
  oled.print(month);
  oled.print(".");
  oled.print(year);
}

void roomInfoMenu() {
  oled.setCursorXY(0, 10);
  oled.println(room_name);

  oled.setCursorXY(0, 24);
  oled.print("Темп.: "); oled.print(temperature); oled.println(" C");
  oled.print("Влаж.: "); oled.print(humidity);    oled.println(" %");
  oled.print("Давл.: "); oled.print(pressure);    oled.println(" Pa");
}