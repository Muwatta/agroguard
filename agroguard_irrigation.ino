/*
 * AgroGuard – TWO-WAY Communication
 * Arduino ←→ Python (Bi-directional)
 */

const int MOISTURE_PIN = A0;
const int RELAY_PIN = 7;
const int LED_PIN = 13;

const int DRY_THRESHOLD = 600;
const int WET_THRESHOLD = 400;

unsigned long lastRead = 0;
bool pumpOn = false;

// ============================================
// PUMP CONTROL
// ============================================
void setPump(bool on) {
  pumpOn = on;
  digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  digitalWrite(LED_PIN, on ? HIGH : LOW);
  Serial.print(on ? "PUMP:ON" : "PUMP:OFF");
  Serial.print("\n");
}

// ============================================
// COMMAND HANDLER - Receives commands from Python
// ============================================
void handleCommands() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "PUMP_ON") {
      setPump(true);
      Serial.println("STATUS:PUMP_ON_BY_COMMAND");
    }
    else if (command == "PUMP_OFF") {
      setPump(false);
      Serial.println("STATUS:PUMP_OFF_BY_COMMAND");
    }
    else if (command == "STATUS") {
      Serial.println("AGROGUARD:READY");
    }
    else if (command.startsWith("THRESHOLD:")) {
      int newThreshold = command.substring(10).toInt();
      Serial.print("STATUS:THRESHOLD_SET_TO:");
      Serial.println(newThreshold);
    }
  }
}

// ============================================
// READ MOISTURE SENSOR
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
// SETUP
// ============================================
void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  setPump(false);
  Serial.println("AGROGUARD:READY");
  Serial.println("STATUS:TWO_WAY_COMMUNICATION_ACTIVE");
  delay(2000);
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
  // CHECK FOR COMMANDS FROM PYTHON
  handleCommands();
  
  unsigned long now = millis();
  
  // Read moisture every 5 seconds
  if (now - lastRead >= 5000) {
    lastRead = now;
    
    int raw = readMoisture();
    int pct = toPercent(raw);
    
    // Send to Python
    Serial.print("MOISTURE,");
    Serial.print(raw);
    Serial.print(",");
    Serial.println(pct);
    
    // Auto-irrigation logic
    if (!pumpOn && pct < 30) {
      Serial.println("STATUS:SOIL_DRY_AUTO_START");
      setPump(true);
    }
    else if (pumpOn && pct >= 60) {
      Serial.println("STATUS:SOIL_WET_AUTO_STOP");
      setPump(false);
    }
  }
}