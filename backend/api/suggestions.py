from fastapi import HTTPException
import logging

from config.settings import client
from config.models import MissionRequest
from config.prompts import get_instructions
from services.storage import load_enriched_cache
from services.search import ConnectionSemanticSearch

logger = logging.getLogger(__name__)

async def get_suggestions(request: MissionRequest):
    try:
        # Load enriched cache
        enriched_cache = load_enriched_cache()
        
        if not enriched_cache:
            raise HTTPException(
                status_code=400, 
                detail="No connections found. Please upload a CSV file first."
            )
        
        # Initialize semantic search
        semantic_search = ConnectionSemanticSearch()
        
        # Extract mission attributes using LLM
        mission_attributes = semantic_search.extract_mission_attributes(request.mission)
        logger.info(f"Extracted mission attributes: {mission_attributes}")
        
        # Get top connections using semantic search
        top_connections = semantic_search.search_top_connections(mission_attributes, n_results=15)
        
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
        
        # Create simplified prompt for LLM with only top matches
        connections_text = []
        for conn in matched_connections[:10]:  # Limit to top 10 for LLM
            name = f"{conn['first_name']} {conn['last_name']}"
            info = f"{name}: {conn.get('headline', 'N/A')}"
            
            if conn.get("summary"):
                info += f" | Summary: {conn['summary'][:100]}..."
            if conn.get("company"):
                info += f" | Company: {conn['company']}"
            if conn.get("current_company"):
                info += f" | Current Company: {conn['current_company']}"
            if conn.get("current_title"):
                info += f" | Current Title: {conn['current_title']}"
            if conn.get("location"):
                info += f" | Location: {conn['location']}"
            if conn.get("industry"):
                info += f" | Industry: {conn['industry']}"
            
            connections_text.append(info)

        prompt = get_instructions(request.mission, connections_text)
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.1
        )
        ai_response = response.choices[0].message.content

        # Parse AI response
        try:
            import json as json_parser
            suggestions_json = json_parser.loads(ai_response)
        except:
            try:
                import re  
                json_pattern = r'```(?:json)?\s*(.*?)\s*```'
                match = re.search(json_pattern, ai_response, re.DOTALL)
                if match:
                    json_content = match.group(1).strip()
                    suggestions_json = json_parser.loads(json_content)
                else:
                    suggestions_json = ai_response
            except:
                suggestions_json = ai_response

        # Enhance suggestions with connection data
        enhanced_suggestions = []
        if isinstance(suggestions_json, list):
            for suggestion in suggestions_json:
                matching_conn = None
                for conn in matched_connections:
                    conn_name = f"{conn['first_name']} {conn['last_name']}"
                    if suggestion.get("name", "").lower() in conn_name.lower():
                        matching_conn = conn
                        break
                
                enhanced_suggestion = {
                    **suggestion,
                    "linkedin_url": matching_conn.get("url", "") if matching_conn else "",
                    "profile_summary": matching_conn.get("summary", "") if matching_conn else "",
                    "location": matching_conn.get("location", "") if matching_conn else "",
                    "connection_strength": "Medium"
                }
                enhanced_suggestions.append(enhanced_suggestion)
        
        return {
            "mission": request.mission,
            "mission_attributes": mission_attributes,
            "suggestions": enhanced_suggestions if enhanced_suggestions else suggestions_json,
            "semantic_matches_found": len(top_connections),
            "using_semantic_search": True
        }
    
    except Exception as e:
        logger.error(f"Error in get_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))