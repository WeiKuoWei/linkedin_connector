import logging
import json
import re

logger = logging.getLogger(__name__)

def format_connections_for_llm(matched_connections):
    """Format matched connections for LLM processing"""
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
    
    return connections_text

def parse_ai_response(ai_response):
    """Parse AI response into structured JSON"""
    try:
        return json.loads(ai_response)
    except json.JSONDecodeError:
        try:
            # Try to extract JSON from markdown code block
            json_pattern = r'```(?:json)?\s*(.*?)\s*```'
            match = re.search(json_pattern, ai_response, re.DOTALL)
            if match:
                json_content = match.group(1).strip()
                return json.loads(json_content)
            else:
                return ai_response
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return ai_response

def enhance_suggestions_with_connection_data(suggestions_json, matched_connections):
    """Enhance suggestions with full connection data"""
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
    
    return enhanced_suggestions