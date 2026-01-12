"""
Gmail Email Tools.

LangChain tools for interacting with Gmail API.
"""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from langchain_core.tools import tool

from src.tools.google_auth import get_cached_gmail_service
from src.config import Config


def create_message(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] = [],
    bcc: list[str] = [],
    html: bool = False,
) -> dict:
    """
    Create an email message.
    
    Args:
        to: List of recipient email addresses.
        subject: Email subject.
        body: Email body.
        cc: List of CC recipients.
        bcc: List of BCC recipients.
        html: Whether the body is HTML.
        
    Returns:
        Message object for Gmail API.
    """
    message = MIMEMultipart()
    message["to"] = ", ".join(to)
    message["subject"] = subject
    message["from"] = Config.USER_EMAIL
    
    if cc:
        message["cc"] = ", ".join(cc)
    if bcc:
        message["bcc"] = ", ".join(bcc)
    
    # Add body
    mime_type = "html" if html else "plain"
    message.attach(MIMEText(body, mime_type))
    
    # Encode the message
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw}


@tool
def send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] = [],
    bcc: list[str] = [],
) -> str:
    """
    Send an email using Gmail.
    
    Args:
        to: List of recipient email addresses.
        subject: Email subject line.
        body: Email body content.
        cc: Optional list of CC recipients.
        bcc: Optional list of BCC recipients.
        
    Returns:
        Confirmation message with details.
    """
    try:
        service = get_cached_gmail_service()
        
        # Validate recipients
        if not to:
            return "❌ Error: At least one recipient is required."
        
        # Create the message
        message = create_message(to, subject, body, cc, bcc)
        
        # Send the message
        sent_message = service.users().messages().send(
            userId="me",
            body=message,
        ).execute()
        
        message_id = sent_message.get("id", "N/A")
        
        result = f"✅ Email sent successfully!\n"
        result += f"📧 To: {', '.join(to)}\n"
        result += f"📋 Subject: {subject}\n"
        
        if cc:
            result += f"📋 CC: {', '.join(cc)}\n"
        
        result += f"🆔 Message ID: {message_id}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"


@tool
def draft_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] = [],
) -> str:
    """
    Create an email draft in Gmail (does not send).
    
    Args:
        to: List of recipient email addresses.
        subject: Email subject line.
        body: Email body content.
        cc: Optional list of CC recipients.
        
    Returns:
        Confirmation message with draft details.
    """
    try:
        service = get_cached_gmail_service()
        
        # Create the message
        message = create_message(to, subject, body, cc)
        
        # Create draft
        draft = service.users().drafts().create(
            userId="me",
            body={"message": message},
        ).execute()
        
        draft_id = draft.get("id", "N/A")
        
        result = f"✅ Draft created successfully!\n"
        result += f"📧 To: {', '.join(to)}\n"
        result += f"📋 Subject: {subject}\n"
        result += f"🆔 Draft ID: {draft_id}\n"
        result += f"💡 You can edit and send this draft from Gmail."
        
        return result
        
    except Exception as e:
        return f"❌ Failed to create draft: {str(e)}"


@tool
def search_emails(
    query: str,
    max_results: int = 10,
) -> str:
    """
    Search emails in Gmail.
    
    Args:
        query: Search query (Gmail search syntax).
               Examples: "from:john@example.com", "subject:meeting", "is:unread"
        max_results: Maximum number of results to return.
        
    Returns:
        List of matching emails with summaries.
    """
    try:
        service = get_cached_gmail_service()
        
        # Search for messages
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results,
        ).execute()
        
        messages = results.get("messages", [])
        
        if not messages:
            return f"📭 No emails found matching: '{query}'"
        
        result = f"📬 Found {len(messages)} email(s) matching '{query}':\n\n"
        
        for msg in messages:
            # Get message details
            msg_detail = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            
            headers = {h["name"]: h["value"] for h in msg_detail.get("payload", {}).get("headers", [])}
            
            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "No Subject")
            date = headers.get("Date", "Unknown")
            
            # Truncate long subjects
            if len(subject) > 50:
                subject = subject[:47] + "..."
            
            result += f"• **{subject}**\n"
            result += f"  From: {from_addr}\n"
            result += f"  Date: {date}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Failed to search emails: {str(e)}"


@tool
def get_email_content(message_id: str) -> str:
    """
    Get the full content of an email by its ID.
    
    Args:
        message_id: The Gmail message ID.
        
    Returns:
        Email content with headers and body.
    """
    try:
        service = get_cached_gmail_service()
        
        # Get full message
        message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full",
        ).execute()
        
        # Extract headers
        headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}
        
        from_addr = headers.get("From", "Unknown")
        to_addr = headers.get("To", "Unknown")
        subject = headers.get("Subject", "No Subject")
        date = headers.get("Date", "Unknown")
        
        # Extract body
        body = ""
        payload = message.get("payload", {})
        
        if "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        elif "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break
        
        result = f"📧 **{subject}**\n\n"
        result += f"From: {from_addr}\n"
        result += f"To: {to_addr}\n"
        result += f"Date: {date}\n\n"
        result += f"---\n\n{body[:1000]}"
        
        if len(body) > 1000:
            result += "\n\n... (truncated)"
        
        return result
        
    except Exception as e:
        return f"❌ Failed to get email: {str(e)}"
