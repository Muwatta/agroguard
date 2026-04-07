/*
 * AgroGuard – Interactive OLED Display + Two-Way Communication
 * Features: 
 *   - Animated welcome message
 *   - Real-time soil moisture with bar graph
 *   - Pest alerts with animations
 *   - Interactive menu system
 *   - System status screen
 */

#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>

// OLED Display Settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Pin Definitions
const int MOISTURE_PIN = A0;
const int RELAY_PIN = 7;
const int LED_PIN = 13;

// Thresholds
int dryThresholdPercent = 30;
int wetThresholdPercent = 60;

// Timing
const unsigned long READ_INTERVAL = 5000;
const unsigned long PUMP_MAX_ON_MS = 10000;
const unsigned long PUMP_COOLDOWN_MS = 30000;

unsigned long lastRead = 0;
unsigned long pumpStartTime = 0;
unsigned long lastPumpStopTime = 0;
unsigned long lastAnimationTime = 0;

bool pumpOn = false;
int currentMoisture = 50;
String lastPest = "None";
int lastConfidence = 0;
int currentScreen = 0;  // 0=main, 1=stats, 2=about
unsigned long screenSwitchTime = 0;

// Serial buffer
String commandBuffer = "";

// ============================================
// ANIMATION FUNCTIONS
// ============================================

void drawLoadingBar(int progress, int maxProgress) {
  int barWidth = map(progress, 0, maxProgress, 0, SCREEN_WIDTH - 20);
  display.fillRect(10, 30, barWidth, 8, SSD1306_WHITE);
}

void animateWelcome() {
  // Clear screen
  display.clearDisplay();
  
  // Animated logo - AgroGuard
  for (int i = 0; i < 3; i++) {
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(15, 20);
    
    if (i == 0) display.println("Agro");
    else if (i == 1) display.println("Guard");
    else display.println("AI");
    
    display.display();
    delay(500);
  }
  
  // Loading bar animation
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(20, 15);
  display.println("Initializing System");
  
  for (int i = 0; i <= 100; i += 10) {
    drawLoadingBar(i, 100);
    display.display();
    delay(50);
  }
  
  delay(500);
  
  // System ready
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(15, 20);
  display.println("System Ready!");
  display.setCursor(10, 35);
  display.println("Protecting Crops");
  display.display();
  delay(1500);
}

void animatePestAlert(String pest, int confidence) {
  // Flash effect
  for (int flash = 0; flash < 3; flash++) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    
    if (flash % 2 == 0) {
      display.setCursor(10, 10);
      display.println("!!! WARNING !!!");
      display.setCursor(15, 25);
      display.println("PEST DETECTED");
    } else {
      display.setCursor(20, 20);
      display.println("!!! ALERT !!!");
    }
    display.display();
    delay(200);
  }
  
  // Show pest details
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("=== PEST ALERT ===");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  display.setCursor(0, 20);
  display.print("Pest: ");
  display.println(pest);
  
  display.setCursor(0, 35);
  display.print("Confidence: ");
  display.print(confidence);
  display.println("%");
  
  // Animated exclamation marks
  for (int i = 0; i < 3; i++) {
    display.fillCircle(110, 50, 5, SSD1306_WHITE);
    display.display();
    delay(150);
    display.fillCircle(110, 50, 5, SSD1306_BLACK);
    display.display();
    delay(150);
  }
  
  display.display();
  delay(2000);
}

void drawMoistureBar(int percent) {
  int barWidth = map(percent, 0, 100, 0, 80);
  
  // Choose color based on moisture level
  if (percent < 30) {
    // Dry - Red zone
    display.fillRect(40, 45, barWidth, 8, SSD1306_WHITE);
    display.drawRect(40, 45, 80, 8, SSD1306_WHITE);
    display.setCursor(35, 40);
    display.print("DRY!");
  } else if (percent > 70) {
    // Wet - Blue zone
    display.fillRect(40, 45, barWidth, 8, SSD1306_WHITE);
    display.drawRect(40, 45, 80, 8, SSD1306_WHITE);
    display.setCursor(35, 40);
    display.print("WET!");
  } else {
    // Optimal - Green zone
    display.fillRect(40, 45, barWidth, 8, SSD1306_WHITE);
    display.drawRect(40, 45, 80, 8, SSD1306_WHITE);
    display.setCursor(35, 40);
    display.print("GOOD");
  }
}

