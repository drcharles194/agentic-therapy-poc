"""
Neo4j database service for memory persistence.
"""
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from backend.config import settings

logger = logging.getLogger(__name__)


class Neo4jService:
    """Neo4j database service for memory persistence."""
    
    def __init__(self):
        self.driver = None
        self.database = settings.neo4j_database
        
    async def connect(self):
        """Initialize Neo4j connection."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password)
            )
            
            # Test connection
            await self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
            
            # Initialize schema
            await self._initialize_schema()
            
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None
            raise
    
    async def disconnect(self):
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
            logger.info("Disconnected from Neo4j")
    
    @asynccontextmanager
    async def get_session(self):
        """Get Neo4j session context manager."""
        if not self.driver:
            raise RuntimeError("Neo4j driver not initialized")
        
        async with self.driver.session(database=self.database) as session:
            yield session
    
    async def _initialize_schema(self):
        """Initialize Neo4j schema with constraints and indexes."""
        schema_queries = [
            # User constraints
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT reflection_id_unique IF NOT EXISTS FOR (r:Reflection) REQUIRE r.id IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX reflection_user_timestamp_index IF NOT EXISTS FOR (r:Reflection) ON (r.user_id, r.timestamp)",
            "CREATE INDEX emotion_user_timestamp_index IF NOT EXISTS FOR (e:Emotion) ON (e.user_id, e.timestamp)",
            "CREATE INDEX persona_note_user_index IF NOT EXISTS FOR (pn:PersonaNote) ON (pn.user_id, pn.persona)",
        ]
        
        async with self.get_session() as session:
            for query in schema_queries:
                try:
                    await session.run(query)
                    logger.debug(f"Schema query executed: {query}")
                except Exception as e:
                    logger.warning(f"Schema query failed: {query} - {e}")
    
    async def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Retrieve comprehensive user memory for Sage persona."""
        query = """
        MATCH (u:User {user_id: $user_id})
        
        // Get reflections with persona notes
        OPTIONAL MATCH (u)-[:HAS_REFLECTION]->(r:Reflection)
        WHERE NOT r.archived
        OPTIONAL MATCH (r)-[:HAS_NOTE]->(pn:PersonaNote {persona: 'Sage'})
        
        // Get emotions
        OPTIONAL MATCH (u)-[:EXPERIENCED_EMOTION]->(e:Emotion)
        WHERE e.archived_at IS NULL
        
        // Get self-kindness events
        OPTIONAL MATCH (u)-[:PRACTICED_KINDNESS]->(sk:SelfKindness)
        
        // Get contradictions
        OPTIONAL MATCH (u)-[:HAS_CONTRADICTION]->(c:Contradiction)
        
        RETURN u.user_id as user_id,
               u.name as user_name,
               collect(DISTINCT {
                   id: r.id,
                   content: r.content,
                   timestamp: r.timestamp,
                   archived: r.archived,
                   source: r.source,
                   agent_origin: r.agent_origin,
                   user_id: r.user_id,
                   persona_notes: collect(DISTINCT {
                       persona: pn.persona,
                       type: pn.type,
                       content: pn.content,
                       created_at: pn.created_at,
                       user_id: pn.user_id
                   })
               }) as reflections,
               collect(DISTINCT {
                   label: e.label,
                   intensity: e.intensity,
                   timestamp: e.timestamp,
                   archived_at: e.archived_at,
                   user_id: e.user_id
               }) as emotions,
               collect(DISTINCT {
                   description: sk.description,
                   timestamp: sk.timestamp,
                   user_id: sk.user_id
               }) as self_kindness_events,
               collect(DISTINCT {
                   summary: c.summary,
                   user_id: c.user_id
               }) as contradictions
        """
        
        async with self.get_session() as session:
            result = await session.run(query, user_id=user_id)
            record = await result.single()
            
            if not record:
                # Create new user if doesn't exist
                await self._create_user(user_id)
                return {
                    "user_id": user_id,
                    "user_name": None,
                    "sage": {
                        "reflections": [],
                        "emotions": [],
                        "self_kindness_events": [],
                        "contradictions": []
                    }
                }
            
            # Convert Neo4j record to expected format
            return {
                "user_id": record["user_id"],
                "user_name": record["user_name"],
                "sage": {
                    "reflections": [r for r in record["reflections"] if r["id"] is not None],
                    "emotions": [e for e in record["emotions"] if e["label"] is not None],
                    "self_kindness_events": [sk for sk in record["self_kindness_events"] if sk["description"] is not None],
                    "contradictions": [c for c in record["contradictions"] if c["summary"] is not None]
                }
            }
    
    async def _create_user(self, user_id: str):
        """Create a new user node."""
        query = """
        MERGE (u:User {user_id: $user_id})
        ON CREATE SET u.created_at = datetime(), u.last_active = datetime()
        ON MATCH SET u.last_active = datetime()
        """
        
        async with self.get_session() as session:
            await session.run(query, user_id=user_id)
            logger.info(f"Created/updated user: {user_id}")
    
    async def add_persona_note(self, user_id: str, reflection_id: str, note_data: Dict[str, Any]) -> bool:
        """Add a persona note to a reflection."""
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (r:Reflection {id: $reflection_id, user_id: $user_id})
        
        CREATE (pn:PersonaNote {
            persona: $persona,
            type: $type,
            content: $content,
            created_at: datetime(),
            user_id: $user_id
        })
        
        CREATE (r)-[:HAS_NOTE]->(pn)
        CREATE (u)-[:CREATED_NOTE]->(pn)
        
        RETURN pn.created_at as created_at
        """
        
        try:
            async with self.get_session() as session:
                result = await session.run(
                    query,
                    user_id=user_id,
                    reflection_id=reflection_id,
                    persona=note_data["persona"],
                    type=note_data["type"],
                    content=note_data["content"]
                )
                await result.single()
                return True
        except Exception as e:
            logger.error(f"Failed to add persona note: {e}")
            return False
    
    async def health_check(self) -> Dict[str, str]:
        """Check Neo4j connection health."""
        try:
            if not self.driver:
                return {"status": "disconnected", "message": "Driver not initialized"}
            
            async with self.get_session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
                
            return {"status": "healthy", "message": "Connected"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}


# Global service instance
neo4j_service = Neo4jService() 