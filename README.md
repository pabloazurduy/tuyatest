*ai generated*

# tuya-thermostat-control

Local and cloud control for Tuya thermostats.

## setup

1. Install dependencies:
   pip install tinytuya

2. Configure:
   Copy config.toml.example to config.toml and add your credentials.

## usage

python thermo.py status
python thermo.py set-temp 22
python thermo.py on
python thermo.py off
python thermo.py mode <auto|manual|on|off>
python thermo.py system-mode <comfort|eco>
