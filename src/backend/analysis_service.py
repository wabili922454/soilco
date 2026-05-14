from groq import Groq
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_coords_from_city(city_name):
    """Convert city name to lat/lon using Nominatim (free, no key needed)"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city_name, "format": "json", "limit": 1}
        headers = {"User-Agent": "soilco-app"}
        res = requests.get(url, params=params, headers=headers, timeout=8)
        data = res.json()
        if not data:
            print(f"Nominatim: no results for '{city_name}'")
            return None, None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        print(f"Coords for {city_name}: {lat}, {lon}")
        return lat, lon
    except Exception as e:
        print("Nominatim failed:", e)
        return None, None


def get_soil_ph(lat, lon):
    """Fetch real soil pH from ISRIC SoilGrids API (free, no key needed)"""
    try:
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        params = {
            "lon": lon,
            "lat": lat,
            "property": "phh2o",
            "depth": "0-5cm",
            "value": "mean",
        }
        res = requests.get(url, params=params, timeout=15)
        data = res.json()
        ph_raw = data["properties"]["layers"][0]["depths"][0]["values"]["mean"]
        if ph_raw is None:
            return None
        soil_ph = round(ph_raw / 10, 1)  # SoilGrids returns pH * 10
        print(f"Soil pH at ({lat}, {lon}): {soil_ph}")
        return soil_ph
    except Exception as e:
        print("SoilGrids failed:", e)
        return None


def analyze_crop(crop_name, location=""):
    crop = crop_name.lower()

    if not crop.strip():
        return {"error": "Crop name cannot be empty. Please enter a valid crop name."}

    allowed_crops = [
        "maize", "rice", "wheat", "soybean", "sorghum",
        "millet", "cassava", "groundnut", "sugarcane", "sweet potato",
        "tomato", "onion", "pepper", "cabbage", "carrot",
        "spinach", "cotton", "beans", "potato", "sunflower", "barley"
    ]
    if crop not in allowed_crops:
        return {"error": f"Crop '{crop_name}' is not supported. Please choose from: {', '.join(allowed_crops)}."}

    # --- Step 1: Get coordinates from city name ---
    lat, lon = None, None
    soil_ph = None

    if location and location.strip():
        lat, lon = get_coords_from_city(location.strip())

    # --- Step 2: Get real soil pH from SoilGrids ---
    if lat and lon:
        soil_ph = get_soil_ph(lat, lon)

    # --- Step 3: Build context for Groq prompt ---
    if soil_ph:
        ph_info = f"Real measured soil pH at the farmer's location: {soil_ph}"
        if soil_ph < 5.5:
            ph_context = "The soil is strongly acidic. Lime application is likely needed."
        elif soil_ph < 6.5:
            ph_context = "The soil is mildly acidic, suitable for many crops."
        elif soil_ph < 7.5:
            ph_context = "The soil is neutral, ideal for most crops."
        else:
            ph_context = "The soil is alkaline. Sulfur amendment may be needed."
    else:
        ph_info = "Soil pH data unavailable (no location provided or API unreachable)."
        ph_context = "Use general agronomic knowledge for this crop."

    location_info = f"Farmer location: {location}" if location else "Location not provided."

    # --- Step 4: Call Groq with real soil data ---
    try:
        prompt = f"""
You are an expert agronomist. A farmer wants to grow {crop_name}.

{location_info}
{ph_info}
{ph_context}

Based on this real soil data and the crop's agronomic requirements, provide:
- Daily irrigation needs in mm/day
- Best soil type for this crop
- Expected growth time in weeks
- Recommended nitrogen fertilizer in kg/ha
- Recommended phosphorus fertilizer in kg/ha
- Recommended potassium fertilizer in kg/ha
- Farming difficulty (Easy, Medium, or Hard) — factor in the soil pH when deciding

Return ONLY valid JSON with NO extra text, comments, or explanation.
Use ONLY these exact keys:

{{
    "irrigation_mm_per_day": 0,
    "soil_type": "",
    "growth_weeks": 0,
    "nitrogen_kg_ha": 0,
    "phosphorus_kg_ha": 0,
    "potassium_kg_ha": 0,
    "farming_difficulty": ""
}}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        ai_text = response.choices[0].message.content
        ai_data = json.loads(ai_text)

        return {
            "irrigation_mm_per_day": ai_data.get("irrigation_mm_per_day"),
            "soil_type": ai_data.get("soil_type"),
            "growth_weeks": ai_data.get("growth_weeks"),
            "nitrogen_kg_ha": ai_data.get("nitrogen_kg_ha"),
            "phosphorus_kg_ha": ai_data.get("phosphorus_kg_ha"),
            "potassium_kg_ha": ai_data.get("potassium_kg_ha"),
            "farming_difficulty": ai_data.get("farming_difficulty"),
        }

    except Exception as e:
        print("AI failed:", e)

    # --- Fallback: hardcoded values if Groq fails ---
    is_hot = location.lower() in ["abuja", "ankara", "khartoum"] if location else False

    if crop == "maize":
        water = 6.5 if is_hot else 5.0
        return {
            "irrigation_mm_per_day": water,
            "soil_type": "Loamy",
            "growth_weeks": 12,
            "nitrogen_kg_ha": round(water * 10, 1),
            "phosphorus_kg_ha": round(water * 5, 1),
            "potassium_kg_ha": round(water * 6, 1),
            "farming_difficulty": "Easy",
        }
    elif crop == "rice":
        water = 9.0 if is_hot else 7.5
        return {
            "irrigation_mm_per_day": water,
            "soil_type": "Clay",
            "growth_weeks": 16,
            "nitrogen_kg_ha": round(water * 10, 1),
            "phosphorus_kg_ha": round(water * 5, 1),
            "potassium_kg_ha": round(water * 6, 1),
            "farming_difficulty": "Hard" if water > 8 else "Medium",
        }
    else:
        water = 5.7 if is_hot else 4.2
        return {
            "irrigation_mm_per_day": water,
            "soil_type": "Loamy",
            "growth_weeks": 10,
            "nitrogen_kg_ha": round(water * 10, 1),
            "phosphorus_kg_ha": round(water * 5, 1),
            "potassium_kg_ha": round(water * 6, 1),
            "farming_difficulty": "Medium" if is_hot else "Easy",
        }