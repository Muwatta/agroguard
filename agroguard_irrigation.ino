
const int MOISTURE_PIN = A0;
const int RELAY_PIN = 7;
const int LED_PIN = 13;


int dryThresholdPercent = 30;
int wetThresholdPercent = 60;

const unsigned long READ_INTERVAL = 5000;
const unsigned long PUMP_MAX_ON_MS = 10000;
const unsigned long PUMP_COOLDOWN_MS = 30000;

unsigned long lastRead = 0;
unsigned long pumpStartTime = 0;
unsigned long lastPumpStopTime = 0;

bool pumpOn = false;

// Serial buffer (non-blocking)
String commandBuffer = "";

// PUMP CONTROL
void setPump(bool on) {
  pumpOn = on;

  // Active LOW relay
  digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  digitalWrite(LED_PIN, on ? HIGH : LOW);

  Serial.print("PUMP:");
  Serial.println(on ? "ON" : "OFF");
}

// HANDLE SERIAL COMMANDS (NON-BLOCKING)
void handleCommands() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      commandBuffer.trim();

      // ---------- COMMAND PARSER ----------
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
      else if (commandBuffer.startsWith("THRESHOLD:")) {
        int value = commandBuffer.substring(10).toInt();
        dryThresholdPercent = value;

        Serial.print("ACK:THRESHOLD_SET:");
        Serial.println(value);
      }

      // Reset buffer
      commandBuffer = "";
    } 
    else {
      commandBuffer += c;
    }
  }
}

// SENSOR READING
int readMoisture() {
  long sum = 0;

  for (int i = 0; i < 5; i++) {
    sum += analogRead(MOISTURE_PIN);
    delay(10); // small smoothing delay
  }

  return (int)(sum / 5);
}

// CONVERT TO PERCENTAGE
int toPercent(int raw) {
  const int SENSOR_MIN_RAW = 250;
  const int SENSOR_MAX_RAW = 750;

  int pct = map(raw, SENSOR_MAX_RAW, SENSOR_MIN_RAW, 0, 100);
  return constrain(pct, 0, 100);
}

// SETUP
void setup() {
  Serial.begin(9600);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  setPump(false);

  Serial.println("AGROGUARD:READY");
  Serial.println("STATUS:SYSTEM_INITIALIZED");

  delay(2000);
}

// MAIN LOOP
void loop() {

  // 1. HANDLE INCOMING COMMANDS
  handleCommands();

  unsigned long now = millis();

  // 2. SAFETY: STOP PUMP IF RUNNING TOO LONG
  if (pumpOn && (now - pumpStartTime >= PUMP_MAX_ON_MS)) {
    Serial.println("STATUS:PUMP_TIMEOUT_SAFETY");
    setPump(false);
    lastPumpStopTime = now;
  }

  // 3. PERIODIC SENSOR READ
  if (now - lastRead >= READ_INTERVAL) {
    lastRead = now;

    int raw = readMoisture();
    int pct = toPercent(raw);

    // Send structured data to Python
    Serial.print("MOISTURE,");
    Serial.print(raw);
    Serial.print(",");
    Serial.println(pct);

    // 4. AUTO IRRIGATION LOGIC WITH COOLDOWN
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