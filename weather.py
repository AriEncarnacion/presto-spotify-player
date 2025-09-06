# NAME Multi-City Weather
# DESC Touch to navigate between cities: Santa Rosa, Sonoma, Napa, SF, Tokyo, Kyoto, Okinawa

from presto import Presto
import time
import gc

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
    ],
    "loading": [
        "    ...   ",
        "  Loading ",
        "    ...   "
    ]
}

# Define cities with their coordinates and timezones
CITIES = [
    {
        "lat": 38.44178171092829,
        "lon": -122.71540395103689,
        "city": "Santa Rosa",
        "region": "CA",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    },
    {
        "lat": 38.2975,
        "lon": -122.4581,
        "city": "Sonoma",
        "region": "CA",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    },
    {
        "lat": 38.5025,
        "lon": -122.2654,
        "city": "Napa",
        "region": "CA",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    },
    {
        "lat": 37.7749,
        "lon": -122.4194,
        "city": "San Francisco",
        "region": "CA",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    },
    {
        "lat": 35.6762,
        "lon": 139.6503,
        "city": "Tokyo",
        "region": "",
        "country": "Japan",
        "timezone": "Asia/Tokyo"
    },
    {
        "lat": 35.0116,
        "lon": 135.7681,
        "city": "Kyoto",
        "region": "",
        "country": "Japan",
        "timezone": "Asia/Tokyo"
    },
    {
        "lat": 26.2124,
        "lon": 127.6792,
        "city": "Okinawa",
        "region": "",
        "country": "Japan",
        "timezone": "Asia/Tokyo"
    }
]

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

def fetch_weather_async(location):
    """Fetch weather data asynchronously (returns immediately with None if not cached)"""
    url = build_weather_url(location)
    try:
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
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None

def create_placeholder_weather(location):
    """Create placeholder weather data for optimistic UI"""
    return {
        "temp_f": "--",
        "wind_mph": "--",
        "humidity": "--",
        "low_f": "--",
        "high_f": "--",
        "weather_code": 0,
        "is_day": 1,
        "precipitation": 0,
        "snowfall": 0,
        "location": location,
        "loading": True
    }

def draw(presto, v, city_index, total_cities):
    d = presto.display
    W, H = d.get_bounds()

    BLACK = d.create_pen(0, 0, 0)
    WHITE = d.create_pen(255, 255, 255)
    CYAN  = d.create_pen(0, 255, 255)
    YELLOW = d.create_pen(255, 255, 0)
    GRAY = d.create_pen(128, 128, 128)
    BLUE = d.create_pen(100, 150, 255)

    d.set_pen(BLACK)
    d.clear()

    d.set_pen(WHITE)
    d.set_font("bitmap8")
    
    # Center content area - leave space for arrows on sides
    content_x_offset = 80  # Start content area further from left edge
    
    # Display location name - centered
    location = v.get("location", {})
    city = location.get("city", "Unknown")[:20]
    city_x = W // 2 - (len(city) * 8)  # Rough centering
    d.text(city, city_x, 10, scale=2)
    
    # Show city index (e.g., "1/7") - centered below city
    d.set_pen(GRAY)
    index_text = f"{city_index + 1}/{total_cities}"
    index_x = W // 2 - (len(index_text) * 4)
    d.text(index_text, index_x, 35, scale=1)

    # Get and draw weather art
    if v.get("loading", False):
        weather_type = "loading"
    else:
        weather_type = get_weather_art(
            v.get("weather_code", 0),
            v.get("is_day", 1),
            v.get("temp_f", 0) if v.get("temp_f") != "--" else 0,
            v.get("wind_mph", 0) if v.get("wind_mph") != "--" else 0,
            v.get("precipitation", 0),
            v.get("snowfall", 0)
        )
    
    art = WEATHER_ART.get(weather_type, WEATHER_ART["sun"])
    
    # Draw ASCII art with appropriate color - centered to right of temp
    if weather_type == "loading":
        d.set_pen(GRAY)
    elif weather_type in ["sun", "night_clear"]:
        d.set_pen(YELLOW)
    elif weather_type in ["rain", "heavy_rain", "thunder", "snow"]:
        d.set_pen(CYAN)
    else:
        d.set_pen(GRAY)
    
    # Draw ASCII art - move right to avoid overlap with temperature
    art_x = W - 110  # Shifted right from previous position
    art_y = 65
    for i, line in enumerate(art):
        d.text(line, art_x, art_y + (i * 20), scale=2)

    # Temperature in large font - move left but avoid arrow
    d.set_pen(CYAN)
    temp_display = str(v['temp_f']) + ("F" if v['temp_f'] != "--" else "")
    d.text(temp_display, 50, 75, scale=4)  # Moved left from 80 to 50

    # Weather details below - also moved left
    d.set_pen(WHITE)
    y_pos = 140
    low_display = str(v['low_f']) + ("F" if v['low_f'] != "--" else "")
    high_display = str(v['high_f']) + ("F" if v['high_f'] != "--" else "")
    d.text(f"L: {low_display}  H: {high_display}", 50, y_pos, scale=2)
    y_pos += 35
    wind_display = str(v['wind_mph']) + (" mph" if v['wind_mph'] != "--" else "")
    d.text(f"Wind: {wind_display}", 50, y_pos, scale=2)
    y_pos += 35
    humidity_display = str(v['humidity']) + ("%" if v['humidity'] != "--" else "")
    d.text(f"Humidity: {humidity_display}", 50, y_pos, scale=2)
    
    # Draw navigation arrows - closer to edges and smaller to avoid overlap
    arrow_y = H // 2 - 15  # Center vertically
    arrow_size = 3  # Slightly smaller to avoid overlap
    
    d.set_pen(BLUE)
    
    # Left arrow if not first city - closer to edge
    if city_index > 0:
        d.text("<", 5, arrow_y, scale=arrow_size)
    
    # Right arrow if not last city - closer to edge  
    if city_index < total_cities - 1:
        d.text(">", W - 25, arrow_y, scale=arrow_size)

    presto.update()

