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
    get_user_enrichment_status
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

async def background_enrichment(connections_to_enrich, user_id: str):
    """Background task for enriching profiles with immediate vectorization"""
    
    enriched_cache = load_enriched_cache(user_id)
    max_to_enrich = len(connections_to_enrich)
    
    # Get user-specific status
    user_status = get_user_enrichment_status(user_id)
    
    # Initialize progress tracking for this user (thread-safe)
    with progress_lock:
        user_status["current"] = 0
        user_status["total"] = max_to_enrich
        user_status["completed"] = False
        user_status["in_progress"] = True
    
    # Initialize semantic search for vectorization
    semantic_search = ConnectionSemanticSearch(user_id)
    
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Performance tracking
    pipeline_start_time = time.time()
    
    # Process in batches to avoid race conditions
    batch_size = MAX_CONCURRENT_REQUESTS
    
    async def enrich_single_connection(connection, index):
        async with semaphore:
            start_time = time.time()
            logger.info(f"User {user_id}: Processing connection {index+1}/{max_to_enrich}: {connection['first_name']} {connection['last_name']}")
            
            try:
                # Step 1: Enrichment
                enriched_data = await enrich_profile(connection["url"])
                enriched_connection = format_enriched_connection(connection, enriched_data)
                
                # Step 2: Immediate vectorization if enrichment succeeded
                if enriched_connection.get("enriched", False):
                    try:
                        semantic_search.store_connection_embeddings(enriched_connection)
                        logger.info(f"User {user_id}: ✅ Enriched + Vectorized: {enriched_connection['first_name']} {enriched_connection['last_name']}")
                    except Exception as e:
                        logger.error(f"User {user_id}: ❌ Vectorization failed for {connection['url']}: {str(e)}")
                
                # Thread-safe cache update
                with progress_lock:
                    enriched_cache[connection["url"]] = enriched_connection
                
                # Rate limiting
                await asyncio.sleep(RATE_LIMIT_SLEEP_SECONDS)
                
                return enriched_connection
                
            except Exception as e:
                logger.error(f"User {user_id}: ❌ Failed to process connection {index+1}: {str(e)}")
                return None
    
    try:
        # Process in batches to avoid race conditions
        for batch_start in range(0, max_to_enrich, batch_size):
            batch_end = min(batch_start + batch_size, max_to_enrich)
            batch = connections_to_enrich[batch_start:batch_end]
            
            logger.info(f"User {user_id}: Processing batch {batch_start//batch_size + 1}/{(max_to_enrich + batch_size - 1)//batch_size}")
            
            # Process current batch
            batch_tasks = [
                enrich_single_connection(conn, batch_start + i) 
                for i, conn in enumerate(batch)
            ]
            
            # Wait for entire batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Log any exceptions in this batch
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"User {user_id}: Batch task {batch_start + i + 1} failed: {str(result)}")
            
            # Update progress after batch completion (thread-safe)
            with progress_lock:
                user_status["current"] = batch_end
            
            logger.info(f"User {user_id}: Completed batch {batch_start//batch_size + 1}, progress: {batch_end}/{max_to_enrich}")
        
        # Final save (thread-safe)
        with progress_lock:
            save_enriched_cache(user_id, enriched_cache)
        
        # Performance logging
        total_duration = time.time() - pipeline_start_time
        avg_duration = total_duration / max_to_enrich if max_to_enrich > 0 else 0
        logger.info(f"User {user_id}: 🏁 Pipeline completed: {total_duration:.2f}s total, {avg_duration:.2f}s avg per connection")
        
    except Exception as e:
        logger.error(f"User {user_id}: Error in background enrichment pipeline: {str(e)}")

    finally:
        # Mark enrichment as completed for this user (thread-safe)
        with progress_lock:
            user_status["completed"] = True
            user_status["in_progress"] = False
        logger.info(f"User {user_id}: Background enrichment pipeline completed. Processed {max_to_enrich} profiles.")

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