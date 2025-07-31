import httpx
import asyncio
import logging
import time
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, MAX_CONCURRENT_REQUESTS, RATE_LIMIT_SLEEP_SECONDS, enrichment_status
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

# Replace the entire background_enrichment function with:
async def background_enrichment(connections_to_enrich):
    """Background task for enriching profiles with parallel processing"""
    global enrichment_status
    
    enriched_cache = load_enriched_cache()
    max_to_enrich = len(connections_to_enrich)  # Changed: enrich ALL connections
    
    # Initialize progress tracking
    enrichment_status["current"] = 0
    enrichment_status["total"] = max_to_enrich
    enrichment_status["completed"] = False
    enrichment_status["in_progress"] = True
    
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def enrich_single_connection(connection, index):
        async with semaphore:
            logger.info(f"Enriching connection {index+1}/{max_to_enrich}: {connection['first_name']} {connection['last_name']}")
            
            enriched_data = await enrich_profile(connection["url"])
            enriched_connection = format_enriched_connection(connection, enriched_data)
            
            # Thread-safe cache update
            enriched_cache[connection["url"]] = enriched_connection
            
            # Update progress
            enrichment_status["current"] = index + 1
            
            # Rate limiting between requests
            await asyncio.sleep(RATE_LIMIT_SLEEP_SECONDS)
            
            return enriched_connection
    
    try:
        # Create tasks for all connections
        tasks = [
            enrich_single_connection(conn, i) 
            for i, conn in enumerate(connections_to_enrich)
        ]
        
        # Execute all tasks in parallel
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Final save
        save_enriched_cache(enriched_cache)

        # Vectorize newly enriched connections
        newly_enriched = []
        for connection in connections_to_enrich:
            if enriched_cache[connection["url"]].get("enriched", False):
                newly_enriched.append(enriched_cache[connection["url"]])
        
        if newly_enriched:
            logger.info(f"Vectorizing {len(newly_enriched)} newly enriched connections")
            from semantic_search import ConnectionSemanticSearch
            semantic_search = ConnectionSemanticSearch()
            semantic_search.batch_store_embeddings(newly_enriched)
        
    except Exception as e:
        logger.error(f"Error in background enrichment: {str(e)}")

    finally:
        # Mark enrichment as completed
        enrichment_status["completed"] = True
        enrichment_status["in_progress"] = False
        logger.info(f"Background enrichment completed. Processed {max_to_enrich} profiles.")

async def vectorization_catchup(connections_to_vectorize):
    """Background task for vectorizing enriched connections"""
    from semantic_search import ConnectionSemanticSearch
    
    semantic_search = ConnectionSemanticSearch()
    
    try:
        logger.info(f"Starting vectorization catch-up for {len(connections_to_vectorize)} connections")
        
        # Vectorize in batches
        semantic_search.batch_store_embeddings(connections_to_vectorize)
        
        logger.info("Vectorization catch-up completed successfully")
        
    except Exception as e:
        logger.error(f"Error in vectorization catch-up: {str(e)}")