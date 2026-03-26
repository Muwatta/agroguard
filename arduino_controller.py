#!/usr/bin/env python3
"""
Arduino Controller via Serial USB
Works on Windows (COM port) and Linux (/dev/ttyUSB0)
"""

import serial
import time
import threading
import platform

class ArduinoController:
    def __init__(self):
        self.connected = False
        self.serial = None
        self.simulation_mode = True
        
        # Auto-detect port
        if platform.system() == 'Windows':
            ports = ['COM3', 'COM4', 'COM5', 'COM6']
        else:
            ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyUSB1']
        
        for port in ports:
            try:
                self.serial = serial.Serial(port, 9600, timeout=2)
                time.sleep(2)  # Wait for Arduino reset
                self.connected = True
                self.simulation_mode = False
                print(f"✅ Arduino connected on {port}")
                break
            except Exception as e:
                continue
        
        if not self.connected:
            print("ℹ️ Arduino not connected - running in simulation mode")
    
    def send_command(self, command):
        """Send command to Arduino"""
        if not self.connected:
            print(f"[SIM] Command: {command}")
            if command == "STATUS":
                # Simulated sensor data
                import random
                return f"DATA:{random.randint(50, 90)},{random.randint(25, 35)}"
            return "SIM_OK"
        
        try:
            self.serial.write(f"{command}\n".encode())
            response = self.serial.readline().decode().strip()
            return response
        except Exception as e:
            print(f"Arduino error: {e}")
            return "ERROR"
    
    def sprinkler_on(self, duration=10):
        """Activate sprinkler"""
        print(f"🚿 Arduino: SPRINKLER ON ({duration}s)")
        response = self.send_command("SPRINKLER_ON")
        return response
    
    def get_sensor_data(self):
        """Get soil moisture and temperature"""
        response = self.send_command("STATUS")
        if response and response.startswith("DATA:"):
            parts = response[5:].split(',')
            return {
                "soil_moisture": float(parts[0]),
                "temperature": float(parts[1]),
                "timestamp": time.time()
            }
        return {"soil_moisture": 65.0, "temperature": 28.5, "simulated": True}
    
    def close(self):
        if self.serial:
            self.serial.close()

# Singleton
arduino = ArduinoController()