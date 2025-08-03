import json
import os

def get_user_data_path(user_id: str) -> str:
    """Get user-specific data directory path"""
    user_dir = f"data/{user_id}"
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def load_enriched_cache(user_id: str):
    """Load existing enriched connections cache for specific user"""
    user_dir = get_user_data_path(user_id)
    cache_path = f"{user_dir}/connections_enriched.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}

def save_enriched_cache(user_id: str, cache):
    """Save enriched connections cache for specific user"""
    user_dir = get_user_data_path(user_id)
    with open(f"{user_dir}/connections_enriched.json", "w") as f:
        json.dump(cache, f, indent=2)

def save_connections_list(user_id: str, connections):
    """Save current connections list for specific user"""
    user_dir = get_user_data_path(user_id)
    with open(f"{user_dir}/connections.json", "w") as f:
        json.dump(connections, f, indent=2)