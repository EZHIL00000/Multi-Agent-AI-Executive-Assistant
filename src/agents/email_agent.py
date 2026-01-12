"""
Email Agent Module.

A specialized agent for handling email-related tasks using LangChain and Gmail.
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from src.config import get_llm, Config
from src.tools.email_tools import (
    send_email,
    draft_email,
    search_emails,
    get_email_content,
)


# Email Agent System Prompt
EMAIL_AGENT_PROMPT = """You are an email assistant with access to Gmail.

Your capabilities:
1. Send emails to recipients
2. Create email drafts
3. Search through emails
4. Read email content

User Information:
- Name: {user_name}
- Email: {user_email}

Guidelines for composing emails:
- Write professional, clear, and concise emails
- Use appropriate greetings and sign-offs
- Match the tone to the context (formal for business, friendly for colleagues)
- Always include a clear subject line that summarizes the email
- Sign emails with the user's name

When extracting recipient information:
- "the team" or "design team" -> Ask for specific email addresses if not provided
- Use proper email format (name@domain.com)

Safety:
- Always confirm email content before sending
- Double-check recipient addresses
- For important emails, consider creating a draft first

Be helpful and always confirm what was sent in your final response."""


def create_email_agent():
    """
    Create an email agent with access to Gmail tools.
    
    Returns:
        A LangChain agent configured for email management.
    """
    llm = get_llm(temperature=0.5)  # Moderate temperature for natural writing
    
    tools = [
        send_email,
        draft_email,
        search_emails,
        get_email_content,
    ]
    
    # Format the prompt with user info
    system_prompt = EMAIL_AGENT_PROMPT.format(
        user_name=Config.USER_NAME,
        user_email=Config.USER_EMAIL,
    )
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )
    
    return agent


# Cached agent instance
_email_agent = None


def get_email_agent():
    """Get or create the email agent singleton."""
    global _email_agent
    if _email_agent is None:
        _email_agent = create_email_agent()
    return _email_agent


@tool
def email_agent_tool(request: str) -> str:
    """
    Compose and send emails using natural language.

    Use this tool when the user wants to:
    - Send emails, notifications, or reminders
    - Create email drafts
    - Search through their inbox
    - Read email content

    Args:
        request: Natural language email request.
                Examples:
                - "Send a meeting reminder to john@example.com"
                - "Draft an email to the team about the project update"
                - "Search for emails from the client"
                
    Returns:
        Result of the email operation.
    """
    agent = get_email_agent()
    
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": request}]
        })
        
        # Extract the final message
        if result and "messages" in result and result["messages"]:
            final_message = result["messages"][-1]
            content = final_message.content if hasattr(final_message, "content") else str(final_message)
            
            if isinstance(content, list):
                # Handle Gemini parts (list of dicts)
                return "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
            return str(content)
        
        return "Email operation completed."
        
    except Exception as e:
        return f"❌ Email agent error: {str(e)}"
