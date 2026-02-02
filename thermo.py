#!/usr/bin/env python3
"""
Tuya Thermostat CLI Control via Cloud API
Usage:
    python thermo.py status              # Show current status
    python thermo.py set-temp 22         # Set target temperature (°C)
    python thermo.py on                  # Turn on
    python thermo.py off                 # Turn off
    python thermo.py mode <mode>         # Set mode: auto, manual, on, off
    python thermo.py system-mode <mode>  # Set system mode: comfort, eco
"""

import sys
import tomllib
from pathlib import Path
import tinytuya

# Load configuration from config.toml
CONFIG_PATH = Path(__file__).parent / 'config.toml'

if not CONFIG_PATH.exists():
    print(f"Error: {CONFIG_PATH} not found.")
    print("Please create config.toml with your Tuya credentials.")
    sys.exit(1)

with open(CONFIG_PATH, 'rb') as f:
    config = tomllib.load(f)

# Cloud API credentials
API_REGION = config['cloud']['api_region']
API_KEY = config['cloud']['api_key']
API_SECRET = config['cloud']['api_secret']
DEVICE_ID = config['device']['device_id']

def get_cloud():
    return tinytuya.Cloud(
        apiRegion=API_REGION,
        apiKey=API_KEY,
        apiSecret=API_SECRET
    )

def get_status():
    cloud = get_cloud()
    result = cloud.getstatus(DEVICE_ID)
    
    if not result.get('success'):
        print(f"Error: {result}")
        return None
    
    # Parse status into readable dict
    status = {}
    for item in result.get('result', []):
        status[item['code']] = item['value']
    
    return status

def print_status():
    status = get_status()
    if not status:
        return
    
    print("\n🌡️  WiFi Smart Thermostat Status")
    print("=" * 40)
    print(f"  State:        {'🟢 ON' if status.get('work_state') == 'opened' else '🔴 OFF'}")
    print(f"  Mode:         {status.get('mode', 'unknown')}")
    print(f"  Target Temp:  {status.get('temp_set', 0) / 10:.1f}°C")
    print(f"  Current Temp: {status.get('temp_current', 0) / 10:.1f}°C")
    print(f"  Valve Open:   {status.get('valve_open_degree', 0) / 10:.0f}%")
    print(f"  Battery:      {status.get('battery_percentage', 0)}%")
    print(f"  Child Lock:   {'🔒 On' if status.get('child_lock') else 'Off'}")
    print(f"  System Mode:  {status.get('system_mode', 'unknown')}")
    print()

def send_command(code: str, value):
    """Send a command to the thermostat via cloud API"""
    cloud = get_cloud()
    commands = {'commands': [{'code': code, 'value': value}]}
    result = cloud.sendcommand(DEVICE_ID, commands)
    return result

def set_temperature(temp: float):
    """Set target temperature in Celsius"""
    temp_value = int(temp * 10)  # API uses tenths of degrees
    
    if temp_value < 50 or temp_value > 300:  # 5°C to 30°C
        print("Error: Temperature must be between 5°C and 30°C")
        return False
    
    result = send_command('temp_set', temp_value)
    if result.get('success'):
        print(f"✅ Temperature set to {temp}°C")
        return True
    else:
        print(f"❌ Error: {result}")
        return False

def turn_on():
    result = send_command('work_state', 'opened')
    if result.get('success'):
        print("✅ Thermostat turned ON")
    else:
        print(f"❌ Error: {result}")

def turn_off():
    result = send_command('work_state', 'closed')
    if result.get('success'):
        print("✅ Thermostat turned OFF")
    else:
        print(f"❌ Error: {result}")

def set_mode(mode: str):
    """Set thermostat mode: auto, manual, on, off"""
    valid_modes = ['auto', 'manual', 'on', 'off']
    if mode not in valid_modes:
        print(f"Error: Mode must be one of: {', '.join(valid_modes)}")
        return False
    
    result = send_command('mode', mode)
    if result.get('success'):
        print(f"✅ Mode set to {mode}")
        return True
    else:
        print(f"❌ Error: {result}")
        return False

def set_system_mode(mode: str):
    """Set system mode: comfort, eco"""
    mode_map = {
        'comfort': 'comfort_mode',
        'eco': 'Eco_mode',
        'comfort_mode': 'comfort_mode',
        'eco_mode': 'Eco_mode',
    }
    
    mode_value = mode_map.get(mode.lower())
    if not mode_value:
        print("Error: System mode must be 'comfort' or 'eco'")
        return False
    
    result = send_command('system_mode', mode_value)
    if result.get('success'):
        print(f"✅ System mode set to {mode}")
        return True
    else:
        print(f"❌ Error: {result}")
        return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        print_status()
    
    elif command == 'set-temp':
        if len(sys.argv) < 3:
            print("Usage: python thermo.py set-temp <temperature>")
            return
        try:
            temp = float(sys.argv[2])
            set_temperature(temp)
        except ValueError:
            print("Error: Invalid temperature value")
    
    elif command == 'on':
        turn_on()
    
    elif command == 'off':
        turn_off()
    
    elif command == 'mode':
        if len(sys.argv) < 3:
            print("Usage: python thermo.py mode <auto|manual|on|off>")
            return
        set_mode(sys.argv[2].lower())
    
    elif command == 'system-mode':
        if len(sys.argv) < 3:
            print("Usage: python thermo.py system-mode <comfort|eco>")
            return
        set_system_mode(sys.argv[2].lower())
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()
