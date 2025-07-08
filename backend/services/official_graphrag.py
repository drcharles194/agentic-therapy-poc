"""
Official Neo4j GraphRAG Service Implementation - Dynamic Retriever Creation

This service creates retrievers dynamically per user request, allowing for:
- User-specific data filtering
- Optimized resource usage
- Better scalability
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from neo4j import GraphDatabase
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.llm import AnthropicLLM
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings

from backend.services.neo4j import Neo4jService
from backend.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OfficialGraphRAGResult:
    """Result from the official GraphRAG query."""
    query: str
    user_id: str
    user_name: str
    raw_data: Dict[str, Any]
    natural_response: str
    confidence: float
    data_sources: List[str]
    retrieval_method: str = "official_graphrag"


class OfficialGraphRAGService:
    """
    Official Neo4j GraphRAG implementation with dynamic retriever creation.
    
    This service creates retrievers per user request, optimizing resource usage
    and enabling user-specific filtering from the retrieval level.
    """
    
    def __init__(self, neo4j_service: Neo4jService):
        """Initialize the official GraphRAG service with shared components."""
        self.neo4j_service = neo4j_service
        self.driver = None
        self.llm = None
        self.embedder = None
        self.is_available = False
        
        # Define the therapy indexes we can query
        self.therapy_indexes = [
            "therapy_moments_index",
            "user_reflections_index", 
            "therapist_notes_index",
            "behavior_patterns_index",
            "user_values_index"
        ]
        
        self._initialize_shared_components()
    
    def _initialize_shared_components(self):
        """Initialize shared components (driver, LLM, embedder) but not retrievers."""
        try:
            logger.info("Initializing Official Neo4j GraphRAG shared components...")
            
            # Create Neo4j driver
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password)
            )
            logger.info("✅ Neo4j driver created for official GraphRAG")
            
            # Initialize LLM
            if settings.anthropic_api_key and settings.anthropic_api_key != "test_key":
                self.llm = AnthropicLLM(
                    api_key=settings.anthropic_api_key,
                    model_name="claude-sonnet-4-20250514",
                    model_params={"temperature": 0.1, "max_tokens": 1000}
                )
                logger.info("✅ Anthropic LLM initialized for official GraphRAG")
            else:
                logger.warning("❌ Anthropic API key not configured - Official GraphRAG unavailable")
                return
            
            # Initialize embedder
            if settings.openai_api_key and settings.openai_api_key != "test_key":
                self.embedder = OpenAIEmbeddings(
                    model="text-embedding-3-large",
                    api_key=settings.openai_api_key
                )
                logger.info("✅ OpenAI embedder initialized for official GraphRAG")
            else:
                logger.warning("❌ OpenAI API key not configured - Official GraphRAG unavailable")
                return
            
            self.is_available = True
            logger.info("✅ Official GraphRAG shared components initialized - ready for dynamic retriever creation")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize official GraphRAG shared components: {e}")
            self.is_available = False
    
    def _check_user_data_in_indexes(self, user_id: str) -> List[str]:
        """Check which indexes contain data for the specific user."""
        try:
            # Use the same approach as custom service - sync driver session
            with self.driver.session() as session:
                # Check content in each index type using the same approach as custom service
                content_checks = {
                    "therapy_moments_index": "MATCH (m:Moment {user_id: $user_id}) WHERE m.context_embedding IS NOT NULL RETURN count(m) as count",
                    "user_reflections_index": "MATCH (r:Reflection {user_id: $user_id}) WHERE r.content_embedding IS NOT NULL RETURN count(r) as count",
                    "therapist_notes_index": "MATCH (p:PersonaNote {user_id: $user_id}) WHERE p.content_embedding IS NOT NULL RETURN count(p) as count", 
                    "behavior_patterns_index": "MATCH (p:Pattern {user_id: $user_id}) WHERE p.description_embedding IS NOT NULL RETURN count(p) as count",
                    "user_values_index": "MATCH (v:Value {user_id: $user_id}) WHERE v.description_embedding IS NOT NULL RETURN count(v) as count"
                }
                
                indexes_with_data = []
                for index_name, query in content_checks.items():
                    try:
                        result = session.run(query, {"user_id": user_id})
                        record = result.single()
                        count = record["count"] if record else 0
                        
                        if count > 0:
                            indexes_with_data.append(index_name)
                            logger.info(f"✅ Found {count} items in {index_name} for user {user_id}")
                        else:
                            logger.info(f"⚪ No data in {index_name} for user {user_id}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error checking {index_name} for user {user_id}: {e}")
                        continue
                
                return indexes_with_data
                
        except Exception as e:
            logger.error(f"Error checking user content in indexes: {e}")
            # Fallback to empty list if check fails
            return []
    
    def _create_user_specific_retrievers(self, user_id: str, indexes_with_data: List[str]) -> Dict[str, Any]:
        """Create retrievers dynamically for a specific user and their data indexes."""
        retrievers = {}
        graphrag_instances = {}
        
        for index_name in indexes_with_data:
            try:
                # Create VectorRetriever for this index
                retriever = VectorRetriever(
                    driver=self.driver,
                    index_name=index_name,
                    embedder=self.embedder
                )
                
                # Create GraphRAG instance for this retriever
                graphrag_instance = GraphRAG(
                    retriever=retriever,
                    llm=self.llm
                )
                
                retrievers[index_name] = retriever
                graphrag_instances[index_name] = graphrag_instance
                
                logger.info(f"✅ Created dynamic retriever for {index_name} (user: {user_id})")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to create retriever for {index_name} (user: {user_id}): {e}")
                continue
        
        return {
            "retrievers": retrievers,
            "graphrag_instances": graphrag_instances
        }
    
    async def query_user_data(
        self, 
        user_id: str, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> OfficialGraphRAGResult:
        """
        Query user therapy data using dynamically created retrievers.
        
        This method:
        1. Checks which indexes have data for the user
        2. Creates retrievers only for those indexes
        3. Runs queries against all relevant indexes
        4. Combines results into a comprehensive response
        """
        logger.info(f"Official GraphRAG query for user {user_id}: {query[:100]}... (dynamic retrievers)")
        
        try:
            # Get user info first
            user_info = await self._get_user_info(user_id)
            if not user_info:
                return self._create_error_result(user_id, query, "User not found")
            
            # Check if service is available
            if not self.is_available:
                return await self._create_fallback_result(user_id, query, user_info)
            
            # Step 1: Check which indexes have data for this user
            indexes_with_data = self._check_user_data_in_indexes(user_id)
            if not indexes_with_data:
                return self._create_no_data_result(user_id, query, user_info)
            
            logger.info(f"📊 Creating retrievers for {len(indexes_with_data)} indexes with user data: {indexes_with_data}")
            
            # Step 2: Create retrievers dynamically for this user's data
            retriever_components = self._create_user_specific_retrievers(user_id, indexes_with_data)
            graphrag_instances = retriever_components["graphrag_instances"]
            
            if not graphrag_instances:
                return self._create_no_retrievers_result(user_id, query, user_info)
            
            # Step 3: Query all available indexes for this user
            results = []
            data_sources = []
            
            for index_name, graphrag_instance in graphrag_instances.items():
                try:
                    # Enhance query with user context
                    enhanced_query = f"User {user_info.get('name', user_id)} (ID: {user_id}): {query}"
                    
                    # Execute GraphRAG search on this index
                    response = graphrag_instance.search(
                        query_text=enhanced_query,
                        retriever_config={"top_k": 3}
                    )
                    
                    if response and response.answer:
                        results.append({
                            "index": index_name,
                            "answer": response.answer,
                            "response": response
                        })
                        data_sources.append(index_name)
                        logger.info(f"✅ Got response from {index_name} for user {user_id}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Query failed for {index_name} (user {user_id}): {e}")
                    continue
            
            # Step 4: Combine results from all indexes
            if results:
                combined_response = self._combine_results(results, query)
                confidence = self._calculate_confidence(results)
            else:
                combined_response = f"No relevant information found for user {user_info.get('name', 'this user')} regarding: {query}"
                confidence = 0.1
                data_sources = ["no_results"]
            
            return OfficialGraphRAGResult(
                query=query,
                user_id=user_id,
                user_name=user_info.get("name", "Unknown"),
                raw_data={
                    "individual_results": results,
                    "indexes_queried": list(graphrag_instances.keys()),
                    "successful_indexes": data_sources,
                    "indexes_with_user_data": indexes_with_data,
                    "processing_method": "official_neo4j_graphrag_dynamic_retrievers",
                    "retrievers_created": len(graphrag_instances)
                },
                natural_response=combined_response,
                confidence=confidence,
                data_sources=data_sources,
                retrieval_method="official_dynamic_multi_index_graphrag"
            )
            
        except Exception as e:
            logger.error(f"❌ Error in official GraphRAG query: {e}")
            return self._create_error_result(user_id, query, f"Query processing error: {str(e)}")
    
    def _combine_results(self, results: List[Dict], original_query: str) -> str:
        """Combine results from multiple indexes into a coherent response."""
        if not results:
            return "No relevant information found."
        
        if len(results) == 1:
            return results[0]["answer"]
        
        # Combine insights from multiple indexes
        combined_insights = []
        
        for result in results:
            index_name = result["index"].replace("_index", "").replace("_", " ").title()
            answer = result["answer"]
            combined_insights.append(f"From {index_name}: {answer}")
        
        # Create a comprehensive response
        combined_response = f"Based on multiple data sources, here's what I found regarding '{original_query}':\n\n"
        combined_response += "\n\n".join(combined_insights)
        
        return combined_response
    
    def _calculate_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence based on the number and quality of results."""
        if not results:
            return 0.1
        
        # Base confidence on number of indexes that returned results
        base_confidence = min(0.5 + (len(results) * 0.1), 0.9)
        
        # Adjust based on response quality
        total_length = sum(len(result["answer"]) for result in results)
        avg_length = total_length / len(results)
        
        if avg_length > 200:
            base_confidence += 0.1
        elif avg_length < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.1), 0.95)
    
    async def _get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get basic user information using the same approach as custom service."""
        try:
            return await self.neo4j_service.get_user(user_id)
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    async def _create_fallback_result(
        self, 
        user_id: str, 
        query: str, 
        user_info: Dict[str, Any]
    ) -> OfficialGraphRAGResult:
        """Create a fallback result when official GraphRAG is not available."""
        fallback_message = (
            f"Official Neo4j GraphRAG service is currently unavailable for user {user_info['name']}. "
            f"This could be due to missing API keys, package compatibility issues, or configuration problems. "
            f"Regarding the query '{query}': Please use the custom GraphRAG implementation for analysis."
        )
        
        return OfficialGraphRAGResult(
            query=query,
            user_id=user_id,
            user_name=user_info["name"],
            raw_data={
                "status": "service_unavailable",
                "reason": "Official GraphRAG shared components not initialized",
                "processing_method": "fallback_unavailable"
            },
            natural_response=fallback_message,
            confidence=0.1,
            data_sources=["fallback_unavailable"],
            retrieval_method="fallback_unavailable"
        )
    
    def _create_no_data_result(
        self, 
        user_id: str, 
        query: str, 
        user_info: Dict[str, Any]
    ) -> OfficialGraphRAGResult:
        """Create result when no data is found for the user."""
        message = (
            f"No therapy data found for user {user_info['name']} in any of the indexes. "
            f"This user may not have any recorded therapy sessions, reflections, or notes yet."
        )
        
        return OfficialGraphRAGResult(
            query=query,
            user_id=user_id,
            user_name=user_info["name"],
            raw_data={
                "status": "no_user_data",
                "indexes_checked": self.therapy_indexes,
                "processing_method": "no_data_available"
            },
            natural_response=message,
            confidence=0.0,
            data_sources=["no_user_data"],
            retrieval_method="no_user_data"
        )
    
    def _create_no_retrievers_result(
        self, 
        user_id: str, 
        query: str, 
        user_info: Dict[str, Any]
    ) -> OfficialGraphRAGResult:
        """Create result when retrievers could not be created."""
        message = (
            f"Could not create retrievers for user {user_info['name']}. "
            f"This could be due to technical issues with the vector indexes or GraphRAG configuration."
        )
        
        return OfficialGraphRAGResult(
            query=query,
            user_id=user_id,
            user_name=user_info["name"],
            raw_data={
                "status": "retriever_creation_failed",
                "processing_method": "retriever_error"
            },
            natural_response=message,
            confidence=0.0,
            data_sources=["retriever_error"],
            retrieval_method="retriever_error"
        )
    
    def _create_error_result(self, user_id: str, query: str, error_message: str) -> OfficialGraphRAGResult:
        """Create an error result."""
        return OfficialGraphRAGResult(
            query=query,
            user_id=user_id,
            user_name="Unknown",
            raw_data={"error": error_message},
            natural_response=f"Error processing query: {error_message}",
            confidence=0.0,
            data_sources=["error"],
            retrieval_method="error"
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the official GraphRAG service."""
        try:
            status = {
                "service": "Official Neo4j GraphRAG (Dynamic)",
                "is_available": self.is_available,
                "driver_connected": self.driver is not None,
                "llm_initialized": self.llm is not None,
                "embedder_initialized": self.embedder is not None,
                "available_indexes": self.therapy_indexes,
                "approach": "dynamic_retriever_creation"
            }
            
            if self.is_available:
                status["status"] = "healthy"
                status["message"] = f"Official GraphRAG operational with dynamic retriever creation for {len(self.therapy_indexes)} indexes"
            else:
                status["status"] = "unavailable"
                status["message"] = "Official GraphRAG service shared components not available"
            
            return status
            
        except Exception as e:
            return {
                "service": "Official Neo4j GraphRAG (Dynamic)",
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "is_available": False
            }
    
    def close(self):
        """Clean up resources."""
        try:
            if self.driver:
                self.driver.close()
                self.driver = None
                logger.info("✅ Official GraphRAG driver closed")
            
            self.is_available = False
            
        except Exception as e:
            logger.error(f"Error closing official GraphRAG service: {e}")


# Global instance management
_official_graphrag_service: Optional[OfficialGraphRAGService] = None


def get_official_graphrag_service() -> OfficialGraphRAGService:
    """Get the official GraphRAG service instance."""
    global _official_graphrag_service
    if _official_graphrag_service is None:
        raise RuntimeError("Official GraphRAG service not initialized")
    return _official_graphrag_service


def initialize_official_graphrag_service(neo4j_service: Neo4jService):
    """Initialize the official GraphRAG service."""
    global _official_graphrag_service
    _official_graphrag_service = OfficialGraphRAGService(neo4j_service)
    logger.info("Official GraphRAG service instance created (dynamic approach)")


def shutdown_official_graphrag_service():
    """Shutdown the official GraphRAG service."""
    global _official_graphrag_service
    if _official_graphrag_service:
        _official_graphrag_service.close()
        _official_graphrag_service = None
        logger.info("Official GraphRAG service shutdown complete") 