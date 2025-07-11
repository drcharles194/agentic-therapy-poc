"""
Anthropic Claude API service for generating Sage responses.
"""
import logging
from typing import Dict, Any, Optional

import anthropic

from backend.config import settings

logger = logging.getLogger(__name__)


class AnthropicService:
    """Anthropic Claude API service for generating persona responses."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Anthropic client."""
        try:
            if settings.anthropic_api_key and settings.anthropic_api_key != "test_key":
                self.client = anthropic.Anthropic(
                    api_key=settings.anthropic_api_key
                )
                logger.info("Anthropic Claude client initialized")
            else:
                logger.warning("Anthropic API key not configured - falling back to mock responses")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.client = None
    
    async def generate_sage_response(self, rendered_prompt: str, user_message: str) -> str:
        """
        Generate a Sage response using Claude API.
        
        Args:
            rendered_prompt: The complete system prompt with user context
            user_message: The user's current message
            
        Returns:
            Claude's response as Sage
        """
        if not self.client:
            logger.warning("Anthropic client not available - using fallback response")
            return self._generate_fallback_response(user_message)
        
        try:
            # Create the messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            
            # Detect if this is a memory analysis task and adjust token limits accordingly
            is_memory_analysis = (
                "analyze this conversation for memory storage" in user_message.lower() or
                "respond in this exact json format" in rendered_prompt.lower() or
                "should_store" in rendered_prompt.lower()
            )
            
            max_tokens = 2000 if is_memory_analysis else 500
            temperature = 0.3 if is_memory_analysis else 0.8  # Lower temperature for JSON structure
            
            # Generate response using the direct Anthropic client
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                temperature=temperature,
                system=rendered_prompt,
                messages=messages
            )
            
            # Extract the response text
            sage_response = response.content[0].text.strip()
            
            # For non-memory analysis, ensure response follows Sage guidelines
            if not is_memory_analysis:
                sage_response = self._ensure_sage_tone(sage_response)
            
            # Log successful API call
            total_chars = len(rendered_prompt) + len(user_message) + len(sage_response)
            analysis_type = "memory analysis" if is_memory_analysis else "Sage response"
            logger.info(f"Claude API call ({analysis_type}) - Input: {len(rendered_prompt + user_message)} chars, Output: {len(sage_response)} chars, Max tokens: {max_tokens}")
            
            return sage_response
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            return self._generate_fallback_response(user_message)
    
    def _ensure_sage_tone(self, response: str) -> str:
        """Ensure the response maintains Sage's gentle, non-directive tone."""
        # Remove common directive phrases that might slip through
        directive_patterns = [
            ("You should", "You might find"),
            ("You need to", "You could explore"),
            ("You must", "You might consider"),
            ("I recommend", "I wonder if"),
            ("Try this", "What if you"),
            ("Here's what you should do", "What feels right for you"),
        ]
        
        filtered_response = response
        for directive, gentle in directive_patterns:
            if directive.lower() in filtered_response.lower():
                filtered_response = filtered_response.replace(directive, gentle)
                logger.debug(f"Softened directive language: {directive} -> {gentle}")
        
        return filtered_response
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate a fallback response when Claude API is unavailable."""
        logger.info("Using fallback response generation")
        
        # Simple pattern-based responses (same as mock system)
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
    
    async def health_check(self) -> Dict[str, str]:
        """Check Anthropic service health."""
        try:
            if not self.client:
                return {
                    "status": "unavailable", 
                    "message": f"API key not configured (current: {settings.anthropic_api_key[:8]}...)"
                }
            
            # Test with a simple prompt
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                temperature=0.1,
                system="You are a helpful assistant. Respond with exactly 'OK' to confirm you're working.",
                messages=[{"role": "user", "content": "Test connection"}]
            )
            
            response_text = response.content[0].text.strip()
            
            if response_text:
                return {"status": "healthy", "message": f"Claude API responding (test: {response_text[:20]}...)"}
            else:
                return {"status": "unhealthy", "message": "Empty response from Claude API"}
                
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        if not self.client:
            return {"model": "fallback", "status": "unavailable"}
        
        return {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500,
            "temperature": 0.8,
            "status": "configured"
        }


# Global service instance
anthropic_service = AnthropicService() 