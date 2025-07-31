import chromadb
import logging
from typing import List, Dict, Any
from config import chroma_client, embedding_model, client

logger = logging.getLogger(__name__)

class ConnectionSemanticSearch:
    def __init__(self):
        self.collections = {}
        self.attributes = ['summary', 'position', 'location', 'industry']
        self._init_collections()
        
    def is_connection_vectorized(self, connection_url: str) -> bool:
        """Check if a connection is already vectorized in all collections"""
        conn_id = connection_url.replace('https://www.linkedin.com/in/', '')
        if not conn_id:
            return False
        
        try:
            for attr in self.attributes:
                result = self.collections[attr].get(ids=[conn_id])
                if not result['ids'] or len(result['ids']) == 0:
                    return False
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
    
    def store_connection_embeddings(self, connection: Dict[str, Any]):
        """Store embeddings for a single connection across all attributes"""
        conn_id = connection.get('url', '').replace('https://www.linkedin.com/in/', '')
        if not conn_id:
            return
        
        # Prepare texts for each attribute
        texts = {
            'summary': connection.get('summary', '') or 'N/A',
            'position': connection.get('headline', '') or connection.get('position', '') or 'N/A',
            'location': connection.get('location', '') or 'N/A',
            'industry': connection.get('industry', '') or 'N/A'
        }
        
        # Store embeddings in each collection
        for attr in self.attributes:
            try:
                # Generate embedding
                embedding = embedding_model.encode([texts[attr]])[0].tolist()
                
                # Store in ChromaDB
                self.collections[attr].upsert(
                    ids=[conn_id],
                    embeddings=[embedding],
                    documents=[texts[attr]],
                    metadatas=[{
                        'name': f"{connection.get('first_name', '')} {connection.get('last_name', '')}",
                        'company': connection.get('current_company', '') or connection.get('company', ''),
                        'url': connection.get('url', '')
                    }]
                )
            except Exception as e:
                logger.error(f"Failed to store embedding for {attr}: {e}")
    
    def extract_mission_attributes(self, mission: str) -> Dict[str, str]:
        """Extract structured attributes from mission using LLM"""
        prompt = f"""
        Identify the position, location, and industry in the mission. Return ONLY a valid JSON object with this exact structure:
        
        {{
            "position": "Position mentioned in the mission or N/A",
            "location": "Location mentioned in the mission or N/A", 
            "industry": "Industry mentioned in the mission or N/A"
        }}
        
        Mission: {mission}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            import json
            attributes = json.loads(response.choices[0].message.content.strip())
            return {
                'summary': mission,
                'position': attributes.get('position', 'N/A'),
                'location': attributes.get('location', 'N/A'),
                'industry': attributes.get('industry', 'N/A')
            }
        except Exception as e:
            logger.error(f"Failed to extract mission attributes: {e}")
            return {
                'summary': mission,
                'position': 'N/A',
                'location': 'N/A',
                'industry': 'N/A'
            }
    
    def search_top_connections(self, mission_attributes: Dict[str, str], n_results: int = 15) -> List[Dict]:
        """Search for top connections using semantic similarity across all attributes"""
        all_scores = {}
        
        # Search each attribute collection
        for attr in self.attributes:
            query_text = mission_attributes.get(attr, 'N/A')
            if query_text == 'N/A':
                continue
                
            try:
                # embed the query_text
                query_embedding = embedding_model.encode([query_text])[0].tolist()

                # get results for the whole collection
                collection_size = self.collections[attr].count()
                results = self.collections[attr].query(
                    query_embeddings=query_embedding,
                    n_results=collection_size,
                    include=['distances', 'metadatas']
                )

                # Check if results are empty
                if not results['ids'] or not results['ids'][0]:
                    logger.warning(f"No results found for {attr} with query: {query_text}")
                    continue
            
                # Convert distances to similarities and accumulate scores
                for i, distance in enumerate(results['distances'][0]):
                    conn_id = results['ids'][0][i]
                    similarity = max(0.0, 1.0 - distance)  # ChromaDB uses distance = 1 - similarity
                    
                    if conn_id not in all_scores:
                        all_scores[conn_id] = {
                            'total_similarity': 0,
                            'metadata': results['metadatas'][0][i]
                        }
                    all_scores[conn_id]['total_similarity'] += similarity
                    
            except Exception as e:
                logger.error(f"Failed to search {attr} collection: {e}")
        
        # Sort by total similarity and return top N
        sorted_connections = sorted(
            all_scores.items(), 
            key=lambda x: x[1]['total_similarity'], 
            reverse=True
        )[:n_results]
        
        logger.info(f"Found {len(sorted_connections)} top connections based on mission attributes")

        return [
            {
                'id': conn_id,
                'similarity_score': data['total_similarity'],
                'name': data['metadata'].get('name', ''),
                'company': data['metadata'].get('company', ''),
                'url': data['metadata'].get('url', '')
            }
            for conn_id, data in sorted_connections
        ]