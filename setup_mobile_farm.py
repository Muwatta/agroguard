#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mobile Farm Hardware Setup Guide
"""

print("=" * 60)
print("AGROGUARD - MOBILE FARM HARDWARE SETUP")
print("=" * 60)

print("\ní³‹ COMPONENTS NEEDED:")
print("  1. Raspberry Pi 4 (or Arduino Uno)")
print("  2. USB Camera or Pi Camera")
print("  3. 5V Buzzer module")
print("  4. 5V Relay module (for sprinkler)")
print("  5. 12V water pump or solenoid valve")
print("  6. Small water container (2-5 liters)")
print("  7. Tubing and connectors")
print("  8. Jumper wires")
print("  9. Small plant pot with soil")
print(" 10. Seeds or small plant")

print("\ní´Œ WIRING DIAGRAM:")
print("  Raspberry Pi GPIO:")
print("    GPIO17 (Pin 11) -> Buzzer (+)")
print("    GND (Pin 6)     -> Buzzer (-)")
print("    GPIO18 (Pin 12) -> Relay IN")
print("    GND (Pin 14)    -> Relay GND")
print("    Relay COM -> 12V power (+)")
print("    Relay NO  -> Water pump (+)")
print("    Water pump (-) -> GND")

print("\ní¼± MOBILE FARM SETUP:")
print("  1. Plant seeds in small pot (2-3 weeks before demo)")
print("  2. Position camera facing the plant")
print("  3. Place water pump near water container")
print("  4. Run tubing from pump to plant soil")
print("  5. Test sprinkler manually")

print("\níº€ DEPLOYMENT STEPS:")
print("  1. Install OS on Raspberry Pi (Raspberry Pi OS Lite)")
print("  2. Install dependencies:")
print("     sudo apt update")
print("     sudo apt install python3-pip python3-opencv")
print("     pip3 install -r requirements.txt")
print("  3. Enable camera: sudo raspi-config")
print("  4. Copy project files to Pi")
print("  5. Run: python3 app.py")

print("\nâœ… Ready for real hardware!")
