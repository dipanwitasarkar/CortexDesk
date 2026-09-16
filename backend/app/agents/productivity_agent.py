from app.agents.base_agent import BaseAgent
from app.services.memory_service import memory_service
from app.models.memory import MemoryType
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta


class ProductivityAgent(BaseAgent):
    """
    Productivity Agent - Handles productivity and work management.
    Responsibilities:
    - Calendar management
    - Task management
    - Email assistance
    - Meeting notes
    - Work journal
    - Status reports
    """
    
    def __init__(self):
        super().__init__(
            name="productivity",
            description="Handles productivity tasks including calendar, tasks, emails, meetings, and work journal"
        )

    def get_system_prompt(self) -> str:
        return """You are the Productivity Agent for a Windows AI Assistant. Your role is to help users with productivity and work management:

1. Manage calendar events and meetings
2. Track and manage tasks
3. Assist with email drafting and management
4. Capture and organize meeting notes
5. Maintain work journal
6. Generate status reports
7. Provide daily briefings

You have access to:
- Long-term memory for storing work-related information
- Task and calendar management capabilities
- Work journal functionality

Be organized, proactive, and helpful in managing the user's productivity."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process productivity-related requests"""
        user_message = input_data.get("message", "")
        user_id = input_data.get("user_id")
        context = input_data.get("context", {})
        agent_plan = input_data.get("agent_plan", {})
        
        # Determine the type of productivity task
        task_type = await self._classify_task(user_message, context)
        
        # Execute based on task type
        if task_type == "calendar_management":
            return await self._handle_calendar_management(user_message, user_id, context)
        elif task_type == "task_management":
            return await self._handle_task_management(user_message, user_id, context)
        elif task_type == "email_assistance":
            return await self._handle_email_assistance(user_message, user_id, context)
        elif task_type == "meeting_notes":
            return await self._handle_meeting_notes(user_message, user_id, context)
        elif task_type == "work_journal":
            return await self._handle_work_journal(user_message, user_id, context)
        elif task_type == "status_report":
            return await self._handle_status_report(user_message, user_id, context)
        elif task_type == "daily_briefing":
            return await self._handle_daily_briefing(user_message, user_id, context)
        else:
            return await self._handle_general_productivity_task(user_message, user_id, context)

    async def _classify_task(self, user_message: str, context: Dict[str, Any]) -> str:
        """Classify the type of productivity task"""
        
        prompt = f"""Classify the following productivity-related request into one of these categories:
- calendar_management: Calendar events, meetings, scheduling
- task_management: Tasks, to-dos, reminders
- email_assistance: Email drafting, management
- meeting_notes: Meeting notes, summaries
- work_journal: Work journal entries, work history
- status_report: Status reports, progress updates
- daily_briefing: Daily briefings, priorities
- general: General productivity questions

User request: {user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond with just the category name."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        return response.strip().lower().replace("-", "_")

    async def _handle_calendar_management(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar management requests"""
        
        # Extract calendar details
        calendar_details = await self._extract_calendar_details(user_message, context)
        
        # For now, store as memory (future: integrate with Outlook/Teams)
        if calendar_details.get("action") == "add_event":
            memory_id = await memory_service.store_long_term_memory(
                user_id=user_id,
                memory_type=MemoryType.PROJECT,
                content=f"Calendar event: {calendar_details.get('title', '')} at {calendar_details.get('time', '')}",
                importance=0.7,
                source="calendar",
                metadata=calendar_details
            )
            
            return {
                "response": f"Calendar event added: {calendar_details.get('title', '')}",
                "memory_id": memory_id,
                "event_details": calendar_details
            }
        
        elif calendar_details.get("action") == "list_events":
            # Retrieve calendar-related memories
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query="calendar events meetings schedule",
                memory_type=MemoryType.PROJECT,
                limit=10
            )
            
            events_summary = await self._summarize_calendar_events(memories)
            
            return {
                "response": events_summary,
                "events_found": len(memories)
            }
        
        else:
            return {
                "response": "I can help you add calendar events or list your upcoming events. What would you like to do?",
                "requires_confirmation": True
            }

    async def _handle_task_management(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task management requests"""
        
        # Extract task details
        task_details = await self._extract_task_details(user_message, context)
        
        if task_details.get("action") == "add_task":
            memory_id = await memory_service.store_long_term_memory(
                user_id=user_id,
                memory_type=MemoryType.PROJECT,
                content=f"Task: {task_details.get('description', '')}",
                importance=task_details.get("priority", 0.5),
                source="tasks",
                metadata=task_details
            )
            
            return {
                "response": f"Task added: {task_details.get('description', '')}",
                "memory_id": memory_id,
                "task_details": task_details
            }
        
        elif task_details.get("action") == "list_tasks":
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query="tasks to-dos action items",
                memory_type=MemoryType.PROJECT,
                limit=10
            )
            
            tasks_summary = await self._summarize_tasks(memories)
            
            return {
                "response": tasks_summary,
                "tasks_found": len(memories)
            }
        
        else:
            return {
                "response": "I can help you add tasks or list your current tasks. What would you like to do?",
                "requires_confirmation": True
            }

    async def _handle_email_assistance(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email assistance requests"""
        
        # Extract email details
        email_details = await self._extract_email_details(user_message, context)
        
        if email_details.get("action") == "draft_email":
            draft = await self._draft_email(
                email_details.get("recipient", ""),
                email_details.get("subject", ""),
                email_details.get("content", ""),
                email_details.get("tone", "professional")
            )
            
            return {
                "response": draft,
                "email_details": email_details,
                "requires_confirmation": True
            }
        
        else:
            return {
                "response": "I can help you draft emails. Please provide the recipient, subject, and key points you want to include.",
                "requires_confirmation": True
            }

    async def _handle_meeting_notes(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meeting notes requests"""
        
        # Extract meeting details
        meeting_details = await self._extract_meeting_details(user_message, context)
        
        if meeting_details.get("action") == "capture_notes":
            memory_id = await memory_service.store_long_term_memory(
                user_id=user_id,
                memory_type=MemoryType.WORK_JOURNAL,
                content=f"Meeting notes: {meeting_details.get('notes', '')}",
                importance=0.8,
                source="meeting",
                metadata=meeting_details
            )
            
            # Also generate a summary
            summary = await self._summarize_meeting(meeting_details)
            
            return {
                "response": f"Meeting notes captured. Summary: {summary}",
                "memory_id": memory_id,
                "meeting_details": meeting_details
            }
        
        elif meeting_details.get("action") == "search_notes":
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=meeting_details.get("search_query", "meeting notes"),
                memory_type=MemoryType.WORK_JOURNAL,
                limit=5
            )
            
            notes_summary = await self._summarize_meeting_notes(memories)
            
            return {
                "response": notes_summary,
                "notes_found": len(memories)
            }
        
        else:
            return {
                "response": "I can help you capture meeting notes or search through past meeting notes. What would you like to do?",
                "requires_confirmation": True
            }

    async def _handle_work_journal(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle work journal requests"""
        
        # Extract journal details
        journal_details = await self._extract_journal_details(user_message, context)
        
        if journal_details.get("action") == "add_entry":
            memory_id = await memory_service.store_long_term_memory(
                user_id=user_id,
                memory_type=MemoryType.WORK_JOURNAL,
                content=f"Work journal: {journal_details.get('entry', '')}",
                importance=0.6,
                source="work_journal",
                metadata=journal_details
            )
            
            return {
                "response": "Work journal entry added",
                "memory_id": memory_id,
                "journal_details": journal_details
            }
        
        elif journal_details.get("action") == "query_journal":
            time_range = journal_details.get("time_range", "week")
            
            # Build query based on time range
            if time_range == "today":
                query = "work journal today"
            elif time_range == "week":
                query = "work journal this week"
            elif time_range == "month":
                query = "work journal this month"
            else:
                query = f"work journal {time_range}"
            
            memories = await memory_service.retrieve_memories(
                user_id=user_id,
                query=query,
                memory_type=MemoryType.WORK_JOURNAL,
                limit=10
            )
            
            journal_summary = await self._summarize_work_journal(user_message, memories)
            
            return {
                "response": journal_summary,
                "entries_found": len(memories),
                "time_range": time_range
            }
        
        else:
            return {
                "response": "I can help you add work journal entries or query your work history. What would you like to do?",
                "requires_confirmation": True
            }

    async def _handle_status_report(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status report requests"""
        
        # Extract report details
        report_details = await self._extract_report_details(user_message, context)
        
        # Retrieve relevant work information
        time_range = report_details.get("time_range", "week")
        
        # Get work journal entries
        memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query=f"work completed tasks projects {time_range}",
            memory_type=MemoryType.WORK_JOURNAL,
            limit=15
        )
        
        # Get project information
        project_memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query="projects milestones deliverables",
            memory_type=MemoryType.PROJECT,
            limit=10
        )
        
        # Generate status report
        report = await self._generate_status_report(
            user_message,
            memories,
            project_memories,
            report_details
        )
        
        return {
            "response": report,
            "time_range": time_range,
            "journal_entries": len(memories),
            "projects": len(project_memories)
        }

    async def _handle_daily_briefing(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle daily briefing requests"""
        
        # Get today's priorities
        tasks = await memory_service.retrieve_memories(
            user_id=user_id,
            query="tasks priorities today",
            memory_type=MemoryType.PROJECT,
            limit=5
        )
        
        # Get recent work
        recent_work = await memory_service.retrieve_memories(
            user_id=user_id,
            query="work journal yesterday recent work",
            memory_type=MemoryType.WORK_JOURNAL,
            limit=5
        )
        
        # Get upcoming meetings
        meetings = await memory_service.retrieve_memories(
            user_id=user_id,
            query="calendar meetings today upcoming",
            memory_type=MemoryType.PROJECT,
            limit=5
        )
        
        # Generate daily briefing
        briefing = await self._generate_daily_briefing(
            user_message,
            tasks,
            recent_work,
            meetings
        )
        
        return {
            "response": briefing,
            "tasks_count": len(tasks),
            "recent_work_count": len(recent_work),
            "meetings_count": len(meetings)
        }

    async def _handle_general_productivity_task(self, user_message: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general productivity questions"""
        
        prompt = f"""Answer this productivity-related question:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Provide helpful, actionable advice for productivity and work management."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.5)
        
        return {
            "response": response
        }

    async def _extract_calendar_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract calendar details from user message"""
        
        prompt = f"""Extract calendar details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (add_event, list_events)
- title: event title (if adding)
- time: event time (if adding)
- duration: event duration (if adding)
- attendees: event attendees (if adding)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_task_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract task details from user message"""
        
        prompt = f"""Extract task details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (add_task, list_tasks, complete_task)
- description: task description
- priority: task priority (0.0 to 1.0)
- due_date: task due date (if specified)
- project: related project (if specified)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_email_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract email details from user message"""
        
        prompt = f"""Extract email details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (draft_email, send_email)
- recipient: email recipient
- subject: email subject
- content: key points to include in email
- tone: email tone (professional, casual, formal)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_meeting_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meeting details from user message"""
        
        prompt = f"""Extract meeting details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (capture_notes, search_notes)
- notes: meeting notes (if capturing)
- search_query: search query (if searching)
- attendees: meeting attendees
- date: meeting date"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_journal_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract journal details from user message"""
        
        prompt = f"""Extract journal details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- action: type of action (add_entry, query_journal)
- entry: journal entry (if adding)
- time_range: time range for query (today, week, month)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}

    async def _extract_report_details(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract report details from user message"""
        
        prompt = f"""Extract report details from this request:

{user_message}

Context: {json.dumps(context, indent=2) if context else "None"}

Respond in JSON format with these fields:
- time_range: time range for report (day, week, month)
- report_type: type of report (status, progress, summary)
- audience: target audience (manager, team, client)"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.call_llm(messages, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"time_range": "week", "report_type": "status"}

    async def _draft_email(self, recipient: str, subject: str, content: str, tone: str) -> str:
        """Draft an email"""
        
        prompt = f"""Draft a {tone} email with the following details:

To: {recipient}
Subject: {subject}
Key points to include: {content}

Write a complete, professional email."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _summarize_calendar_events(self, memories: List[Dict[str, Any]]) -> str:
        """Summarize calendar events"""
        
        events = [m['payload'] for m in memories]
        
        prompt = f"""Summarize these calendar events:

{json.dumps(events, indent=2)}

Provide a clear summary of upcoming events and meetings."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _summarize_tasks(self, memories: List[Dict[str, Any]]) -> str:
        """Summarize tasks"""
        
        tasks = [m['payload'] for m in memories]
        
        prompt = f"""Summarize these tasks:

{json.dumps(tasks, indent=2)}

Provide a clear summary of current tasks and their priorities."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _summarize_meeting(self, meeting_details: Dict[str, Any]) -> str:
        """Summarize meeting"""
        
        prompt = f"""Summarize this meeting:

{json.dumps(meeting_details, indent=2)}

Provide a brief summary of the key points and action items."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _summarize_meeting_notes(self, memories: List[Dict[str, Any]]) -> str:
        """Summarize meeting notes"""
        
        notes = [m['payload'] for m in memories]
        
        prompt = f"""Summarize these meeting notes:

{json.dumps(notes, indent=2)}

Provide a clear summary of past meetings and key decisions."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _summarize_work_journal(self, user_message: str, memories: List[Dict[str, Any]]) -> str:
        """Summarize work journal"""
        
        entries = [m['payload'] for m in memories]
        
        prompt = f"""Summarize this work journal in response to the user's request:

User request: {user_message}

Journal entries:
{json.dumps(entries, indent=2)}

Provide a clear summary of work activities and accomplishments."""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _generate_status_report(
        self,
        user_message: str,
        work_memories: List[Dict[str, Any]],
        project_memories: List[Dict[str, Any]],
        report_details: Dict[str, Any]
    ) -> str:
        """Generate status report"""
        
        prompt = f"""Generate a {report_details.get('report_type', 'status')} report for {report_details.get('time_range', 'week')}:

User request: {user_message}

Work completed:
{json.dumps([m['payload'] for m in work_memories], indent=2)}

Projects:
{json.dumps([m['payload'] for m in project_memories], indent=2)}

Generate a professional status report with:
1. Summary of work completed
2. Current project status
3. Key achievements
4. Blockers or challenges
5. Next steps"""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)

    async def _generate_daily_briefing(
        self,
        user_message: str,
        tasks: List[Dict[str, Any]],
        recent_work: List[Dict[str, Any]],
        meetings: List[Dict[str, Any]]
    ) -> str:
        """Generate daily briefing"""
        
        prompt = f"""Generate a daily briefing:

User request: {user_message}

Today's priorities:
{json.dumps([m['payload'] for m in tasks], indent=2)}

Recent work:
{json.dumps([m['payload'] for m in recent_work], indent=2)}

Upcoming meetings:
{json.dumps([m['payload'] for m in meetings], indent=2)}

Generate a concise daily briefing covering:
1. Today's top priorities
2. Recent work context
3. Upcoming meetings
4. Recommended focus areas"""

        messages = [{"role": "user", "content": prompt}]
        return await self.call_llm(messages, temperature=0.5)
