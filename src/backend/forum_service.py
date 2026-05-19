from backend.supabase_client import supabase

def post_to_forum(user_id: str, author_name: str, content: str) -> bool:
    if not supabase:
        print("❌ Database client uninitialized. Cannot post message.")
        return False
    try:
        data = {"user_id": user_id, "author_name": author_name, "content": content}
        supabase.table("forum").insert(data).execute()
        return True
    except Exception as e:
        print(f"forum post failed: {e}")
        return False

def get_forum_posts(limit: int = 50) -> list:
    if not supabase:
        print("❌ Database client uninitialized. Returning empty timeline.")
        return []
    try:
        response = supabase.table("forum") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"forum fetch failed: {e}")
        return []
