from app.agents.base_agent import BaseAgent
from app.services.memory_service import memory_service
from app.services.llm_service import llm_service
from app.core.qdrant import qdrant_manager
from app.models.memory import MemoryType
from typing import Dict, Any, List, Optional
import json
from pathlib import Path


class KnowledgeAgent(BaseAgent):
    """
    Knowledge Agent - Handles knowledge retrieval and synthesis.
    Responsibilities:
    - Document search
    - PDF search
    - Meeting notes retrieval
    - RAG retrieval
    - Knowledge synthesis
    """
    
    def __init__(self):
        super().__init__(
            name="knowledge",
            description="Handles document search, RAG retrieval, and knowledge synthesis"
        )

    def get_system_prompt(self) -> str:
        return """You are the Knowledge Agent for a Windows AI Assistant. Your role is to help users find and synthesize information:

1. Search across documents (PDF, DOCX, TXT, Markdown, notes)
2. Retrieve relevant information using semantic search (RAG)
3. Synthesize information from multiple sources
4. Answer questions based on stored knowledge
5. Help users find specific information in their knowledge base
6. Summarize and connect related concepts

You have access to:
- Long-term memory with semantic search
- Document indexing and retrieval
- Knowledge synthesis capabilities

Be thorough in your search and provide well-sourced, accurate information."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process knowledge-related requests"""
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id")
        context = input_data.get("context", {})
        agent_plan = input_data.get("agent_plan", "")
        
        # Try to retrieve from memory
        try:
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=user_message,
                limit=5
            )
            
            if memories:
                # memories is a list of dictionaries from Qdrant
                memory_context = "\n".join([m.get("payload", {}).get("content", str(m)) for m in memories])
                context_prompt = f"Based on your stored information:\n{memory_context}\n\nUser question: {user_message}"
            else:
                context_prompt = f"User question: {user_message}"
            
            # Use LLM to generate a response
            try:
                print(f"[DEBUG] Knowledge agent calling LLM with prompt: {context_prompt[:100]}...")
                response = await llm_service.generate_simple_response(
                    message=context_prompt,
                    context=context,
                    chat_history=[]
                )
                print(f"[DEBUG] Knowledge agent got LLM response: {response[:100]}...")
                
                return {
                    "success": True,
                    "response": response,
                    "agent_used": self.name,
                    "metadata": {
                        "memories_found": len(memories) if memories else 0,
                        "llm_used": True
                    }
                }
            except Exception as llm_error:
                print(f"[DEBUG] Knowledge agent LLM failed: {str(llm_error)}")
                # Fallback if LLM fails
                return {
                    "success": True,
                    "response": f"I can help with basic questions about '{user_message}'. Advanced knowledge retrieval features are limited with the local gpt2 model. For full functionality, consider using a more powerful LLM.",
                    "agent_used": self.name,
                    "metadata": {
                        "error": str(llm_error),
                        "llm_failed": True
                    }
                }
                
        except Exception as e:
            print(f"[DEBUG] Knowledge agent failed: {str(e)}")
            # Fallback response if anything fails
            return {
                "success": True,
                "response": f"I can help with basic questions about '{user_message}'. Note: Advanced knowledge retrieval features are limited with the local gpt2 model. For full functionality, consider using a more powerful LLM.",
                "agent_used": self.name,
                "metadata": {
                    "error": str(e),
                    "embedding_disabled": True
                }
            }

    async def _classify_task(self, user_message: str, context: Dict[str, Any]) -> str:
        """Classify the type of knowledge task"""
        
        prompt = f"""Classify the following knowledge-related request into one of these categories:
- document_search: Search for specific documents or information within documents
- rag_retrieval: Retrieve relevant information using semantic search
- knowledge_synthesis: Synthesize information from multiple sources
- document_summary: Summarize a specific document or set of documents
- general: General knowledge questions

User request: {user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond with just the category name."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip().lower().replace("-", "_")

    async def _handle_document_search(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document search requests"""
        
        # Extract search parameters
        search_params = await self._extract_search_params(user_message, context)
        
        # Retrieve relevant memories/documents
        memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query=user_message,
            memory_type=search_params.get("memory_type"),
            limit=search_params.get("limit", 5)
        )
        
        if not memories:
            return {
                "response": "I couldn't find any relevant documents in your knowledge base. You may need to add more documents or try a different search query.",
                "memories_found": 0
            }
        
        # Summarize findings
        summary = await self._summarize_document_findings(user_message, memories)
        
        return {
            "response": summary,
            "memories_found": len(memories),
            "memories": memories
        }

    async def _handle_rag_retrieval(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RAG-based retrieval"""
        
        # Generate query embedding
        query_embedding = await llm_service.generate_embedding(user_message)
        
        # Search in Qdrant
        results = await qdrant_manager.search(
            collection_name="ai_assistant_memory",
            query_vector=query_embedding,
            limit=5,
            filter_dict={"user_id": user_id}
        )
        
        if not results:
            return {
                "response": "I couldn't find relevant information in my knowledge base to answer your question.",
                "results_found": 0
            }
        
        # Generate response using retrieved context
        context_text = "\n\n".join([
            f"Source: {r['payload'].get('source', 'Unknown')}\nContent: {r['payload'].get('content', '')}"
            for r in results
        ])
        
        rag_prompt = f"""Answer the following question using the provided context:

Question: {user_message}

Context:
{context_text}

If the context doesn't contain enough information to answer the question, say so. Provide a clear, well-sourced answer."""

        messages = [{"role": "user", "content": rag_prompt}]
        response = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": response,
            "results_found": len(results),
            "sources": [r['payload'] for r in results]
        }

    async def _handle_knowledge_synthesis(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge synthesis from multiple sources"""
        
        # Extract topics to synthesize
        topics = await self._extract_topics(user_message)
        
        # Retrieve information for each topic
        all_memories = []
        for topic in topics:
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=topic,
                limit=3
            )
            all_memories.extend(memories)
        
        if not all_memories:
            return {
                "response": "I couldn't find enough information to synthesize a comprehensive answer. You may need to add more relevant documents to your knowledge base.",
                "topics": topics
            }
        
        # Synthesize information
        synthesis_prompt = f"""Synthesize information from multiple sources to answer this question:

Question: {user_message}

Topics covered: {', '.join(topics)}

Available information:
{json.dumps([m['payload'] for m in all_memories], indent=2)}

Provide a comprehensive, well-structured answer that:
1. Directly addresses the question
2. Synthesizes information from multiple sources
3. Identifies connections and patterns
4. Highlights any conflicting information
5. Provides clear conclusions"""

        messages = [{"role": "user", "content": synthesis_prompt}]
        response = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": response,
            "topics": topics,
            "sources_count": len(all_memories)
        }

    async def _handle_document_summary(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document summary requests"""
        
        # Extract document identifier
        doc_info = await self._extract_document_info(user_message, context)
        
        if doc_info.get("document_id"):
            # Retrieve specific document
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=doc_info["document_id"],
                limit=1
            )
        else:
            # Search for documents matching the query
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=user_message,
                limit=3
            )
        
        if not memories:
            return {
                "response": "I couldn't find the document you're referring to. Please provide more specific information.",
                "memories_found": 0
            }
        
        # Generate summary
        document_content = memories[0]['payload'].get('content', '')
        summary_prompt = f"""Summarize this document:

Document: {memories[0]['payload'].get('source', 'Unknown')}

Content:
{document_content}

User's specific focus: {user_message}

Provide a clear, concise summary highlighting the key points."""

        messages = [{"role": "user", "content": summary_prompt}]
        summary = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": summary,
            "document_source": memories[0]['payload'].get('source'),
            "memories_found": len(memories)
        }

    async def _handle_general_knowledge_task(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general knowledge questions"""
        
        # Try RAG first
        rag_result = await self._handle_rag_retrieval(user_message, user_id, context)
        
        # If RAG didn't find anything, try general LLM response
        if rag_result["results_found"] == 0:
            prompt = f"""Answer this question to the best of your ability:

{user_message}

If this is about specific information that might be in the user's documents, mention that they should add relevant documents to their knowledge base for more accurate answers."""

            messages = [{"role": "user", "content": prompt}]
            response = await self.call_llm(messages, temperature=0.5)
            
            return {
                "response": response,
                "used_rag": False
            }
        
        return rag_result

    async def _extract_search_params(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search parameters from user message"""
        
        prompt = f"""Extract search parameters from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- memory_type: type of memory to search (personal, project, preference, knowledge, work_journal)
- limit: maximum number of results (default: 5)
- time_range: optional time filter (recent, all, or specific date range)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"limit": 5}

    async def _extract_topics(self, user_message: str) -> List[str]:
        """Extract topics for knowledge synthesis"""
        
        prompt = f"""Extract the main topics from this question that should be searched in the knowledge base:

{user_message}

Respond as a JSON array of topic strings (max 5 topics)."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [user_message]

    async def _extract_document_info(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document information from user message"""
        
        prompt = f"""Extract document information from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- document_id: document identifier (if mentioned)
- document_type: type of document (pdf, docx, txt, markdown, note)
- document_title: title of document (if mentioned)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _summarize_document_findings(self, user_message: str, memories: List[Dict[str, Any]]) -> str:
        """Summarize document search findings"""
        
        findings = []
        for memory in memories:
            payload = memory['payload']
            findings.append(f"- {payload.get('source', 'Unknown')}: {payload.get('content', '')[:200]}...")
        
        prompt = f"""Summarize these document findings in response to the user's request:

User request: {user_message}

Findings:
{chr(10).join(findings)}

Provide a clear summary highlighting the most relevant information and sources."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)
