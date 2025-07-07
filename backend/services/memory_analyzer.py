"""
Intelligent Memory Analyzer Service

Uses Claude to analyze conversations and propose memory updates
for reflections, emotions, and insights worth storing.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
import re

from backend.services.anthropic_service import anthropic_service
from backend.services.neo4j import neo4j_service

logger = logging.getLogger(__name__)


class MemoryAnalyzer:
    """Analyzes conversations to propose intelligent memory updates."""
    
    def __init__(self):
        """Initialize the MemoryAnalyzer."""
        pass

    def _extract_moment_context(self, user_message: str) -> str:
        """Extract meaningful context from user message for moment description."""
        if not user_message:
            return "General conversation"
        
        # Truncate very long messages
        if len(user_message) > 100:
            user_message = user_message[:100] + "..."
        
        # Clean up the message for context
        context = user_message.strip()
        
        # If the message starts with common conversational patterns, extract the key part
        if context.lower().startswith(("i feel", "i'm feeling", "i am feeling")):
            return f"Expressing feelings: {context}"
        elif context.lower().startswith(("i think", "i'm thinking", "i am thinking")):
            return f"Sharing thoughts: {context}"
        elif context.lower().startswith(("i want", "i'm wanting", "i need")):
            return f"Discussing needs/wants: {context}"
        elif context.lower().startswith(("my", "i have", "i had")):
            return f"Personal experience: {context}"
        elif "?" in context:
            return f"Seeking guidance: {context}"
        else:
            return f"Discussion: {context}"
    
    def _create_contextual_analysis_prompt(self, user_message: str, sage_response: str, existing_memory: Dict[str, Any]) -> str:
        """Create analysis prompt with existing memory context to prevent duplicates."""
        
        # Extract existing data for context
        existing_emotions = existing_memory.get("sage", {}).get("emotions", [])
        existing_reflections = existing_memory.get("sage", {}).get("reflections", [])
        existing_values = existing_memory.get("sage", {}).get("values", [])
        existing_patterns = existing_memory.get("sage", {}).get("patterns", [])
        existing_contradictions = existing_memory.get("sage", {}).get("contradictions", [])
        
        # Build context strings
        emotion_context = ""
        if existing_emotions:
            recent_emotions = [f"- {e.get('label', 'Unknown emotion')} ({e.get('intensity', 0.5):.1f})" for e in existing_emotions[-5:]]
            emotion_context = f"""
EXISTING EMOTIONS (last 5):
{chr(10).join(recent_emotions)}
"""

        reflection_context = ""
        if existing_reflections:
            recent_reflections = [f"- {r.get('content', 'Reflection without content')[:100]}..." for r in existing_reflections[-3:]]
            reflection_context = f"""
EXISTING REFLECTIONS (last 3):
{chr(10).join(recent_reflections)}
"""

        values_context = ""
        if existing_values:
            recent_values = [f"- {v.get('name', 'Unnamed value')}: {v.get('description', '')[:60]}..." for v in existing_values[-3:]]
            values_context = f"""
EXISTING VALUES (last 3):
{chr(10).join(recent_values)}
"""

        patterns_context = ""
        if existing_patterns:
            recent_patterns = [f"- {p.get('description', 'Pattern without description')[:80]}..." for p in existing_patterns[-3:]]
            patterns_context = f"""
EXISTING PATTERNS (last 3):
{chr(10).join(recent_patterns)}
"""

        contradiction_context = ""
        if existing_contradictions:
            recent_contradictions = [f"- {c.get('summary', 'Contradiction without summary')[:80]}..." for c in existing_contradictions[-3:]]
            contradiction_context = f"""
EXISTING CONTRADICTIONS:
{chr(10).join(recent_contradictions)}
"""

        # Create enhanced prompt
        contextual_prompt = f"""
You are a memory analyst for the Sage therapeutic AI system. Your job is to analyze conversations and identify what's worth storing in the user's memory graph.

CRITICAL: Review the user's EXISTING MEMORY below to avoid duplicates and identify new insights:

{emotion_context}{reflection_context}{values_context}{patterns_context}{contradiction_context}

