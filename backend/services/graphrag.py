"""
GraphRAG service using optimized direct vector search.

This service provides intelligent querying of user therapy data using
direct vector similarity search with pre-generated embeddings and Anthropic Claude.
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from neo4j import GraphDatabase
from neo4j_graphrag.llm import AnthropicLLM

from backend.services.neo4j import Neo4jService
from backend.config import settings
from backend.utils.graphrag_utils import (
    index_name_to_friendly,
    calculate_dynamic_confidence,
    get_index_config,
    get_user_content_check_queries
)

logger = logging.getLogger(__name__)


@dataclass
class GraphRAGResult:
    """Result from a GraphRAG query."""
    query: str
    user_id: str
    user_name: str
    raw_data: Dict[str, Any]
    natural_response: str
    confidence: float
    data_sources: List[str]


class Neo4jGraphRAGService:
    """
    Optimized Neo4j GraphRAG service using direct vector similarity search.
    
    This service uses pre-generated embeddings stored in the database to avoid
    OpenAI API calls during queries, providing faster and more cost-effective
    therapy data analysis with Anthropic Claude for response generation.
    """
    
    def __init__(self, neo4j_service: Neo4jService):
        """Initialize GraphRAG service with Neo4j connection."""
        self.neo4j_service = neo4j_service
        self.sync_driver = None
        self.llm = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize the GraphRAG components using direct vector search approach."""
        try:
            # Create synchronous driver for GraphRAG
            self.sync_driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password)
            )
            logger.info("Created synchronous Neo4j driver for GraphRAG")
            
            # Initialize the LLM
            if settings.anthropic_api_key and settings.anthropic_api_key != "test_key":
                self.llm = AnthropicLLM(
                    api_key=settings.anthropic_api_key,
                    model_name="claude-sonnet-4-20250514",
                    model_params={"temperature": 0.1, "max_tokens": 1000}
                )
                logger.info("Neo4j GraphRAG AnthropicLLM initialized")
            else:
                logger.warning("Anthropic API key not configured - GraphRAG will have limited functionality")
                return
            
            # Set up the 5 separate vector indexes (embeddings are handled by Neo4jService)
            self._setup_therapy_indexes()
            
            logger.info("GraphRAG service initialized with direct vector search (no OpenAI calls during queries)")
            
        except Exception as e:
            logger.error(f"Failed to initialize GraphRAG components: {e}")
            self.llm = None
    
    def _setup_therapy_indexes(self):
        """
        Set up content-type specific vector indexes for therapy data (Option A).
        
        Creates separate indexes for:
        1. therapy_moments_index → Moment.context_embedding  
        2. user_reflections_index → Reflection.content_embedding
        3. therapist_notes_index → PersonaNote.content_embedding
        4. behavior_patterns_index → Pattern.description_embedding
        5. user_values_index → Value.description_embedding
        """
        try:
            with self.sync_driver.session() as session:
                # Define our content-type specific indexes
                indexes_to_create = [
                    {
                        "name": "therapy_moments_index",
                        "node_type": "Moment", 
                        "property": "context_embedding",
                        "description": "Therapy session contexts and situations"
                    },
                    {
                        "name": "user_reflections_index",
                        "node_type": "Reflection",
                        "property": "content_embedding", 
                        "description": "User insights and realizations"
                    },
                    {
                        "name": "therapist_notes_index",
                        "node_type": "PersonaNote",
                        "property": "content_embedding",
                        "description": "Therapist observations and notes"
                    },
                    {
                        "name": "behavior_patterns_index", 
                        "node_type": "Pattern",
                        "property": "description_embedding",
                        "description": "Behavioral and emotional patterns"
                    },
                    {
                        "name": "user_values_index",
                        "node_type": "Value", 
                        "property": "description_embedding",
                        "description": "User values and motivations"
                    }
                ]
                
                # Check existing indexes
                existing_indexes = session.run("SHOW INDEXES YIELD name").data()
                existing_names = {idx["name"] for idx in existing_indexes}
                
                # Create missing indexes using text-embedding-3-large dimensions (3072)
                for index_config in indexes_to_create:
                    if index_config["name"] not in existing_names:
                        logger.info(f"Creating vector index: {index_config['name']} for {index_config['description']}")
                        
                        create_query = f"""
                        CREATE VECTOR INDEX {index_config['name']} IF NOT EXISTS
                        FOR (n:{index_config['node_type']}) ON (n.{index_config['property']})
                        OPTIONS {{
                            indexConfig: {{
                                `vector.dimensions`: 3072,
                                `vector.similarity_function`: 'cosine'
                            }}
                        }}
                        """
                        
                        session.run(create_query)
                        logger.info(f"✅ Created {index_config['name']}")
                    else:
                        logger.info(f"✅ Index {index_config['name']} already exists")
                
                logger.info("All therapy vector indexes are ready")
                
        except Exception as e:
            logger.error(f"Error setting up therapy indexes: {e}")
    
    def close(self):
        """Clean up resources."""
        if self.sync_driver:
            self.sync_driver.close()
            self.sync_driver = None
            logger.info("Synchronous Neo4j driver closed")
    
    async def query_user_data(
        self,
        user_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> GraphRAGResult:
        """
        Query user therapy data using optimized direct vector search.
        
        Uses pre-generated embeddings to avoid OpenAI calls during queries.
        """
        logger.info(f"Neo4j GraphRAG query for user {user_id}: {query}...")
        
        try:
            # Get user info
            user_info = await self._get_user_info(user_id)
            if not user_info:
                return self._create_error_result(user_id, query, "User not found")
            
            if not self.llm:
                logger.warning("GraphRAG LLM not available, using fallback")
                return await self._fallback_query(user_id, query, user_info)
            
            # Check which indexes have user-specific content to avoid unnecessary API calls
            available_indexes = await self._check_user_content_in_indexes(user_id)
            
            if not available_indexes:
                return GraphRAGResult(
                    query=query,
                    user_id=user_id,
                    user_name=user_info.get('name', 'Unknown'),
                    raw_data={"message": "No therapy content found"},
                    natural_response=f"I don't see any therapy content available for {user_info.get('name', 'this user')} yet. Once they have some therapy sessions, I'll be able to provide insights about their progress and patterns.",
                    confidence=0.95,  # High confidence when definitively no data exists
                    data_sources=[]
                )
            
            logger.info(f"Found content in {len(available_indexes)} indexes: {list(available_indexes.keys())}")
            
            # Pre-embed the query once using our existing embedding service (no OpenAI call needed)
            try:
                from backend.services.embedding import embedding_service
                await embedding_service.initialize()  # Ensure it's initialized
                
                enhanced_query = f"Question about user {user_info.get('name', user_id)}: {query} Please focus on therapy-related content for this specific user."
                query_embedding = await embedding_service.generate_embedding(enhanced_query)
                logger.info("Pre-generated query embedding (avoiding OpenAI calls in GraphRAG)")
                
            except Exception as e:
                logger.error(f"Failed to generate query embedding: {e}")
                return self._create_error_result(user_id, query, "Embedding generation failed")
            
            # Search only indexes with content using direct vector similarity
            all_results = []
            
            # Query only indexes that have user content using optimized vector search
            for index_name in available_indexes.keys():
                try:
                    logger.info(f"Querying {index_name} with direct vector search...")
                    
                    # Get relevant context using direct vector similarity search
                    relevant_content = await self._direct_vector_search(
                        index_name, user_id, query_embedding, top_k=5
                    )
                    
                    if relevant_content:
                        # Use only the LLM for response generation (no more OpenAI embedding calls)
                        response_text = await self._generate_response_from_content(
                            query, user_info, relevant_content, index_name
                        )
                        
                        if response_text and not self._is_empty_response(response_text):
                            result_data = {
                                "index": index_name,
                                "response": response_text,
                                "source": index_name_to_friendly(index_name),
                                "content_count": available_indexes[index_name],
                                "retrieved_items": len(relevant_content)
                            }
                            all_results.append(result_data)
                    
                except Exception as e:
                    logger.warning(f"Error querying {index_name}: {e}")
                    continue
            
            if not all_results:
                return GraphRAGResult(
                    query=query,
                    user_id=user_id,
                    user_name=user_info.get('name', 'Unknown'),
                    raw_data={"message": "No relevant insights found"},
                    natural_response=f"I found therapy content for {user_info.get('name', 'this user')}, but couldn't generate specific insights for your question. Please try asking about specific aspects like emotions, patterns, or recent sessions.",
                    confidence=0.25,  # Low confidence when content exists but no insights generated
                    data_sources=list(available_indexes.keys())
                )
            
            # Combine results with better formatting
            combined_response = await self._create_structured_response(all_results, query, user_info)
            
            # Calculate dynamic confidence based on results quality
            confidence = calculate_dynamic_confidence(all_results, available_indexes, "custom")
            
            return GraphRAGResult(
                query=query,
                user_id=user_id,
                user_name=user_info.get('name', 'Unknown'),
                raw_data={"analysis_sections": all_results, "available_indexes": available_indexes},
                natural_response=combined_response,
                confidence=confidence,
                data_sources=[result["source"] for result in all_results]
            )
            
        except Exception as e:
            logger.error(f"Error in GraphRAG query: {e}")
            return self._create_error_result(user_id, query, f"GraphRAG error: {str(e)}")
    
    async def _check_user_content_in_indexes(self, user_id: str) -> Dict[str, int]:
        """
        Check which indexes contain content for this user to avoid unnecessary API calls.
        Returns dict mapping index_name -> content_count for indexes with content.
        """
        try:
            with self.sync_driver.session() as session:
                # Check content in each index type using shared queries
                content_checks = get_user_content_check_queries()
                
                available_indexes = {}
                for index_name, query in content_checks.items():
                    result = session.run(query, {"user_id": user_id})
                    count = result.single()["count"]
                    if count > 0:
                        available_indexes[index_name] = count
                        logger.info(f"Found {count} items in {index_name} for user {user_id}")
                
                return available_indexes
                
        except Exception as e:
            logger.error(f"Error checking user content in indexes: {e}")
            # Fallback to all indexes if check fails
            return {name: 1 for name in self.graphrag_instances.keys()}
    
    def _is_empty_response(self, response_text: str) -> bool:
        """Check if a GraphRAG response indicates no relevant content."""
        empty_indicators = [
            "no context or data provided",
            "no information available",
            "cannot provide specific information", 
            "no records associated with this user",
            "no therapy data",
            "no relevant data",
            "insufficient information"
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in empty_indicators)
    
    async def _create_structured_response(self, results: List[Dict], query: str, user_info: Dict) -> str:
        """Create a unified therapeutic summary from multiple GraphRAG results."""
        if not results:
            return "No relevant therapy data found for this user."
        
        user_name = user_info.get('name', 'this user')
        
        # Collect all insights to create a unified narrative
        all_insights = []
        source_summary = []
        
        for result in results:
            source = result['source']
            content = result['response'].strip()
            count = result.get('content_count', 0)
            
            if content and len(content) > 20:  # Only include meaningful responses
                all_insights.append(content)
                source_summary.append(f"{source} ({count} entries)")
        
        if not all_insights:
            return f"I found therapy content for {user_name}, but couldn't generate specific insights for your question. Please try asking about specific aspects like emotions, patterns, or recent sessions."
        
        # Create a unified therapeutic response by combining insights
        combined_insights = await self._synthesize_unified_response(
            query, user_name, all_insights, source_summary
        )
        
        return combined_insights
    
    async def _synthesize_unified_response(
        self, 
        query: str, 
        user_name: str, 
        insights: List[str], 
        sources: List[str]
    ) -> str:
        """Synthesize multiple insights into a unified therapeutic response."""
        
        # Create synthesis prompt
        synthesis_prompt = f"""
You are a skilled therapist reviewing multiple data sources about {user_name}. Your task is to provide a comprehensive, unified response to this question: "{query}"

Available insights from different therapeutic data sources:

{chr(10).join([f"Source {i+1}: {insight}" for i, insight in enumerate(insights)])}

Instructions:
- Synthesize these insights into ONE cohesive therapeutic response
- Focus on the most relevant patterns and themes
- Provide specific, actionable therapeutic insights
- Use clear, professional language appropriate for clinical review
- Structure your response with clear paragraphs - DO NOT use markdown formatting
- Use plain text only - no asterisks, hashtags, or other markdown symbols
- If insights conflict, acknowledge the complexity
- Conclude with therapeutic implications or recommendations

Data sources analyzed: {', '.join(sources)}

Unified Response (plain text only):"""

        try:
            # Generate unified response
            unified_response = await self._call_llm_directly(synthesis_prompt)
            
            if unified_response and len(unified_response.strip()) > 50:
                # Add metadata footer (plain text, no confidence in text)
                footer = f"\n\nAnalysis Summary: Based on {len(insights)} therapeutic data sources"
                return unified_response.strip() + footer
            else:
                # Fallback to simple combination
                return self._create_fallback_summary(query, user_name, insights, sources)
                
        except Exception as e:
            logger.error(f"Error synthesizing unified response: {e}")
            return self._create_fallback_summary(query, user_name, insights, sources)
    
    def _create_fallback_summary(self, query: str, user_name: str, insights: List[str], sources: List[str]) -> str:
        """Create a simple fallback summary when synthesis fails."""
        
        # Simple combination approach (plain text)
        response_parts = [
            f"Based on analysis of {user_name}'s therapeutic data:",
            ""
        ]
        
        # Add key insights
        for i, insight in enumerate(insights[:3]):  # Top 3 insights
            if insight and len(insight.strip()) > 20:
                # Clean up the insight text
                clean_insight = insight.strip()
                if not clean_insight.endswith('.'):
                    clean_insight += '.'
                response_parts.append(f"• {clean_insight}")
        
        # Add therapeutic implications
        response_parts.extend([
            "",
            f"From a clinical perspective, these patterns suggest {user_name} is actively engaged in therapeutic work with identifiable areas for continued exploration and growth.",
            "",
            f"Sources: {', '.join(sources)}"
        ])
        
        return "\n".join(response_parts)
    

    
    async def _get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get basic user information."""
        try:
            return await self.neo4j_service.get_user(user_id)
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    async def _fallback_query(self, user_id: str, query: str, user_info: Dict[str, Any]) -> GraphRAGResult:
        """Fallback when GraphRAG is not available."""
        try:
            # Simple fallback response when GraphRAG is not working
            response = f"I found user {user_info.get('name', 'this user')} in the system, but GraphRAG is not currently available. "
            response += "Please ensure both OpenAI and Anthropic API keys are configured properly. "
            response += "For now, I cannot provide detailed insights about their therapy data."
            
            return GraphRAGResult(
                query=query,
                user_id=user_id,
                user_name=user_info.get('name', 'Unknown'),
                raw_data={"user_info": user_info, "fallback": True},
                natural_response=response,
                confidence=0.1,  # Very low confidence for fallback
                data_sources=["Fallback - GraphRAG unavailable"]
            )
            
        except Exception as e:
            logger.error(f"Error in fallback query: {e}")
        
        return self._create_error_result(user_id, query, "Unable to process query")
    
    def _create_error_result(self, user_id: str, query: str, error_message: str) -> GraphRAGResult:
        """Create an error result."""
        return GraphRAGResult(
            query=query,
            user_id=user_id,
            user_name="Unknown",
            raw_data={"error": error_message},
            natural_response=f"I'm sorry, I encountered an issue processing your query: {error_message}",
            confidence=0.0,
            data_sources=[]
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the optimized GraphRAG service."""
        status = {
            "service": "Neo4j GraphRAG (Direct Vector Search)",
            "status": "unknown",
            "components": {
                "sync_driver": bool(self.sync_driver),
                "llm": bool(self.llm),
                "direct_vector_search": True,
                "openai_calls_during_query": False
            }
        }
        
        if self.sync_driver and self.llm:
            try:
                # Test basic connectivity
                with self.sync_driver.session() as session:
                    session.run("RETURN 1")
                
                # Test embedding service availability  
                from backend.services.embedding import embedding_service
                await embedding_service.initialize()
                
                status["status"] = "healthy"
                status["message"] = "Direct vector search enabled - no OpenAI calls during queries"
                status["indexes_available"] = [
                    "therapy_moments_index",
                    "user_reflections_index", 
                    "therapist_notes_index",
                    "behavior_patterns_index",
                    "user_values_index"
                ]
            except Exception as e:
                status["status"] = "unhealthy"
                status["error"] = str(e)
        else:
            status["status"] = "degraded"
            status["message"] = "GraphRAG components not fully initialized"
        
        return status

    async def _direct_vector_search(
        self, 
        index_name: str, 
        user_id: str, 
        query_embedding: List[float], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform direct vector similarity search using pre-generated embeddings.
        This avoids OpenAI API calls by using embeddings already stored in the database.
        """
        # Map index names to node types and properties using shared config
        index_config = get_index_config()
        
        config = index_config.get(index_name)
        if not config:
            logger.warning(f"Unknown index configuration: {index_name}")
            return []
        
        try:
            with self.sync_driver.session() as session:
                # Use vector similarity search with the pre-generated embedding
                search_query = f"""
                CALL db.index.vector.queryNodes('{index_name}', $top_k, $query_embedding)
                YIELD node, score
                WHERE node.user_id = $user_id
                RETURN node.{config['content_property']} as content,
                       node.user_id as user_id,
                       node.timestamp as timestamp,
                       score
                ORDER BY score DESC
                """
                
                results = session.run(search_query, {
                    "query_embedding": query_embedding,
                    "user_id": user_id,
                    "top_k": top_k
                })
                
                relevant_content = []
                for record in results:
                    if record["content"]:  # Only include non-empty content
                        relevant_content.append({
                            "content": record["content"],
                            "user_id": record["user_id"],
                            "timestamp": record["timestamp"],
                            "similarity_score": record["score"]
                        })
                
                logger.info(f"Found {len(relevant_content)} relevant items in {index_name} for user {user_id}")
                return relevant_content
                
        except Exception as e:
            logger.error(f"Error in direct vector search for {index_name}: {e}")
            return []
    
    async def _generate_response_from_content(
        self,
        query: str,
        user_info: Dict[str, Any],
        relevant_content: List[Dict[str, Any]],
        index_name: str
    ) -> str:
        """
        Generate response using only the LLM (no embedding calls).
        """
        if not relevant_content:
            return ""
        
        user_name = user_info.get('name', 'this user')
        source_type = index_name.replace('_index', '').replace('_', ' ').title()
        
        # Prepare context from retrieved content
        context_items = []
        for item in relevant_content[:3]:  # Use top 3 most relevant items
            content = item.get('content', '').strip()
            if content and len(content) > 10:  # Only include meaningful content
                context_items.append(f"- {content}")
        
        if not context_items:
            return ""
        
        context_text = '\n'.join(context_items)
        
        # Create prompt for LLM
        prompt = f"""
Based on the following {source_type.lower()} data for {user_name}, please answer this question: "{query}"

Relevant {source_type.lower()}:
{context_text}

Instructions:
- Focus specifically on {user_name}'s situation
- Provide therapeutic insights based on the available data
- Be concise but meaningful
- If the data doesn't clearly address the question, say so briefly

Response:"""

        try:
            # Use only the LLM (no embeddings)
            response = await self._call_llm_directly(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return ""
    
    async def _call_llm_directly(self, prompt: str) -> str:
        """Call the LLM directly without any embeddings."""
        try:
            # Use the Anthropic LLM directly
            messages = [{"role": "user", "content": prompt}]
            
            # This uses the same pattern as the Neo4j GraphRAG package but without embeddings
            response = await self.llm.ainvoke(messages[0]["content"])
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Direct LLM call failed: {e}")
            return ""


# We'll keep the old name for compatibility but use the new implementation
GraphRAGService = Neo4jGraphRAGService 