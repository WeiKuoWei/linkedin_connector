import logging
from services.storage import load_enriched_cache, save_enriched_cache, save_connections_list
from services.search import ConnectionSemanticSearch

logger = logging.getLogger(__name__)

def identify_new_connections(new_connections, user_id: str):
    """Identify connections that need enrichment"""
    enriched_cache = load_enriched_cache(user_id)
    
    new_urls_to_enrich = []
    for conn in new_connections:
        if conn["url"] not in enriched_cache or enriched_cache[conn["url"]].get("enriched", False) == False:
            new_urls_to_enrich.append(conn)
    
    return enriched_cache, new_urls_to_enrich

def update_connections_cache(new_connections, enriched_cache, user_id: str):
    """Update existing connections with new basic info"""
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
    save_enriched_cache(user_id, enriched_cache)
    save_connections_list(user_id, new_connections)

def analyze_vectorization_status(enriched_cache, user_id: str):
    """Check vectorization status for enriched connections"""
    semantic_search = ConnectionSemanticSearch(user_id)
    all_enriched = [conn for conn in enriched_cache.values() if conn.get("enriched", False)]
    unvectorized_connections = semantic_search.get_unvectorized_connections(enriched_cache)
    
    return len(all_enriched), unvectorized_connections