## DEDUPLICATION RULES:
1. **EMOTIONS**: Only store if significantly different from recent emotions or if intensity changed notably
2. **REFLECTIONS**: Only store genuinely new insights, not variations of existing ones
3. **VALUES**: Only store newly revealed or clarified core values, not variations of existing ones
4. **PATTERNS**: Only store newly identified recurring patterns, not variations of existing ones
5. **CONTRADICTIONS**: Only store if revealing new value tensions not already captured

## CURRENT CONVERSATION:
User Message: "{user_message}"
Sage Response: "{sage_response}"

Review this conversation and identify ONLY NEW content worth storing:

1. **MOMENT TITLE**: Create a concise, therapeutic title that captures the essence of this conversation moment (3-6 words)
2. **REFLECTIONS**: Deep insights, realizations, or meaningful thoughts that are genuinely new
3. **EMOTIONS**: Clear emotional states that are new or show significant intensity changes
4. **VALUES**: Core values, principles, or what matters most to the user (newly revealed or clarified)
5. **PATTERNS**: Recurring behavioral, emotional, or thought patterns (newly identified)
6. **CONTRADICTIONS**: New value tensions or conflicts not already identified

## MOMENT TITLE GUIDELINES:
- Keep it therapeutic and meaningful (e.g., "Grief after father's death", "Workplace boundary setting", "Self-doubt about relationships")
- Focus on the core emotional/psychological theme
- Use clinical but compassionate language
- Avoid raw quotes; use descriptive, professional phrasing

### EMOTIONS (if any)  
- Must be specific emotions with clear evidence
- Include precise intensity (0.1-1.0) based on user's words
- Example: "anxiety" with intensity 0.8 because user said "I'm terrified of making the wrong choice"
- NOT generic emotions without supporting evidence

### VALUES (if any)
- Must be core values explicitly expressed or clearly implied
- Include specific description of what this value means to the user
- Example: "family" - "Being present and supportive for my children is my highest priority"
- NOT inferred values without clear evidence

### PATTERNS (if any)
- Must be recurring behaviors/thoughts with specific description
- Include frequency and clear behavioral description
- Example: "I consistently avoid difficult conversations by changing the subject or making jokes, especially when emotions get intense"
- NOT vague patterns like "avoids things" or "gets stressed"

### CONTRADICTIONS (if any)
- Must show clear tension between two specific values/desires
- Include detailed explanation of the conflict
- Example: "Wants independence but constantly seeks approval from others for major decisions"
- NOT general conflicts without specifics

**STRICT RULES:**
- If you cannot provide substantial, meaningful content for a category, DO NOT include it
- Empty or minimal responses will be rejected
- Be selective - quality over quantity
- Only store content that adds genuine therapeutic value beyond what's already known
- Explicitly expressed by the user (not inferred)
- Genuinely NEW or significantly different from existing memories
- Respectful of the user's privacy and autonomy

