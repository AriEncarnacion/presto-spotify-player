# NAME SF Weather
# DESC Current temp, today’s low/high, wind, humidity (San Francisco)

from presto import Presto
import time

# MicroPython "requests" shim: some builds ship "requests", others "urequests"
try:
    import requests
except ImportError:
    import urequests as requests

# ASCII art for weather conditions (compact for small display)
WEATHER_ART = {
    "sun": [
        "   \\|/   ",
        "  --O--  ",
        "   /|\\   "
    ],
    "cloud": [
        "  .--.   ",
        " (    )  ",
        "(_____) "
    ],
    "rain": [
        "  .--.   ",
        " (    )  ",
        "  ||||   "
    ],
    "heavy_rain": [
        "  .--.   ",
        " (    )  ",
        " ||||||  "
    ],
    "snow": [
        "  .--.   ",
        " (    )  ",
        " * * * * "
    ],
    "thunder": [
        "  .--.   ",
        " (    )  ",
        "  /\\/\\   "
    ],
    "fog": [
        " ~ ~ ~ ~ ",
        "~ ~ ~ ~  ",
        " ~ ~ ~ ~ "
    ],
    "wind": [
        " ~~~>    ",
        "  ~~~>   ",
        " ~~~>    "
    ],
    "night_clear": [
        "    *    ",
        "  ( )    ",
        "    *    "
    ],
    "night_cloud": [
        "  ( )-.  ",
        " (    )  ",
        "(_____) "
    ]
}

def get_location():
    """Get current location based on IP address"""
    try:
        # Use ip-api.com for free geolocation (no API key required)
        r = requests.get("http://ip-api.com/json/")
        data = r.json()
        r.close()
        
        if data.get("status") == "success":
            return {
                "lat": data["lat"],
                "lon": data["lon"],
                "city": data.get("city", "Unknown"),
                "region": data.get("regionName", ""),
                "country": data.get("country", ""),
                "timezone": data.get("timezone", "America/Los_Angeles")
            }
    except:
        pass
    
    # Fallback to Santa Rosa if geolocation fails
    return {
        "lat": 38.44178171092829,
        "lon": -122.71540395103689,
        "city": "Santa Rosa",
        "region": "California",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    }

def build_weather_url(location):
    """Build weather API URL for given location"""
    lat = location["lat"]
    lon = location["lon"]
    timezone = location["timezone"].replace("/", "%2F")
    
    return (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,precipitation,snowfall,is_day"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&temperature_unit=fahrenheit&wind_speed_unit=mph"
        f"&timezone={timezone}"
    )

def get_weather_art(weather_code, is_day, temp_f, wind_mph, precipitation, snowfall):
    """
    Determine which ASCII art to show based on weather conditions.
    Weather codes: https://open-meteo.com/en/docs
    """
    # Thunder conditions (95, 96, 99)
    if weather_code in [95, 96, 99]:
        return "thunder"
    
    # Snow conditions (71-77, 85-86) or if it's snowing
    if weather_code in [71, 72, 73, 75, 77, 85, 86] or (snowfall and snowfall > 0):
        return "snow"
    
    # Rain conditions (51-67, 80-82)
    if weather_code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "heavy_rain"
    elif weather_code in [51, 53, 55, 56, 57]:
        return "rain"
    elif precipitation and precipitation > 0:
        return "rain"
    
    # Fog conditions (45, 48)
    if weather_code in [45, 48]:
        return "fog"
    
    # High wind conditions
    if wind_mph > 25:
        return "wind"
    
    # Cloud conditions (1-3)
    if weather_code in [2, 3]:
        if is_day:
            return "cloud"
        else:
            return "night_cloud"
    
    # Clear conditions
    if is_day:
        return "sun"
    else:
        return "night_clear"

def fetch_weather(location):
    url = build_weather_url(location)
    r = requests.get(url)
    data = r.json()
    r.close()

    cur = data["current"]
    daily = data["daily"]

    return {
        "temp_f": round(cur["temperature_2m"]),
        "wind_mph": round(cur["wind_speed_10m"]),
        "humidity": int(cur["relative_humidity_2m"]),
        "low_f":   round(daily["temperature_2m_min"][0]),
        "high_f":  round(daily["temperature_2m_max"][0]),
        "weather_code": cur.get("weather_code", 0),
        "is_day": cur.get("is_day", 1),
        "precipitation": cur.get("precipitation", 0),
        "snowfall": cur.get("snowfall", 0),
        "location": location,
    }

def draw(presto, v):
    d = presto.display
    W, H = d.get_bounds()

    BLACK = d.create_pen(0, 0, 0)
    WHITE = d.create_pen(255, 255, 255)
    CYAN  = d.create_pen(0, 255, 255)
    YELLOW = d.create_pen(255, 255, 0)
    GRAY = d.create_pen(128, 128, 128)

    d.set_pen(BLACK)
    d.clear()

    d.set_pen(WHITE)
    d.set_font("bitmap8")
    # Display location name (truncate if too long)
    location = v.get("location", {})
    city = location.get("city", "Unknown")[:20]  # Limit city name length
    d.text(city, 16, 10, scale=2)

    # Get and draw weather art
    weather_type = get_weather_art(
        v.get("weather_code", 0),
        v.get("is_day", 1),
        v["temp_f"],
        v["wind_mph"],
        v.get("precipitation", 0),
        v.get("snowfall", 0)
    )
    
    art = WEATHER_ART.get(weather_type, WEATHER_ART["sun"])
    
    # Draw ASCII art with appropriate color
    if weather_type in ["sun", "night_clear"]:
        d.set_pen(YELLOW)
    elif weather_type in ["rain", "heavy_rain", "thunder", "snow"]:
        d.set_pen(CYAN)
    else:
        d.set_pen(GRAY)
    
    # Draw ASCII art on the right side
    art_x = W - 120
    art_y = 45
    for i, line in enumerate(art):
        d.text(line, art_x, art_y + (i * 20), scale=2)

    # Temperature in large font on the left
    d.set_pen(CYAN)
    d.text(f"{v['temp_f']}F", 16, 55, scale=4)

    # Weather details below
    d.set_pen(WHITE)
    y_pos = 120
    d.text(f"L: {v['low_f']}F  H: {v['high_f']}F", 16, y_pos, scale=2)
    y_pos += 35
    d.text(f"Wind: {v['wind_mph']} mph", 16, y_pos, scale=2)
    y_pos += 35
    d.text(f"Humidity: {v['humidity']}%", 16, y_pos, scale=2)

    presto.update()

def main():
    presto = Presto(ambient_light=True)  # auto ambient backlighting
    presto.connect()                     # reads WIFI_SSID/WIFI_PASSWORD from secrets.py

    # Get location once at startup
    location = get_location()
    
    REFRESH_SECS = 10 * 60
    while True:
        try:
            vals = fetch_weather(location)
            draw(presto, vals)
        except Exception as e:
            d = presto.display
            RED = d.create_pen(255, 0, 0)
            BLACK = d.create_pen(0, 0, 0)
            d.set_pen(BLACK); d.clear()
            d.set_pen(RED); d.set_font("bitmap8")
            d.text("Weather fetch failed", 16, 16, scale=2)
            d.text(str(e), 16, 56, scale=1)
            presto.update()
            time.sleep(15)
        time.sleep(REFRESH_SECS)

main()