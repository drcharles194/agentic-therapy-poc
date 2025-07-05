"""
Core agent logic for the Sage persona (The Nurturer).
"""
import logging
from typing import Dict, Any
from jinja2 import Template
from pathlib import Path

from backend.personas.sage.memory import get_user_context
from backend.services.anthropic_service import anthropic_service
from backend.services.memory_analyzer import memory_analyzer
from backend.services.neo4j import neo4j_service
from backend.config import settings

logger = logging.getLogger(__name__)


class SageHandler:
    """Handler for the Sage persona - warm, non-directive, supportive."""
    
    def __init__(self):
        """Initialize the Sage handler with prompt template."""
        self.persona_name = "Sage"
        self.prompt_template = self._load_prompt_template()
        self.enable_intelligent_memory = True  # Feature flag for memory intelligence
    
    def _load_prompt_template(self) -> Template:
        """Load the Jinja2 prompt template for Sage."""
        template_path = Path(__file__).parent / "prompt.j2"
        
        if not template_path.exists():
            logger.warning(f"Prompt template not found at {template_path}, using default")
            # Fallback template if file doesn't exist yet
            default_template = """
You are Sage, the nurturing presence in the Collaborative ecosystem. 
You hold space for users to reflect gently on their emotional world. 
Do not advise or instruct. Mirror and validate.

{% if user_context %}
User Context:
- Name: {{ user_context.user_name or "Friend" }}
{% if user_context.sage.reflections %}
- Recent reflections: {{ user_context.sage.reflections[-3:] | map(attribute='content') | join(', ') }}
{% endif %}
{% if user_context.sage.emotions %}
- Current emotions: {{ user_context.sage.emotions | map(attribute='label') | join(', ') }}
{% endif %}
{% if user_context.sage.contradictions %}
- Value tensions: {{ user_context.sage.contradictions | map(attribute='summary') | join('; ') }}
{% endif %}
{% endif %}

User message: {{ user_message }}

Respond with warmth and gentle curiosity. Help them explore what's beneath the surface.
            """.strip()
            return Template(default_template)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return Template(template_content)
    
    async def generate_response(self, user_id: str, user_message: str) -> str:
        """
        Generate a Sage response for the given user message.
        
        Args:
            user_id: User identifier
            user_message: The user's input message
            
        Returns:
            Sage's response as a string
        """
        logger.info(f"Generating Sage response for user {user_id}")
        
        try:
            # Get user context from memory
            user_context = await get_user_context(user_id)
            
            # Render the prompt with context
            rendered_prompt = self.prompt_template.render(
                user_context=user_context,
                user_message=user_message
            )
            
            logger.debug(f"Rendered prompt for user {user_id}: {rendered_prompt[:100]}...")
            
            # Use Anthropic service to generate response
            response = await anthropic_service.generate_sage_response(rendered_prompt, user_message)
            
            # Intelligent Memory Processing
            if self.enable_intelligent_memory:
                logger.info(f"Starting intelligent memory processing for user {user_id}")
                try:
                    await self._process_intelligent_memory(user_id, user_message, response)
                    logger.info(f"Intelligent memory processing completed for user {user_id}")
                except Exception as e:
                    logger.error(f"Memory processing failed for user {user_id}: {e}")
                    import traceback
                    logger.error(f"Memory processing traceback: {traceback.format_exc()}")
                    # Continue without failing the response
            else:
                logger.info(f"Intelligent memory disabled for user {user_id}")
            
            logger.info(f"Generated Sage response for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating Sage response for user {user_id}: {e}")
            # Fallback response
            return "I'm here with you. Sometimes words feel hard to find, and that's okay too."

    async def _process_intelligent_memory(self, user_id: str, user_message: str, sage_response: str):
        """
        Use AI to analyze the conversation and intelligently store meaningful content.
        
        Args:
            user_id: User identifier
            user_message: User's message
            sage_response: Sage's generated response
        """
        logger.info(f"Processing intelligent memory for user {user_id}")
        
        try:
            # Analyze conversation with Claude
            analysis = await memory_analyzer.analyze_conversation(
                user_id=user_id,
                user_message=user_message,
                sage_response=sage_response
            )
            
            # Check if Claude thinks anything should be stored
            if not analysis.get("should_store", False):
                logger.info(f"Claude determined no memory storage needed for user {user_id}: {analysis.get('reasoning', 'No reason given')}")
                return
            
            # Create memory proposals from analysis
            proposals = memory_analyzer.create_memory_proposals(analysis)
            
            if not proposals:
                logger.info(f"No memory proposals generated for user {user_id}")
                return
            
            # Process each proposal through governance
            approved_count = 0
            for proposal in proposals:
                # Apply governance rules
                if self._validate_memory_proposal(proposal):
                    # Store in Neo4j
                    success = await neo4j_service.process_memory_proposal(user_id, proposal)
                    if success:
                        approved_count += 1
                    else:
                        logger.warning(f"Failed to store memory proposal: {proposal['update_type']}")
                else:
                    logger.info(f"Memory proposal rejected by governance: {proposal['update_type']}")
            
            logger.info(f"Intelligent memory processing complete for user {user_id}: {approved_count}/{len(proposals)} proposals approved")
            
        except Exception as e:
            logger.error(f"Error in intelligent memory processing for user {user_id}: {e}")
            # Don't let memory failures break the conversation

    def _validate_memory_proposal(self, proposal: Dict[str, Any]) -> bool:
        """
        Apply governance rules to validate memory proposals.
        Following the "any criteria met" approach from Memory Interaction Architecture.
        
        Args:
            proposal: Memory proposal to validate
            
        Returns:
            bool: True if proposal should be approved
        """
        update_type = proposal.get("update_type")
        data = proposal.get("data", {})
        
        # Storage criteria - if ANY are met, store the memory
        criteria = {
            'emotional_significance': False,
            'therapeutic_value': False,
            'user_growth': False,
            'unique_insight': True,  # Assume unique unless proven duplicate
            'privacy_safe': True     # Assume safe unless proven otherwise
        }
        
        if update_type == "reflection":
            content = data.get("content", "").strip()
            # Reject only truly empty content or spam
            if len(content) < 3:
                return False
            # Basic privacy check - reject if contains obvious sensitive info
            sensitive_patterns = ["ssn", "social security", "credit card", "password", "phone number"]
            if any(pattern in content.lower() for pattern in sensitive_patterns):
                criteria['privacy_safe'] = False
            else:
                criteria['therapeutic_value'] = True  # All reflections have therapeutic value
                # Check for emotional significance
                emotion_words = ["feel", "felt", "emotion", "hurt", "pain", "joy", "sad", "angry", "afraid", "anxious", "hopeful"]
                if any(word in content.lower() for word in emotion_words):
                    criteria['emotional_significance'] = True
                
        elif update_type == "emotion":
            label = data.get("label", "").strip()
            intensity = data.get("intensity", 0)
            # Very permissive - store any detected emotion
            if label and intensity > 0:
                criteria['emotional_significance'] = True
                criteria['therapeutic_value'] = True
                # Only reject if obviously invalid
                if intensity > 1.0 or len(label) < 2:
                    return False
                
        elif update_type == "self_kindness":
            description = data.get("description", "").strip()
            # Any self-kindness is therapeutically valuable
            if len(description) >= 3:
                criteria['user_growth'] = True
                criteria['therapeutic_value'] = True
                
        elif update_type == "contradiction":
            summary = data.get("summary", "").strip()
            # Contradictions show important internal conflicts
            if len(summary) >= 5:
                criteria['therapeutic_value'] = True
                criteria['emotional_significance'] = True
                
        elif update_type == "persona_note":
            content = data.get("content", "").strip()
            # Therapeutic notes are always valuable
            if len(content) >= 3:
                criteria['therapeutic_value'] = True
        
        # Store if ANY criteria met and privacy is safe
        should_store = criteria['privacy_safe'] and any([
            criteria['emotional_significance'],
            criteria['therapeutic_value'], 
            criteria['user_growth'],
            criteria['unique_insight']
        ])
        
        if not should_store:
            logger.debug(f"Memory proposal rejected - criteria: {criteria}")
        else:
            logger.debug(f"Memory proposal approved - criteria: {criteria}")
            
        return should_store


# Global instance
sage_handler = SageHandler() 