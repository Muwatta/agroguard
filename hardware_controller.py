#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Real hardware controller for Raspberry Pi/Arduino
"""

import time
import platform

# Try to import RPi.GPIO (for Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
    print("‚úÖ Raspberry Pi GPIO detected")
except ImportError:
    IS_RASPBERRY_PI = False
    print("‚ö†Ô∏è Not running on Raspberry Pi - using simulation")

class HardwareController:
    def __init__(self):
        self.simulation_mode = not IS_RASPBERRY_PI
        
        # Pin definitions (adjust as needed)
        self.BUZZER_PIN = 17
        self.SPRINKLER_PIN = 18
        
        if not self.simulation_mode:
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
            GPIO.setup(self.SPRINKLER_PIN, GPIO.OUT)
            
            # Initial state OFF
            GPIO.output(self.BUZZER_PIN, GPIO.LOW)
            GPIO.output(self.SPRINKLER_PIN, GPIO.LOW)
            
            print(f"Ì¥ß Real hardware initialized (GPIO mode)")
            print(f"   Buzzer: GPIO{self.BUZZER_PIN}")
            print(f"   Sprinkler: GPIO{self.SPRINKLER_PIN}")
        else:
            print(f"Ì¥ß Hardware controller initialized (SIMULATION MODE)")
    
    def alert_buzzer(self, duration=1):
        """Turn on buzzer for specified duration"""
        if not self.simulation_mode:
            print(f"Ì¥î BUZZER ON (GPIO{self.BUZZER_PIN})")
            GPIO.output(self.BUZZER_PIN, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.BUZZER_PIN, GPIO.LOW)
            print(f"Ì¥î BUZZER OFF")
        else:
            print(f"Ì¥î BUZZER ({duration}s) - SIMULATED")
        
        return True
    
    def sprinkler_on(self, duration=10):
        """Turn on sprinkler for specified duration"""
        if not self.simulation_mode:
            print(f"Ì∫ø SPRINKLER ON (GPIO{self.SPRINKLER_PIN})")
            GPIO.output(self.SPRINKLER_PIN, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.SPRINKLER_PIN, GPIO.LOW)
            print(f"Ì∫ø SPRINKLER OFF")
        else:
            print(f"Ì∫ø SPRINKLER ON ({duration}s) - SIMULATED")
        
        return True
    
    def sprinkler_off(self):
        """Turn off sprinkler immediately"""
        if not self.simulation_mode:
            GPIO.output(self.SPRINKLER_PIN, GPIO.LOW)
            print(f"Ì∫ø SPRINKLER OFF (manual)")
        else:
            print(f"Ì∫ø SPRINKLER OFF - SIMULATED")
        
        return True
    
    def get_status(self):
        """Get current hardware status"""
        if not self.simulation_mode:
            return {
                "mode": "REAL",
                "buzzer_pin": self.BUZZER_PIN,
                "sprinkler_pin": self.SPRINKLER_PIN,
                "buzzer_state": GPIO.input(self.BUZZER_PIN),
                "sprinkler_state": GPIO.input(self.SPRINKLER_PIN)
            }
        else:
            return {
                "mode": "SIMULATION",
                "buzzer_pin": self.BUZZER_PIN,
                "sprinkler_pin": self.SPRINKLER_PIN
            }
    
    def cleanup(self):
        """Cleanup GPIO on exit"""
        if not self.simulation_mode:
            GPIO.cleanup()
            print("Ì¥ß GPIO cleaned up")

# Create global instance
hardware = HardwareController()
