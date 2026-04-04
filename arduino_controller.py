#!/usr/bin/env python3
"""
Arduino Controller - Matches agroguard_irrigation.ino
Supports: MOISTURE reading, PUMP control, STATUS messages
"""

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
        self._running = False
        
        # Auto-detect and connect
        self._connect()
        
        # Start background reader if connected
        if self.connected:
            self._running = True
            threading.Thread(target=self._read_loop, daemon=True).start()
    
    def _connect(self):
        """Auto-detect Arduino on common ports"""
        if platform.system() == 'Windows':
            ports = ['COM3', 'COM4', 'COM5', 'COM6']
        else:
            ports = ['/dev/ttyUSB0', '/dev/ttyACM0']
        
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
                    if "AGROGUARD" in response or "MOISTURE" in response:
                        self.connected = True
                        self.simulation_mode = False
                        print(f"✅ Arduino connected on {port}")
                        return
                
                self.ser.close()
            except:
                pass
        
        self.connected = False
        self.simulation_mode = True
        print("ℹ️ Arduino not found - SIMULATION MODE")
    
    def _read_loop(self):
        """Read data from Arduino continuously"""
        while self._running and self.connected:
            try:
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    self._parse_line(line)
            except:
                pass
            time.sleep(0.1)
    
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
        
        # STATUS messages
        elif line.startswith("STATUS:"):
            print(f"📡 {line}")
        
        # AGROGUARD:READY
        elif "READY" in line:
            print(f"✅ Arduino ready: {line}")
    
    def send_command(self, cmd):
        """Send command to Arduino"""
        if not self.connected:
            print(f"[SIM] Command: {cmd}")
            return
        
        try:
            self.ser.write(f"{cmd}\n".encode())
        except Exception as e:
            print(f"❌ Send failed: {e}")
    
    # ========== PUBLIC METHODS ==========
    
    def sprinkler_on(self, duration=10):
        """Turn sprinkler ON"""
        print(f"🚿 Sprinkler ON ({duration}s)")
        self.send_command("PUMP_ON")
        # Note: Arduino handles timing, or you can use time.sleep(duration)
        return True
    
    def sprinkler_off(self):
        """Turn sprinkler OFF"""
        print(f"🚿 Sprinkler OFF")
        self.send_command("PUMP_OFF")
        return True
    
    def get_moisture(self):
        """Get current moisture percentage"""
        return self.moisture
    
    def get_sensor_data(self):
        """Get all sensor data"""
        return {
            "soil_moisture": self.moisture,
            "pump_status": self.pump_on,
            "connected": self.connected,
            "simulated": self.simulation_mode
        }
    
    def get_status(self):
        """Get connection status"""
        return {
            "connected": self.connected,
            "simulation_mode": self.simulation_mode,
            "moisture": self.moisture
        }
    
    def close(self):
        """Close serial connection"""
        self._running = False
        if self.ser:
            self.ser.close()

# Global instance
arduino = ArduinoController()