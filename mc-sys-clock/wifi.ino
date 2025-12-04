void connectWifi() {
  delay(10);

  WiFi.mode(WIFI_STA);
  WiFi.begin(config.wifi_ssid, config.wifi_pass);

  oled.clear();
  oled.println("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    oled.print(".");
    oled.update();
  }
  oled.clear();
  oled.home();

  oled.println("WiFi подключен");
  oled.println("IP адрес: ");
  oled.println(WiFi.localIP());

  oled.update();
  delay(5000);
}

void startAP() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ap_ssid.c_str(), AP_DEFAULT_PASS);
  delay(1000);
  
  Serial.println("AP started:");
  Serial.println("SSID: " + ap_ssid);
  Serial.println("IP: " + WiFi.softAPIP().toString());
}