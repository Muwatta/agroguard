#!/usr/bin/env python3
"""
Hardware Controller - Works on Windows (simulation) and Raspberry Pi (real GPIO)
"""

import time
import threading
import platform

# Check if running on Raspberry Pi
IS_RASPBERRY_PI = platform.machine().startswith('arm') or platform.system() == 'Linux'

# Try to import GPIO - fall back to simulation if not available
try:
    if IS_RASPBERRY_PI:
        import RPi.GPIO as GPIO
        GPIO_AVAILABLE = True
        print("✅ Raspberry Pi GPIO detected")
    else:
        GPIO_AVAILABLE = False
        print("ℹ️ Running on Windows - GPIO simulation mode")
except ImportError:
    GPIO_AVAILABLE = False
    print("ℹ️ GPIO not available - simulation mode")

class HardwareController:
    def __init__(self):
        self.relay_pin = 17
        self.buzzer_pin = 27
        self.sensor_pin = 22
        
        self.sprinkler_status = False
        self.simulation_mode = not GPIO_AVAILABLE
        
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            GPIO.setup(self.relay_pin, GPIO.OUT)
            GPIO.setup(self.buzzer_pin, GPIO.OUT)
            GPIO.setup(self.sensor_pin, GPIO.IN)
            
            GPIO.output(self.relay_pin, GPIO.LOW)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
            
            print("🔧 Hardware controller initialized (REAL GPIO)")
        else:
            print("🔧 Hardware controller initialized (SIMULATION MODE)")
    
    def sprinkler_on(self, duration=10):
        """Turn on sprinkler/pump"""
        if self.sprinkler_status:
            return  # Already running
            
        self.sprinkler_status = True
        print(f"🚿 SPRINKLER ON ({duration}s) - {'REAL' if GPIO_AVAILABLE else 'SIMULATED'}")
        
        if GPIO_AVAILABLE:
            GPIO.output(self.relay_pin, GPIO.HIGH)
        
        # Run in thread so it doesn't block
        def auto_off():
            time.sleep(duration)
            self.sprinkler_off()
        
        threading.Thread(target=auto_off).start()
        return True
    
    def sprinkler_off(self):
        """Turn off sprinkler"""
        self.sprinkler_status = False
        print("🚿 SPRINKLER OFF")
        
        if GPIO_AVAILABLE:
            GPIO.output(self.relay_pin, GPIO.LOW)
        return True
    
    def alert_buzzer(self, duration=2):
        """Sound alert buzzer"""
        print(f"🔔 BUZZER ({duration}s) - {'REAL' if GPIO_AVAILABLE else 'SIMULATED'}")
        
        if GPIO_AVAILABLE:
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
        else:
            # Windows beep
            print("\a")  # System beep
            time.sleep(duration)
        return True
    
    def read_soil_moisture(self):
        """Read soil moisture (0-100%)"""
        if GPIO_AVAILABLE:
            # Read from analog sensor via ADC or digital
            value = GPIO.input(self.sensor_pin)
            return 100 if value else 45  # Example conversion
        else:
            # Simulated value
            import random
            return random.randint(40, 80)
    
    def get_status(self):
        """Get current hardware status"""
        return {
            "sprinkler": self.sprinkler_status,
            "soil_moisture": self.read_soil_moisture(),
            "mode": "REAL" if GPIO_AVAILABLE else "SIMULATION",
            "platform": platform.system()
        }
    
    def cleanup(self):
        """Cleanup GPIO"""
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("GPIO cleaned up")

# Singleton instance
hardware = HardwareController()