"""
Calendar Agent Module.

A specialized agent for handling calendar-related tasks using LangChain.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from src.config import get_llm
from src.tools.calendar_tools import (
    create_calendar_event,
    delete_calendar_event,
    get_available_time_slots,
    list_upcoming_events,
    update_calendar_event,
)


# Calendar Agent System Prompt
CALENDAR_AGENT_PROMPT = """You are a calendar scheduling assistant with access to Google Calendar.

Your capabilities:
1. Create calendar events with specific times and attendees
2. Check availability for specific dates
3. List upcoming events
4. Update or delete existing events

When parsing natural language dates and times:
- "next Tuesday" means the upcoming Tuesday from today
- "tomorrow" means the day after today
- "at 2pm" means 14:00:00
- Always use ISO format for dates (YYYY-MM-DD) and times (HH:MM:SS)

Current date and time: {current_datetime}
Timezone: Asia/Kolkata (IST)

Guidelines:
- Always confirm the exact date/time before creating events
- When checking availability, use the get_available_time_slots tool first
- Include all relevant attendee emails when creating meetings
- Provide clear confirmations with event details
- If a time is ambiguous, ask for clarification

Be helpful, accurate, and always confirm what was scheduled in your final response."""


def get_current_datetime_str() -> str:
    """Get current datetime as a formatted string."""
    tz = ZoneInfo("Asia/Kolkata")
    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y at %I:%M %p %Z")


def create_calendar_agent():
    """
    Create a calendar agent with access to Google Calendar tools.
    
    Returns:
        A LangChain agent configured for calendar management.
    """
    llm = get_llm(temperature=0.3)  # Lower temperature for more precise scheduling
    
    tools = [
        create_calendar_event,
        get_available_time_slots,
        list_upcoming_events,
        delete_calendar_event,
        update_calendar_event,
    ]
    
    # Format the prompt with current datetime
    system_prompt = CALENDAR_AGENT_PROMPT.format(
        current_datetime=get_current_datetime_str()
    )
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )
    
    return agent


# Cached agent instance
_calendar_agent = None


def get_calendar_agent():
    """Get or create the calendar agent singleton."""
    global _calendar_agent
    if _calendar_agent is None:
        _calendar_agent = create_calendar_agent()
    return _calendar_agent


@tool
def calendar_agent_tool(request: str) -> str:
    """
    Schedule and manage calendar events using natural language.

    Use this tool when the user wants to:
    - Create, modify, or delete calendar appointments
    - Check availability for meetings
    - View upcoming scheduled events
    - Schedule meetings with attendees

    Args:
        request: Natural language scheduling request.
                Examples: 
                - "Schedule a team meeting tomorrow at 2pm"
                - "What's on my calendar this week?"
                - "Check availability for Friday afternoon"
                
    Returns:
        Result of the calendar operation.
    """
    agent = get_calendar_agent()
    
    # Add current datetime context to the request
    context = f"Current datetime: {get_current_datetime_str()}\n\nUser request: {request}"
    
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": context}]
        })
        
        # Extract the final message
        if result and "messages" in result and result["messages"]:
            final_message = result["messages"][-1]
            content = final_message.content if hasattr(final_message, "content") else str(final_message)
            
            if isinstance(content, list):
                # Handle Gemini parts (list of dicts)
                return "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
            return str(content)
        
        return "Calendar operation completed."
        
    except Exception as e:
        return f"❌ Calendar agent error: {str(e)}"
