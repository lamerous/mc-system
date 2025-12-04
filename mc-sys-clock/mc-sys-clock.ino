#define IIC_SDA_PIN       4
#define IIC_SCL_PIN       5
#define BTN_PIN           12
#define BAT_FULL          3600
#define BAT_EMPTY         2600
#define AP_DEFAULT_SUFX   "CLOCK-"
#define AP_DEFAULT_PASS   "00000000"
#define EEPROM_SIZE       512
#define CONFIG_VERSION    "CFG_v1"

#include <Wire.h>
#include <elapsedMillis.h>
#include <GyverOLED_fix.h>
#include <GyverOLEDMenu.h>
#include <EncButton.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <PubSubClient.h>
#include <EEPROM.h>
#include <ArduinoJson.h>

ADC_MODE(ADC_VCC);

// Структура для хранения конфигурации
struct Config {
  char version[10];
  char wifi_ssid[32];
  char wifi_pass[64];
  char room_name[32];
  char mqtt_broker[40];
  int mqtt_port;
  bool first_start;
};

Config config;

class Menu {
  private:
    int cur_item = 0;
    int max_items = 0;
    int home_pos_x = 0;
    int home_pos_y = 0;
    GyverOLED<SSD1306_128x64>* oled;
    String* items = nullptr;
    String* messages = nullptr;
    
  public:
    Menu(GyverOLED<SSD1306_128x64>* oled_ptr);
    ~Menu();
    void selectNext();
    void addItem(String item, String message);
    void setHomePos(int x, int y);
    void draw();
    void draw_message();
    void changeItemName(int ind, String item);
    int getCurItem();
};

GyverOLED<SSD1306_128x64> oled;
Menu messageMenu(&oled);

Button btn(BTN_PIN);

WiFiClient espClient;
PubSubClient client(espClient);
ESP8266WebServer server(80);

int batMv = 2600;

uint32_t chipID = ESP.getChipId();
String ap_ssid = AP_DEFAULT_SUFX + String(chipID, HEX);
String clock_id = String(chipID, HEX);

int hours = 7;
int minutes = 37;
int seconds = 0;
int day = 27;
int month = 10;
int year = 2025;

String room_name = "";

float temperature = -999;
float humidity = -999;
float pressure = -999;

int cur_menu = 0;
int menu_count = 3;

bool showColon = true;
bool showDebugInfo = false;
bool mqttErr = false;
bool startMqttReconnect = false;
bool previousMqttConnectError = false;
bool draw_message = false;
bool sendedMqttGreeting = false;
bool timeUpdated = false;

elapsedMillis colonTimer;
elapsedMillis batteryCheckTimer;

void setup() {
  Serial.begin(9600);

  loadConfig();

  while (!oled.init(IIC_SDA_PIN, IIC_SCL_PIN)) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
  }

  for (uint8_t i = 0; i < 6; i++) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(30);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(30);
  }

  digitalWrite(LED_BUILTIN, HIGH);

  batMv = ESP.getVcc();

  Wire.setClock(600000L);

  messageMenu.setHomePos(0, 9);
  initMessageMenu();

  setupWebServer();

  if (config.first_start) {
    startAP();
    //setupWebServer();
  } else {
    connectToStoredWifi();
    
    if (WiFi.status() == WL_CONNECTED) {
      client.setServer(config.mqtt_broker, config.mqtt_port);
      client.setCallback(callback);
      delay(500);
    }
  }

  oled.clear();
  oled.update();
}

void loop() {
  btn.tick();
  handleWebClient();

  if (config.first_start) {
    firstStartUpMenu();
    return;
  }

  if (WiFi.status() == WL_CONNECTED && !config.first_start) {
    handleMQTT();
    if (!sendedMqttGreeting) {
      sendFirstConnectionMessage();
      sendedMqttGreeting = true;
    }
  }

  if (showDebugInfo) {
    showDebugInfoMenu();

    if (btn.click()) {
      WiFi.enableAP(false);
      connectToStoredWifi();
    
      if (WiFi.status() == WL_CONNECTED) {
        client.setServer(config.mqtt_broker, config.mqtt_port);
        client.setCallback(callback);
      }
      showDebugInfo = false;
    }

    return;
  }

  if (draw_message) {
    messageMenu.draw_message();
    if (btn.click()){
      draw_message = false;
    }
    return;
  }

  if (cur_menu == 2) {
    if (btn.click()){
      messageMenu.selectNext();
    }
    if (btn.hold() && messageMenu.getCurItem() != 0) {
      draw_message = true;
      return;
    }
  }

  // Основная логика
  if (btn.hold()) {
    cur_menu++;
    if (cur_menu >= menu_count) {
      cur_menu = 0;
    }
  }

  if (cur_menu == 0){
    if (btn.hasClicks(2)) {
      showDebugInfo = true;
    }
    if (btn.hasClicks(3)){
      startMqttReconnect = true;
    }
  }
  oled.clear();

  switch (cur_menu) {
    case 0:
      drawDateTimeMenu();
      break;
    case 1:
      roomInfoMenu();
      break;
    case 2:
      messageMenu.draw();
      break;
  }
  
  drawHeader();
  oled.update();
}