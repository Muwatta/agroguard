#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  // try 0x3F if 0x27 fails

// Pin definitions
const int MOISTURE_PIN = A0;
const int RELAY_PIN = 7;
const int LED_PIN = 13;
const int BUTTON_PIN = 2;           // <-- NEW: button to change screen (optional)

int dryThresholdPercent = 30;
int wetThresholdPercent = 60;

const unsigned long READ_INTERVAL = 2000;      // read every 2 seconds (faster feedback)
const unsigned long PUMP_MAX_ON_MS = 3600000;  // <-- NEW: 1 hour max (instead of 10 sec)
const unsigned long PUMP_COOLDOWN_MS = 5000;   // 5 sec cooldown after stopping (prevents rapid cycling)

unsigned long lastRead = 0;
unsigned long pumpStartTime = 0;
unsigned long lastPumpStopTime = 0;

bool pumpOn = false;
int currentMoisturePercent = 50;

// Calibration
int sensorMinRaw = 1023, sensorMaxRaw = 0;
bool calibrated = false;
int calibrationSamples = 0;

// Pest & screen
String lastPest = "None";
int lastConfidence = 0;
int currentScreen = 0;  // 0=main, 1=stats, 2=about

// Button debounce
unsigned long lastButtonPress = 0;
const unsigned long DEBOUNCE_DELAY = 300;

// Serial buffer
String commandBuffer = "";

// ======================== LCD Helper ========================
void lcdPrintBoth(const char* line1, const char* line2 = "") {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  if (strlen(line2) > 0) {
    lcd.setCursor(0, 1);
    lcd.print(line2);
  }
}

void drawMoistureBar(int percent) {
  // Draw a simple text bar on the second line (e.g., "###----- 50%")
  lcd.setCursor(0, 1);
  int bars = map(percent, 0, 100, 0, 16);
  for (int i = 0; i < 16; i++) {
    lcd.print(i < bars ? '#' : '-');
  }
  lcd.setCursor(0, 0);
  lcd.print("Mois:");
  lcd.print(percent);
  lcd.print("%");
  lcd.print(" ");
  lcd.print(pumpOn ? "PMP ON" : "PMP OFF");
}

// ======================== Animations (no backlight flashing) ========================
void animateWelcome() {
  lcd.backlight();  // ensure backlight is on
  lcdPrintBoth("AgroGuard AI", "Initializing...");
  delay(1000);
  for (int i = 0; i <= 100; i += 10) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Loading ");
    lcd.print(i);
    lcd.print("%");
    lcd.setCursor(0, 1);
    int bars = map(i, 0, 100, 0, 16);
    for (int j = 0; j < 16; j++) lcd.print(j < bars ? '#' : '-');
    delay(80);
  }
  lcdPrintBoth("System Ready!", "Protecting crops");
  delay(1500);
}

void animatePestAlert(String pest, int confidence) {
  // No backlight flashing – just show alert on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("!!! PEST !!!");
  lcd.setCursor(0, 1);
  lcd.print(pest);
  lcd.print(" ");
  lcd.print(confidence);
  lcd.print("%");
  delay(2000);
  // Redraw current screen
  if (currentScreen == 0) drawMainScreen();
  else if (currentScreen == 1) drawStatsScreen();
  else drawAboutScreen();
}

// ======================== Screens ========================
void drawMainScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("M:");
  lcd.print(currentMoisturePercent);
  lcd.print("% ");
  lcd.print(pumpOn ? "P ON" : "P OFF");
  lcd.setCursor(0, 1);
  if (currentMoisturePercent < dryThresholdPercent)
    lcd.print("DRY -> WATER");
  else if (currentMoisturePercent >= wetThresholdPercent)
    lcd.print("WET -> STOP");
  else
    lcd.print("MOISTURE OK");
  // Show last pest on the right if space
  if (lastPest != "None" && lastConfidence > 0) {
    lcd.setCursor(10, 1);
    lcd.print(lastPest.substring(0,5));
  }
}

void drawStatsScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Dry:");
  lcd.print(dryThresholdPercent);
  lcd.print("% Wet:");
  lcd.print(wetThresholdPercent);
  lcd.setCursor(0, 1);
  lcd.print("Uptime:");
  lcd.print(millis() / 1000 / 60);
  lcd.print("m");
  // Stay on this screen until button press or 10 seconds
  unsigned long start = millis();
  while (millis() - start < 10000) {
    if (digitalRead(BUTTON_PIN) == LOW) break;
    delay(50);
  }
  currentScreen = 0;
  drawMainScreen();
}

void drawAboutScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("AgroGuard AI v2");
  lcd.setCursor(0, 1);
  lcd.print("Smart Irrigation");
  delay(3000);
  currentScreen = 0;
  drawMainScreen();
}

// ======================== Pump & Sensor ========================
void setPump(bool on) {
  pumpOn = on;
  // Relay: active HIGH (change if your relay needs LOW)
  digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  digitalWrite(LED_PIN, on ? HIGH : LOW);
  Serial.print("PUMP:"); Serial.println(on ? "ON" : "OFF");
  if (currentScreen == 0) drawMainScreen();
}

