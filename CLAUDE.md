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

## Documentation
Key documentation files are available in the `docs/` directory:
- **EzWiFi Documentation**: `docs/EzWiFi_docs.md` - WiFi connectivity and network operations
- **Pico Graphics Documentation**: `docs/pico_graphics.md` - Display and graphics API reference
- **Pico Vector Library**: `docs/pico_vector.md` - Vector graphics library documentation
- **Presto Function Reference**: `docs/presto_function_reference.md` - General Presto platform functions
- **Best Practices**: `docs/best_practices.md` - Community-recommended coding practices

## Development Guidelines
**IMPORTANT**: When writing or modifying any code for this project, always reference `docs/best_practices.md` first to ensure compliance with community-recommended best practices. This includes:
- Code structure and organization
- Performance optimization techniques
- Memory management considerations
- Display and UI patterns
- Error handling approaches