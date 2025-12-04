#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <elapsedMillis.h>

#define DHT_PIN 8
#define DHT_TYPE DHT22
#define GAS_PIN A3
#define GAS_D_PIN 7

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

String mqtt_server = "192.168.0.106";
//IPAddress ip(169, 254, 190, 224);
int mqtt_port = 1883;
String room_name = "room1";
int duration = 1000;

elapsedMillis sendTimer;

EthernetClient ethClient;
EthernetServer server(80);
PubSubClient mqttClient(ethClient);

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  pinMode(6, OUTPUT);
  pinMode(GAS_D_PIN, INPUT);
  pinMode(GAS_PIN, INPUT);

  Ethernet.begin(mac);
  server.begin();
  
  delay(1000);
  mqttClient.setServer(mqtt_server.c_str(), mqtt_port);
  
  // Подключение к MQTT
  mqttClient.connect("arduinoClient");

  dht.begin();
}

void loop() {
  EthernetClient client = server.available();
  
  if (client) {
    handleWebClient(client);
  }
  if (mqttClient.connected() && sendTimer >= duration) {
    mqttClient.publish((room_name + "/sensors/temperature").c_str(), String(dht.readTemperature()).c_str());
    mqttClient.publish((room_name + "/sensors/humidity").c_str(), String(dht.readHumidity()).c_str());
    mqttClient.publish((room_name + "/sensors/gases").c_str(), String(analogRead(GAS_PIN)).c_str());

    sendTimer = 0;
  }
  
  mqttClient.loop();
}

void handleWebClient(EthernetClient client) {
  String request = "";
  String currentLine = "";
  bool isPost = false;
  int contentLength = 0;
  
  // Сбрасываем флаги для нового запроса
  isPost = false;
  contentLength = 0;
  
  while (client.connected()) {
    if (client.available()) {
      char c = client.read();
      request += c;
      
      if (c == '\n') {
        if (currentLine.startsWith("POST")) {
          isPost = true;
        }
        if (currentLine.startsWith("Content-Length: ")) {
          contentLength = currentLine.substring(16).toInt();
        }
        
        if (currentLine.length() == 0) {
          if (isPost && contentLength > 0) {
            String postData = "";
            int bytesRead = 0;
            unsigned long timeout = millis();

            while (bytesRead < contentLength && (millis() - timeout) < 3000) {
              if (client.available()) {
                c = client.read();
                postData += c;
                bytesRead++;
                timeout = millis();
              }
            }
            
            Serial.print("Received POST data: ");
            Serial.println(postData);
            
            processPostData(postData);
          }
          
          sendSimpleConfigPage(client);
          break;
        }
        currentLine = "";
      } else if (c != '\r') {
        currentLine += c;
      }
    }
  }
  
  delay(1);
  client.stop();
}

void processPostData(String postData) {
  postData.replace("+", " ");
  
  Serial.print("Processing POST data: ");
  Serial.println(postData);
  
  String newRoom = getValue(postData, "room=", "&");
  String newBroker = getValue(postData, "broker=", "&");
  String newPort = getValue(postData, "port=", "&");
  String newDelay = getValue(postData, "delay=", "&");

  Serial.print("Extracted values - Room: '");
  Serial.print(newRoom);
  Serial.print("', Broker: '");
  Serial.print(newBroker);
  Serial.print("', Port: '");
  Serial.print(newPort);
  Serial.print("', Delay: '");
  Serial.print(newDelay);
  Serial.println("'");
  
  if (newRoom.length() > 0) {
    room_name = newRoom;
    Serial.println("Room updated");
  }
  if (newBroker.length() > 0) {
    mqtt_server = newBroker;
    Serial.println("Broker updated");
  }
  if (newPort.length() > 0) {
    mqtt_port = newPort.toInt();
    Serial.println("Port updated");
  }
  if (newDelay.length() > 0) {
    duration = newDelay.toInt();
    Serial.println("Delay updated");
  }
  
  mqttClient.setServer(mqtt_server.c_str(), mqtt_port);
}

void sendSimpleConfigPage(EthernetClient client) {
  // Минимальные HTTP заголовки
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println("Connection: close");
  client.println();

  // Минимальная HTML страница
  client.println("<!DOCTYPE html>");
  client.println("<html><body>");
  client.println("<h1>Config</h1>");
  client.println("<form method='post'>");
  client.println("Room:<br><input name='room' value='" + room_name + "'><br>");
  client.println("Broker:<br><input name='broker' value='" + mqtt_server + "'><br>");
  client.println("Port:<br><input name='port' value='" + String(mqtt_port) + "'><br>");
  client.println("Delay:<br><input name='delay' value='" + String(duration) + "'><br>");
  client.println("<input type='submit' value='Save'>");
  client.println("</form>");
  client.println("</body></html>");
}


String getValue(String data, String separator, String terminator) {
  int startIndex = data.indexOf(separator);
  if (startIndex == -1) {
    Serial.print("Separator not found: ");
    Serial.println(separator);
    return "";
  }
  startIndex += separator.length();
  int endIndex = data.indexOf(terminator, startIndex);
  if (endIndex == -1) {
    endIndex = data.length();
  }
  String result = data.substring(startIndex, endIndex);

  result.replace("%20", " ");
  result.replace("%2F", "/");
  result.replace("%3A", ":");
  
  return result;
}