#!/usr/bin/env python3
"""
Personal Assistant - Demo Script

This demo showcases the multi-agent personal assistant capabilities.
Perfect for portfolio demonstrations and testing.

Run with: python demo.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import Config
from src.agents.supervisor import PersonalAssistant


console = Console()


def print_header():
    """Print demo header."""
    header = """
# 🤖 Personal Assistant Demo

This demo showcases a **multi-agent AI system** with:
- 📅 **Calendar Agent**: Google Calendar integration
- 📧 **Email Agent**: Gmail integration  
- 🎯 **Supervisor Agent**: Intelligent task routing

Built with **LangChain** and **Google Gemini**.
    """
    console.print(Panel(
        Markdown(header),
        title="[bold cyan]Portfolio Demo[/bold cyan]",
        border_style="cyan",
    ))


def demo_request(assistant: PersonalAssistant, request: str, description: str):
    """Execute a demo request and display results."""
    console.print()
    console.print(Panel(
        f"[bold]{description}[/bold]\n\n[dim italic]\"{request}\"[/dim italic]",
        title="[yellow]Demo Request[/yellow]",
        border_style="yellow",
    ))
    
    console.print()
    
    # Show processing spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Processing with AI agents...", total=None)
        
        try:
            response = assistant.chat(request)
        except Exception as e:
            response = f"❌ Error: {str(e)}"
    
    # Display response
    console.print(Panel(
        Markdown(response),
        title="[green]Assistant Response[/green]",
        border_style="green",
        padding=(1, 2),
    ))
    
    console.print()
    console.print("[dim]─" * 60 + "[/dim]")


def run_demo():
    """Run the full demo sequence."""
    print_header()
    
    # Check configuration
    missing = Config.validate()
    if missing:
        console.print(Panel(
            f"[red]Missing configuration: {', '.join(missing)}[/red]\n\n"
            "Please set up your .env file before running the demo.\n"
            "Copy .env.example to .env and add your API keys.",
            title="[red]Configuration Error[/red]",
            border_style="red",
        ))
        return 1
    
    console.print("\n[cyan]Initializing Personal Assistant...[/cyan]")
    
    try:
        assistant = PersonalAssistant(name="Demo Assistant")
        console.print("[green]✅ Assistant initialized successfully![/green]\n")
    except Exception as e:
        console.print(f"[red]Failed to initialize: {e}[/red]")
        return 1
    
    console.print("[bold yellow]Starting demo sequence...[/bold yellow]")
    console.print("[dim]Press Ctrl+C to skip to the next demo or exit.[/dim]\n")
    
    # Demo 1: List upcoming events
    try:
        demo_request(
            assistant,
            "What's on my calendar for the next 3 days?",
            "📅 Demo 1: Viewing Calendar",
        )
        time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Skipped.[/yellow]")
    
    # Demo 2: Check availability
    try:
        demo_request(
            assistant,
            "Am I free tomorrow afternoon between 2pm and 5pm?",
            "📅 Demo 2: Checking Availability", 
        )
        time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Skipped.[/yellow]")
    
    # Demo 3: Schedule a meeting
    try:
        demo_request(
            assistant,
            "Schedule a team sync meeting for tomorrow at 3pm for 30 minutes",
            "📅 Demo 3: Creating Calendar Event",
        )
        time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Skipped.[/yellow]")
    
    # Demo 4: Search emails
    try:
        demo_request(
            assistant,
            "Search for recent emails in my inbox",
            "📧 Demo 4: Searching Emails",
        )
        time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Skipped.[/yellow]")
    
    # Demo 5: Draft an email
    try:
        demo_request(
            assistant,
            "Draft an email to demo@example.com about the project status update",
            "📧 Demo 5: Drafting Email",
        )
        time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[yellow]Skipped.[/yellow]")
    
    # Demo 6: Multi-agent coordination
    try:
        demo_request(
            assistant,
            "Check what meetings I have tomorrow and summarize them for me",
            "🎯 Demo 6: Multi-Agent Coordination",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Skipped.[/yellow]")
    
    # Summary
    console.print()
    console.print(Panel(
        Markdown("""
## Demo Complete! 🎉

This demonstration showed:

1. **Calendar Agent** - Managing Google Calendar events
2. **Email Agent** - Composing and managing Gmail
3. **Supervisor Agent** - Routing requests to the right specialist

### Architecture Highlights

- **Supervisor Pattern**: Central agent coordinates specialized workers
- **Tool Abstraction**: Sub-agents wrapped as high-level tools
- **Real API Integration**: Connected to Google Calendar & Gmail
- **Conversation Memory**: Maintains context across requests

### Technologies Used

- 🧠 **LangChain** - Agent framework
- 💎 **Google Gemini** - LLM backbone
- 📅 **Google Calendar API** - Event management
- 📧 **Gmail API** - Email operations
- 🎨 **Rich** - Beautiful terminal UI

---

*Run `python main.py` for interactive mode!*
        """),
        title="[bold green]Summary[/bold green]",
        border_style="green",
    ))
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_demo())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted.[/yellow]")
        sys.exit(0)
