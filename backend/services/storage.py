import json
import os

def load_enriched_cache():
    """Load existing enriched connections cache (URL-keyed dictionary)"""
    cache_path = "data/connections_enriched.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}

def save_enriched_cache(cache):
    """Save enriched connections cache"""
    os.makedirs("data", exist_ok=True)
    with open("data/connections_enriched.json", "w") as f:
        json.dump(cache, f, indent=2)

def save_connections_list(connections):
    """Save current connections list for compatibility"""
    os.makedirs("data", exist_ok=True)
    with open("data/connections.json", "w") as f:
        json.dump(connections, f, indent=2)