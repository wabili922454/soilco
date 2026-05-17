import os
import requests
from dotenv import load_dotenv

# ─── SMART PATH CONFIGURATION ───
# Just like we did for Supabase, this makes sure Python can find the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

# Grab your OpenWeatherMap API key from the environment variables
OWM_API_KEY = os.getenv("OWM_API_KEY")

def get_weather(lat: float, lon: float) -> dict | None:
    """
    Fetches current weather metrics from OpenWeatherMap using coordinates.
    Returns a dictionary of metrics, or None if the request fails (Rule 5 - Option A).
    """
    if not OWM_API_KEY:
        print("⚠️ Weather Error: OWM_API_KEY is missing from your .env file.")
        return None

    # This is the official API endpoint for current weather data (metric units = Celsius/meters)
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        
        # If the API key is wrong or the service is down, this forces it into the except block safely
        response.raise_for_status()
        
        data = response.json()

        # OpenWeatherMap nested format check: data['rain']['1h']
        # If it isn't currently raining, the API completely hides the 'rain' key. 
        # We check for it safely here so your code doesn't crash.
        rain_data = data.get("rain", {})
        rain_mm = rain_data.get("1h", 0.0)  # If no rain, default to 0.0 mm

        # Constructing the exact data shape your frontend expects (Rule 6)
        weather_dict = {
            "temp": float(data["main"]["temp"]),
            "humidity": int(data["main"]["humidity"]),
            "wind": float(data["wind"]["speed"]),
            "rain": float(rain_mm)  # Kept in millimeters per team agreement (Rule 3)
        }
        
        return weather_dict

    except Exception as e:
        print("Weather API request failed:", e)
        return None  # Rule 5: Return None on failure
    
def calculate_irrigation_advice(temp: float, humidity: int) -> dict:
    """
    Agricultural algorithm that calculates evaporation risks and 
    provides smart watering adjustments based on live atmospheric data.
    """
    # Default baseline recommendations
    status = "Normal"
    recommendation = "Maintain your standard soil moisture targets today."
    icon_alert = "info"

    # Scenario A: High Evaporation Risk (Hot and Dry)
    if temp > 30 and humidity < 45:
        status = "Critical Overheat"
        recommendation = "High evaporation risk detected! Increase automated watering volumes by 25% to protect roots."
        icon_alert = "warning"
    
    # Scenario B: High Fungal/Rot Risk (Warm and Extremely Humid)
    elif temp > 22 and humidity > 85:
        status = "Saturated Environment"
        recommendation = "Excess moisture levels present. Reduce watering cycles to mitigate risk of root rot or fungal growth."
        icon_alert = "water_drop"

    # Scenario C: Low Evaporation Risk (Cold or Rainy environment)
    elif temp < 12:
        status = "Low Transpiration"
        recommendation = "Low temperatures detected. Crops require less water; suspend unnecessary irrigation intervals."
        icon_alert = "ac_unit"

    return {
        "status": status,
        "advice": recommendation,
        "icon": icon_alert
    }    