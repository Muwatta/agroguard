/*
 * AgroGuard – Automated Irrigation System
 * Hardware: Arduino Uno/Nano + Capacitive Soil Moisture Sensor + 5V Relay + Water Pump
 *
 * Wiring:
 *   Soil Moisture Sensor  → A0 (analog), VCC→5V, GND→GND
 *   Relay IN              → D7
 *   Relay VCC             → 5V, GND → GND
 *   Water Pump            → Relay COM/NO terminals (external 5–12V supply)
 *   Status LED (optional) → D13 (built-in)
 *
 * Serial output at 9600 baud – readable on PC or Raspberry Pi.
 */

// ─── Pin Definitions ────────────────────────────────────────────────────────
const int MOISTURE_PIN  = A0;   // Analog moisture sensor
const int RELAY_PIN     = 7;    // Relay IN (active LOW for most relay modules)
const int LED_PIN       = 13;   // Built-in LED

// ─── Thresholds (0–1023, lower = wetter for resistive; adjust per sensor) ──
const int DRY_THRESHOLD  = 600; // below this → soil is dry → pump ON
const int WET_THRESHOLD  = 400; // above this (when pumping) → soil is wet enough → pump OFF

// ─── Timing ─────────────────────────────────────────────────────────────────
const unsigned long READ_INTERVAL    = 5000;   // ms between sensor reads
const unsigned long PUMP_MAX_ON_MS   = 10000;  // safety: never run pump >10 s at once
const unsigned long PUMP_COOLDOWN_MS = 30000;  // wait 30 s before next pump cycle

// ─── State ───────────────────────────────────────────────────────────────────
bool  pumpOn           = false;
unsigned long lastRead = 0;
unsigned long pumpStartTime    = 0;
unsigned long lastPumpStopTime = 0;

// ─── Helpers ─────────────────────────────────────────────────────────────────
void setPump(bool on) {
  pumpOn = on;
  // Most relay modules are active-LOW (LOW = pump ON)
  digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  digitalWrite(LED_PIN,   on ? HIGH : LOW);
  Serial.print(on ? "PUMP:ON" : "PUMP:OFF");
  Serial.print("\n");
}

int readMoisture() {
  // Average 5 readings to reduce noise
  long sum = 0;
  for (int i = 0; i < 5; i++) {
    sum += analogRead(MOISTURE_PIN);
    delay(10);
  }
  return (int)(sum / 5);
}

// Map raw ADC value to 0–100% (wet = 100%, dry = 0%)
// Calibrate MIN_RAW (submerged) and MAX_RAW (dry air) per your sensor.
const int SENSOR_MIN_RAW = 250;   // wet (submerged)
const int SENSOR_MAX_RAW = 750;   // dry (air)

int toPercent(int raw) {
  int pct = map(raw, SENSOR_MAX_RAW, SENSOR_MIN_RAW, 0, 100);
  return constrain(pct, 0, 100);
}

// ─── Setup ───────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN,   OUTPUT);
  setPump(false);   // ensure pump is OFF at start
  Serial.println("AGROGUARD:READY");
  delay(2000);
}

// ─── Loop ────────────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  // ── Safety: cut pump if it has been on too long ──────────────────────────
  if (pumpOn && (now - pumpStartTime >= PUMP_MAX_ON_MS)) {
    Serial.println("STATUS:PUMP_TIMEOUT_SAFETY");
    setPump(false);
    lastPumpStopTime = now;
  }

  // ── Read sensor every READ_INTERVAL ──────────────────────────────────────
  if (now - lastRead >= READ_INTERVAL) {
    lastRead = now;

    int raw = readMoisture();
    int pct = toPercent(raw);

    // Send CSV line to Raspberry Pi: MOISTURE,raw,percent
    Serial.print("MOISTURE,");
    Serial.print(raw);
    Serial.print(",");
    Serial.println(pct);

    // ── Irrigation logic ─────────────────────────────────────────────────
    bool cooldownElapsed = (now - lastPumpStopTime >= PUMP_COOLDOWN_MS);

    if (!pumpOn) {
      if (pct < 30 && cooldownElapsed) {       // soil is dry
        Serial.println("STATUS:SOIL_DRY_STARTING_PUMP");
        setPump(true);
        pumpStartTime = now;
      }
    } else {
      if (pct >= 60) {                          // soil is now wet enough
        Serial.println("STATUS:SOIL_WET_STOPPING_PUMP");
        setPump(false);
        lastPumpStopTime = now;
      }
    }
  }
}
