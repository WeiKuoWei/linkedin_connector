from fastapi import HTTPException, UploadFile, File, BackgroundTasks
import pandas as pd
import logging
import io

from config.settings import enrichment_status
from services.storage import load_enriched_cache, save_enriched_cache, save_connections_list
from services.enrichment import background_enrichment, vectorization_catchup
from services.search import ConnectionSemanticSearch

logger = logging.getLogger(__name__)

async def get_enrichment_progress():
    """Get current enrichment progress"""
    return enrichment_status

async def upload_csv(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Upload and parse LinkedIn connections CSV file with background enrichment"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        
        # Parse CSV (skip first 3 rows like LinkedIn export format)
        df = pd.read_csv(io.StringIO(content.decode('utf-8')), skiprows=3)
        
        # Validate required columns
        required_columns = ["First Name", "Last Name", "URL", "Company", "Position"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process connections from CSV
        new_connections = []
        for _, row in df.iterrows():
            connection = {
                "first_name": str(row.get("First Name", "")).strip(),
                "last_name": str(row.get("Last Name", "")).strip(),
                "url": str(row.get("URL", "")).strip(),
                "email": str(row.get("Email Address", "")).strip(),
                "company": str(row.get("Company", "")).strip(),
                "position": str(row.get("Position", "")).strip(),
                "connected_on": str(row.get("Connected On", "")).strip(),
                "enriched": False
            }
            # Only add if has name and valid URL
            if (connection["first_name"] and connection["last_name"] and 
                connection["url"] and connection["url"].startswith("https://www.linkedin.com/in/")):
                new_connections.append(connection)
        
        # Load existing enriched cache (URL-keyed)
        enriched_cache = load_enriched_cache()
        
        # Identify new connections that need enrichment
        new_urls_to_enrich = []
        for conn in new_connections:
            if conn["url"] not in enriched_cache or enriched_cache[conn["url"]].get("enriched", False) == False:
                new_urls_to_enrich.append(conn)
        
        logger.info(f"Found {len(new_urls_to_enrich)} new connections to enrich out of {len(new_connections)} total connections")
        
        # Update existing connections with any new basic info
        for connection in new_connections:
            if connection["url"] in enriched_cache:
                cached_conn = enriched_cache[connection["url"]]
                # Update basic info but preserve enriched data
                cached_conn.update({
                    "first_name": connection["first_name"],
                    "last_name": connection["last_name"],
                    "email": connection["email"],
                    "company": connection["company"] or cached_conn.get("company", ""),
                    "position": connection["position"] or cached_conn.get("position", ""),
                    "connected_on": connection["connected_on"]
                })
            else:
                # Add new connection to cache (not yet enriched)
                enriched_cache[connection["url"]] = connection
        
        # Save updated cache and connections list
        save_enriched_cache(enriched_cache)
        save_connections_list(new_connections)
        
        # Check vectorization status for all enriched connections
        semantic_search = ConnectionSemanticSearch()
        all_enriched = [conn for conn in enriched_cache.values() if conn.get("enriched", False)]
        unvectorized_connections = semantic_search.get_unvectorized_connections(enriched_cache)
        
        total_enriched = len(all_enriched)
        needs_vectorization = len(unvectorized_connections)
        
        logger.info(f"Vectorization status: {total_enriched} enriched, {needs_vectorization} need vectorization")
        
        # Start background tasks
        will_enrich = len(new_urls_to_enrich)
        if new_urls_to_enrich and background_tasks:
            background_tasks.add_task(background_enrichment, new_urls_to_enrich)
        
        # Start vectorization catch-up if needed
        if unvectorized_connections and background_tasks:
            background_tasks.add_task(vectorization_catchup, unvectorized_connections)
        
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
            "filename": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")