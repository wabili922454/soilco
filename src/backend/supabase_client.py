from dotenv import load_dotenv
import os
from supabase import create_client, Client

# ─── FIXING THE PATH ───
# This finds the absolute path of the folder your project lives in,
# ensuring Python finds the .env file even if you run from inside the 'src' folder.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")

# Force load the .env file from that precise location
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Extra guard check: Print a friendly message if the variables are still missing
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("⚠️ WARNING: Your .env keys could not be loaded! Check your .env file location.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ─── USER ANALYSIS HISTORY ───

def save_analysis(user_id: str, crop_name: str, analysis_data: dict) -> bool:
    try:
        data = {
            "user_id": user_id,
            "crop_name": crop_name,
            "irrigation_mm": analysis_data.get("irrigation_mm_per_day"),
            "soil_type": analysis_data.get("soil_type"),
            "growth_weeks": analysis_data.get("growth_weeks"),
            "nitrogen": analysis_data.get("nitrogen_kg_ha"),
            "phosphorus": analysis_data.get("phosphorus_kg_ha"),
            "potassium": analysis_data.get("potassium_kg_ha"),
            "farming_difficulty": analysis_data.get("farming_difficulty")
        }
        supabase.table("soil_analyses").insert(data).execute()
        return True
    except Exception as e:
        print("Database save failed:", e)
        return None

def get_recent_analyses(user_id: str, limit: int = 3) -> list | None:
    try:
        response = (
            supabase.table("soil_analyses")
            .select("*")
            .eq("user_id", user_id)
            .order("analyzed_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        print("Database fetch failed:", e)
        return None
    
def update_user_preferences(user_id: str, irrigation_alerts: bool, weekly_reports: bool) -> bool:
    """
    Updates or saves the user's notification preferences into the profiles/users table.
    Returns True if successful, False if it fails.
    """
    if not supabase:
        print("❌ Database client uninitialized. Cannot update preferences.")
        return False

    try:
        data = {
            "irrigation_alerts": irrigation_alerts,
            "weekly_reports": weekly_reports,
            "updated_at": "now()"  # Keeps track of the last time they changed settings
        }
        
        # Target the user's configuration profile row using their unique ID handle
        response = supabase.table("profiles").update(data).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"⚠️ Rule 5 Error Handling triggered in update_user_preferences: {e}")
        return False    