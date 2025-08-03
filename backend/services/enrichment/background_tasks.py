import asyncio
import logging
from config.constants import MAX_CONCURRENT_REQUESTS, RATE_LIMIT_SLEEP_SECONDS
from config.settings import update_user_progress
from services.storage import load_enriched_cache, save_enriched_cache
from services.search import ConnectionSemanticSearch
from .profile_fetcher import enrich_profile
from .data_formatter import format_enriched_connection

logger = logging.getLogger(__name__)

async def vectorization_catchup(connections_to_vectorize, user_id: str):  
    """Background task for vectorizing enriched connections"""    
    semantic_search = ConnectionSemanticSearch(user_id) 
    
    try:
        logger.info(f"Starting vectorization catch-up for {len(connections_to_vectorize)} connections")
        semantic_search.batch_store_embeddings(connections_to_vectorize)
        logger.info("Vectorization catch-up completed successfully")
    except Exception as e:
        logger.error(f"Error in vectorization catch-up: {str(e)}")

async def background_enrichment(connections_to_enrich, user_id: str):
    """Simplified background enrichment with accurate progress tracking"""
    
    enriched_cache = load_enriched_cache(user_id)
    total = len(connections_to_enrich)
    completed_count = 0
    
    # Initialize progress
    update_user_progress(user_id, 0, total, False)
    
    # Initialize semantic search
    semantic_search = ConnectionSemanticSearch(user_id)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def enrich_single_connection(connection, index):
        nonlocal completed_count
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