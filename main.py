# Example Usage of TinyTuya
import tinytuya
import time
import tomllib
from pathlib import Path

# Load configuration from config.toml
CONFIG_PATH = Path(__file__).parent / 'config.toml'

if not CONFIG_PATH.exists():
    print(f"Error: {CONFIG_PATH} not found.")
    print("Please create config.toml with your Tuya credentials.")
    exit(1)

with open(CONFIG_PATH, 'rb') as f:
    config = tomllib.load(f)

# Enable debug to see what's happening
tinytuya.set_debug(True)

# Configuration from config.toml
DEVICE_ID = config['device']['device_id']
IP_ADDRESS = config['device']['ip_address']
LOCAL_KEY = config['device']['local_key']
VERSION = config['device']['version']

print(f"Connecting to {IP_ADDRESS}...")

d = tinytuya.Device(DEVICE_ID, IP_ADDRESS, LOCAL_KEY, version=VERSION)
d.set_socketPersistent(True)

# Retry loop
for i in range(3):
    try:
        data = d.status()
        if data and 'Error' not in data:
            print('\nSUCCESS! Device status: %r' % data)
            break
        print(f"Attempt {i+1} failed: {data}")
    except Exception as e:
        print(f"Attempt {i+1} Exception: {e}")
    time.sleep(2)