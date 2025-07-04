"""
Core agent logic for the Sage persona (The Nurturer).
"""
import logging
from typing import Dict, Any
from jinja2 import Template
from pathlib import Path

from backend.personas.sage.memory import get_user_context
from backend.config import settings

logger = logging.getLogger(__name__)


class SageHandler:
    """Handler for the Sage persona - warm, non-directive, supportive."""
    
    def __init__(self):
        """Initialize the Sage handler with prompt template."""
        self.persona_name = "Sage"
        self.prompt_template = self._load_prompt_template()
    
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
            
            # TODO: Integrate with LangChain + Anthropic Claude
            # For now, return a simple Sage-like response
            response = self._generate_mock_sage_response(user_message, user_context)
            
            logger.info(f"Generated Sage response for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating Sage response for user {user_id}: {e}")
            # Fallback response
            return "I'm here with you. Sometimes words feel hard to find, and that's okay too."
    
    def _generate_mock_sage_response(self, user_message: str, user_context: Dict[str, Any]) -> str:
        """Generate a mock Sage response until LangChain integration is complete."""
        
        # Simple response patterns based on message content
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['overwhelmed', 'stressed', 'anxious']):
            return ("That sounds like a lot to carry right now. "
                   "What would it feel like to set one small thing down, just for a moment?")
        
        elif any(word in message_lower for word in ['sad', 'sadness', 'grief', 'loss']):
            return ("I can feel the weight of that sadness. "
                   "Sadness often holds such important truths. What is yours telling you?")
        
        elif any(word in message_lower for word in ['stuck', 'trapped', 'can\'t move']):
            return ("Being stuck can feel so heavy. Sometimes the way forward "
                   "isn't about moving at all, but about understanding what's holding us. "
                   "What do you sense beneath that stuckness?")
        
        elif any(word in message_lower for word in ['angry', 'frustrated', 'mad']):
            return ("That anger has something to say. Anger often protects something tender underneath. "
                   "What might it be guarding for you?")
        
        else:
            # General reflective response
            return (f"I hear you saying: '{user_message}'. "
                   "That sounds like something that carries weight for you. "
                   "Would you like to explore what's beneath the surface?")


# Global instance
sage_handler = SageHandler() 