from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    
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

    location =  location.lower() 
    hot_regions = ["abuja", "ankara", "khartoum"]
    is_hot = location in hot_regions


    try:
        prompt = f"""
        Crop: {crop_name}
        Location: {location}

        Provide:
        - irrigation (mm/day)
        - soil type
        - growth time (weeks)
        - nitrogen (kg/ha)
        - phosphorus (kg/ha)
        - potassium (kg/ha)
        - farming difficulty (Easy, Medium, Hard)

        Return ONLY valid JSON.

        Rules:
        - Do NOT use crop name as a key
        - Do NOT use location as a key
        - Do NOT add comments
        - Do NOT add explanations
        - Do NOT use nested objects
        - Use ONLY these exact keys:

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
        # print(ai_text) # debug 

        ai_data = json.loads(ai_text)

        return{
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


    if crop == "maize":
        water = 6.5 if is_hot else 5.0

        nitrogen = water * 10
        phosphorus = water * 5
        potassium = water * 6

        return {
            "irrigation_mm_per_day":water,
            "soil_type": "Loamy",
            "growth_weeks": 12,
            "nitrogen_kg_ha": round(nitrogen, 1),
            "phosphorus_kg_ha": round(phosphorus, 1),
            "potassium_kg_ha": round(potassium, 1),
            "farming_difficulty": "Easy",
        }

    elif crop == "rice":
        water = 9.0 if is_hot else 7.5
        nitrogen = water * 10
        phosphorus = water * 5
        potassium = water * 6

        return {
            "irrigation_mm_per_day": water,
            "soil_type": "Clay",
            "growth_weeks": 16,
            "nitrogen_kg_ha": round(nitrogen, 1),
            "phosphorus_kg_ha": round(phosphorus, 1),
            "potassium_kg_ha": round(potassium, 1),
            "farming_difficulty": "Hard" if water > 8 else "Medium",
        }

    else:
        water = 5.7 if is_hot else 4.2
        nitrogen = water * 10
        phosphorus = water * 5
        potassium = water * 6

        return {
            "irrigation_mm_per_day": water,
            "soil_type": "Loamy",
            "growth_weeks": 10,
            "nitrogen_kg_ha": round(nitrogen, 1),
            "phosphorus_kg_ha": round(phosphorus, 1),
            "potassium_kg_ha": round(potassium, 1),
            "farming_difficulty": "Medium" if is_hot  else "Easy",
        }