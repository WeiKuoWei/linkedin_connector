import httpx
import asyncio
import logging
import time
import threading
from config.settings import (
    RAPIDAPI_KEY, 
    RAPIDAPI_HOST, 
    MAX_CONCURRENT_REQUESTS, 
    RATE_LIMIT_SLEEP_SECONDS,
    update_user_progress
)
from services.storage import load_enriched_cache, save_enriched_cache
from services.search import ConnectionSemanticSearch


# Global lock for thread-safe operations
progress_lock = threading.Lock()
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
            # start_time = time.time()
            response = await http_client.get(
                f"https://{RAPIDAPI_HOST}/get-profile-data-by-url",
                headers=headers,
                params={"url": url},
                timeout=30.0
            )

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

async def vectorization_catchup(connections_to_vectorize, user_id: str):  
    """Background task for vectorizing enriched connections"""    
    semantic_search = ConnectionSemanticSearch(user_id) 
    
    try:
        logger.info(f"Starting vectorization catch-up for {len(connections_to_vectorize)} connections")
        
        # Vectorize in batches
        semantic_search.batch_store_embeddings(connections_to_vectorize)
        
        logger.info("Vectorization catch-up completed successfully")
        
    except Exception as e:
        logger.error(f"Error in vectorization catch-up: {str(e)}")

async def background_enrichment(connections_to_enrich, user_id: str):
    """Simplified background enrichment with accurate progress tracking"""
    
    enriched_cache = load_enriched_cache(user_id)
    total = len(connections_to_enrich)
    completed_count = 0  # Add counter
    
    # Initialize progress
    update_user_progress(user_id, 0, total, False)
    
    # Initialize semantic search
    semantic_search = ConnectionSemanticSearch(user_id)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def enrich_single_connection(connection, index):
        nonlocal completed_count  # Access counter
        async with semaphore:
            try:
                # Enrichment
                enriched_data = await enrich_profile(connection["url"])
                enriched_connection = format_enriched_connection(connection, enriched_data)
                
                # Vectorization if enriched
                if enriched_connection.get("enriched", False):
                    semantic_search.store_connection_embeddings(enriched_connection)
                
                # Update cache
                enriched_cache[connection["url"]] = enriched_connection
                
                # Increment counter and update progress
                completed_count += 1
                update_user_progress(user_id, completed_count, total, False)
                
                await asyncio.sleep(RATE_LIMIT_SLEEP_SECONDS)
                
            except Exception as e:
                logger.error(f"Failed to process connection {index+1}: {str(e)}")
                # Still increment on failure
                completed_count += 1
                update_user_progress(user_id, completed_count, total, False)
    
    try:
        # Process all connections
        tasks = [
            enrich_single_connection(conn, i) 
            for i, conn in enumerate(connections_to_enrich)
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save and mark complete
        save_enriched_cache(user_id, enriched_cache)
        update_user_progress(user_id, total, total, True)
        
    except Exception as e:
        logger.error(f"Error in enrichment: {str(e)}")
        update_user_progress(user_id, total, total, True)