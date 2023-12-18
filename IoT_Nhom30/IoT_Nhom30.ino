#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long startTime = 0;  // Thời điểm bắt đầu hoạt động của đèn
unsigned long totalOnTime = 0;  // Tổng thời gian đèn đã hoạt động

void setup_wifi() { 
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA); 
  WiFi.begin(ssid, password); 

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String temp;

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) { 
    temp += (char)payload[i];
  }
  
  Serial.println(temp);
  if (temp.equals("F") ) {
    Serial.println("f");
    digitalWrite(2, LOW);  
  } else {
    Serial.println("n");
    digitalWrite(2, HIGH);
  }
}

void reconnect() { 
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to " + clientId);
      // Once connected, publish an announcement...
      char payload[16];
        sprintf(payload, "%lu", totalOnTime);
      Serial.print("Total on time: ");
      Serial.println(payload);
      client.publish("/PTIT_Test/at161/time", payload); 
      // ... and resubscribe
      client.subscribe("/PTIT_Test/at161/mqtt");
      client.subscribe("/PTIT_Test/at161/time"); 
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void trackLightOnTime()
{
  if (digitalRead(2) == HIGH)  // Kiểm tra trạng thái đèn
  {
    if (startTime == 0)  // Nếu đèn mới bật, ghi lại thời điểm bắt đầu
    {
      startTime = millis();
    }
  }
  else  // Nếu đèn tắt
  {
    if (startTime != 0)  // Nếu đèn đã từng được bật
    {
      unsigned long currentTime = millis();
      unsigned long onTime = currentTime - startTime;  // Tính thời gian hoạt động của đèn
      totalOnTime += onTime;  // Cộng dồn thời gian hoạt động vào tổng thời gian
      startTime = 0;  // Đặt lại thời điểm bắt đầu
    }
  }
}
void setup() {
  pinMode(2, OUTPUT);
  Serial.begin(115200);
  setup_wifi(); 
  client.setServer(mqtt_server, 1883); 
  client.setCallback(callback); 
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  trackLightOnTime();
  client.loop();
}