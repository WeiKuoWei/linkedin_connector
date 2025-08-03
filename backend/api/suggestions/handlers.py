from fastapi import HTTPException, Depends
import logging

from config.settings import client
from services.auth import get_current_user as verify_supabase_token
from config.models import MissionRequest
from config.prompts import get_instructions
from config.constants import N_RESULTS
from services.storage import load_enriched_cache
from services.search import ConnectionSemanticSearch
from .processors import format_connections_for_llm, parse_ai_response, enhance_suggestions_with_connection_data

logger = logging.getLogger(__name__)

async def get_suggestions(
    request: MissionRequest,
    user: dict = Depends(verify_supabase_token)
):
    user_id = user["user_id"]
    
    try:
        # Load enriched cache for this user
        enriched_cache = await load_enriched_cache(user_id)
        
        if not enriched_cache:
            raise HTTPException(
                status_code=400, 
                detail="No connections found. Please upload a CSV file first."
            )
        
        # Initialize semantic search for this user
        semantic_search = ConnectionSemanticSearch(user_id)
        
        # Extract mission attributes using LLM
        mission_attributes = semantic_search.extract_mission_attributes(request.mission)
        logger.info(f"User {user_id}: Extracted mission attributes: {mission_attributes}")
        
        # Get top connections using semantic search
        top_connections = semantic_search.search_top_connections(mission_attributes, n_results=N_RESULTS)
        
        if not top_connections:
            raise HTTPException(
                status_code=400, 
                detail="No relevant connections found for your mission."
            )
        
        # Get full connection data for top matches
        matched_connections = []
        for conn in top_connections:
            full_conn = enriched_cache.get(conn['url'])
            if full_conn:
                matched_connections.append(full_conn)
        
        # Format connections for LLM processing
        connections_text = format_connections_for_llm(matched_connections)
        
        # Get AI suggestions
        prompt = get_instructions(request.mission, connections_text)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.1
        )
        ai_response = response.choices[0].message.content

        # Parse and enhance AI response
        suggestions_json = parse_ai_response(ai_response)
        enhanced_suggestions = enhance_suggestions_with_connection_data(suggestions_json, matched_connections)
        
        total_enriched = len([conn for conn in enriched_cache.values() if conn.get("enriched", False)])
        
        return {
            "mission": request.mission,
            "mission_attributes": mission_attributes,
            "suggestions": enhanced_suggestions if enhanced_suggestions else suggestions_json,
            "semantic_matches_found": len(top_connections),
            "using_semantic_search": True,
            "total_connections": len(enriched_cache),
            "enriched_connections": total_enriched,
            "user_id": user_id
        }
    
    except Exception as e:
        logger.error(f"Error in get_suggestions for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))