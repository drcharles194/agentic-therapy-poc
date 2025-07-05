"""
Intelligent Memory Analyzer Service

Uses Claude to analyze conversations and propose memory updates
for reflections, emotions, and insights worth storing.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from backend.services.anthropic_service import anthropic_service

logger = logging.getLogger(__name__)


class MemoryAnalyzer:
    """Analyzes conversations to propose intelligent memory updates."""
    
    def __init__(self):
        self.analysis_prompt_template = """
You are a memory analyst for the Sage therapeutic AI system. Your job is to analyze conversations and identify what's worth storing in the user's memory graph.

Review this conversation and identify:

1. **REFLECTIONS**: Deep insights, realizations, or meaningful thoughts from the user that reveal something important about their inner world
2. **EMOTIONS**: Clear emotional states expressed by the user (not assumptions)  
3. **SELF-KINDNESS**: Moments where the user was compassionate to themselves
4. **CONTRADICTIONS**: Value tensions or conflicting desires/beliefs the user expressed

Only propose storing content that is:
- Explicitly expressed by the user (not inferred)
- Meaningful enough to inform future therapeutic conversations
- Respectful of the user's privacy and autonomy

User Message: "{user_message}"
Sage Response: "{sage_response}"

IMPORTANT: Be selective. Not every conversation needs memory storage. Only store content that would genuinely help Sage provide better therapeutic support in future conversations.

Respond in this exact JSON format:
{{
  "should_store": true/false,
  "reflections": [
    {{
      "content": "user's exact words or paraphrased insight",
      "significance": "why this reflection is therapeutically valuable",
      "source": "user"
    }}
  ],
  "emotions": [
    {{
      "label": "anxiety/sadness/joy/etc",
      "intensity": 0.1-1.0,
      "evidence": "what in their words suggests this emotion"
    }}
  ],
  "self_kindness_events": [
    {{
      "description": "specific self-compassionate action or thought",
      "evidence": "user's words that show this"
    }}
  ],
  "contradictions": [
    {{
      "summary": "brief description of the value tension",
      "details": "the conflicting desires/beliefs expressed"
    }}
  ],
  "reasoning": "brief explanation of storage decisions"
}}
"""

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
            # Create analysis prompt
            analysis_prompt = self.analysis_prompt_template.format(
                user_message=user_message,
                sage_response=sage_response
            )
            
            # Get Claude's analysis
            analysis_response = await anthropic_service.generate_sage_response(
                analysis_prompt, 
                "Please analyze this conversation for memory storage."
            )
            
            # Parse the JSON response
            import json
            import re
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
        Convert analysis results into memory update proposals.
        
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
        
        # Create reflection proposals
        for reflection in analysis.get("reflections", []):
            reflection_id = str(uuid.uuid4())
            proposals.append({
                "update_type": "reflection",
                "data": {
                    "id": reflection_id,
                    "content": reflection["content"],
                    "timestamp": timestamp,
                    "archived": False,
                    "source": reflection.get("source", "user"),
                    "agent_origin": None,
                    "user_id": user_id,
                    "significance": reflection.get("significance", "")
                }
            })
            
            # If there are insights about this reflection, create persona notes
            if reflection.get("significance"):
                proposals.append({
                    "update_type": "persona_note",
                    "data": {
                        "reflection_id": reflection_id,
                        "type": "observation",
                        "content": f"Therapeutic significance: {reflection['significance']}",
                        "user_id": user_id
                    }
                })
        
        # Create emotion proposals
        for emotion in analysis.get("emotions", []):
            proposals.append({
                "update_type": "emotion",
                "data": {
                    "label": emotion["label"],
                    "intensity": emotion.get("intensity", 0.5),
                    "timestamp": timestamp,
                    "archived_at": None,
                    "user_id": user_id,
                    "evidence": emotion.get("evidence", "")
                }
            })
        
        # Create self-kindness proposals
        for kindness in analysis.get("self_kindness_events", []):
            proposals.append({
                "update_type": "self_kindness",
                "data": {
                    "description": kindness["description"],
                    "timestamp": timestamp,
                    "user_id": user_id,
                    "evidence": kindness.get("evidence", "")
                }
            })
        
        # Create contradiction proposals
        for contradiction in analysis.get("contradictions", []):
            proposals.append({
                "update_type": "contradiction",
                "data": {
                    "summary": contradiction["summary"],
                    "details": contradiction.get("details", ""),
                    "user_id": user_id
                }
            })
        
        logger.info(f"Created {len(proposals)} memory proposals for user {user_id}")
        return proposals


# Global service instance
memory_analyzer = MemoryAnalyzer() 