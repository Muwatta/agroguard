"""
SIMPLE Arduino Controller for AgroGuard
One file - everything in one place
"""

import serial
import time
import threading

class ArduinoController:
    def __init__(self):
        self.ser = None
        self.connected = False
        self.moisture = 0
        
    def connect(self, port="COM3"):
        """Connect to Arduino"""
        try:
            self.ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)
            self.connected = True
            print(f"✅ Arduino connected on {port}")
            
            # Start reading thread
            self._running = True
            threading.Thread(target=self._read_data, daemon=True).start()
            return True
        except:
            print(f"⚠️ Arduino not found on {port} - running without sensors")
            return False
    
    def _read_data(self):
        """Read moisture data from Arduino"""
        while self._running and self.connected:
            try:
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    if "MOISTURE" in line:
                        parts = line.split(",")
                        if len(parts) >= 3:
                            self.moisture = int(parts[2])
            except:
                pass
            time.sleep(1)
    
    def get_moisture(self):
        return self.moisture
    
    def water_pump(self, seconds=10):
        """Turn on water pump"""
        if self.connected:
            try:
                self.ser.write(b"WATER\n")
                print(f"��� Pump ON for {seconds}s")
            except:
                print("⚠️ Pump command failed")
        else:
            print("⚠️ Pump: Simulation mode")
    
    def disconnect(self):
        self._running = False
        if self.ser:
            self.ser.close()
        self.connected = False

# Create global instance
arduino = ArduinoController()
