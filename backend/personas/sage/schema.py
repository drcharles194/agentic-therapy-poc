"""
Neo4j graph schema definition for the Sage persona.

This module defines a complex graph structure that reflects the interconnected
nature of human psychological experiences, with many-to-many relationships
between emotions, reflections, contradictions, and contextual moments.
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
    """
    Enhanced schema for complex human psychological experiences.
    
    This schema recognizes that:
    - Emotions can co-occur and influence each other
    - Reflections can build on previous reflections  
    - Contradictions emerge from multiple emotions and reflections
    - Context and time create meaning
    - Everything is interconnected in the human experience
    """
    
    # Core node definitions
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
        
        "Moment": NodeType(
            label="Moment",
            properties={
                "id": "string",
                "timestamp": "datetime",
                "context": "string",  # Brief description of what was happening
                "user_id": "string",
                "session_id": "string"  # Groups related moments in a conversation
            },
            indexes=["id", "user_id", "timestamp", "session_id"]
        ),
        
        "Emotion": NodeType(
            label="Emotion",
            properties={
                "id": "string",
                "label": "string",  # Primary emotion (anxiety, sadness, joy, etc.)
                "intensity": "float",  # 0.0 to 1.0
                "nuance": "string",  # Optional: "anticipatory anxiety", "grief-tinged joy"
                "bodily_sensation": "string",  # Optional: physical manifestation
                "user_id": "string"
            },
            indexes=["id", "user_id", "label"]
        ),
        
        "Reflection": NodeType(
            label="Reflection", 
            properties={
                "id": "string",
                "content": "string",
                "insight_type": "string",  # "realization", "pattern_recognition", "memory", "value_clarification"
                "depth_level": "integer",  # 1=surface, 2=moderate, 3=deep insight
                "confidence": "float",  # How certain the user feels about this insight
                "user_id": "string"
            },
            indexes=["id", "user_id", "insight_type"]
        ),
        
        "Contradiction": NodeType(
            label="Contradiction",
            properties={
                "id": "string", 
                "summary": "string",
                "tension_type": "string",  # "values", "desires", "beliefs", "behaviors"
                "intensity": "float",  # How painful/significant this contradiction feels
                "user_id": "string"
            },
            indexes=["id", "user_id", "tension_type"]
        ),
        
        "Value": NodeType(
            label="Value",
            properties={
                "id": "string",
                "name": "string",  # "freedom", "security", "connection", etc.
                "description": "string",  # How the user defines this value
                "importance": "float",  # 0.0 to 1.0
                "user_id": "string"
            },
            indexes=["id", "user_id", "name"]
        ),
        
        "Pattern": NodeType(
            label="Pattern",
            properties={
                "id": "string",
                "description": "string",  # Observed behavioral/emotional pattern
                "pattern_type": "string",  # "emotional", "behavioral", "cognitive", "relational"
                "frequency": "string",  # "rare", "occasional", "frequent", "constant"
                "user_id": "string"
            },
            indexes=["id", "user_id", "pattern_type"]
        ),
        
        "PersonaNote": NodeType(
            label="PersonaNote",
            properties={
                "id": "string",
                "persona": "string",  # "Sage"
                "note_type": "string",  # "observation", "connection", "gentle_question", "validation"
                "content": "string",
                "created_at": "datetime", 
                "user_id": "string"
            },
            indexes=["id", "user_id", "persona", "created_at"]
        )
    }
    
    # Complex relationship definitions
    RELATIONSHIPS = {
        # User connections
        "HAD_MOMENT": RelationshipType(
            type="HAD_MOMENT",
            from_node="User", 
            to_node="Moment"
        ),
        
        # Moment connections - moments can contain multiple emotions/reflections
        "FELT_DURING": RelationshipType(
            type="FELT_DURING",
            from_node="Emotion",
            to_node="Moment",
            properties={
                "prominence": "float",  # How prominent this emotion was in the moment
                "trigger": "string"  # What seemed to trigger this emotion
            }
        ),
        
        "REALIZED_DURING": RelationshipType(
            type="REALIZED_DURING", 
            from_node="Reflection",
            to_node="Moment",
            properties={
                "spontaneity": "float"  # How spontaneous vs. worked-toward this insight was
            }
        ),
        
        "EXPERIENCED_TENSION_DURING": RelationshipType(
            type="EXPERIENCED_TENSION_DURING",
            from_node="Contradiction", 
            to_node="Moment"
        ),
        
        # Emotion interconnections - emotions can influence each other
        "CO_OCCURS_WITH": RelationshipType(
            type="CO_OCCURS_WITH",
            from_node="Emotion",
            to_node="Emotion",
            properties={
                "frequency": "float",  # How often these emotions appear together
                "influence_strength": "float"  # How much one affects the other
            }
        ),
        
        "TRANSFORMS_INTO": RelationshipType(
            type="TRANSFORMS_INTO",
            from_node="Emotion", 
            to_node="Emotion",
            properties={
                "duration": "string",  # How long the transformation takes
                "trigger_type": "string"  # What typically causes this transformation
            }
        ),
        
        # Reflection interconnections - insights build on each other
        "BUILDS_ON": RelationshipType(
            type="BUILDS_ON",
            from_node="Reflection",
            to_node="Reflection",
            properties={
                "connection_type": "string"  # "expands", "contradicts", "clarifies", "applies"
            }
        ),
        
        "CHALLENGES": RelationshipType(
            type="CHALLENGES", 
            from_node="Reflection",
            to_node="Reflection",
            properties={
                "resolution_status": "string"  # "unresolved", "integrated", "abandoned"
            }
        ),
        
        # Emotion-Reflection connections - emotions can inspire insights and vice versa
        "INSPIRED_BY": RelationshipType(
            type="INSPIRED_BY",
            from_node="Reflection",
            to_node="Emotion",
            properties={
                "inspiration_type": "string"  # "curiosity", "pain", "joy", "confusion"
            }
        ),
        
        "EXPLAINS": RelationshipType(
            type="EXPLAINS",
            from_node="Reflection", 
            to_node="Emotion",
            properties={
                "clarity_level": "float"  # How well this insight explains the emotion
            }
        ),
        
        # Contradiction relationships - contradictions emerge from conflicting elements
        "CREATES_TENSION": RelationshipType(
            type="CREATES_TENSION",
            from_node="Value",
            to_node="Contradiction", 
            properties={
                "conflict_intensity": "float"
            }
        ),
        
        "CONTRIBUTES_TO_TENSION": RelationshipType(
            type="CONTRIBUTES_TO_TENSION",
            from_node="Emotion",
            to_node="Contradiction"
        ),
        
        "REVEALS_TENSION": RelationshipType(
            type="REVEALS_TENSION",
            from_node="Reflection", 
            to_node="Contradiction"
        ),
        
        # Value relationships
        "HOLDS_VALUE": RelationshipType(
            type="HOLDS_VALUE",
            from_node="User",
            to_node="Value",
            properties={
                "strength": "float",  # How strongly held
                "awareness_level": "float"  # How conscious the user is of this value
            }
        ),
        
        "CONFLICTS_WITH": RelationshipType(
            type="CONFLICTS_WITH",
            from_node="Value",
            to_node="Value",
            properties={
                "conflict_context": "string"  # When/where this conflict appears
            }
        ),
        
        # Pattern relationships
        "EXHIBITS_PATTERN": RelationshipType(
            type="EXHIBITS_PATTERN",
            from_node="User",
            to_node="Pattern"
        ),
        
        "MANIFESTS_AS": RelationshipType(
            type="MANIFESTS_AS",
            from_node="Pattern",
            to_node="Emotion",
            properties={
                "consistency": "float"  # How consistently this pattern produces this emotion
            }
        ),
        
        "REINFORCES_PATTERN": RelationshipType(
            type="REINFORCES_PATTERN", 
            from_node="Reflection",
            to_node="Pattern"
        ),
        
        # Persona note relationships - can connect to any element
        "OBSERVES": RelationshipType(
            type="OBSERVES",
            from_node="PersonaNote",
            to_node="Emotion"
        ),
        
        "REFLECTS_ON": RelationshipType(
            type="REFLECTS_ON",
            from_node="PersonaNote", 
            to_node="Reflection"
        ),
        
        "NOTES_TENSION": RelationshipType(
            type="NOTES_TENSION",
            from_node="PersonaNote",
            to_node="Contradiction"
        ),
        
        "IDENTIFIES_PATTERN": RelationshipType(
            type="IDENTIFIES_PATTERN",
            from_node="PersonaNote",
            to_node="Pattern"
        )
    }
    
    @classmethod
    def get_schema_creation_queries(cls) -> List[str]:
        """Generate Cypher queries to create schema indexes and constraints."""
        queries = []
        
        # Create uniqueness constraints
        queries.append("CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
        queries.append("CREATE CONSTRAINT moment_id_unique IF NOT EXISTS FOR (m:Moment) REQUIRE m.id IS UNIQUE")
        queries.append("CREATE CONSTRAINT emotion_id_unique IF NOT EXISTS FOR (e:Emotion) REQUIRE e.id IS UNIQUE")
        queries.append("CREATE CONSTRAINT reflection_id_unique IF NOT EXISTS FOR (r:Reflection) REQUIRE r.id IS UNIQUE")
        queries.append("CREATE CONSTRAINT contradiction_id_unique IF NOT EXISTS FOR (c:Contradiction) REQUIRE c.id IS UNIQUE")
        queries.append("CREATE CONSTRAINT value_id_unique IF NOT EXISTS FOR (v:Value) REQUIRE v.id IS UNIQUE")
        queries.append("CREATE CONSTRAINT pattern_id_unique IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE")
        queries.append("CREATE CONSTRAINT persona_note_id_unique IF NOT EXISTS FOR (pn:PersonaNote) REQUIRE pn.id IS UNIQUE")
        
        # Create performance indexes
        performance_indexes = [
            "CREATE INDEX user_last_active_index IF NOT EXISTS FOR (u:User) ON (u.last_active)",
            "CREATE INDEX moment_user_timestamp_index IF NOT EXISTS FOR (m:Moment) ON (m.user_id, m.timestamp)",
            "CREATE INDEX moment_session_index IF NOT EXISTS FOR (m:Moment) ON (m.session_id)",
            "CREATE INDEX emotion_user_label_index IF NOT EXISTS FOR (e:Emotion) ON (e.user_id, e.label)",
            "CREATE INDEX reflection_user_type_index IF NOT EXISTS FOR (r:Reflection) ON (r.user_id, r.insight_type)",
            "CREATE INDEX contradiction_user_type_index IF NOT EXISTS FOR (c:Contradiction) ON (c.user_id, c.tension_type)",
            "CREATE INDEX value_user_importance_index IF NOT EXISTS FOR (v:Value) ON (v.user_id, v.importance)",
            "CREATE INDEX pattern_user_frequency_index IF NOT EXISTS FOR (p:Pattern) ON (p.user_id, p.frequency)",
            "CREATE INDEX persona_note_user_created_index IF NOT EXISTS FOR (pn:PersonaNote) ON (pn.user_id, pn.created_at)"
        ]
        
        queries.extend(performance_indexes)
        return queries
    
    @classmethod 
    def get_internal_memory_query(cls, user_id: str) -> str:
        """
        Generate a comprehensive Cypher query for internal backend usage (Sage's context).
        
        This query captures the full web of relationships between emotions, reflections,
        contradictions, values, and patterns to provide rich context for AI reasoning.
        Optimized for completeness and psychological modeling accuracy.
        """
        return """
        MATCH (u:User {user_id: $user_id})
        
        // Get recent moments with their connections
        OPTIONAL MATCH (u)-[:HAD_MOMENT]->(m:Moment)
        WHERE m.timestamp > datetime() - duration('P30D')  // Last 30 days
        
        // Get emotions connected to these moments
        OPTIONAL MATCH (e:Emotion)-[felt:FELT_DURING]->(m)
        OPTIONAL MATCH (r:Reflection)-[realized:REALIZED_DURING]->(m)  
        OPTIONAL MATCH (c:Contradiction)-[:EXPERIENCED_TENSION_DURING]->(m)
        
        // Get all emotions for this user (even if not connected to moments)
        OPTIONAL MATCH (e_all:Emotion {user_id: $user_id})
        
        // Get emotional relationships
        OPTIONAL MATCH (e_all)-[co:CO_OCCURS_WITH]->(e2:Emotion)
        OPTIONAL MATCH (e_all)-[trans:TRANSFORMS_INTO]->(e3:Emotion)
        
        // Get all reflections for this user
        OPTIONAL MATCH (r_all:Reflection {user_id: $user_id})
        
        // Get reflection relationships
        OPTIONAL MATCH (r_all)-[builds:BUILDS_ON]->(r2:Reflection)
        OPTIONAL MATCH (r_all)-[challenges:CHALLENGES]->(r3:Reflection)
        OPTIONAL MATCH (r_all)-[inspired:INSPIRED_BY]->(e4:Emotion)
        OPTIONAL MATCH (r_all)-[explains:EXPLAINS]->(e5:Emotion)
        
        // Get values
        OPTIONAL MATCH (u)-[holds:HOLDS_VALUE]->(v:Value)
        OPTIONAL MATCH (v)-[conflicts:CONFLICTS_WITH]->(v2:Value)
        
        // Get patterns
        OPTIONAL MATCH (u)-[:EXHIBITS_PATTERN]->(p:Pattern)
        OPTIONAL MATCH (p)-[manifests:MANIFESTS_AS]->(e6:Emotion)
        
        // Get persona notes
        OPTIONAL MATCH (pn:PersonaNote {user_id: $user_id})
        WHERE pn.created_at > datetime() - duration('P7D')  // Last week's notes
        
        RETURN 
            {
                user_id: u.user_id,
                name: u.name,
                created_at: toString(u.created_at),
                last_active: toString(u.last_active)
            } as u,
            
            // Moments with their emotions/reflections/contradictions
            collect(DISTINCT {
                moment: {
                    id: m.id,
                    timestamp: toString(m.timestamp),
                    context: m.context,
                    user_id: m.user_id,
                    session_id: m.session_id
                },
                emotions: CASE WHEN e IS NOT NULL THEN [{emotion: properties(e), prominence: felt.prominence, trigger: felt.trigger}] ELSE [] END,
                reflections: CASE WHEN r IS NOT NULL THEN [{reflection: properties(r), spontaneity: realized.spontaneity}] ELSE [] END,
                contradictions: CASE WHEN c IS NOT NULL THEN [properties(c)] ELSE [] END
            }) AS moments,
            
            // All emotions with their relationships
            collect(DISTINCT {
                emotion: properties(e_all),
                co_occurs_with: CASE WHEN e2 IS NOT NULL THEN [{emotion: properties(e2), frequency: co.frequency, influence: co.influence_strength}] ELSE [] END,
                transforms_into: CASE WHEN e3 IS NOT NULL THEN [{emotion: properties(e3), duration: trans.duration, trigger: trans.trigger_type}] ELSE [] END
            }) AS emotional_patterns,
            
            // All reflections with their relationships
            collect(DISTINCT {
                reflection: properties(r_all),
                builds_on: CASE WHEN r2 IS NOT NULL THEN [{reflection: properties(r2), connection_type: builds.connection_type}] ELSE [] END,
                challenges: CASE WHEN r3 IS NOT NULL THEN [{reflection: properties(r3), resolution: challenges.resolution_status}] ELSE [] END,
                inspired_by: CASE WHEN e4 IS NOT NULL THEN [{emotion: properties(e4), inspiration_type: inspired.inspiration_type}] ELSE [] END,
                explains: CASE WHEN e5 IS NOT NULL THEN [{emotion: properties(e5), clarity: explains.clarity_level}] ELSE [] END
            }) AS reflective_web,
            
            // Values with conflicts
            collect(DISTINCT {
                value: properties(v),
                strength: holds.strength,
                awareness: holds.awareness_level,
                conflicts_with: CASE WHEN v2 IS NOT NULL THEN [{value: properties(v2), context: conflicts.conflict_context}] ELSE [] END
            }) AS value_system,
            
            // Patterns with manifestations
            collect(DISTINCT {
                pattern: properties(p),
                emotional_manifestations: CASE WHEN e6 IS NOT NULL THEN [{emotion: properties(e6), consistency: manifests.consistency}] ELSE [] END
            }) AS patterns,
            
            // Persona notes
            collect(DISTINCT {
                id: pn.id,
                persona: pn.persona,
                note_type: pn.note_type,
                content: pn.content,
                created_at: toString(pn.created_at),
                user_id: pn.user_id
                         }) AS recent_persona_notes
        """

    @classmethod 
    def get_external_memory_query(cls, user_id: str) -> str:
        """
        Generate a simple Cypher query for external frontend usage (memory sidebar).
        
        This query retrieves basic user memory data optimized for human-readable display.
        Focuses on clear, simple data structures that are easy to render in the UI.
        Avoids complex relationships that might confuse users.
        """
        return """
        MATCH (u:User {user_id: $user_id})
        
        // Get recent moments (last 30 days)
        OPTIONAL MATCH (u)-[:HAD_MOMENT]->(m:Moment)
        WHERE m.timestamp > datetime() - duration('P30D')
        
        // Get all user emotions 
        OPTIONAL MATCH (e_all:Emotion {user_id: $user_id})
        
        // Get all user reflections
        OPTIONAL MATCH (r_all:Reflection {user_id: $user_id})
        
        // Get user values
        OPTIONAL MATCH (u)-[:HOLDS_VALUE]->(v:Value)
        
        // Get user patterns
        OPTIONAL MATCH (u)-[:EXHIBITS_PATTERN]->(p:Pattern)
        
        // Get recent persona notes
        OPTIONAL MATCH (pn:PersonaNote {user_id: $user_id})
        WHERE pn.created_at > datetime() - duration('P7D')
        
        WITH u, m, e_all, r_all, v, p, pn
        
        RETURN 
            // User info
            {
                user_id: u.user_id,
                name: u.name,
                created_at: toString(u.created_at),
                last_active: toString(u.last_active)
            } as user,
            
            // Moments (simplified) - filter out nulls
            [x IN collect(DISTINCT m) WHERE x IS NOT NULL | {
                id: x.id,
                timestamp: toString(x.timestamp),
                context: x.context,
                session_id: x.session_id
            }] as moments,
            
            // All emotions - filter out nulls
            [x IN collect(DISTINCT e_all) WHERE x IS NOT NULL | {
                id: x.id,
                label: x.label,
                intensity: x.intensity,
                nuance: x.nuance,
                bodily_sensation: x.bodily_sensation
            }] as emotions,
            
            // All reflections - filter out nulls  
            [x IN collect(DISTINCT r_all) WHERE x IS NOT NULL | {
                id: x.id,
                content: x.content,
                insight_type: x.insight_type,
                depth_level: x.depth_level,
                confidence: x.confidence
            }] as reflections,
            
            // Values - filter out nulls
            [x IN collect(DISTINCT v) WHERE x IS NOT NULL | {
                id: x.id,
                name: x.name,
                description: x.description,
                importance: x.importance
            }] as values,
            
            // Patterns - filter out nulls
            [x IN collect(DISTINCT p) WHERE x IS NOT NULL | {
                id: x.id,
                description: x.description,
                pattern_type: x.pattern_type,
                frequency: x.frequency
            }] as patterns,
            
            // Recent notes - filter out nulls
            [x IN collect(DISTINCT pn) WHERE x IS NOT NULL | {
                id: x.id,
                persona: x.persona,
                note_type: x.note_type,
                content: x.content,
                created_at: toString(x.created_at)
            }] as notes
        """


# Schema instance for import
sage_schema = SageSchema() 