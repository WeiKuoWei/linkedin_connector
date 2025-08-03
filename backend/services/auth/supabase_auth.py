import os
from fastapi import HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def verify_supabase_token(token: str):
    """Verify Supabase JWT token using JWKS and return user info"""
    try:
        # Use Supabase client to verify token (handles JWKS automatically)
        response = supabase.auth.get_user(token)
        
        if response.user:
            return {
                "user_id": response.user.id,
                "email": response.user.email,
                "user": response.user
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")