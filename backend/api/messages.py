from fastapi import HTTPException
import logging

from config.settings import client
from config.models import MessageRequest
from config.prompts import get_linkedin_message_prompt

logger = logging.getLogger(__name__)

async def generate_message(request: MessageRequest):
    """Generate a personalized LinkedIn message for reconnection"""
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
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        message_text = response.choices[0].message.content.strip()
        
        return {
            "message": message_text,
            "recipient": request.name,
            "company": request.company
        }
    
    except Exception as e:
        logger.error(f"Error generating message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")