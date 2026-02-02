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
    return tinytuya.Cloud(apiRegion=API_REGION, apiKey=API_KEY, apiSecret=API_SECRET)

def send_command(code, value):
    result = get_cloud().sendcommand(DEVICE_ID, {'commands': [{'code': code, 'value': value}]})
    if result.get('success'):
        print(f"✅ {code} -> {value}")
    else:
        print(f"❌ Error: {result}")
    return result.get('success')

def print_status():
    result = get_cloud().getstatus(DEVICE_ID)
    if not result.get('success'):
        print(f"Error: {result}")
        return
    status = {item['code']: item['value'] for item in result.get('result', [])}
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

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    arg = sys.argv[2].lower() if len(sys.argv) > 2 else None
    
    match cmd:
        case 'status':
            print_status()
        case 'on':
            send_command('work_state', 'opened')
        case 'off':
            send_command('work_state', 'closed')
        case 'set-temp' if arg:
            temp = int(float(arg) * 10)
            if 50 <= temp <= 300:
                send_command('temp_set', temp)
            else:
                print("Error: Temperature must be between 5°C and 30°C")
        case 'mode' if arg in ['auto', 'manual', 'on', 'off']:
            send_command('mode', arg)
        case 'system-mode' if arg in ['comfort', 'eco']:
            send_command('system_mode', 'comfort_mode' if arg == 'comfort' else 'Eco_mode')
        case _:
            print(f"Unknown command: {cmd}")
            print(__doc__)

if __name__ == '__main__':
    main()
