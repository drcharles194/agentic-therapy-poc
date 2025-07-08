"""
Shared utilities for GraphRAG implementations.

This module contains common functionality used by both custom and official
GraphRAG services to ensure consistency and reduce code duplication.
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def index_name_to_friendly(index_name: str) -> str:
    """Convert technical index names to user-friendly display names."""
    friendly_names = {
        "therapy_moments_index": "Therapy Moments",
        "user_reflections_index": "User Reflections", 
        "therapist_notes_index": "Therapist Notes",
        "behavior_patterns_index": "Behavior Patterns",
        "user_values_index": "User Values"
    }
    return friendly_names.get(index_name, index_name.replace('_index', '').replace('_', ' ').title())


def calculate_dynamic_confidence(
    results: List[Dict], 
    available_indexes: Dict[str, int] = None,
    implementation_type: str = "custom"
) -> float:
    """
    Calculate dynamic confidence based on results quality and data availability.
    
    Args:
        results: List of results from GraphRAG queries
        available_indexes: Dict mapping index names to content counts (for custom implementation)
        implementation_type: "custom" or "official" to adjust calculation method
        
    Returns:
        Confidence score between 0.1 and 0.95
    """
    if not results:
        return 0.1
    
    num_sources = len(results)
    
    # Base confidence calculation
    if implementation_type == "custom" and available_indexes:
        # Custom implementation: factor in coverage ratio
        total_available = len(available_indexes)
        coverage_ratio = num_sources / max(total_available, 1)
        
        if coverage_ratio >= 0.8:  # 4/5 or 3/4 indexes
            base_confidence = 0.85
        elif coverage_ratio >= 0.6:  # 3/5 indexes
            base_confidence = 0.75
        elif coverage_ratio >= 0.4:  # 2/5 indexes
            base_confidence = 0.65
        else:  # 1 index
            base_confidence = 0.55
    else:
        # Official implementation: based on absolute number of sources
        if num_sources >= 4:
            base_confidence = 0.85
        elif num_sources == 3:
            base_confidence = 0.75  
        elif num_sources == 2:
            base_confidence = 0.65
        else:
            base_confidence = 0.55
    
    # Quality assessment based on response content
    quality_bonus = 0.0
    
    # Calculate average response length
    if implementation_type == "custom":
        # Custom uses 'response' field
        total_length = sum(len(result.get("response", "")) for result in results)
    else:
        # Official uses 'answer' field
        total_length = sum(len(result.get("answer", "")) for result in results)
    
    avg_length = total_length / num_sources if num_sources > 0 else 0
    
    # Quality multipliers based on response length
    if avg_length > 300:  # Detailed responses
        quality_bonus += 0.1
    elif avg_length > 150:  # Moderate responses
        quality_bonus += 0.05
    elif avg_length < 50:   # Short responses
        quality_bonus -= 0.1
    
    # Check for generic/insufficient responses
    generic_indicators = ["no relevant information", "not found", "insufficient data", "no therapy data"]
    
    if implementation_type == "custom":
        response_texts = [result.get("response", "").lower() for result in results]
    else:
        response_texts = [result.get("answer", "").lower() for result in results]
    
    has_generic = any(
        any(indicator in response_text for indicator in generic_indicators)
        for response_text in response_texts
    )
    
    if has_generic:
        quality_bonus -= 0.15
    
    # Custom implementation: factor in retrieval metrics
    if implementation_type == "custom" and available_indexes:
        total_items = sum(result.get('retrieved_items', 0) for result in results)
        avg_items_per_source = total_items / num_sources if num_sources > 0 else 0
        
        # Bonus for high-quality retrieval
        if avg_items_per_source >= 3:
            quality_bonus += 0.1
        elif avg_items_per_source >= 2:
            quality_bonus += 0.05
        elif avg_items_per_source < 1:
            quality_bonus -= 0.1
            
        # Bonus for multiple data points in available indexes
        total_content = sum(available_indexes.values())
        if total_content >= 10:
            quality_bonus += 0.05
        elif total_content < 3:
            quality_bonus -= 0.05
    
    final_confidence = base_confidence + quality_bonus
    
    # Ensure confidence stays within bounds
    return min(max(final_confidence, 0.1), 0.95)


def get_all_therapy_indexes() -> List[str]:
    """Get list of all therapy-related vector indexes."""
    return [
        "therapy_moments_index",
        "user_reflections_index", 
        "therapist_notes_index",
        "behavior_patterns_index",
        "user_values_index"
    ]


def get_index_config() -> Dict[str, Dict[str, str]]:
    """Get configuration mapping for all therapy indexes."""
    return {
        "therapy_moments_index": {
            "node_type": "Moment",
            "embedding_property": "context_embedding",
            "content_property": "context",
            "description": "Therapy session contexts and situations"
        },
        "user_reflections_index": {
            "node_type": "Reflection", 
            "embedding_property": "content_embedding",
            "content_property": "content",
            "description": "User insights and realizations"
        },
        "therapist_notes_index": {
            "node_type": "PersonaNote",
            "embedding_property": "content_embedding", 
            "content_property": "content",
            "description": "Therapist observations and notes"
        },
        "behavior_patterns_index": {
            "node_type": "Pattern",
            "embedding_property": "description_embedding",
            "content_property": "description",
            "description": "Behavioral and emotional patterns"
        },
        "user_values_index": {
            "node_type": "Value",
            "embedding_property": "description_embedding",
            "content_property": "description",
            "description": "User values and motivations"
        }
    }


def get_user_content_check_queries() -> Dict[str, str]:
    """Get Cypher queries to check user content in each index."""
    return {
        "therapy_moments_index": "MATCH (m:Moment {user_id: $user_id}) WHERE m.context_embedding IS NOT NULL RETURN count(m) as count",
        "user_reflections_index": "MATCH (r:Reflection {user_id: $user_id}) WHERE r.content_embedding IS NOT NULL RETURN count(r) as count",
        "therapist_notes_index": "MATCH (p:PersonaNote {user_id: $user_id}) WHERE p.content_embedding IS NOT NULL RETURN count(p) as count", 
        "behavior_patterns_index": "MATCH (p:Pattern {user_id: $user_id}) WHERE p.description_embedding IS NOT NULL RETURN count(p) as count",
        "user_values_index": "MATCH (v:Value {user_id: $user_id}) WHERE v.description_embedding IS NOT NULL RETURN count(v) as count"
    } 