Respond in this exact JSON format:
{{
  "should_store": true/false,
  "moment_title": "Therapeutic title (3-6 words): focus on core emotional/psychological theme, use clinical but compassionate language",
  "reflections": [
    {{
      "content": "user's exact words or paraphrased insight",
      "significance": "why this reflection is therapeutically valuable AND new",
      "source": "user"
    }}
  ],
  "emotions": [
    {{
      "label": "anxiety/sadness/joy/etc",
      "intensity": 0.1-1.0,
      "evidence": "what in their words suggests this emotion",
      "why_new": "why this emotion observation is different from existing ones"
    }}
  ],
  "values": [
    {{
      "name": "core value name (e.g., 'family', 'autonomy', 'authenticity')",
      "description": "what this value means to the user",
      "importance": 0.1-1.0,
      "evidence": "user's words that reveal this value",
      "why_new": "why this value identification is new or newly clarified"
    }}
  ],
  "patterns": [
    {{
      "description": "clear description of the recurring pattern",
      "pattern_type": "behavioral/emotional/cognitive",
      "frequency": "frequent/occasional/rare",
      "evidence": "user's words that show this pattern",
      "why_new": "why this pattern identification is new"
    }}
  ],
  "contradictions": [
    {{
      "summary": "clear description of the value tension",
      "details": "detailed explanation of the conflicting desires/beliefs",
      "why_new": "why this tension is different from existing contradictions"
    }}
  ],
  "reasoning": "brief explanation of storage decisions with reference to existing memory"
}}
"""

        return contextual_prompt

    async def analyze_conversation(
        self, 
        user_id: str, 
        user_message: str, 
        sage_response: str
    ) -> Dict[str, Any]:
        """
        Analyze a conversation to propose memory updates.
        
        Args:
            user_id: User identifier
            user_message: The user's message
            sage_response: Sage's response
            
        Returns:
            Analysis results with proposed memory updates
        """
        logger.info(f"Analyzing conversation for memory storage: user {user_id}")
        
        try:
            # Get existing user memory to inform analysis
            existing_memory = await neo4j_service.get_user_memory(user_id)
            
            # Create analysis prompt with existing context
            analysis_prompt = self._create_contextual_analysis_prompt(
                user_message, sage_response, existing_memory
            )
            
            # Get Claude's analysis
            analysis_response = await anthropic_service.generate_sage_response(
                analysis_prompt, 
                "Please analyze this conversation for memory storage."
            )
            
            # Parse the JSON response
            try:
                # Strip markdown code blocks if present
                clean_response = analysis_response.strip()
                if clean_response.startswith('```json'):
                    clean_response = re.sub(r'^```json\s*', '', clean_response)
                if clean_response.endswith('```'):
                    clean_response = re.sub(r'\s*```$', '', clean_response)
                elif clean_response.startswith('```'):
                    clean_response = re.sub(r'^```\s*', '', clean_response)
                
                analysis_data = json.loads(clean_response.strip())
                
                # Debug log the structure for troubleshooting
                logger.debug(f"Claude analysis keys for user {user_id}: {list(analysis_data.keys())}")
                if analysis_data.get("should_store"):
                    counts = {
                        "moments": 1,  # Always create one moment
                        "reflections": len(analysis_data.get("reflections", [])),
                        "emotions": len(analysis_data.get("emotions", [])),
                        "values": len(analysis_data.get("values", [])),
                        "patterns": len(analysis_data.get("patterns", [])),
                        "contradictions": len(analysis_data.get("contradictions", []))
                    }
                    logger.debug(f"Claude proposed memory counts for user {user_id}: {counts}")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse analysis JSON: {e}. Raw response: {analysis_response[:200]}...")
                return {"should_store": False, "reasoning": "Failed to parse analysis"}
            
            # Add metadata
            analysis_data["user_id"] = user_id
            analysis_data["timestamp"] = datetime.utcnow().isoformat()
            analysis_data["conversation"] = {
                "user_message": user_message,
                "sage_response": sage_response
            }
            
            logger.info(f"Memory analysis completed for user {user_id}: should_store={analysis_data.get('should_store')}")
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error analyzing conversation for user {user_id}: {e}")
            return {
                "should_store": False,
                "reasoning": f"Analysis failed: {str(e)}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    def create_memory_proposals(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert analysis results into memory update proposals using the new complex schema.
        
        Args:
            analysis: Results from analyze_conversation
            
        Returns:
            List of memory update proposals
        """
        if not analysis.get("should_store", False):
            return []
        
        proposals = []
        user_id = analysis["user_id"]
        timestamp = analysis["timestamp"]
        
        # Create a unique session ID for this conversation
        session_id = f"session_{int(datetime.now().timestamp())}_{user_id.split('_')[-1]}"
        
        # Always create a moment for this interaction
        moment_id = str(uuid.uuid4())
        
        # Use AI-generated moment title, or fallback to extracted context
        moment_title = analysis.get("moment_title")
        if not moment_title:
            # Fallback to extracted context if AI didn't provide a title
            user_message = analysis.get("conversation", {}).get("user_message", "")
            moment_title = self._extract_moment_context(user_message)
        
        proposals.append({
            "update_type": "moment",
            "data": {
                "id": moment_id,
                "timestamp": timestamp,
                "context": moment_title,
                "user_id": user_id,
                "session_id": session_id
            }
        })
        
        # Create reflection proposals with new schema
        for reflection in analysis.get("reflections", []):
            # Skip if missing essential content
            if not reflection.get("content"):
                logger.warning(f"Skipping reflection proposal with missing content for user {user_id}")
                continue
                
            reflection_id = str(uuid.uuid4())
            proposals.append({
                "update_type": "reflection",
                "data": {
                    "id": reflection_id,
                    "content": reflection.get("content", ""),
                    "insight_type": "realization",
                    "depth_level": 2,  # Therapist-validated insights are deeper
                    "confidence": 0.8,  # High confidence from Claude analysis
                    "user_id": user_id,
                    "moment_id": moment_id,
                    "significance": reflection.get("significance", "")
                }
            })
            
            # If there are insights about this reflection, create persona notes
            if reflection.get("significance"):
                proposals.append({
                    "update_type": "persona_note",
                    "data": {
                        "id": str(uuid.uuid4()),
                        "persona": "Sage",
                        "note_type": "observation",
                        "content": f"Therapeutic significance: {reflection['significance']}",
                        "user_id": user_id,
                        "reflection_id": reflection_id
                    }
                })
        
        # Create emotion proposals with new schema
        for emotion in analysis.get("emotions", []):
            # Skip if missing essential label
            if not emotion.get("label"):
                logger.warning(f"Skipping emotion proposal with missing label for user {user_id}")
                continue
                
            proposals.append({
                "update_type": "emotion",
                "data": {
                    "id": str(uuid.uuid4()),
                    "label": emotion.get("label", "unknown"),
                    "intensity": emotion.get("intensity", 0.5),
                    "nuance": emotion.get("evidence", "Detected in therapeutic conversation"),
                    "bodily_sensation": "unspecified",
                    "user_id": user_id,
                    "moment_id": moment_id
                }
            })
        
        # Create contradiction proposals with new schema
        for contradiction in analysis.get("contradictions", []):
            # Skip if missing essential summary
            if not contradiction.get("summary"):
                logger.warning(f"Skipping contradiction proposal with missing summary for user {user_id}")
                continue
                
            proposals.append({
                "update_type": "contradiction",
                "data": {
                    "id": str(uuid.uuid4()),
                    "summary": contradiction.get("summary", ""),
                    "tension_type": "values",  # Default to values tension
                    "intensity": 0.6,  # Medium intensity by default
                    "user_id": user_id,
                    "moment_id": moment_id,
                    "details": contradiction.get("details", "")
                }
            })
        
        # Create value proposals with new schema
        for value in analysis.get("values", []):
            # Skip if missing essential name
            if not value.get("name"):
                logger.warning(f"Skipping value proposal with missing name for user {user_id}")
                continue
                
            proposals.append({
                "update_type": "value",
                "data": {
                    "id": str(uuid.uuid4()),
                    "name": value.get("name", ""),
                    "description": value.get("description", ""),
                    "importance": value.get("importance", 0.7),
                    "strength": 0.8,  # New values are typically strongly held
                    "awareness_level": 0.9,  # Explicitly stated values have high awareness
                    "user_id": user_id,
                    "evidence": value.get("evidence", "")
                }
            })
        
        # Create pattern proposals with new schema
        for pattern in analysis.get("patterns", []):
            # Skip if missing essential description
            if not pattern.get("description"):
                logger.warning(f"Skipping pattern proposal with missing description for user {user_id}")
                continue
                
            proposals.append({
                "update_type": "pattern",
                "data": {
                    "id": str(uuid.uuid4()),
                    "description": pattern.get("description", ""),
                    "pattern_type": pattern.get("pattern_type", "behavioral"),
                    "frequency": pattern.get("frequency", "occasional"),
                    "user_id": user_id,
                    "evidence": pattern.get("evidence", "")
                }
            })
        
        logger.info(f"Created {len(proposals)} complex memory proposals for user {user_id}")
        return proposals


# Global service instance
memory_analyzer = MemoryAnalyzer() 