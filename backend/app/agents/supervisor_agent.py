from app.agents.base_agent import BaseAgent
from app.services.observability_db import observability_db
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Orchestrates all other agents.
    Responsibilities:
    - Understand user intent
    - Create execution plan
    - Select appropriate agents
    - Merge results from multiple agents
    - Generate final response
    """
    
    def __init__(self, available_agents: List[BaseAgent]):
        super().__init__(
            name="supervisor",
            description="Orchestrates all agents and manages task execution"
        )
        self.available_agents = {agent.name: agent for agent in available_agents}

    def get_system_prompt(self) -> str:
        return """You are the Supervisor Agent for a Windows AI Assistant. Your role is to:

1. Understand the user's intent and classify the request
2. Determine which agent(s) should handle the request
3. Create an execution plan if multiple agents are needed
4. Coordinate agent execution
5. Merge results from multiple agents into a coherent response
6. Generate the final response to the user

Available agents:
- code: For code-related tasks (repository search, code explanation, architecture analysis)
- knowledge: For document search, RAG retrieval, knowledge synthesis
- windows: For Windows automation (open apps, file search, clipboard, screenshots)
- system: For system administration (WSL, Podman, Docker, processes, services)
- productivity: For calendar, tasks, emails, meetings, work journal

You NEVER directly perform work - you always delegate to the appropriate agents.
Be concise and clear in your planning and coordination."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and coordinate agents"""
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id")
        chat_id = input_data.get("chat_id")
        context = input_data.get("context", {})
        
        # Create trace ID for this request
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Log agent start
        await observability_db.record_log(
            level="INFO",
            logger_name="supervisor_agent",
            message=f"Supervisor agent started processing message: {user_message[:50]}...",
            context={"trace_id": trace_id, "chat_id": chat_id, "user_id": user_id}
        )
        
        # Record trace start
        await observability_db.record_trace(
            trace_id=trace_id,
            span_id=span_id,
            operation_name="supervisor.process",
            service_name="supervisor_agent",
            start_time=start_time,
            status="running"
        )
        
        # For local gpt2, use direct LLM generation instead of complex orchestration
        try:
            from app.services.llm_service import llm_service
            
            # Generate response using local gpt2
            response = await llm_service.generate_simple_response(
                message=user_message,
                context=context,
                chat_history=[]
            )
            
            # Record trace completion
            end_time = datetime.utcnow()
            await observability_db.record_trace(
                trace_id=trace_id,
                span_id=span_id,
                operation_name="supervisor.process",
                service_name="supervisor_agent",
                start_time=start_time,
                end_time=end_time,
                status="success",
                metadata={"response_length": len(response)}
            )
            
            # Log agent completion
            await observability_db.record_log(
                level="INFO",
                logger_name="supervisor_agent",
                message=f"Supervisor agent completed successfully",
                context={"trace_id": trace_id, "chat_id": chat_id, "response_length": len(response)}
            )
            
            # Record metric
            await observability_db.record_metric(
                metric_name="agent.supervisor.success",
                metric_value=1,
                metric_type="counter",
                tags={"operation": "process"}
            )
            
            return {
                "response": response,
                "agents_used": ["supervisor"],
                "agent_results": [],
                "execution_plan": {}
            }
        except Exception as e:
            # Record trace failure
            end_time = datetime.utcnow()
            await observability_db.record_trace(
                trace_id=trace_id,
                span_id=span_id,
                operation_name="supervisor.process",
                service_name="supervisor_agent",
                start_time=start_time,
                end_time=end_time,
                status="error",
                metadata={"error": str(e)}
            )
            
            # Log agent error
            await observability_db.record_log(
                level="ERROR",
                logger_name="supervisor_agent",
                message=f"Supervisor agent failed: {str(e)}",
                context={"trace_id": trace_id, "chat_id": chat_id, "error": str(e)}
            )
            
            # Record error metric
            await observability_db.record_metric(
                metric_name="agent.supervisor.error",
                metric_value=1,
                metric_type="counter",
                tags={"operation": "process", "error_type": type(e).__name__}
            )
            
            # Fallback to simple response if LLM fails
            return {
                "response": f"I heard you ask about '{user_message}'. I'm running on a local gpt2 model which has limited capabilities. For better responses, consider using a more powerful LLM like Groq or RunPod.",
                "agents_used": ["supervisor"],
                "agent_results": [],
                "execution_plan": {},
                "error": str(e)
            }

    async def _select_agents(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select appropriate agents based on user intent"""
        
        # Build intent classification prompt
        prompt = f"""Classify the following user request and determine which agent(s) should handle it.

User request: {user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with this structure:
{{
    "intent": "brief description of user intent",
    "agents": ["agent1", "agent2"],
    "plan": {{
        "agent1": "specific instructions for agent1",
        "agent2": "specific instructions for agent2"
    }}
}}

Available agents: code, knowledge, windows, system, productivity"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            # Parse JSON response
            selection = json.loads(response)
            return selection
        except json.JSONDecodeError:
            # Fallback to simple keyword matching
            return self._fallback_agent_selection(user_message)

    def _fallback_agent_selection(self, user_message: str) -> Dict[str, Any]:
        """Fallback agent selection based on keywords"""
        message_lower = user_message.lower()
        
        keywords = {
            "code": ["code", "repository", "git", "function", "class", "bug", "debug", "pr", "pull request"],
            "knowledge": ["document", "pdf", "search", "find", "information", "what is", "explain"],
            "windows": ["open", "launch", "screenshot", "clipboard", "file", "folder", "desktop"],
            "system": ["docker", "podman", "wsl", "process", "service", "system", "log"],
            "productivity": ["calendar", "meeting", "task", "email", "journal", "schedule"]
        }
        
        selected_agents = []
        for agent, agent_keywords in keywords.items():
            if any(keyword in message_lower for keyword in agent_keywords):
                selected_agents.append(agent)
        
        if not selected_agents:
            selected_agents = ["knowledge"]  # Default to knowledge agent
        
        return {
            "intent": "keyword-based classification",
            "agents": selected_agents,
            "plan": {}
        }

    async def _merge_results(
        self,
        user_message: str,
        agent_results: List[Dict[str, Any]],
        agent_selection: Dict[str, Any]
    ) -> str:
        """Merge results from multiple agents into coherent response"""
        
        if len(agent_results) == 1:
            # Single agent result
            result = agent_results[0]
            if result["success"]:
                return result.get("result", {}).get("response", "No response from agent")
            else:
                return f"Error from {result['agent']}: {result.get('error', 'Unknown error')}"
        
        # Multiple agents - merge results
        successful_results = [r for r in agent_results if r["success"]]
        failed_results = [r for r in agent_results if not r["success"]]
        
        if not successful_results:
            return "All agents failed to process your request."
        
        # Build merge prompt
        results_summary = []
        for result in successful_results:
            agent_name = result["agent"]
            agent_result = result.get("result", {})
            response = agent_result.get("response", str(agent_result))
            results_summary.append(f"{agent_name}: {response}")
        
        if failed_results:
            errors = [f"{r['agent']}: {r.get('error', 'Unknown error')}" for r in failed_results]
            results_summary.append(f"Errors: {'; '.join(errors)}")
        
        merge_prompt = f"""Merge the following agent results into a coherent response to the user's request.

User request: {user_message}

Agent results:
{chr(10).join(results_summary)}

Generate a clear, helpful response that combines the relevant information from all agents."""

        messages = [{"role": "user", "content": merge_prompt}]
        return await self.call_llm(messages, temperature=0.5)
