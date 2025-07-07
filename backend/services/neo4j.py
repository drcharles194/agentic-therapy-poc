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

# Suppress Neo4j notification warnings about unknown relationships/properties
# These are expected while we're building out the complex schema
neo4j_logger = logging.getLogger("neo4j.notifications")
neo4j_logger.setLevel(logging.ERROR)


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
    
    async def _execute_query(self, query: str, parameters: Dict[str, Any] = None, 
                           operation_name: str = "query") -> Any:
        """Execute a query with standardized error handling."""
        try:
            async with self.get_session() as session:
                result = await session.run(query, parameters or {})
                return await result.single()
        except Exception as e:
            logger.error(f"Failed to execute {operation_name}: {e}")
            return None
    
    async def _schema_already_initialized(self) -> bool:
        """Check if schema has already been initialized by looking for schema dummy user."""
        try:
            result = await self._execute_query(
                "MATCH (u:User {user_id: '__SCHEMA_DUMMY__'}) RETURN COUNT(u) as count",
                operation_name="schema check"
            )
            return result and result["count"] > 0
        except Exception:
            return False
    
    async def _ensure_user_exists(self, user_id: str) -> bool:
        """Ensure a User node exists for the given user_id."""
        query = """
        MERGE (u:User {user_id: $user_id})
        ON CREATE SET 
            u.name = null,
            u.created_at = datetime(),
            u.last_active = datetime()
        ON MATCH SET 
            u.last_active = datetime()
        RETURN u.user_id as user_id
        """
        
        result = await self._execute_query(
            query,
            {"user_id": user_id},
            "user existence check"
        )
        return result is not None
    
    async def _initialize_schema(self):
        """Initialize Neo4j schema with constraints and indexes using new complex schema."""
        # Check if schema has already been initialized
        if await self._schema_already_initialized():
            logger.info("Schema already initialized, skipping initialization")
            return
        
        logger.info("Initializing complex Neo4j schema...")
        
        # Import the new schema
        from backend.personas.sage.schema import sage_schema
        
        # Get schema creation queries from the new schema
        schema_queries = sage_schema.get_schema_creation_queries()
        
        async with self.get_session() as session:
            for query in schema_queries:
                try:
                    await session.run(query)
                    logger.debug(f"Schema query executed: {query}")
                except Exception as e:
                    logger.warning(f"Schema query failed: {query} - {e}")
        
        # Create dummy user with full complex schema
        await self._create_schema_dummy_user()
        logger.info("Complex schema initialization completed")
        
    async def _create_schema_dummy_user(self):
        """Create a dummy user with all complex schema elements to prevent Neo4j warnings."""
        dummy_user_query = """
        // Create dummy user
        MERGE (u:User {user_id: '__SCHEMA_DUMMY__'})
        ON CREATE SET 
            u.name = 'Schema Dummy',
            u.created_at = datetime(),
            u.last_active = datetime()
        
        // Create dummy moment with all properties
        MERGE (m:Moment {id: '__SCHEMA_DUMMY_MOMENT__'})
        ON CREATE SET 
            m.timestamp = datetime(),
            m.context = 'Schema initialization moment',
            m.user_id = '__SCHEMA_DUMMY__',
            m.session_id = '__SCHEMA_DUMMY_SESSION__'
        
        // Create dummy emotion with all new properties
        MERGE (e:Emotion {id: '__SCHEMA_DUMMY_EMOTION__'})
        ON CREATE SET 
            e.label = 'neutral',
            e.intensity = 0.5,
            e.nuance = 'schema-generated neutrality',
            e.bodily_sensation = 'no sensation',
            e.user_id = '__SCHEMA_DUMMY__'
        
        // Create dummy reflection with all new properties
        MERGE (r:Reflection {id: '__SCHEMA_DUMMY_REFLECTION__'})
        ON CREATE SET 
            r.content = 'This is a schema dummy reflection',
            r.insight_type = 'realization',
            r.depth_level = 1,
            r.confidence = 0.5,
            r.user_id = '__SCHEMA_DUMMY__'
        
        // Create dummy contradiction with all new properties
        MERGE (c:Contradiction {id: '__SCHEMA_DUMMY_CONTRADICTION__'})
        ON CREATE SET 
            c.summary = 'Schema dummy tension',
            c.tension_type = 'values',
            c.intensity = 0.3,
            c.user_id = '__SCHEMA_DUMMY__'
        
        // Create dummy value with all properties
        MERGE (v:Value {id: '__SCHEMA_DUMMY_VALUE__'})
        ON CREATE SET 
            v.name = 'schema_completeness',
            v.description = 'The value of having complete schemas',
            v.importance = 0.8,
            v.user_id = '__SCHEMA_DUMMY__'
        
        // Create dummy pattern with all properties
        MERGE (p:Pattern {id: '__SCHEMA_DUMMY_PATTERN__'})
        ON CREATE SET 
            p.description = 'Schema generation patterns',
            p.pattern_type = 'behavioral',
            p.frequency = 'rare',
            p.user_id = '__SCHEMA_DUMMY__'
        
        // Create dummy persona note with all new properties
        MERGE (pn:PersonaNote {id: '__SCHEMA_DUMMY_NOTE__'})
        ON CREATE SET 
            pn.persona = 'Schema',
            pn.note_type = 'observation',
            pn.content = 'Schema successfully initialized',
            pn.created_at = datetime(),
            pn.user_id = '__SCHEMA_DUMMY__'
        
        // Create all complex relationships
        MERGE (u)-[:HAD_MOMENT]->(m)
        MERGE (e)-[:FELT_DURING {prominence: 0.5, trigger: 'schema_init'}]->(m)
        MERGE (r)-[:REALIZED_DURING {spontaneity: 0.0}]->(m)
        MERGE (c)-[:EXPERIENCED_TENSION_DURING]->(m)
        MERGE (u)-[:HOLDS_VALUE {strength: 0.8, awareness_level: 1.0}]->(v)
        MERGE (u)-[:EXHIBITS_PATTERN]->(p)
        MERGE (p)-[:MANIFESTS_AS {consistency: 1.0}]->(e)
        MERGE (pn)-[:OBSERVES]->(e)
        MERGE (pn)-[:REFLECTS_ON]->(r)
        
        RETURN u.user_id as created
        """
        
        try:
            await self._execute_query(dummy_user_query, operation_name="complex schema dummy user creation")
            logger.info("Complex schema dummy user created successfully")
        except Exception as e:
            logger.warning(f"Failed to create complex schema dummy user: {e}")
    
    async def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Retrieve comprehensive user memory using the new complex schema."""
        # Import the new schema to get the query
        from backend.personas.sage.schema import sage_schema
        
        # Ensure user exists first
        await self._ensure_user_exists(user_id)
        
        # Get the internal memory query from the schema (complex, for AI reasoning)
        internal_query = sage_schema.get_internal_memory_query(user_id)
        
        try:
            result = await self._execute_query(
                internal_query, 
                {"user_id": user_id}, 
                "internal user memory retrieval"
            )
            
            if result:
                # Process the new complex structure
                return {
                    "user_id": user_id,
                    "user_name": result.get("u", {}).get("name"),
                    "sage": {
                        "moments": [m for m in result.get("moments", []) if m.get("moment")],
                        "emotional_patterns": [ep for ep in result.get("emotional_patterns", []) if ep.get("emotion")],
                        "reflective_web": [rw for rw in result.get("reflective_web", []) if rw.get("reflection")],
                        "value_system": [vs for vs in result.get("value_system", []) if vs.get("value")],
                        "patterns": [p for p in result.get("patterns", []) if p.get("pattern")],
                        "recent_persona_notes": [note for note in result.get("recent_persona_notes", []) if note]
                    }
                }
        except Exception as e:
            logger.error(f"Error retrieving complex user memory: {e}")
        
        # Return empty memory structure on error
        return {
            "user_id": user_id,
            "user_name": None,
            "sage": {
                "moments": [],
                "emotions": [],
                "reflections": [],
                "patterns": [],
                "values": [],
                "contradictions": [],
                "persona_notes": []
            }
        }

    async def get_user_memory_for_display(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user memory for external usage (frontend display)."""
        # Import the new schema to get the query
        from backend.personas.sage.schema import sage_schema
        
        # Ensure user exists first
        await self._ensure_user_exists(user_id)
        
        # Get the external memory query from the schema (simplified, for UI display)
        external_query = sage_schema.get_external_memory_query(user_id)
        
        try:
            result = await self._execute_query(
                external_query, 
                {"user_id": user_id}, 
                "external user memory retrieval"
            )
            
            if result:
                # Transform the result for frontend compatibility
                return {
                    "user_id": user_id,
                    "user_name": result.get("user", {}).get("name"),
                    "sage": {
                        "moments": [m for m in (result.get("moments", []) or []) if m is not None],
                        "emotions": [e for e in (result.get("emotions", []) or []) if e is not None],
                        "reflections": [r for r in (result.get("reflections", []) or []) if r is not None],
                        "values": [v for v in (result.get("values", []) or []) if v is not None],
                        "patterns": [p for p in (result.get("patterns", []) or []) if p is not None],
                        "notes": [n for n in (result.get("notes", []) or []) if n is not None]
                    }
                }
        except Exception as e:
            logger.error(f"Error retrieving user memory for display: {e}")
        
        # Return empty memory structure on error
        return {
            "user_id": user_id,
            "user_name": None,
            "sage": {
                "moments": [],
                "emotions": [],
                "reflections": [],
                "values": [],
                "patterns": [],
                "notes": []
            }
        }
    
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
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "reflection_id": reflection_id,
                "persona": note_data["persona"],
                "type": note_data.get("type", "note"),
                "content": note_data["content"]
            },
            "persona note addition"
        )
        return result is not None
    
    async def health_check(self) -> Dict[str, str]:
        """Check Neo4j connection health."""
        try:
            if not self.driver:
                return {"status": "disconnected", "message": "Driver not initialized"}
            
            result = await self._execute_query("RETURN 1 as test", operation_name="health check")
            if result:
                return {"status": "healthy", "message": "Connected"}
            else:
                return {"status": "unhealthy", "message": "Query failed"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}

    async def add_reflection(self, user_id: str, reflection_data: Dict[str, Any]) -> bool:
        """Add a reflection to user's memory."""
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (r:Reflection {
            id: $id,
            content: $content,
            timestamp: $timestamp,
            archived: $archived,
            source: $source,
            agent_origin: $agent_origin,
            user_id: $user_id
        })
        
        CREATE (u)-[:HAS_REFLECTION]->(r)
        
        RETURN r.id as reflection_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "id": reflection_data["id"],
                "content": reflection_data["content"],
                "timestamp": reflection_data["timestamp"],
                "archived": reflection_data.get("archived", False),
                "source": reflection_data.get("source", "user"),
                "agent_origin": reflection_data.get("agent_origin", None),
            },
            "reflection addition"
        )
        
        if result:
            logger.info(f"Added reflection for user {user_id}: {reflection_data['id']}")
            return True
        return False

    async def add_emotion(self, user_id: str, emotion_data: Dict[str, Any]) -> bool:
        """Add an emotion observation to user's memory."""
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (e:Emotion {
            label: $label,
            intensity: $intensity,
            timestamp: $timestamp,
            archived_at: $archived_at,
            user_id: $user_id
        })
        
        CREATE (u)-[:EXPERIENCED_EMOTION]->(e)
        
        RETURN e.label as emotion_label
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "label": emotion_data["label"],
                "intensity": emotion_data.get("intensity", 0.5),
                "timestamp": emotion_data["timestamp"],
                "archived_at": emotion_data.get("archived_at", None)
            },
            "emotion addition"
        )
        
        if result:
            logger.info(f"Added emotion for user {user_id}: {emotion_data['label']}")
            return True
        return False

    async def add_self_kindness_event(self, user_id: str, kindness_data: Dict[str, Any]) -> bool:
        """Add a self-kindness event to user's memory."""
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (sk:SelfKindness {
            description: $description,
            timestamp: $timestamp,
            user_id: $user_id
        })
        
        CREATE (u)-[:PRACTICED_KINDNESS]->(sk)
        
        RETURN sk.description as kindness_description
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "description": kindness_data["description"],
                "timestamp": kindness_data["timestamp"]
            },
            "self-kindness event addition"
        )
        
        if result:
            logger.info(f"Added self-kindness event for user {user_id}: {kindness_data['description'][:50]}...")
            return True
        return False

    async def add_contradiction(self, user_id: str, contradiction_data: Dict[str, Any]) -> bool:
        """Add a value contradiction to user's memory."""
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (c:Contradiction {
            summary: $summary,
            user_id: $user_id
        })
        
        CREATE (u)-[:HAS_CONTRADICTION]->(c)
        
        RETURN c.summary as contradiction_summary
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "summary": contradiction_data["summary"]
            },
            "contradiction addition"
        )
        
        if result:
            logger.info(f"Added contradiction for user {user_id}: {contradiction_data['summary'][:50]}...")
            return True
        return False

    # New complex schema methods
    async def add_moment(self, user_id: str, moment_data: Dict[str, Any]) -> bool:
        """Add a moment to user's memory using the new complex schema."""
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (m:Moment {
            id: $id,
            timestamp: datetime($timestamp),
            context: $context,
            user_id: $user_id,
            session_id: $session_id
        })
        
        CREATE (u)-[:HAD_MOMENT]->(m)
        
        RETURN m.id as moment_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "id": moment_data["id"],
                "timestamp": moment_data["timestamp"],
                "context": moment_data["context"],
                "session_id": moment_data["session_id"]
            },
            "moment addition"
        )
        
        if result:
            logger.info(f"Added moment for user {user_id}: {moment_data['id']}")
            return True
        return False

    async def add_complex_reflection(self, user_id: str, reflection_data: Dict[str, Any]) -> bool:
        """Add a reflection using the new complex schema."""
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (m:Moment {id: $moment_id, user_id: $user_id})
        
        CREATE (r:Reflection {
            id: $id,
            content: $content,
            insight_type: $insight_type,
            depth_level: $depth_level,
            confidence: $confidence,
            user_id: $user_id
        })
        
        CREATE (r)-[:REALIZED_DURING {spontaneity: $spontaneity}]->(m)
        
        RETURN r.id as reflection_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "moment_id": reflection_data["moment_id"],
                "id": reflection_data["id"],
                "content": reflection_data.get("content", ""),
                "insight_type": reflection_data.get("insight_type", "realization"),
                "depth_level": reflection_data.get("depth_level", 1),
                "confidence": reflection_data.get("confidence", 0.5),
                "spontaneity": reflection_data.get("spontaneity", 0.7)
            },
            "complex reflection addition"
        )
        
        if result:
            logger.info(f"Added complex reflection for user {user_id}: {reflection_data['id']}")
            return True
        return False

    async def add_complex_emotion(self, user_id: str, emotion_data: Dict[str, Any]) -> bool:
        """Add an emotion using the new complex schema."""
        # VALIDATION: Ensure essential fields are present and meaningful
        label = emotion_data.get("label", "").strip()
        if not label or label.lower() in ["unknown", "unknown emotion"]:
            logger.warning(f"Refusing to add emotion with invalid label for user {user_id}: '{label}'")
            return False
            
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (m:Moment {id: $moment_id, user_id: $user_id})
        
        CREATE (e:Emotion {
            id: $id,
            label: $label,
            intensity: $intensity,
            nuance: $nuance,
            bodily_sensation: $bodily_sensation,
            user_id: $user_id
        })
        
        CREATE (e)-[:FELT_DURING {prominence: $prominence, trigger: $trigger}]->(m)
        
        RETURN e.id as emotion_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "moment_id": emotion_data["moment_id"],
                "id": emotion_data["id"],
                "label": emotion_data.get("label", "unknown"),
                "intensity": emotion_data.get("intensity", 0.5),
                "nuance": emotion_data.get("nuance", ""),
                "bodily_sensation": emotion_data.get("bodily_sensation", "unspecified"),
                "prominence": emotion_data.get("prominence", 0.5),
                "trigger": emotion_data.get("trigger", "conversation")
            },
            "complex emotion addition"
        )
        
        if result:
            logger.info(f"Added complex emotion for user {user_id}: {emotion_data['label']}")
            return True
        return False

    async def add_complex_contradiction(self, user_id: str, contradiction_data: Dict[str, Any]) -> bool:
        """Add a contradiction using the new complex schema."""
        # VALIDATION: Ensure essential fields are present and meaningful
        summary = contradiction_data.get("summary", "").strip()
        if not summary or len(summary) < 5:
            logger.warning(f"Refusing to add contradiction with insufficient summary for user {user_id}: '{summary}'")
            return False
            
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (m:Moment {id: $moment_id, user_id: $user_id})
        
        CREATE (c:Contradiction {
            id: $id,
            summary: $summary,
            tension_type: $tension_type,
            intensity: $intensity,
            user_id: $user_id
        })
        
        CREATE (c)-[:EXPERIENCED_TENSION_DURING]->(m)
        
        RETURN c.id as contradiction_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "moment_id": contradiction_data["moment_id"],
                "id": contradiction_data["id"],
                "summary": contradiction_data.get("summary", ""),
                "tension_type": contradiction_data.get("tension_type", "values"),
                "intensity": contradiction_data.get("intensity", 0.5)
            },
            "complex contradiction addition"
        )
        
        if result:
            logger.info(f"Added complex contradiction for user {user_id}: {contradiction_data['summary'][:50]}...")
            return True
        return False

    async def add_complex_value(self, user_id: str, value_data: Dict[str, Any]) -> bool:
        """Add a value using the new complex schema."""
        # VALIDATION: Ensure essential fields are present and meaningful
        name = value_data.get("name", "").strip()
        if not name or name.lower() in ["unnamed value"]:
            logger.warning(f"Refusing to add value with invalid name for user {user_id}: '{name}'")
            return False
            
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (v:Value {
            id: $id,
            name: $name,
            description: $description,
            importance: $importance,
            user_id: $user_id
        })
        
        CREATE (u)-[:HOLDS_VALUE {strength: $strength, awareness_level: $awareness_level}]->(v)
        
        RETURN v.id as value_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "id": value_data["id"],
                "name": value_data.get("name", ""),
                "description": value_data.get("description", ""),
                "importance": value_data.get("importance", 0.5),
                "strength": value_data.get("strength", 0.5),
                "awareness_level": value_data.get("awareness_level", 0.5)
            },
            "complex value addition"
        )
        
        if result:
            logger.info(f"Added complex value for user {user_id}: {value_data['name']}")
            return True
        return False

    async def add_complex_pattern(self, user_id: str, pattern_data: Dict[str, Any]) -> bool:
        """Add a pattern using the new complex schema."""
        # VALIDATION: Ensure essential fields are present and meaningful
        description = pattern_data.get("description", "").strip()
        if not description or len(description) < 10 or description.lower().startswith("pattern without"):
            logger.warning(f"Refusing to add pattern with insufficient description for user {user_id}: '{description}'")
            return False
            
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (p:Pattern {
            id: $id,
            description: $description,
            pattern_type: $pattern_type,
            frequency: $frequency,
            user_id: $user_id
        })
        
        CREATE (u)-[:EXHIBITS_PATTERN]->(p)
        
        RETURN p.id as pattern_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "id": pattern_data["id"],
                "description": pattern_data.get("description", ""),
                "pattern_type": pattern_data.get("pattern_type", "behavioral"),
                "frequency": pattern_data.get("frequency", "occasional")
            },
            "complex pattern addition"
        )
        
        if result:
            logger.info(f"Added complex pattern for user {user_id}: {pattern_data['description'][:50]}...")
            return True
        return False

    async def add_complex_persona_note(self, user_id: str, note_data: Dict[str, Any]) -> bool:
        """Add a persona note using the new complex schema."""
        # VALIDATION: Ensure essential fields are present and meaningful
        content = note_data.get("content", "").strip()
        if not content or len(content) < 5:
            logger.warning(f"Refusing to add persona note with insufficient content for user {user_id}: '{content}'")
            return False
            
        query = """
        MATCH (u:User {user_id: $user_id})
        
        CREATE (pn:PersonaNote {
            id: $id,
            persona: $persona,
            note_type: $note_type,
            content: $content,
            created_at: datetime(),
            user_id: $user_id
        })
        
        // Create relationships based on what's available
        WITH pn, u
        OPTIONAL MATCH (e:Emotion {id: $emotion_id})
        OPTIONAL MATCH (r:Reflection {id: $reflection_id})
        FOREACH (x IN CASE WHEN e IS NOT NULL THEN [1] ELSE [] END | 
            CREATE (pn)-[:OBSERVES]->(e))
        FOREACH (x IN CASE WHEN r IS NOT NULL THEN [1] ELSE [] END | 
            CREATE (pn)-[:REFLECTS_ON]->(r))
        
        RETURN pn.id as note_id
        """
        
        result = await self._execute_query(
            query,
            {
                "user_id": user_id,
                "id": note_data["id"],
                "persona": note_data.get("persona", "Sage"),
                "note_type": note_data.get("note_type", "observation"),
                "content": note_data.get("content", ""),
                "emotion_id": note_data.get("emotion_id"),
                "reflection_id": note_data.get("reflection_id")
            },
            "complex persona note addition"
        )
        
        if result:
            logger.info(f"Added complex persona note for user {user_id}: {note_data['id']}")
            return True
        return False

    async def process_memory_proposal(self, user_id: str, proposal: Dict[str, Any]) -> bool:
        """Process a memory update proposal from the intelligent system using the new complex schema."""
        # Ensure user exists before processing any memory proposals
        await self._ensure_user_exists(user_id)
        
        update_type = proposal.get("update_type")
        data = proposal.get("data", {})
        
        try:
            if update_type == "moment":
                return await self.add_moment(user_id, data)
            elif update_type == "reflection":
                return await self.add_complex_reflection(user_id, data)
            elif update_type == "emotion":
                return await self.add_complex_emotion(user_id, data)
            elif update_type == "contradiction":
                return await self.add_complex_contradiction(user_id, data)
            elif update_type == "value":
                return await self.add_complex_value(user_id, data)
            elif update_type == "pattern":
                return await self.add_complex_pattern(user_id, data)
            elif update_type == "persona_note":
                return await self.add_complex_persona_note(user_id, data)
            else:
                logger.warning(f"Unknown memory proposal type: {update_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process complex memory proposal {update_type}: {e}")
            return False


# Global service instance
neo4j_service = Neo4jService() 