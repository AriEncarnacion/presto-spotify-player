"""
Simple WiFi connection test app for Primordi Presto
Displays "Successful" or "Failed" based on WiFi connection status
"""

from presto import Presto
from secrets import WIFI_SSID, WIFI_PASSWORD

presto = Presto()
display = presto.display

# Try to connect to WiFi
try:
    # Attempt connection
    presto.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # If we get here, connection was successful
    message = "Successful :)"
    green_pen = display.create_pen(0, 255, 0)
    display.set_pen(green_pen)
    display.text(message, 10, 60)
    
except Exception as e:
    # Connection failed
    message = "Failed :("
    red_pen = display.create_pen(255, 0, 0)
    display.set_pen(red_pen)
    display.text(message, 10, 60)

# Update the display
presto.update()