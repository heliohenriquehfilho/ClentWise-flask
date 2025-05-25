from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

def load_supabase():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    return supabase