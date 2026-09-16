from app.agents.base_agent import BaseAgent
from app.services.observability_db import observability_db
from app.services.llm_service import llm_service
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
        
        try:
            # Step 1: Intent classification and agent selection
            await observability_db.record_log(
                level="INFO",
                logger_name="supervisor_agent",
                message="Starting intent classification and agent selection",
                context={"trace_id": trace_id, "chat_id": chat_id, "user_message": user_message}
            )
            
            agent_selection = await self._select_agents(user_message, context)
            selected_agents = agent_selection.get("agents", [])
            execution_plan = agent_selection.get("plan", {})
            
            await observability_db.record_log(
                level="INFO",
                logger_name="supervisor_agent",
                message=f"Agent selection completed: {selected_agents}",
                context={"trace_id": trace_id, "chat_id": chat_id, "selected_agents": selected_agents, "execution_plan": execution_plan, "agent_selection_full": agent_selection}
            )
            
            # Step 2: Execute selected agents
            agent_results = []
            agents_used = []
            
            for agent_name in selected_agents:
                if agent_name in self.available_agents:
                    agent = self.available_agents[agent_name]
                    
                    await observability_db.record_log(
                        level="INFO",
                        logger_name="supervisor_agent",
                        message=f"Executing {agent_name} agent",
                        context={"trace_id": trace_id, "chat_id": chat_id, "agent": agent_name}
                    )
                    
                    try:
                        agent_start = datetime.utcnow()
                        agent_span_id = str(uuid.uuid4())
                        
                        # Record agent trace start
                        await observability_db.record_trace(
                            trace_id=trace_id,
                            span_id=agent_span_id,
                            operation_name=f"{agent_name}.execute",
                            service_name=agent_name,
                            start_time=agent_start,
                            status="running",
                            parent_span_id=span_id
                        )
                        
                        # Execute agent
                        agent_input = {
                            "message": user_message,
                            "user_id": user_id,
                            "chat_id": chat_id,
                            "context": context,
                            "plan": execution_plan.get(agent_name, "")
                        }
                        
                        result = await agent.execute(agent_input)
                        
                        agent_end = datetime.utcnow()
                        
                        # Record agent trace completion
                        await observability_db.record_trace(
                            trace_id=trace_id,
                            span_id=agent_span_id,
                            operation_name=f"{agent_name}.execute",
                            service_name=agent_name,
                            start_time=agent_start,
                            end_time=agent_end,
                            status="success" if result.get("success") else "error",
                            metadata={"agent": agent_name, "result_keys": list(result.keys())}
                        )
                        
                        # Log agent completion
                        await observability_db.record_log(
                            level="INFO",
                            logger_name=agent_name,
                            message=f"{agent_name} agent completed: {result.get('success', False)}",
                            context={"trace_id": trace_id, "chat_id": chat_id, "agent": agent_name, "success": result.get("success")}
                        )
                        
                        # Record agent metric
                        await observability_db.record_metric(
                            metric_name=f"agent.{agent_name}.success" if result.get("success") else f"agent.{agent_name}.error",
                            metric_value=1,
                            metric_type="counter",
                            tags={"operation": "execute"}
                        )
                        
                        agent_results.append({
                            "agent": agent_name,
                            "success": result.get("success", False),
                            "result": result
                        })
                        agents_used.append(agent_name)
                        
                    except Exception as e:
                        await observability_db.record_log(
                            level="ERROR",
                            logger_name=agent_name,
                            message=f"{agent_name} agent failed: {str(e)}",
                            context={"trace_id": trace_id, "chat_id": chat_id, "agent": agent_name, "error": str(e)}
                        )
                        
                        agent_results.append({
                            "agent": agent_name,
                            "success": False,
                            "error": str(e)
                        })
            
            # Step 3: Merge results and generate final response
            await observability_db.record_log(
                level="INFO",
                logger_name="supervisor_agent",
                message="Merging agent results and generating final response",
                context={"trace_id": trace_id, "chat_id": chat_id, "agent_results_count": len(agent_results)}
            )
            
            if agent_results:
                final_response = await self._merge_results(user_message, agent_results, agent_selection)
            else:
                # Fallback to direct LLM if no agents were selected
                from app.services.llm_service import llm_service
                final_response = await llm_service.generate_simple_response(
                    message=user_message,
                    context=context,
                    chat_history=[]
                )
                await observability_db.record_log(
                    level="INFO",
                    logger_name="supervisor_agent",
                    message="No agents selected, using direct LLM response",
                    context={"trace_id": trace_id, "chat_id": chat_id}
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
                metadata={
                    "agents_used": agents_used,
                    "agent_results_count": len(agent_results),
                    "response_length": len(final_response)
                }
            )
            
            # Log supervisor completion
            await observability_db.record_log(
                level="INFO",
                logger_name="supervisor_agent",
                message=f"Supervisor agent completed successfully with {len(agents_used)} agents",
                context={"trace_id": trace_id, "chat_id": chat_id, "agents_used": agents_used, "response_length": len(final_response)}
            )
            
            # Record success metric
            await observability_db.record_metric(
                metric_name="agent.supervisor.success",
                metric_value=1,
                metric_type="counter",
                tags={"operation": "process", "agents_count": len(agents_used)}
            )
            
            return {
                "response": final_response,
                "agents_used": agents_used,
                "agent_results": agent_results,
                "execution_plan": execution_plan
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
            
            # Log supervisor error
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
            
            # Fallback response
            return {
                "response": f"I encountered an error processing your request: {str(e)}. I tried to use the multi-agent system but something went wrong.",
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
        
        # For local gpt2, use enhanced keyword-based selection
        message_lower = user_message.lower()
        
        keywords = {
            "code": ["code", "repository", "git", "function", "class", "bug", "debug", "pr", "pull request", "programming", "software", "api", "library", "framework", "syntax", "variable", "method", "algorithm", "data structure"],
            "knowledge": ["document", "pdf", "search", "find", "information", "what is", "explain", "python", "javascript", "language", "concept", "definition", "meaning", "how does", "how to", "tutorial", "guide", "learn", "understand"],
            "windows": ["open", "launch", "screenshot", "clipboard", "file", "folder", "desktop", "window", "application", "app", "program", "notepad", "explorer", "task manager", "settings", "control panel"],
            "system": ["docker", "podman", "wsl", "process", "service", "system", "log", "command", "terminal", "bash", "shell", "linux", "kernel", "memory", "cpu", "disk", "network"],
            "productivity": ["calendar", "meeting", "task", "email", "journal", "schedule", "appointment", "reminder", "todo", "deadline", "event", "organize", "plan", "time"]
        }
        
        selected_agents = []
        matched_keywords = {}
        
        for agent, agent_keywords in keywords.items():
            matched = [keyword for keyword in agent_keywords if keyword in message_lower]
            if matched:
                selected_agents.append(agent)
                matched_keywords[agent] = matched
        
        # If no agents matched, default to knowledge agent for general questions
        if not selected_agents:
            selected_agents = ["knowledge"]
            matched_keywords["knowledge"] = ["default_selection"]
        
        # Create execution plan based on matched keywords
        execution_plan = {}
        for agent in selected_agents:
            if agent in matched_keywords:
                execution_plan[agent] = f"Handle aspects related to: {', '.join(matched_keywords[agent])}"
            else:
                execution_plan[agent] = "General processing"
        
        return {
            "intent": f"Keyword-based classification: {', '.join(selected_agents)}",
            "agents": selected_agents,
            "plan": execution_plan
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
                # The result structure is: result["result"]["result"]["response"]
                # Due to base agent wrapping the agent's return value
                agent_result = result.get("result", {})
                actual_result = agent_result.get("result", {})
                response = actual_result.get("response", "No response from agent")
                
                # If response is too short, provide helpful message
                if not response or len(response.strip()) < 10:
                    return f"I understand you're asking about '{user_message}'. However, the local GPT-2 model I'm currently using is very limited and cannot generate meaningful responses. For better results, please switch to a cloud LLM provider (Groq is free) using the LLM configuration button (Ctrl+L)."
                return response
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
        merged_response = await self.call_llm(messages, temperature=0.5)
        
        # If merged response is too short, provide helpful message
        if not merged_response or len(merged_response.strip()) < 10:
            return f"I understand you're asking about '{user_message}'. However, the local GPT-2 model I'm currently using is very limited and cannot generate meaningful responses. For better results, please switch to a cloud LLM provider (Groq is free) using the LLM configuration button (Ctrl+L)."
        
        return merged_response

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ) -> str:
        """Call LLM directly (override base agent method)"""
        return await llm_service.generate_simple_response(
            message=messages[-1]["content"],
            context={},
            chat_history=[]
        )
