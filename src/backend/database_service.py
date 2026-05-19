from backend.supabase_client import supabase

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
        return False

def get_recent_analyses(user_id: str, limit: int = 3) -> list | None:
    try:
        response = (
            supabase.table("soil_analyses")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data
    except Exception as e:
        print("Database fetch failed:", e)
        return None

def update_user_preferences(user_id: str, irrigation_alerts: bool, weekly_reports: bool) -> bool:
    try:
        data = {
            "irrigation_alerts": irrigation_alerts,
            "weekly_reports": weekly_reports,
        }
        # Fixed: profiles table uses user_id not id
        supabase.table("profiles").update(data).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"update_user_preferences failed: {e}")
        return False