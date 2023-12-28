#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

const char* ssid = "NodeMCU";
const char* password = "12345678";
ESP8266WebServer server(80);

float temperature = 0.0;
bool relayState = false;
unsigned long relayStartTime = 0;
const unsigned long relayDuration = 2000;
const unsigned long temperatureInterval = 100;
const int numReadings = 100;
float temperatureReadings[numReadings];
int currentReading = 0;
String readingsData="";
float temps[100];

void handleRoot() {
  server.send(200, "text/plain", String(readingsData));
}

void handleTemperature() {
  if (server.hasArg("data") && server.arg("data") == "TurnOnRelay") {
    relayState = true;
    relayStartTime = millis(); // Store the current time

    digitalWrite(14, HIGH); // Turn on the relay

    server.send(200, "text/plain", "Relay turned on");
  } else {
    server.send(400, "text/plain", "Invalid request");
  }
}

void handleRelay() {
  relayState = true;
  //relayStartTime = millis(); 
  
  // Store the current time

  digitalWrite(14, HIGH); // Turn on the relay
  delay(relayDuration);
  digitalWrite(14, LOW); 
  server.send(200, "text/plain", "Relay turned on");
}



void setup() {
  
  Serial.begin(115200);
  mlx.begin();
  pinMode(14,OUTPUT);
  digitalWrite(14, LOW);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  IPAddress apIP(192, 168, 1, 1);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  server.on("/", handleRoot);
  server.on("/temperature", handleTemperature);
  server.on("/relay", handleRelay);
  server.begin();
  Serial.println("Server started");
    

  //Serial.println(IP);
}

void loop() {

  server.handleClient();
   if (relayState && (millis() - relayStartTime) <= relayDuration){
      digitalWrite(14, HIGH);
   }
  if (relayState && (millis() - relayStartTime) >= relayDuration) {
    digitalWrite(14, LOW); // Turn off the relay
    relayState = false; // Reset relay state
    readingsData="";
    for (int i = 0; i < 100; i++) {
      temps[i]=mlx.readObjectTempC();
      readingsData+=String(temps[i]);
      readingsData+=",";
      Serial.println(readingsData);
      delay(100);
    }
   
    handleRoot();
 
  }
 
}
