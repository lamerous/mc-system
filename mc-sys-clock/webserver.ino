void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/save", HTTP_POST, handleSaveConfig);
  server.on("/reset", handleReset);
  server.on("/restart", []() {
    server.send(200, "text/html", "<html><body><h1>Restarting...</h1></body></html>");
    delay(1000);
    ESP.restart();
  });
  
  server.begin();
  Serial.println("HTTP server started");
}

void handleWebClient() {
  server.handleClient();
}

void handleRoot() {
  String html = R"=====(
<!DOCTYPE html>
<html>
<head>
    <title>Clock Configuration</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .buttons { display: flex; justify-content: space-between; margin-top: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Clock Configuration</h1>
        
        <form action="/save" method="post">
            <div class="form-group">
                <label>WiFi SSID:</label>
                <input type="text" name="ssid" value=")=====" + String(config.wifi_ssid) + R"=====(" required>
            </div>
            
            <div class="form-group">
                <label>WiFi Password:</label>
                <input type="password" name="password" value=")=====" + String(config.wifi_pass) + R"=====(" required>
            </div>
            
            <div class="form-group">
                <label>Room Name:</label>
                <input type="text" name="room_name" value=")=====" + room_name + R"=====(" required>
            </div>
            
            <div class="form-group">
                <label>MQTT Broker:</label>
                <input type="text" name="mqtt_broker" value=")=====" + String(config.mqtt_broker) + R"=====(" required>
            </div>
            
            <div class="form-group">
                <label>MQTT Port:</label>
                <input type="number" name="mqtt_port" value=")=====" + String(config.mqtt_port) + R"=====(" required>
            </div>
            
            <div class="buttons">
                <button type="submit">Save Configuration</button>
                <button type="button" onclick="location.href='/reset'">Reset to Defaults</button>
                <button type="button" onclick="location.href='/restart'">Restart Device</button>
            </div>
        </form>
        
        <div style="margin-top: 20px; padding: 10px; background: #e9ecef; border-radius: 4px;">
            <strong>Current Status:</strong><br>
            WiFi: )=====" + String(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected") + R"=====(<br>
            IP: )=====" + WiFi.localIP().toString() + R"=====(<br>
            Room Name: )=====" + room_name + R"=====(<br>
            AP SSID: )=====" + ap_ssid + R"=====(<br>
            Mode: )=====" + String(config.first_start ? "First Start" : "Normal") + R"=====(
        </div>
    </div>
</body>
</html>
)=====";

  server.send(200, "text/html", html);
}

void handleSaveConfig() {
  if (server.hasArg("ssid")) strcpy(config.wifi_ssid, server.arg("ssid").c_str());
  if (server.hasArg("password")) strcpy(config.wifi_pass, server.arg("password").c_str());
  if (server.hasArg("room_name")) strcpy(config.room_name, server.arg("room_name").c_str());
  if (server.hasArg("mqtt_broker")) strcpy(config.mqtt_broker, server.arg("mqtt_broker").c_str());
  if (server.hasArg("mqtt_port")) config.mqtt_port = server.arg("mqtt_port").toInt();

  config.first_start = false;
  
  saveConfig();

  room_name = String(config.room_name);
  
  String html = R"=====(
<!DOCTYPE html>
<html>
<head>
    <title>Configuration Saved</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success">
            <h2>Configuration Saved Successfully!</h2>
            <p>The device will now attempt to connect with new settings.</p>
            <p><strong>Room Name:</strong> )=====" + room_name + R"=====(</p>
        </div>
        <br>
        <button onclick="location.href='/'">Back to Configuration</button>
        <button onclick="location.href='/restart'">Restart Now</button>
    </div>
</body>
</html>
)=====";
  
  server.send(200, "text/html", html);
}

void handleReset() {
  resetConfig();
  
  String html = R"=====(
<!DOCTYPE html>
<html>
<head>
    <title>Configuration Reset</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Configuration Reset to Defaults</h1>
    <p>Room name reset to: room1</p>
    <p><a href="/">Back to configuration</a></p>
</body>
</html>
)=====";
  
  server.send(200, "text/html", html);
}