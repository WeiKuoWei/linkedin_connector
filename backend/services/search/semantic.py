import logging
from typing import List, Dict, Any
from config.settings import client, N_RESULTS, get_embeddings
from .embeddings import EmbeddingManager

logger = logging.getLogger(__name__)

class SemanticSearch:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()

        self.weights = {
            'summary': 1,
            'position': 1,
            'industry': 1,
            'location': 1
        }
        
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
                model="gpt-4.1",
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
    
    def search_top_connections(self, mission_attributes: Dict[str, str], n_results: int = N_RESULTS) -> List[Dict]:
        """Search for top connections using semantic similarity across all attributes"""
        
        all_scores = {}
        
        # Search each attribute collection
        for attr in self.embedding_manager.attributes:
            query_text = mission_attributes.get(attr, 'N/A')
            if query_text == 'N/A':
                continue
                
            weight = self.weights.get(attr, 1.0)

            try:
                # embed the query_text
                # query_embedding = embedding_model.encode([query_text])[0].tolist()
                query_embedding = get_embeddings([query_text])[0]


                # get results for the whole collection
                collection_size = self.embedding_manager.collections[attr].count()
                results = self.embedding_manager.collections[attr].query(
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
                    similarity = max(0.0, 1.0 - distance)
                    weighted_similarity = similarity * weight 
                    
                    if conn_id not in all_scores:
                        all_scores[conn_id] = {
                            'total_similarity': 0,
                            'metadata': results['metadatas'][0][i]
                        }
                    all_scores[conn_id]['total_similarity'] += weighted_similarity
                    
            except Exception as e:
                logger.error(f"Failed to search {attr} collection: {e}")
        
        # Sort by total similarity and return top N
        sorted_connections = sorted(
            all_scores.items(), 
            key=lambda x: x[1]['total_similarity'], 
            reverse=True
        )[:n_results]
        
        logger.info(f"Found {len(sorted_connections)} top connections out of {collection_size} based on mission attributes")

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