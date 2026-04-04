
import serial
import time
import threading

class SimpleArduino:
    def __init__(self, port="COM3"):
        self.port = port
        self.ser = None
        self.connected = False
        self.moisture = 0
        
    def connect(self):
        """Connect to Arduino - students run this once"""
        try:
            self.ser = serial.Serial(self.port, 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"✅ Connected to Arduino on {self.port}")
            
            # Start reading thread
            self.running = True
            threading.Thread(target=self._read_serial, daemon=True).start()
            return True
        except Exception as e:
            print(f"❌ Cannot connect: {e}")
            print("   Check: USB cable? Port number? Arduino powered?")
            return False
    
    def _read_serial(self):
        """Keep reading moisture data"""
        while self.running and self.connected:
            try:
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    if line.startswith("MOISTURE"):
                        parts = line.split(",")
                        if len(parts) >= 3:
                            self.moisture = int(parts[2])  # Percentage
                            print(f"Soil Moisture: {self.moisture}%")
            except:
                pass
            time.sleep(0.5)
    
    def get_moisture(self):
        """Get current moisture percentage"""
        return self.moisture
    
    def water_pump(self, seconds=5):
        """Turn on water pump"""
        if not self.connected:
            print("❌ Arduino not connected")
            return
        try:
            self.ser.write(b"WATER\n")
            print(f"Water pump ON for {seconds} seconds")
            # Note: Arduino handles the timing
        except:
            print("❌ Failed to send command")
    
    def disconnect(self):
        """Close connection"""
        self.running = False
        if self.ser:
            self.ser.close()
        self.connected = False
        print("Disconnected from Arduino")

# Test function - students can run this to test
def test_arduino():
    print("=" * 40)
    print("Testing Arduino Connection")
    print("=" * 40)
    print("1. Plug Arduino via USB")
    print("2. Check port number (COM3, COM4, etc.)")
    print("")
    
    port = input("Enter port (e.g., COM3): ").strip() or "COM3"
    
    arduino = SimpleArduino(port)
    if arduino.connect():
        print("\n✅ Arduino connected! Reading moisture...")
        print("Press Ctrl+C to stop\n")
        try:
            while True:
                time.sleep(2)
                print(f"Moisture: {arduino.get_moisture()}%")
        except KeyboardInterrupt:
            arduino.disconnect()
    else:
        print("\n❌ Could not connect. Check:")
        print("   - USB cable connected?")
        print("   - Correct port number?")
        print("   - Arduino powered on?")

if __name__ == "__main__":
    test_arduino()
