from .embeddings import EmbeddingManager
from .semantic import SemanticSearch
from config.constants import N_RESULTS

class ConnectionSemanticSearch:
    """User-specific semantic search for connections"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.embedding_manager = EmbeddingManager(user_id)
        self.semantic_search = SemanticSearch(user_id)
    
    def is_connection_vectorized(self, connection_url: str) -> bool:
        return self.embedding_manager.is_connection_vectorized(connection_url)
    
    def get_unvectorized_connections(self, enriched_connections):
        return self.embedding_manager.get_unvectorized_connections(enriched_connections)
    
    def batch_store_embeddings(self, connections):
        return self.embedding_manager.batch_store_embeddings(connections)
    
    def store_connection_embeddings(self, connection):
        return self.embedding_manager.store_connection_embeddings(connection)
    
    def extract_mission_attributes(self, mission: str):
        return self.semantic_search.extract_mission_attributes(mission)
    
    def search_top_connections(self, mission_attributes, n_results: int = N_RESULTS):
        return self.semantic_search.search_top_connections(mission_attributes, n_results)

__all__ = ['ConnectionSemanticSearch', 'EmbeddingManager', 'SemanticSearch']