// ============================================
// DISPLAY SCREENS
// ============================================

void drawMainScreen() {
  display.clearDisplay();
  
  // Title with border
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("[ AgroGuard AI System ]");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  // Soil Moisture
  display.setCursor(0, 16);
  display.print("Soil: ");
  display.print(currentMoisture);
  display.print("%");
  
  // Moisture bar
  drawMoistureBar(currentMoisture);
  
  // Pump Status with icon
  display.setCursor(0, 56);
  display.print("Pump: ");
  if (pumpOn) {
    display.print("[ACTIVE]");
    // Animated pump indicator
    if ((millis() / 500) % 2 == 0) {
      display.fillCircle(120, 58, 3, SSD1306_WHITE);
    }
  } else {
    display.print("[IDLE]");
  }
  
  // Last pest detection
  display.setCursor(0, 28);
  display.print("Last Pest: ");
  display.print(lastPest);
  
  if (lastConfidence > 0) {
    display.setCursor(0, 38);
    display.print("Conf: ");
    display.print(lastConfidence);
    display.print("%");
  }
  
  // Interactive hint
  display.setCursor(0, 50);
  display.print("Press Button for Menu");
  
  display.display();
}

void drawStatsScreen() {
  display.clearDisplay();
  
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("=== SYSTEM STATS ===");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  display.setCursor(0, 16);
  display.print("Uptime: ");
  display.print(millis() / 1000 / 60);
  display.println(" min");
  
  display.setCursor(0, 26);
  display.print("Pump Cycles: ");
  // You can track this variable
  display.println("0");
  
  display.setCursor(0, 36);
  display.print("Dry Threshold: ");
  display.print(dryThresholdPercent);
  display.println("%");
  
  display.setCursor(0, 46);
  display.print("Wet Threshold: ");
  display.print(wetThresholdPercent);
  display.println("%");
  
  display.setCursor(0, 56);
  display.print("Mode: ");
  display.print("AUTO");
  
  display.display();
}

void drawAboutScreen() {
  display.clearDisplay();
  
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("=== ABOUT AGROGUARD ===");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  display.setCursor(0, 16);
  display.println("AI Pest Detection");
  display.setCursor(0, 26);
  display.println("Smart Irrigation");
  display.setCursor(0, 36);
  display.println("Real-time Alerts");
  
  display.setCursor(0, 50);
  display.print("Version: 2.0");
  
  display.display();
}

// ============================================
// PUMP CONTROL
// ============================================
void setPump(bool on) {
  pumpOn = on;
  digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  digitalWrite(LED_PIN, on ? HIGH : LOW);
  
  Serial.print("PUMP:");
  Serial.println(on ? "ON" : "OFF");
  drawMainScreen();  // Update display immediately
}

