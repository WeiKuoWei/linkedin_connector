from sqlmodel import Session, select
from sqlalchemy.dialects.postgresql import insert
from config.database import get_session
from models.database import UserConnection
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

async def load_enriched_cache(user_id: str) -> Dict[str, dict]:
    """Load user's connections from database"""
    async with get_session() as session:
        statement = select(UserConnection).where(UserConnection.user_id == user_id)
        result = await session.exec(statement)
        connections = result.all()
        
        # Convert to current cache format
        cache = {}
        for conn in connections:
            cache[conn.url] = {
                "first_name": conn.first_name,
                "last_name": conn.last_name,
                "url": conn.url,
                "company": conn.company,
                "position": conn.position,
                "email": conn.email,
                "connected_on": conn.connected_on,
                "enriched": conn.enriched,
                **conn.profile_data  # Spread enriched data
            }
        return cache

async def save_enriched_cache(user_id: str, cache: Dict[str, dict]):
    """Save connections to database"""
    async with get_session() as session:
        for url, conn_data in cache.items():
            # Separate base fields from profile data
            base_fields = {
                'user_id': user_id,
                'url': url,
                'first_name': conn_data.get('first_name', ''),
                'last_name': conn_data.get('last_name', ''),
                'company': conn_data.get('company'),
                'position': conn_data.get('position'),
                'email': conn_data.get('email'),
                'connected_on': conn_data.get('connected_on'),
                'enriched': conn_data.get('enriched', False),
                'updated_at': datetime.utcnow()
            }
            
            # Everything else goes in profile_data JSONB
            profile_data = {k: v for k, v in conn_data.items() 
                          if k not in base_fields.keys()}
            base_fields['profile_data'] = profile_data
            
            # Upsert (insert or update)
            stmt = insert(UserConnection).values(**base_fields)
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id', 'url'],
                set_=dict(
                    first_name=stmt.excluded.first_name,
                    last_name=stmt.excluded.last_name,
                    company=stmt.excluded.company,
                    position=stmt.excluded.position,
                    enriched=stmt.excluded.enriched,
                    profile_data=stmt.excluded.profile_data,
                    updated_at=stmt.excluded.updated_at
                )
            )
            await session.exec(stmt)
        
        await session.commit()

async def save_connections_list(user_id: str, connections: List[dict]):
    """Save basic connections list (for compatibility)"""
    # Convert to cache format and save
    cache = {conn['url']: conn for conn in connections}
    await save_enriched_cache(user_id, cache)