int readRawMoisture() {
  long sum = 0;
  for (int i=0; i<5; i++) { sum += analogRead(MOISTURE_PIN); delay(10); }
  return sum / 5;
}

void autoCalibrate(int raw) {
  if (!calibrated && calibrationSamples < 20) {
    if (raw < sensorMinRaw) sensorMinRaw = raw;
    if (raw > sensorMaxRaw) sensorMaxRaw = raw;
    calibrationSamples++;
    if (calibrationSamples >= 20) {
      calibrated = true;
      Serial.print("CAL: MIN="); Serial.print(sensorMinRaw);
      Serial.print(" MAX="); Serial.println(sensorMaxRaw);
      lcdPrintBoth("Calibrated!", "Ready");
      delay(1000);
      drawMainScreen();
    }
  }
}

int rawToPercent(int raw) {
  if (!calibrated) return map(constrain(raw, 250, 750), 750, 250, 0, 100);
  return constrain(map(raw, sensorMinRaw, sensorMaxRaw, 0, 100), 0, 100);
}

// ======================== Irrigation Logic (continuous pump) ========================
void manageIrrigation(int pct) {
  unsigned long now = millis();
  
  // Safety: stop pump only if it runs longer than allowed (now 1 hour)
  if (pumpOn && (now - pumpStartTime >= PUMP_MAX_ON_MS)) {
    Serial.println("SAFETY: PUMP TIMEOUT (1 hour)");
    setPump(false);
    lastPumpStopTime = now;
  }
  
  bool cooldownOk = (now - lastPumpStopTime >= PUMP_COOLDOWN_MS);
  
  // Start pump if dry and cooldown finished
  if (!pumpOn && pct < dryThresholdPercent && cooldownOk) {
    Serial.println("SOIL_DRY -> PUMP ON");
    setPump(true);
    pumpStartTime = now;
  }
  // Stop pump if wet
  else if (pumpOn && pct >= wetThresholdPercent) {
    Serial.println("SOIL_WET -> PUMP OFF");
    setPump(false);
    lastPumpStopTime = now;
  }
}

// ======================== Serial & Button Handling ========================
void handleSerialCommands() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      commandBuffer.trim();
      if (commandBuffer == "PUMP_ON") { setPump(true); pumpStartTime = millis(); Serial.println("ACK:PUMP_ON"); }
      else if (commandBuffer == "PUMP_OFF") { setPump(false); lastPumpStopTime = millis(); Serial.println("ACK:PUMP_OFF"); }
      else if (commandBuffer == "STATUS") Serial.println("AGROGUARD:READY");
      else if (commandBuffer == "SCREEN_STATS") { drawStatsScreen(); currentScreen = 1; }
      else if (commandBuffer == "SCREEN_ABOUT") { drawAboutScreen(); currentScreen = 2; }
      else if (commandBuffer == "SCREEN_MAIN") { currentScreen = 0; drawMainScreen(); }
      else if (commandBuffer.startsWith("PEST:")) {
        String data = commandBuffer.substring(5);
        int comma = data.indexOf(',');
        if (comma > 0) {
          lastPest = data.substring(0, comma);
          lastConfidence = data.substring(comma + 1).toInt();
          animatePestAlert(lastPest, lastConfidence);
          if (currentScreen == 0) drawMainScreen();
        }
      }
      else if (commandBuffer.startsWith("THRESHOLD:")) {
        dryThresholdPercent = commandBuffer.substring(10).toInt();
        Serial.print("THRESHOLD_SET:"); Serial.println(dryThresholdPercent);
        lcdPrintBoth("Threshold set", (String(dryThresholdPercent) + "% dry").c_str());
        delay(1000);
        drawMainScreen();
      }
      commandBuffer = "";
    } else commandBuffer += c;
  }
}

void handleButton() {
  if (digitalRead(BUTTON_PIN) == LOW && (millis() - lastButtonPress > DEBOUNCE_DELAY)) {
    lastButtonPress = millis();
    currentScreen = (currentScreen + 1) % 3;
    switch(currentScreen) {
      case 1: drawStatsScreen(); break;
      case 2: drawAboutScreen(); break;
      default: drawMainScreen();
    }
  }
}

// ======================== Setup ========================
void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // internal pull-up, button to GND
  setPump(false);
  
  lcd.init();
  lcd.backlight();          // keep backlight ON permanently
  lcd.clear();
  animateWelcome();
  drawMainScreen();
  Serial.println("AGROGUARD:READY");
}

// ======================== Loop ========================
void loop() {
  handleSerialCommands();
  handleButton();           // <-- NEW: manual screen switching
  
  unsigned long now = millis();
  if (now - lastRead >= READ_INTERVAL) {
    lastRead = now;
    int raw = readRawMoisture();
    autoCalibrate(raw);
    int pct = rawToPercent(raw);
    currentMoisturePercent = pct;
    Serial.print("MOISTURE,"); Serial.print(raw); Serial.print(","); Serial.println(pct);
    manageIrrigation(pct);
    if (currentScreen == 0) drawMainScreen();
  }
}