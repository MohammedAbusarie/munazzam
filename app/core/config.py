# app/core/config.py

import os
from supabase import create_client, Client

# These should be set as environment variables in a production environment
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_KEY"

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Returns the initialized Supabase client instance."""
    return supabase_client