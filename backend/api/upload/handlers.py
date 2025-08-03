from fastapi import HTTPException, UploadFile, File, BackgroundTasks, Depends
import logging

from config.settings import get_user_enrichment_status
from services.auth import get_current_user as verify_supabase_token
from services.enrichment import background_enrichment, vectorization_catchup
from .validators import validate_csv_file, process_connections_from_df
from .processors import identify_new_connections, update_connections_cache, analyze_vectorization_status

logger = logging.getLogger(__name__)

async def get_enrichment_progress(user: dict = Depends(verify_supabase_token)):
    """Get current enrichment progress for specific user"""
    user_id = user["user_id"]
    return get_user_enrichment_status(user_id)

async def upload_csv(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None,
    user: dict = Depends(verify_supabase_token)
):
    """Upload and parse LinkedIn connections CSV file with background enrichment"""
    user_id = user["user_id"]
    
    try:
        # Read and validate file
        content = await file.read()
        df = validate_csv_file(file, content)
        
        # Process connections from CSV
        new_connections = process_connections_from_df(df)
        
        # Identify new connections and update cache
        enriched_cache, new_urls_to_enrich = identify_new_connections(new_connections, user_id)
        
        logger.info(f"User {user_id}: Found {len(new_urls_to_enrich)} new connections to enrich out of {len(new_connections)} total connections")
        
        # Update connections cache
        update_connections_cache(new_connections, enriched_cache, user_id)
        
        # Check vectorization status
        total_enriched, unvectorized_connections = analyze_vectorization_status(enriched_cache, user_id)
        needs_vectorization = len(unvectorized_connections)
        
        logger.info(f"User {user_id}: Vectorization status: {total_enriched} enriched, {needs_vectorization} need vectorization")
        
        # Start background tasks
        will_enrich = len(new_urls_to_enrich)
        if new_urls_to_enrich and background_tasks:
            background_tasks.add_task(background_enrichment, new_urls_to_enrich, user_id)
        
        if unvectorized_connections and background_tasks:
            background_tasks.add_task(vectorization_catchup, unvectorized_connections, user_id)
        
        return {
            "message": f"Successfully processed {len(new_connections)} connections",
            "count": len(new_connections),
            "total_in_cache": len(enriched_cache),
            "total_enriched": total_enriched,
            "needs_vectorization": needs_vectorization,
            "new_connections_found": len(new_urls_to_enrich),
            "will_enrich": will_enrich,
            "enrichment_started": len(new_urls_to_enrich) > 0,
            "vectorization_started": needs_vectorization > 0,
            "filename": file.filename,
            "user_id": user_id
        }
    
    except Exception as e:
        logger.error(f"Error processing file for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")