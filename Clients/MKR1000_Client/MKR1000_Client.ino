/*
   Client for Labadmin
   This code allows you to read an RFID card and to post its value to the server

   Hardware:
   MKR1000
   RFID-RC522
   Use of the EmojiShield is suggested

*/

#include <WiFi101.h>
#include<WiFiSSLClient.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include "MFRC522.h"

#define RST_PIN 6
#define SS_PIN 11
#define SERVER "labchat.officine.cc"

MFRC522 mfrc522(SS_PIN, RST_PIN);

// Your WiFi credentials
const char* ssid = "xxxx";
const char* password = "yyyy";

// Put here the device_token of the machine you are using
String DEVICE_TOKEN = "zzzz";

WiFiSSLClient client;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.print("connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  SPI.begin();         // Init SPI bus
  mfrc522.PCD_Init();    // Init MFRC522
}

void loop() {

  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    delay(50);
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  String nfc_tag = dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
  PostToServer(nfc_tag);

}

void PostToServer(String nfc_tag) {

  StaticJsonBuffer<200> jsonBuffer;
  JsonObject& root = jsonBuffer.createObject();
  root["nfc_id"] = nfc_tag;
  String output;
  root.printTo(output);

  if (client.connect(SERVER, 8443)) {
    client.println("POST /labadmin/labadmin/opendoorbynfc/ HTTP/1.1");
    client.println("Host: labchat.officine.cc:8443");
    client.println("Authorization: Token " + DEVICE_TOKEN);
    client.println("Content-Type:  application/json");
    client.println("Connection: close");
    client.print("Content-Length: ");
    client.println(output.length());
    client.println();
    client.println(output);

    Serial.println("request sent");

    while (client.connected()) {
      if ( client.available()) {
        char str = client.read();
        Serial.print(str);
      }
    }
    client.stop();  // DISCONNECT FROM THE SERVER
  }
  else {
    Serial.println("CONNECTION FAILED");
  }
}

String dump_byte_array(byte *buffer, byte bufferSize) {
  String out = "";
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    out += String(buffer[i]);
  }
  Serial.println(out);
  return out;
}