// ============================================
// COMMAND HANDLER (From Python)
// ============================================
void handleCommands() {
  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n') {
      commandBuffer.trim();
      
      if (commandBuffer == "PUMP_ON") {
        setPump(true);
        pumpStartTime = millis();
        Serial.println("ACK:PUMP_ON");
      }
      else if (commandBuffer == "PUMP_OFF") {
        setPump(false);
        lastPumpStopTime = millis();
        Serial.println("ACK:PUMP_OFF");
      }
      else if (commandBuffer == "STATUS") {
        Serial.println("AGROGUARD:READY");
      }
      else if (commandBuffer == "SCREEN_MAIN") {
        currentScreen = 0;
        drawMainScreen();
        Serial.println("ACK:SCREEN_MAIN");
      }
      else if (commandBuffer == "SCREEN_STATS") {
        currentScreen = 1;
        drawStatsScreen();
        Serial.println("ACK:SCREEN_STATS");
      }
      else if (commandBuffer == "SCREEN_ABOUT") {
        currentScreen = 2;
        drawAboutScreen();
        Serial.println("ACK:SCREEN_ABOUT");
      }
      else if (commandBuffer.startsWith("PEST:")) {
        String pestData = commandBuffer.substring(5);
        int commaPos = pestData.indexOf(',');
        if (commaPos > 0) {
          lastPest = pestData.substring(0, commaPos);
          lastConfidence = pestData.substring(commaPos + 1).toInt();
          animatePestAlert(lastPest, lastConfidence);
          drawMainScreen();
        }
      }
      else if (commandBuffer.startsWith("THRESHOLD:")) {
        int value = commandBuffer.substring(10).toInt();
        dryThresholdPercent = value;
        Serial.print("ACK:THRESHOLD_SET:");
        Serial.println(value);
        drawStatsScreen();
      }
      
      commandBuffer = "";
    } 
    else {
      commandBuffer += c;
    }
  }
}

// ============================================
// SENSOR READING
// ============================================
int readMoisture() {
  long sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += analogRead(MOISTURE_PIN);
    delay(10);
  }
  return (int)(sum / 5);
}

int toPercent(int raw) {
  const int SENSOR_MIN_RAW = 250;
  const int SENSOR_MAX_RAW = 750;
  int pct = map(raw, SENSOR_MAX_RAW, SENSOR_MIN_RAW, 0, 100);
  return constrain(pct, 0, 100);
}

// ============================================
// BUTTON HANDLER (Interactive)
// ============================================
void handleInteractiveInput() {
  // Using a button on pin 2 (optional)
  // For now, auto-rotate screens every 10 seconds
  if (millis() - screenSwitchTime > 10000) {
    screenSwitchTime = millis();
    currentScreen = (currentScreen + 1) % 3;
    
    switch(currentScreen) {
      case 0:
        drawMainScreen();
        break;
      case 1:
        drawStatsScreen();
        break;
      case 2:
        drawAboutScreen();
        break;
    }
  }
}

// ============================================
// SETUP
// ============================================
void setup() {
  Serial.begin(9600);
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  setPump(false);
  
  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("OLED not found!");
  } else {
    // Animated welcome sequence
    animateWelcome();
  }
  
  Serial.println("AGROGUARD:READY");
  Serial.println("STATUS:SYSTEM_INITIALIZED");
  Serial.println("OLED:INTERACTIVE_MODE_ACTIVE");
  
  drawMainScreen();
  screenSwitchTime = millis();
  delay(2000);
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
  // Handle commands from Python
  handleCommands();
  
  // Handle interactive display (auto-rotate or button)
  handleInteractiveInput();
  
  unsigned long now = millis();
  
  // Safety: Stop pump if running too long
  if (pumpOn && (now - pumpStartTime >= PUMP_MAX_ON_MS)) {
    Serial.println("STATUS:PUMP_TIMEOUT_SAFETY");
    setPump(false);
    lastPumpStopTime = now;
  }
  
  // Periodic sensor read
  if (now - lastRead >= READ_INTERVAL) {
    lastRead = now;
    
    int raw = readMoisture();
    int pct = toPercent(raw);
    currentMoisture = pct;
    
    // Send to Python
    Serial.print("MOISTURE,");
    Serial.print(raw);
    Serial.print(",");
    Serial.println(pct);
    
    // Update main screen if currently showing
    if (currentScreen == 0) {
      drawMainScreen();
    }
    
    // Auto-irrigation logic
    bool cooldownElapsed = (now - lastPumpStopTime >= PUMP_COOLDOWN_MS);
    
    if (!pumpOn && pct < dryThresholdPercent && cooldownElapsed) {
      Serial.println("STATUS:SOIL_DRY_AUTO_START");
      setPump(true);
      pumpStartTime = now;
    }
    else if (pumpOn && pct >= wetThresholdPercent) {
      Serial.println("STATUS:SOIL_WET_AUTO_STOP");
      setPump(false);
      lastPumpStopTime = now;
    }
  }
}