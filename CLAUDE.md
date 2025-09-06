# Primordi Presto MicroPython Project

## Project Overview
This is a collection of useful apps for the Primordi Presto microcontroller running MicroPython.

## Important Notes

### Module Imports
Module imports in this project may appear to fail or be "not found" when running on desktop Python. This is expected behavior - these libraries are installed on the microcontroller itself and are not available in the desktop Python environment. Examples include:
- `presto` module
- `urequests` module (MicroPython version of requests)

### Current Apps

#### weather.py
A weather application that displays current conditions for San Francisco using the Open-Meteo API. Features:
- Current temperature
- Daily high/low temperatures  
- Wind speed
- Humidity
- Auto-refreshes every 10 minutes
- Requires WiFi credentials in `secrets.py`

### WiFi Configuration
WiFi credentials should be stored in `secrets.py` with the following variables:
- `WIFI_SSID`
- `WIFI_PASSWORD`

### Development Environment
- Platform: Primordi Presto
- Language: MicroPython
- Display: Bitmap display with pen-based drawing API
- Connectivity: WiFi support via `presto.connect()`