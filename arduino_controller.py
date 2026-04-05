import serial
import time
import threading
import platform

class ArduinoController:
    def __init__(self):
        self.connected = False
        self.ser = None
        self.simulation_mode = True
        self.moisture = 50
        self.pump_on = False
        self.dry_threshold = 30
        self.wet_threshold = 60
        self._running = False
        self._response_buffer = ""
        
        # Auto-detect and connect
        self._connect()
        
        # Start background reader if connected
        if self.connected:
            self._running = True
            threading.Thread(target=self._read_loop, daemon=True).start()
    
    def _connect(self):
        """Auto-detect Arduino on common ports"""
        if platform.system() == 'Windows':
            ports = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7']
        else:
            ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyUSB1']
        
        for port in ports:
            try:
                self.ser = serial.Serial(port, 9600, timeout=1)
                time.sleep(2)
                
                # Send test command
                self.ser.write(b"STATUS\n")
                time.sleep(0.5)
                
                # Check response
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    if "AGROGUARD" in response:
                        self.connected = True
                        self.simulation_mode = False
                        print(f"✅ Arduino connected on {port}")
                        print(f"   Response: {response}")
                        return
                
                self.ser.close()
            except Exception as e:
                continue
        
        self.connected = False
        self.simulation_mode = True
        print("ℹ️ Arduino not found - SIMULATION MODE")
        print("   Connect Arduino via USB and restart to use real hardware")
    
    def _read_loop(self):
        """Read data from Arduino continuously"""
        while self._running and self.connected:
            try:
                if self.ser and self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
                    self._response_buffer += data
                    
                    # Process complete lines
                    while '\n' in self._response_buffer:
                        line, self._response_buffer = self._response_buffer.split('\n', 1)
                        self._parse_line(line.strip())
            except Exception as e:
                pass
            time.sleep(0.05)
    
    def _parse_line(self, line):
        """Parse Arduino output lines"""
        if not line:
            return
        
        # MOISTURE,raw,percent
        if line.startswith("MOISTURE"):
            parts = line.split(',')
            if len(parts) >= 3:
                self.moisture = int(parts[2])
                print(f"💧 Moisture: {self.moisture}%")
        
        # PUMP:ON or PUMP:OFF
        elif line.startswith("PUMP:"):
            self.pump_on = (line == "PUMP:ON")
            print(f"🚿 Pump: {'ON' if self.pump_on else 'OFF'}")
        
        # ACK:... (command acknowledgements)
        elif line.startswith("ACK:"):
            print(f"✅ {line}")
        
        # STATUS messages
        elif line.startswith("STATUS:"):
            msg = line[7:]
            if "DRY" in msg:
                print(f"🌵 {msg}")
            elif "WET" in msg:
                print(f"💧 {msg}")
            elif "TIMEOUT" in msg:
                print(f"⏱️ {msg}")
            else:
                print(f"📡 {msg}")
        
        # AGROGUARD:READY
        elif "AGROGUARD" in line:
            print(f"🤖 {line}")
        
        # Unknown messages
        else:
            if line.strip():
                print(f"📟 {line}")
    
    def send_command(self, cmd, wait_response=True):
        """Send command to Arduino"""
        if not self.connected:
            print(f"[SIM] Command: {cmd}")
            return self._simulate_response(cmd)
        
        try:
            self.ser.write(f"{cmd}\n".encode())
            if wait_response:
                time.sleep(0.3)
                # Read any immediate response
                response = ""
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                return response
            return "OK"
        except Exception as e:
            print(f"❌ Send failed: {e}")
            return "ERROR"
    
    def _simulate_response(self, command):
        """Simulate Arduino response for testing"""
        if command == "STATUS":
            return "AGROGUARD:SIMULATION"
        elif command == "PUMP_ON":
            self.pump_on = True
            return "ACK:PUMP_ON"
        elif command == "PUMP_OFF":
            self.pump_on = False
            return "ACK:PUMP_OFF"
        elif command.startswith("THRESHOLD:"):
            val = int(command.split(":")[1])
            self.dry_threshold = val
            return f"ACK:THRESHOLD_SET:{val}"
        elif command.startswith("PEST:"):
            # For OLED simulation
            pest_data = command[5:]
            print(f"OLED would show: {pest_data}")
            return "ACK:PEST_RECEIVED"
        return "OK"

    def change_screen(self, screen_name):
        command = f"SCREEN_{screen_name.upper()}"
        self.send_command(command)
        print(f"📟 OLED: Switching to {screen_name} screen")

    def get_oled_status(self):
        return {
            "active": True,
            "screens": ["main", "stats", "about"],
            "current_screen": "main"  # You can track this
        }
    
    def send_pest_alert(self, pest, confidence):
        confidence_pct = int(confidence * 100)
        command = f"PEST:{pest},{confidence_pct}"
        
        if not self.connected:
            print(f"[SIM] OLED would show: {pest} ({confidence_pct}%)")
        else:
            self.send_command(command)
            print(f"📟 OLED: {pest} ({confidence_pct}%)")
    
    def sprinkler_on(self, duration=10):
        """Turn sprinkler ON"""
        print(f"🚿 Sprinkler ON for {duration}s")
        response = self.send_command("PUMP_ON")
        
        # If in real mode, Arduino handles timing
        if self.simulation_mode:
            # Simulate auto-off after duration
            def auto_off():
                time.sleep(duration)
                if self.pump_on:
                    self.sprinkler_off()
            threading.Thread(target=auto_off, daemon=True).start()
        
        return True
    
    def sprinkler_off(self):
        """Turn sprinkler OFF immediately"""
        print(f"🚿 Sprinkler OFF")
        self.send_command("PUMP_OFF")
        return True
    
    def get_moisture(self):
        """Get current soil moisture percentage"""
        return self.moisture
    
    def get_sensor_data(self):
        """Get all sensor data"""
        return {
            "soil_moisture": self.moisture,
            "pump_status": self.pump_on,
            "dry_threshold": self.dry_threshold,
            "connected": self.connected,
            "simulated": self.simulation_mode,
            "timestamp": time.time()
        }
    
    def get_status(self):
        """Get connection status"""
        return {
            "connected": self.connected,
            "simulation_mode": self.simulation_mode,
            "moisture": self.moisture,
            "pump": "ON" if self.pump_on else "OFF",
            "port": self.ser.port if self.ser else None
        }
    
    def set_threshold(self, percent):
        """Set dry threshold (0-100)"""
        if 0 <= percent <= 100:
            self.dry_threshold = percent
            self.send_command(f"THRESHOLD:{percent}")
            print(f"🌵 Dry threshold set to {percent}%")
            return True
        return False
    
    def test_connection(self):
        """Test if Arduino is responding"""
        if not self.connected:
            print("❌ Arduino not connected")
            return False
        
        response = self.send_command("STATUS")
        if "AGROGUARD" in response:
            print("✅ Arduino is responding")
            return True
        else:
            print("⚠️ Arduino not responding")
            return False
    
    def close(self):
        """Close serial connection"""
        self._running = False
        if self.ser:
            self.ser.close()
            print("🔌 Serial connection closed")

# ============================================
# TEST FUNCTION
# ============================================

def test_arduino():
    """Test the Arduino connection"""
    print("=" * 50)
    print("Testing Arduino Communication")
    print("=" * 50)
    
    arduino = ArduinoController()
    
    print("\n📡 Sending STATUS...")
    response = arduino.send_command("STATUS")
    print(f"Response: {response}")
    
    print("\n📊 Getting sensor data...")
    data = arduino.get_sensor_data()
    print(f"Moisture: {data['soil_moisture']}%")
    print(f"Pump: {'ON' if data['pump_status'] else 'OFF'}")
    
    print("\n🔧 Testing pump control...")
    arduino.sprinkler_on(3)
    time.sleep(4)
    arduino.sprinkler_off()
    
    print("\n🌵 Testing threshold...")
    arduino.set_threshold(40)
    
    print("\n📟 Testing OLED alert...")
    arduino.send_pest_alert("armyworm", 0.95)
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)
    
    arduino.close()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    test_arduino()

# Create global instance for import
arduino = ArduinoController()