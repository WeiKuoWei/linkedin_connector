import httpx
import asyncio
import logging
import time
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, NUMBER_OF_ENRICHMENTS, RATE_LIMIT_SLEEP_SECONDS, enrichment_status
from storage import load_enriched_cache, save_enriched_cache

logger = logging.getLogger(__name__)

async def enrich_profile(url: str):
    """Fetch detailed profile data from LinkedIn URL using RapidAPI"""
    if not url or not url.startswith("https://www.linkedin.com/in/"):
        return None
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        async with httpx.AsyncClient() as http_client:
            start_time = time.time()
            response = await http_client.get(
                f"https://{RAPIDAPI_HOST}/get-profile-data-by-url",
                headers=headers,
                params={"url": url},
                timeout=30.0
            )

            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"LinkedIn API call duration for {url}: {duration:.2f} seconds")

            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"LinkedIn API error for {url}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error enriching profile {url}: {str(e)}")
        return None

def format_enriched_connection(connection, enriched_data):
    """Format connection with enriched data"""
    if not enriched_data:
        return connection
    
    # Extract key information from enriched data
    summary = enriched_data.get("summary", "")
    headline = enriched_data.get("headline", connection.get("position", ""))
    
    # Get most recent position
    positions = enriched_data.get("position", [])
    current_position = positions[0] if positions else {}
    
    # Get location
    geo = enriched_data.get("geo", {})
    location = geo.get("full", "")
    
    # Get education
    educations = enriched_data.get("educations", [])
    education_summary = []
    for edu in educations[:2]:  # Top 2 schools
        school = edu.get("schoolName", "")
        if school:
            education_summary.append(school)
    
    return {
        **connection,
        "enriched": True,
        "summary": summary,
        "headline": headline,
        "current_company": current_position.get("companyName", connection.get("company", "")),
        "current_title": current_position.get("title", connection.get("position", "")),
        "location": location,
        "education": ", ".join(education_summary),
        "industry": current_position.get("companyIndustry", ""),
        "company_size": current_position.get("companyStaffCountRange", "")
    }

async def background_enrichment(connections_to_enrich):
    """Background task for enriching profiles"""
    global enrichment_status
    
    enriched_cache = load_enriched_cache()
    enrichment_count = 0
    max_to_enrich = min(NUMBER_OF_ENRICHMENTS, len(connections_to_enrich))
    
    # Initialize progress tracking
    enrichment_status["current"] = 0
    enrichment_status["total"] = max_to_enrich
    enrichment_status["completed"] = False
    enrichment_status["in_progress"] = True
    
    try:
        for i, connection in enumerate(connections_to_enrich[:max_to_enrich]):
            logger.info(f"Enriching new connection {i+1}/{max_to_enrich}: {connection['first_name']} {connection['last_name']}")
            
            # Update progress
            enrichment_status["current"] = i + 1
            
            enriched_data = await enrich_profile(connection["url"])
            enriched_connection = format_enriched_connection(connection, enriched_data)
            
            # Add to cache with URL as key
            enriched_cache[connection["url"]] = enriched_connection
            enrichment_count += 1
            
            # Save cache after each enrichment
            save_enriched_cache(enriched_cache)
            
            # Respect rate limits
            await asyncio.sleep(RATE_LIMIT_SLEEP_SECONDS)
        
        # Add remaining new connections (not enriched due to limit) to cache
        for connection in connections_to_enrich[max_to_enrich:]:
            connection["enriched"] = False
            enriched_cache[connection["url"]] = connection
        
        # Final save
        save_enriched_cache(enriched_cache)
        
    except Exception as e:
        logger.error(f"Error in background enrichment: {str(e)}")
    finally:
        # Mark enrichment as completed
        enrichment_status["completed"] = True
        enrichment_status["in_progress"] = False
        logger.info(f"Background enrichment completed. Enriched {enrichment_count} profiles.")