"""
Neo4j graph schema definition for the Sage persona.

This module defines the graph structure for Sage-specific memory storage,
including nodes, relationships, and query patterns.
"""
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class NodeType:
    """Definition of a Neo4j node type."""
    label: str
    properties: Dict[str, str]
    indexes: List[str] = None


@dataclass
class RelationshipType:
    """Definition of a Neo4j relationship type."""
    type: str
    from_node: str
    to_node: str
    properties: Dict[str, str] = None


class SageSchema:
    """Schema definition for Sage persona memory graph."""
    
    # Node definitions
    NODES = {
        "User": NodeType(
            label="User",
            properties={
                "user_id": "string",
                "name": "string",
                "created_at": "datetime",
                "last_active": "datetime"
            },
            indexes=["user_id"]
        ),
        
        "Reflection": NodeType(
            label="Reflection",
            properties={
                "id": "string",
                "content": "string",
                "timestamp": "datetime",
                "archived": "boolean",
                "source": "string",  # 'user', 'agent', etc.
                "agent_origin": "string",  # optional, which agent created this
                "user_id": "string"
            },
            indexes=["id", "user_id", "timestamp"]
        ),
        
        "Emotion": NodeType(
            label="Emotion",
            properties={
                "label": "string",  # e.g., 'sadness', 'joy', 'anxiety'
                "intensity": "float",  # 0.0 to 1.0
                "timestamp": "datetime",
                "archived_at": "datetime",  # optional
                "user_id": "string"
            },
            indexes=["user_id", "timestamp", "label"]
        ),
        
        "SelfKindness": NodeType(
            label="SelfKindness",
            properties={
                "description": "string",
                "timestamp": "datetime",
                "user_id": "string"
            },
            indexes=["user_id", "timestamp"]
        ),
        
        "Contradiction": NodeType(
            label="Contradiction",
            properties={
                "summary": "string",
                "identified_at": "datetime",
                "user_id": "string"
            },
            indexes=["user_id"]
        ),
        
        "PersonaNote": NodeType(
            label="PersonaNote",
            properties={
                "persona": "string",  # e.g., 'Sage'
                "type": "string",  # e.g., 'gentle_reframe', 'observation'
                "content": "string",
                "created_at": "datetime",
                "user_id": "string"
            },
            indexes=["user_id", "persona", "created_at"]
        )
    }
    
    # Relationship definitions
    RELATIONSHIPS = {
        "HAS_REFLECTION": RelationshipType(
            type="HAS_REFLECTION",
            from_node="User",
            to_node="Reflection"
        ),
        
        "FELT_IN": RelationshipType(
            type="FELT_IN",
            from_node="Emotion",
            to_node="Reflection",
            properties={
                "context": "string"  # optional additional context
            }
        ),
        
        "EXPERIENCED_EMOTION": RelationshipType(
            type="EXPERIENCED_EMOTION",
            from_node="User",
            to_node="Emotion"
        ),
        
        "PRACTICED_KINDNESS": RelationshipType(
            type="PRACTICED_KINDNESS",
            from_node="User",
            to_node="SelfKindness"
        ),
        
        "HAS_CONTRADICTION": RelationshipType(
            type="HAS_CONTRADICTION",
            from_node="User",
            to_node="Contradiction"
        ),
        
        "HAS_NOTE": RelationshipType(
            type="HAS_NOTE",
            from_node="Reflection",
            to_node="PersonaNote"
        ),
        
        "CREATED_NOTE": RelationshipType(
            type="CREATED_NOTE",
            from_node="User",
            to_node="PersonaNote"
        )
    }
    
    @classmethod
    def get_schema_creation_queries(cls) -> List[str]:
        """Generate Cypher queries to create schema indexes and constraints."""
        queries = []
        
        # Create uniqueness constraints
        queries.append("CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
        queries.append("CREATE CONSTRAINT reflection_id_unique IF NOT EXISTS FOR (r:Reflection) REQUIRE r.id IS UNIQUE")
        
        # Create indexes for performance
        for node_label, node_def in cls.NODES.items():
            if node_def.indexes:
                for index_prop in node_def.indexes:
                    if index_prop not in ["user_id", "id"]:  # Skip if already covered by constraints
                        queries.append(f"CREATE INDEX {node_label.lower()}_{index_prop}_index IF NOT EXISTS FOR (n:{node_label}) ON (n.{index_prop})")
        
        return queries
    
    @classmethod
    def get_sage_memory_query(cls, user_id: str) -> str:
        """Generate Cypher query to retrieve all Sage-relevant memory for a user."""
        return f"""
        MATCH (u:User {{user_id: $user_id}})
        
        // Get reflections with persona notes
        OPTIONAL MATCH (u)-[:HAS_REFLECTION]->(r:Reflection)
        WHERE NOT r.archived
        OPTIONAL MATCH (r)-[:HAS_NOTE]->(pn:PersonaNote {{persona: 'Sage'}})
        
        // Get emotions
        OPTIONAL MATCH (u)-[:EXPERIENCED_EMOTION]->(e:Emotion)
        WHERE e.archived_at IS NULL
        
        // Get self-kindness events
        OPTIONAL MATCH (u)-[:PRACTICED_KINDNESS]->(sk:SelfKindness)
        
        // Get contradictions
        OPTIONAL MATCH (u)-[:HAS_CONTRADICTION]->(c:Contradiction)
        
        RETURN u,
               collect(DISTINCT {{
                   reflection: r,
                   persona_notes: collect(DISTINCT pn)
               }}) as reflections,
               collect(DISTINCT e) as emotions,
               collect(DISTINCT sk) as self_kindness_events,
               collect(DISTINCT c) as contradictions
        """


# Schema instance for import
sage_schema = SageSchema() 