# 🤖 Personal Assistant with Multi-Agent Architecture

A production-ready **multi-agent AI personal assistant** built with LangChain, featuring Google Calendar and Gmail integration. This project demonstrates the **supervisor pattern** for AI agent orchestration.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## 🎯 Project Overview

This project showcases advanced AI engineering concepts:

- **Multi-Agent Systems**: Supervisor pattern coordinating specialized sub-agents
- **Real API Integration**: Google Calendar and Gmail APIs (not stubs!)
- **Human-in-the-Loop**: Review and approve sensitive actions
- **Conversation Memory**: Maintains context across interactions
- **Rich CLI Interface**: Beautiful terminal experience

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         USER                                  │
└──────────────────────────┬───────────────────────────────────┘
                           │ Natural Language
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   SUPERVISOR AGENT                            │
│  • Routes requests to appropriate sub-agents                  │
│  • Coordinates multi-domain tasks                             │
│  • Synthesizes responses                                      │
└───────────────┬─────────────────────────────┬────────────────┘
                │                             │
        ┌───────▼───────┐             ┌───────▼───────┐
        │ CALENDAR AGENT │             │  EMAIL AGENT  │
        │  • Scheduling  │             │  • Composing  │
        │  • Availability│             │  • Sending    │
        │  • Events      │             │  • Searching  │
        └───────┬───────┘             └───────┬───────┘
                │                             │
        ┌───────▼───────┐             ┌───────▼───────┐
        │ Google Calendar│             │    Gmail      │
        │      API       │             │     API       │
        └───────────────┘             └───────────────┘
```

## ✨ Features

### Calendar Management
- ✅ Create events with attendees
- ✅ Check availability for meetings
- ✅ List upcoming events
- ✅ Update and delete events
- ✅ Natural language date parsing ("next Tuesday at 2pm")

### Email Communication
- ✅ Send emails with CC/BCC
- ✅ Create drafts
- ✅ Search inbox
- ✅ Read email content
- ✅ Professional email composition

### AI Capabilities
- ✅ Multi-agent coordination
- ✅ Context-aware responses
- ✅ Conversation memory
- ✅ Complex request handling

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Cloud account (for Calendar and Gmail APIs)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   cd "PERSONAL ASSISTANT"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

5. **Set up Google OAuth** (see detailed instructions below)

6. **Run the assistant**
   ```bash
   python main.py
   ```

## 🔐 Google API Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Step 2: Enable APIs

Enable the following APIs for your project:

1. **Google Calendar API**
   - Go to [Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
   - Click "Enable"

2. **Gmail API**
   - Go to [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
   - Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Choose "External" user type
3. Fill in the required information:
   - App name: "Personal Assistant"
   - User support email: Your email
   - Developer contact: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.compose`
5. Add your email as a test user

### Step 4: Create OAuth Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop application"
4. Name it "Personal Assistant Desktop"
5. Click "Create"
6. **Download the JSON file**
7. Rename it to `credentials.json`
8. Place it in the project root directory

### Step 5: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create an API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

## 📁 Project Structure

```
PERSONAL ASSISTANT/
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── credentials.json      # Google OAuth credentials (you create this)
├── token.json            # OAuth token (auto-generated)
├── main.py               # Interactive CLI entry point
├── demo.py               # Portfolio demo script
└── src/
    ├── __init__.py
    ├── config.py         # Configuration management
    ├── tools/
    │   ├── __init__.py
    │   ├── google_auth.py    # OAuth authentication
    │   ├── calendar_tools.py # Calendar API tools
    │   └── email_tools.py    # Gmail API tools
    ├── agents/
    │   ├── __init__.py
    │   ├── calendar_agent.py # Calendar specialist
    │   ├── email_agent.py    # Email specialist
    │   └── supervisor.py     # Supervisor agent
    └── middleware/
        ├── __init__.py
        └── human_review.py   # Human-in-the-loop logic
```

## 💻 Usage

### Interactive Mode

```bash
python main.py
```

Example interactions:
```
You: Schedule a meeting with john@example.com tomorrow at 3pm
Assistant: ✅ Event created successfully!
📅 Title: Meeting
🕐 Start: 2026-01-13T15:00:00
🕑 End: 2026-01-13T16:00:00
👥 Attendees: john@example.com

You: What's on my calendar this week?
Assistant: 📅 Upcoming events (next 7 days):
• Team Meeting - Mon, Jan 13 at 3:00 PM
• Project Review - Wed, Jan 15 at 10:00 AM

You: Send John an email reminder about our meeting
Assistant: ✅ Email sent successfully!
📧 To: john@example.com
📋 Subject: Meeting Reminder - Tomorrow at 3 PM
```

### Demo Mode

Run a pre-configured demonstration:

```bash
python demo.py
```

### Programmatic Usage

```python
from src.agents.supervisor import PersonalAssistant

# Create assistant
assistant = PersonalAssistant(name="My Assistant")

# Chat
response = assistant.chat("Schedule a meeting tomorrow at 2pm")
print(response)

# Reset conversation
assistant.reset_conversation()
```

## 🛠️ API Reference

### Calendar Tools

| Tool | Description |
|------|-------------|
| `create_calendar_event` | Create a new calendar event |
| `get_available_time_slots` | Check availability for a date |
| `list_upcoming_events` | List upcoming calendar events |
| `update_calendar_event` | Modify an existing event |
| `delete_calendar_event` | Remove a calendar event |

### Email Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send an email via Gmail |
| `draft_email` | Create an email draft |
| `search_emails` | Search inbox with query |
| `get_email_content` | Read full email content |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ |
| `USER_EMAIL` | Your Gmail address | ✅ |
| `USER_NAME` | Your name (for signatures) | ✅ |
| `MODEL_NAME` | Gemini model (default: gemini-2.0-flash) | ❌ |
| `LANGSMITH_TRACING` | Enable LangSmith tracing | ❌ |
| `LANGSMITH_API_KEY` | LangSmith API key | ❌ |

## ❓ Troubleshooting

### Common Issues

**"GOOGLE_API_KEY is not configured"**
- Ensure you have a `.env` file with your Gemini API key
- Run `copy .env.example .env` and add your key

**"credentials.json not found"**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in the project root

**"Access denied" during OAuth**
- Add your email as a test user in OAuth consent screen
- Make sure the correct scopes are enabled

**"Quota exceeded"**
- Google APIs have rate limits
- Wait and try again, or check your quota in Cloud Console

## 📝 Resume Description

> **Personal Assistant with Multi-Agent Architecture**
> 
> Built a production-ready AI personal assistant using LangChain's supervisor pattern. The system features:
> - Multi-agent orchestration with specialized Calendar and Email agents
> - Real integration with Google Calendar and Gmail APIs
> - Human-in-the-loop review for sensitive actions
> - Interactive CLI with rich terminal UI
> - Conversation memory for context-aware responses
> 
> **Technologies**: Python, LangChain, LangGraph, Google Gemini, Google Calendar API, Gmail API, OAuth 2.0

## 📄 License

MIT License - feel free to use this project for learning and portfolio purposes.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) for the agent framework
- [Google AI](https://ai.google.dev/) for Gemini API
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

---

Made with ❤️ by Ezhil
