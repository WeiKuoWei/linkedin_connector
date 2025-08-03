from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .supabase_auth import verify_supabase_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI dependency to get current authenticated user"""
    token = credentials.credentials
    user_data = verify_supabase_token(token)
    
    # Add user_id to make it easily accessible
    return {
        "user_id": str(user_data["user_id"]),  # Ensure string format
        "email": user_data["email"],
        "user": user_data["user"]
    }