from fastapi import HTTPException, Depends
import logging

from config.settings import client
from services.auth import get_current_user as verify_supabase_token
from config.models import MessageRequest
from config.prompts import get_linkedin_message_prompt

logger = logging.getLogger(__name__)

async def generate_message(
    request: MessageRequest,
    user: dict = Depends(verify_supabase_token)
):
    """Generate a personalized LinkedIn message for reconnection"""
    user_id = user["user_id"]
    
    try:
        prompt = get_linkedin_message_prompt(
            name=request.name,
            company=request.company,
            role=request.role,
            mission=request.mission,
            profile_summary=request.profile_summary,
            location=request.location
        )
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        message_text = response.choices[0].message.content.strip()
        
        logger.info(f"Generated message for user {user_id}")
        
        return {
            "message": message_text,
            "recipient": request.name,
            "company": request.company,
            "user_id": user_id
        }
    
    except Exception as e:
        logger.error(f"Error generating message for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")