#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hardware controller for AgroGuard
"""

import time

class HardwareController:
    def __init__(self):
        self.simulation_mode = True
        print("Hardware controller initialized (SIMULATION MODE)")
    
    def alert_buzzer(self, duration=1):
        """Trigger buzzer alert"""
        print(f"BUZZER ALERT ({duration}s) - SIMULATED")
        return True
    
    def sprinkler_on(self, duration=10):
        """Turn on sprinkler"""
        print(f"SPRINKLER ON ({duration}s) - SIMULATED")
        time.sleep(duration)
        print("SPRINKLER OFF - SIMULATED")
        return True
    
    def sprinkler_off(self):
        """Turn off sprinkler"""
        print("SPRINKLER OFF - SIMULATED")
        return True
    
    def get_status(self):
        """Get hardware status"""
        return {
            "mode": "SIMULATION",
            "buzzer": "ready",
            "sprinkler": "ready"
        }

# Create global instance
hardware = HardwareController()
