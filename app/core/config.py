# app/core/config.py

import os
from supabase import create_client, Client

# These should be set as environment variables in a production environment
SUPABASE_URL = "https://srxjqmxqblntqufhzjsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNyeGpxbXhxYmxudHF1Zmh6anNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzkxNjY2NCwiZXhwIjoyMDczNDkyNjY0fQ.JBMo8UCWLcPNGxQAuj71bcyDCEu3SJfvB0vvHBm6luQ"

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Returns the initialized Supabase client instance."""
    return supabase_client