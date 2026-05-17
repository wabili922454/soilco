import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Ensure absolute environment loading paths are preserved
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(parent_dir, '.env'))

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

# Safeguard initialization if credentials aren't loaded yet
if not url or not key:
    print("⚠️ Forum Service Warning: Missing Supabase credentials in .env")
    supabase: Client = None
else:
    supabase: Client = create_client(url, key)

def post_to_forum(user_id: str, author_name: str, content: str) -> bool:
    """
    Saves a new community post written by a user into the forum table.
    Returns True if successful, False if it fails.
    """
    if not supabase:
        print("❌ Database client uninitialized. Cannot post message.")
        return False
        
    try:
        data = {
            "user_id": user_id,
            "author_name": author_name,
            "content": content
        }
        # Rule 3 & 4 matching: targeting the standard 'forum' public table
        response = supabase.table("forum").insert(data).execute()
        return True
    except Exception as e:
        print(f"⚠️ Rule 5 Error Handling triggered in post_to_forum: {e}")
        return False

def get_forum_posts(limit: int = 50) -> list:
    """
    Fetches the latest public forum posts ordered by newest first.
    Rule 5 Option A: Returns an empty list safely if database communication fails.
    """
    if not supabase:
        print("❌ Database client uninitialized. Returning empty timeline.")
        return []

    try:
        response = supabase.table("forum") \
            .select("*") \
            .order("created_at", descending=True) \
            .limit(limit) \
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"⚠️ Rule 5 Error Handling triggered in get_forum_posts: {e}")
        return []