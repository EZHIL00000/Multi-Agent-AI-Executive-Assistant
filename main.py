#!/usr/bin/env python3
"""
Personal Assistant - Interactive CLI

A multi-agent personal assistant with Google Calendar and Gmail integration.
Run with: python main.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.theme import Theme
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from src.config import Config
from src.agents.supervisor import PersonalAssistant


# Custom theme for rich console
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "user": "bold blue",
    "assistant": "bold magenta",
})

console = Console(theme=custom_theme)


def display_welcome():
    """Display welcome message and setup status."""
    welcome_text = """
# 🤖 Personal Assistant

Welcome to your AI-powered Personal Assistant!

**Capabilities:**
- 📅 **Calendar Management**: Schedule meetings, check availability, manage events
- 📧 **Email Communication**: Send emails, create drafts, search inbox

**Example commands:**
- "Schedule a meeting tomorrow at 2pm with john@example.com"
- "What's on my calendar this week?"
- "Send an email to the team about the project update"
- "Check if I'm free on Friday afternoon"

Type `help` for more commands, or `quit` to exit.
    """
    
    console.print(Panel(
        Markdown(welcome_text),
        title="[bold cyan]Welcome[/bold cyan]",
        border_style="cyan",
    ))


def display_help():
    """Display help information."""
    help_text = """
## Available Commands

| Command | Description |
|---------|-------------|
| `help` | Show this help message |
| `quit` / `exit` | Exit the assistant |
| `clear` | Clear conversation history |
| `status` | Show connection status |

## Example Requests

### Calendar
- "Schedule a meeting with Sarah tomorrow at 3pm"
- "What meetings do I have this week?"
- "Check availability for Friday afternoon"
- "Cancel my 2pm meeting"

### Email
- "Send John an email about the project deadline"
- "Draft an update email to the team"
- "Search for emails from the client"
- "What unread emails do I have?"

### Combined
- "Schedule a call with Alex and send them a reminder email"
    """
    console.print(Markdown(help_text))


def check_configuration() -> bool:
    """Check if the configuration is valid."""
    missing = Config.validate()
    
    if missing:
        console.print(Panel(
            f"[error]Missing configuration:[/error]\n" +
            "\n".join([f"  • {item}" for item in missing]) +
            "\n\nPlease set these in your .env file or environment variables.",
            title="[error]Configuration Error[/error]",
            border_style="red",
        ))
        return False
    
    return True


def check_google_auth() -> bool:
    """Check Google OAuth setup."""
    from src.config import get_credentials_path
    
    creds_path = get_credentials_path()
    if not creds_path.exists():
        console.print(Panel(
            "[warning]Google OAuth credentials not found.[/warning]\n\n"
            "To use Calendar and Gmail features, you need to set up OAuth:\n\n"
            "1. Go to [link=https://console.cloud.google.com/]Google Cloud Console[/link]\n"
            "2. Create a project and enable Calendar & Gmail APIs\n"
            "3. Create OAuth 2.0 credentials (Desktop application)\n"
            "4. Download and save as 'credentials.json' in the project root\n\n"
            "See README.md for detailed instructions.",
            title="[warning]Setup Required[/warning]",
            border_style="yellow",
        ))
        return False
    
    return True


def display_status():
    """Display current configuration status."""
    from src.config import get_credentials_path, get_token_path
    
    status_items = []
    
    # Check API key
    if Config.GOOGLE_API_KEY:
        status_items.append("✅ Google API Key: Configured")
    else:
        status_items.append("❌ Google API Key: Not configured")
    
    # Check OAuth credentials
    if get_credentials_path().exists():
        status_items.append("✅ OAuth Credentials: Found")
    else:
        status_items.append("❌ OAuth Credentials: Not found")
    
    # Check OAuth token
    if get_token_path().exists():
        status_items.append("✅ OAuth Token: Authenticated")
    else:
        status_items.append("⚠️ OAuth Token: Not authenticated (will prompt on first use)")
    
    # Check LangSmith
    if Config.LANGSMITH_TRACING:
        status_items.append("✅ LangSmith Tracing: Enabled")
    else:
        status_items.append("ℹ️ LangSmith Tracing: Disabled")
    
    # User info
    status_items.append(f"👤 User: {Config.USER_NAME} ({Config.USER_EMAIL})")
    status_items.append(f"🤖 Model: {Config.MODEL_NAME}")
    
    console.print(Panel(
        "\n".join(status_items),
        title="[cyan]Status[/cyan]",
        border_style="cyan",
    ))


def main():
    """Main entry point for the CLI."""
    console.print()
    display_welcome()
    
    # Check configuration
    if not check_configuration():
        console.print("\n[error]Please configure the application before running.[/error]")
        console.print("Copy .env.example to .env and add your API keys.")
        return 1
    
    # Check Google OAuth (warning only)
    check_google_auth()
    
    console.print()
    
    # Initialize the assistant
    try:
        console.print("[info]Initializing assistant...[/info]")
        assistant = PersonalAssistant(name="Assistant")
        console.print("[success]Assistant ready![/success]\n")
    except Exception as e:
        console.print(f"[error]Failed to initialize assistant: {e}[/error]")
        return 1
    
    # Set up command history
    history_file = project_root / ".assistant_history"
    history = FileHistory(str(history_file))
    
    # Main conversation loop
    while True:
        try:
            # Get user input with history and auto-suggest
            user_input = prompt(
                "You: ",
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
            ).strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            lower_input = user_input.lower()
            
            if lower_input in ["quit", "exit", "q"]:
                console.print("\n[info]Goodbye! 👋[/info]")
                break
            
            if lower_input == "help":
                display_help()
                continue
            
            if lower_input == "clear":
                assistant.reset_conversation()
                console.print("[info]Conversation cleared.[/info]\n")
                continue
            
            if lower_input == "status":
                display_status()
                continue
            
            # Stream the response
            console.print()
            console.print("[assistant]Assistant:[/assistant]", end=" ")
            
            try:
                response = assistant.chat(user_input)
                
                # Display response with markdown formatting
                console.print()
                console.print(Panel(
                    Markdown(response),
                    border_style="magenta",
                    padding=(1, 2),
                ))
                console.print()
                
            except Exception as e:
                console.print(f"\n[error]Error: {e}[/error]\n")
                
        except KeyboardInterrupt:
            console.print("\n[info]Use 'quit' to exit.[/info]")
            continue
        except EOFError:
            console.print("\n[info]Goodbye! 👋[/info]")
            break
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
