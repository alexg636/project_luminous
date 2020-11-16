#include <FastLED.h>
#include "WiFi.h"
#include <WiFiUdp.h>


#define LED_PIN     27
#define NUM_LEDS    54
#define BRIGHTNESS  64
CRGB leds[NUM_LEDS];

WiFiUDP Udp; // Creation of wifi Udp instance

char packetBuffer[255];

unsigned int localPort = 9999;

// Access Point
//const char *ssid = "George-esp32";  
//const char *password = "BB9ESERVER";

// Wifi
const char* ssid = "iPhone";
const char* password = "0f9pc020ihapk";

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  // Access Point
//  WiFi.softAP(ssid, password);  // ESP-32 as access point
  // Wifi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to the WiFi network");
  Serial.println("IP Address: ");
  Serial.print(WiFi.localIP());
  Udp.begin(localPort);
  pinMode(LED_PIN, OUTPUT);
  

}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, 4096);
    if (len > 0) packetBuffer[len-1] = 0;
    Serial.print("Received (IP/Size/Data): ");
    Serial.print(Udp.remoteIP());Serial.print(" / ");
    Serial.print(packetSize);Serial.print(" / ");
    Serial.println(packetBuffer);

    Udp.beginPacket(Udp.remoteIP(),Udp.remotePort());
    Udp.printf("received: ");
    Udp.printf(packetBuffer);
    Udp.printf("\r\n");
    Udp.endPacket();
    for (int i = 0; i<packetSize; i++) {
      Serial.print("i = ");
      Serial.print(i);
      Serial.print(" -- ");
      Serial.print(packetBuffer[i], DEC);
      Serial.println();
    }
    FastLED.clear();
    FastLED.show();
    for (int j = 0; j<packetSize/3; j++) {
      leds[j] = CRGB(packetBuffer[j*3], packetBuffer[(j*3)+1], packetBuffer[(j*3)+2]);
    }
    FastLED.show();

     }
}
