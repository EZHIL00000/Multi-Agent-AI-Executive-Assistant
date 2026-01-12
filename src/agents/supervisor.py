"""
Supervisor Agent Module.

The supervisor agent coordinates specialized sub-agents for comprehensive
personal assistant functionality.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from src.config import get_llm, Config
from src.agents.calendar_agent import calendar_agent_tool
from src.agents.email_agent import email_agent_tool


# Supervisor System Prompt
SUPERVISOR_PROMPT = """You are a helpful personal assistant named "{assistant_name}".

You coordinate two specialized capabilities:
1. **Calendar Management** (schedule_event): Schedule meetings, check availability, manage events
2. **Email Communication** (manage_email): Send emails, create drafts, search inbox

Current date and time: {current_datetime}
User: {user_name} ({user_email})

Your approach:
1. Understand what the user needs
2. Break down complex requests into separate tasks
3. Use the appropriate tool(s) to complete each task
4. Coordinate results from multiple tools when needed
5. Provide a clear, unified response

When a request involves multiple actions (e.g., "schedule a meeting AND send invites"):
- Use multiple tools in sequence or parallel
- Synthesize the results into a coherent response

Guidelines:
- Be conversational and helpful
- Confirm important actions before executing (especially emails)
- When information is missing, ask for clarification
- Provide clear summaries of what was done

Examples of requests you can handle:
- "Schedule a meeting with the team tomorrow at 2pm and send them a reminder"
- "What's on my calendar this week?"
- "Draft an email to John about the project status"
- "Check if I'm free on Friday afternoon for a call"

Always be professional, friendly, and proactive in helping the user."""


def get_current_datetime_str() -> str:
    """Get current datetime as a formatted string."""
    tz = ZoneInfo("Asia/Kolkata")
    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y at %I:%M %p %Z")


def create_supervisor_agent(with_memory: bool = True, assistant_name: str = "Assistant"):
    """
    Create the supervisor agent that coordinates calendar and email sub-agents.
    
    Args:
        with_memory: Whether to enable conversation memory.
        assistant_name: Name for the assistant.
        
    Returns:
        A LangChain supervisor agent.
    """
    llm = get_llm(temperature=0.7)
    
    # Wrap sub-agents as tools
    tools = [
        calendar_agent_tool,
        email_agent_tool,
    ]
    
    # Format the system prompt
    system_prompt = SUPERVISOR_PROMPT.format(
        assistant_name=assistant_name,
        current_datetime=get_current_datetime_str(),
        user_name=Config.USER_NAME,
        user_email=Config.USER_EMAIL,
    )
    
    # Create with optional memory
    checkpointer = MemorySaver() if with_memory else None
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=checkpointer,
    )
    
    return agent


def run_supervisor(
    request: str,
    agent=None,
    thread_id: str = "default",
    stream: bool = False,
):
    """
    Run a request through the supervisor agent.
    
    Args:
        request: User's natural language request.
        agent: Optional pre-created agent instance.
        thread_id: Thread ID for conversation memory.
        stream: Whether to stream the response.
        
    Returns:
        The agent's response or a generator for streaming.
    """
    if agent is None:
        agent = create_supervisor_agent()
    
    config = {"configurable": {"thread_id": thread_id}}
    
    if stream:
        return agent.stream(
            {"messages": [{"role": "user", "content": request}]},
            config,
        )
    else:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": request}]},
            config,
        )
        
        if result and "messages" in result and result["messages"]:
            final_message = result["messages"][-1]
            content = final_message.content if hasattr(final_message, "content") else str(final_message)
            
            if isinstance(content, list):
                # Handle Gemini parts (list of dicts)
                return "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
            return str(content)
        
        return "Request completed."


class PersonalAssistant:
    """
    High-level Personal Assistant class for easy usage.
    
    Example:
        assistant = PersonalAssistant()
        response = assistant.chat("Schedule a meeting tomorrow at 2pm")
        print(response)
    """
    
    def __init__(self, name: str = "Assistant"):
        """Initialize the personal assistant."""
        self.name = name
        self.agent = create_supervisor_agent(with_memory=True, assistant_name=name)
        self.thread_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def chat(self, message: str) -> str:
        """
        Send a message to the assistant and get a response.
        
        Args:
            message: User's message.
            
        Returns:
            Assistant's response.
        """
        return run_supervisor(
            request=message,
            agent=self.agent,
            thread_id=self.thread_id,
            stream=False,
        )
    
    def stream(self, message: str):
        """
        Stream a response from the assistant.
        
        Args:
            message: User's message.
            
        Yields:
            Response chunks.
        """
        return run_supervisor(
            request=message,
            agent=self.agent,
            thread_id=self.thread_id,
            stream=True,
        )
    
    def reset_conversation(self):
        """Start a new conversation thread."""
        self.thread_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
