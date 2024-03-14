#include <WiFi.h>
#include <Arduino.h>
#include <ESPAsyncWebSrv.h>
#include <atomic>

// Network Setup
const char *ssid = "ansue";
const char *password = "a98bd13deb90";
//const char *ssid = "SlothSpeedNetwork";
//const char *password = "0Point3MillimetersAnHour";

AsyncWebServer server(80);

std::atomic<bool> trigger{false};
std::atomic<char> action{'0'};

// SMA actuator configs
const int NUM_ACT = 4;
const int sma_pins[NUM_ACT] = {5, 16, 17, 18};  // w, a, s, d (up, left, down, right)
const float sma_duty_cycles[NUM_ACT] = {100.0, 100.0, 100.0, 100.0};
const float sma_resistances[NUM_ACT] = {3.3, 2.9, 3.1, 3.3};
const int act_time = 100; // in millisec

// Power configs
const float MAX_BAT_VOLTAGE = 4.2;
const float target_current = 0.8;
const float actuation_voltage = MAX_BAT_VOLTAGE;
const int bat_monitor_pin = 33;
const int bat_volt_indicator = 15;
float current_bat_voltage;

// PWM Setup
const int sma_channels[NUM_ACT] = {0, 1, 2, 3};
const int PWM_FREQ = 1000;
const int PWM_RES = 16;
const int MAX_DUTY_CYCLE = (int)(pow(2, PWM_RES) - 1);



void setup() {

  analogReadResolution(12);
  // Setting up actuator
  for (int i = 0; i < NUM_ACT; i++) {
    ledcSetup(sma_channels[i], PWM_FREQ, PWM_RES);
    ledcAttachPin(sma_pins[i], sma_channels[i]);
  }
  pinMode(bat_volt_indicator, OUTPUT);
  
  current_bat_voltage = check_bat_level();
  for (int i = 0; i < NUM_ACT; i++) {
    ledcWrite(sma_channels[i], 0);
  }
  
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println(WiFi.localIP());
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());

  server.on("/receiveData", HTTP_POST, [](AsyncWebServerRequest *request) {
    String data = request->arg("data");
    Serial.println("Received data: " + data);
    trigger.store(true);
    action.store(data.c_str()[0]);
    request->send(200, "text/plain", "Data received successfully");
  });

  server.begin();
}

void loop() {
  if (trigger.load()) {
    trigger_actuator();
    trigger.store(false);
  }
  current_bat_voltage = check_bat_level();
}

void trigger_actuator() {
  Serial.println("-----------------------Triggered----------------------");
  Serial.println("Starting Activation...");
  char action_val = action.load();
  if (action_val == 'u') {
      ledcWrite(sma_channels[0], compute_duty_value(sma_duty_cycles[0], sma_resistances[0]));
      Serial.println("up");
  } else if (action_val == 'l') {
      ledcWrite(sma_channels[1], compute_duty_value(sma_duty_cycles[1], sma_resistances[1]));
      Serial.println("left");
  } else if (action_val == 'd') {
      ledcWrite(sma_channels[2], compute_duty_value(sma_duty_cycles[2], sma_resistances[2]));
      Serial.println("down");
  } else if (action_val == 'r') {
      ledcWrite(sma_channels[3], compute_duty_value(sma_duty_cycles[3], sma_resistances[3]));
      Serial.println("right");
  } else {
      for (int i = 0; i < NUM_ACT; i++) {
          int raw_duty_cycle_val = compute_duty_value(sma_duty_cycles[i], sma_resistances[i]);
          ledcWrite(sma_channels[i], raw_duty_cycle_val);
      }
      Serial.println("all");
  }

  delay(act_time);
  for (int j = 0; j < NUM_ACT; j++) {
    ledcWrite(sma_channels[j], 0);
  }
  Serial.println("Ending Activation...");
}

int compute_duty_value(float percentage, float r) {
  float target_voltage = target_current*r;

  // Finds the duty cycle such that avg voltage leads to desired current
  float max_duty;
  if (actuation_voltage == MAX_BAT_VOLTAGE) {
    max_duty = target_voltage/current_bat_voltage;
  } else if (actuation_voltage < target_voltage) {
    max_duty = 100;
  } else {
    max_duty = target_voltage/actuation_voltage;
  }
  // Scales by this max_duty cycle 
  // (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  float scaled_percentage = percentage * max_duty  / 100; 
  float duty_val = scaled_percentage * MAX_DUTY_CYCLE;
  return (int)duty_val;
}
float check_bat_level() {
  float analogVolts = analogReadMilliVolts(bat_monitor_pin)/1000.0 * 2.0; // Monitor circuit is a voltage divider by 2
//    float analogVolts = analogRead(bat_monitor_pin); // Monitor circuit is a voltage divider by 2
  Serial.println("Bat Volts");
  Serial.println(analogVolts);
  if (analogVolts < MAX_BAT_VOLTAGE * 0.83) {
    digitalWrite(bat_volt_indicator, HIGH);
  } else {
    digitalWrite(bat_volt_indicator, LOW);
  }
  return analogVolts;
}