def main():
    presto = Presto(ambient_light=True)  # auto ambient backlighting
    presto.connect()                     # reads WIFI_SSID/WIFI_PASSWORD from secrets.py

    current_city_index = 0
    weather_cache = {}
    last_fetch_time = {}
    fetch_in_progress = {}  # Track which cities are being fetched
    
    # Touch tracking
    last_touch_state = False
    last_touch_x = 0
    
    REFRESH_SECS = 10 * 60  # Refresh weather data every 10 minutes
    
    # Initial draw with placeholder
    current_city = CITIES[current_city_index]
    placeholder_data = create_placeholder_weather(current_city)
    draw(presto, placeholder_data, current_city_index, len(CITIES))
    
    while True:
        try:
            # Check for touch input
            touch_x, touch_y, touch_state = presto.touch_a
            
            # Detect touch release (was touched, now not touched)
            if last_touch_state and not touch_state:
                W, _ = presto.display.get_bounds()
                
                old_city_index = current_city_index
                
                # Left side of screen - previous city (more generous touch zone)
                if last_touch_x < W // 3 and current_city_index > 0:
                    current_city_index -= 1
                
                # Right side of screen - next city (more generous touch zone)
                elif last_touch_x > 2 * W // 3 and current_city_index < len(CITIES) - 1:
                    current_city_index += 1
                
                # If city changed, immediately show placeholder
                if old_city_index != current_city_index:
                    current_city = CITIES[current_city_index]
                    city_key = current_city["city"]
                    
                    # Show cached data or placeholder immediately for responsiveness
                    if city_key in weather_cache:
                        draw(presto, weather_cache[city_key], current_city_index, len(CITIES))
                    else:
                        placeholder_data = create_placeholder_weather(current_city)
                        draw(presto, placeholder_data, current_city_index, len(CITIES))
                    
                    # Mark that we need to fetch this city's data
                    fetch_in_progress[city_key] = True
            
            last_touch_state = touch_state
            if touch_state:
                last_touch_x = touch_x
            
            # Get current city
            current_city = CITIES[current_city_index]
            city_key = current_city["city"]
            
            # Check if we need to fetch new weather data
            current_time = time.time()
            needs_refresh = (
                city_key not in weather_cache or
                city_key not in last_fetch_time or
                current_time - last_fetch_time.get(city_key, 0) > REFRESH_SECS or
                fetch_in_progress.get(city_key, False)
            )
            
            if needs_refresh:
                # Fetch weather for current city
                weather_data = fetch_weather_async(current_city)
                if weather_data:
                    weather_cache[city_key] = weather_data
                    last_fetch_time[city_key] = current_time
                    fetch_in_progress[city_key] = False
                    
                    # Update display with real data if still on same city
                    if current_city_index == CITIES.index(current_city):
                        draw(presto, weather_data, current_city_index, len(CITIES))
                    
                    # Clean up memory after heavy operation
                    gc.collect()
            elif city_key in weather_cache:
                # Use cached data
                weather_data = weather_cache[city_key]
                draw(presto, weather_data, current_city_index, len(CITIES))
            
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
        
        # Short sleep to keep the touch responsive
        time.sleep(0.05)  # Even shorter for better responsiveness

main()