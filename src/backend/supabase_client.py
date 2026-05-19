from dotenv import load_dotenv
import os
from supabase import create_client, Client

# Load .env from the same folder as this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("⚠️ WARNING: Your .env keys could not be loaded! Check your .env file location.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)