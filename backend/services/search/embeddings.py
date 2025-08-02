import chromadb
import logging
from typing import List, Dict, Any
# from config.settings import chroma_client, embedding_model
from config.settings import chroma_client, get_embeddings


logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self):
        self.collections = {}
        self.attributes = ['summary', 'position', 'location', 'industry']
        self._init_collections()
        
    def _init_collections(self):
        """Initialize ChromaDB collections for each attribute"""
        for attr in self.attributes:
            try:
                self.collections[attr] = chroma_client.get_or_create_collection(
                    name=f"connections_{attr}",
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                logger.error(f"Failed to initialize collection for {attr}: {e}")
    
    def is_connection_vectorized(self, connection_url: str) -> bool:
        conn_id = connection_url.replace('https://www.linkedin.com/in/', '')
        if not conn_id:
            return False
        
        logger.info(f"Checking vectorization for: {conn_id}")  # Add this
        
        try:
            for attr in self.attributes:
                result = self.collections[attr].get(ids=[conn_id])
                if not result['ids'] or len(result['ids']) == 0:
                    logger.info(f"Not vectorized in {attr}: {conn_id}")  # Add this
                    return False
            logger.info(f"Already vectorized: {conn_id}")  # Add this
            return True
        except Exception as e:
            logger.error(f"Error checking vectorization for {conn_id}: {e}")
            return False

    def get_unvectorized_connections(self, enriched_connections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of enriched connections that need vectorization"""
        unvectorized = []
        
        for url, connection in enriched_connections.items():
            if connection.get("enriched", False) and not self.is_connection_vectorized(url):
                unvectorized.append(connection)
        
        logger.info(f"Found {len(unvectorized)} connections needing vectorization")
        return unvectorized

    def store_connection_embeddings(self, connection: Dict[str, Any]):
        """Store embeddings for a single connection across all attributes"""
        conn_id = connection.get('url', '').replace('https://www.linkedin.com/in/', '')
        if not conn_id:
            return False
        
        try:
            # Prepare texts for each attribute
            texts = {
                'summary': connection.get('summary', '') or 'N/A',
                'position': connection.get('headline', '') or connection.get('position', '') or 'N/A',
                'location': connection.get('location', '') or 'N/A',
                'industry': connection.get('industry', '') or 'N/A'
            }
            
            # Get all embeddings in parallel (single API call)
            text_list = [texts[attr] for attr in self.attributes]
            embeddings = get_embeddings(text_list)
            
            # Store embeddings in each collection
            for i, attr in enumerate(self.attributes):
                self.collections[attr].upsert(
                    ids=[conn_id],
                    embeddings=[embeddings[i]],
                    documents=[texts[attr]],
                    metadatas=[{
                        'name': f"{connection.get('first_name', '')} {connection.get('last_name', '')}",
                        'company': connection.get('current_company', '') or connection.get('company', ''),
                        'url': connection.get('url', '')
                    }]
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embeddings for {conn_id}: {e}")
            return False
        
    def batch_store_embeddings(self, connections: List[Dict[str, Any]]):
        """Store embeddings for multiple connections in batches"""
        batch_size = 50  # Process in smaller batches
        
        for i in range(0, len(connections), batch_size):
            batch = connections[i:i + batch_size]
            logger.info(f"Vectorizing batch {i//batch_size + 1}/{(len(connections) + batch_size - 1)//batch_size}")
            
            for connection in batch:
                try:
                    self.store_connection_embeddings(connection)
                except Exception as e:
                    logger.error(f"Failed to vectorize connection {connection.get('url', '')}: {e}")
        
        logger.info(f"Completed vectorization of {len(connections)} connections")