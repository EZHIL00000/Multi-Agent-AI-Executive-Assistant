"""
Google OAuth Authentication Module.

Handles OAuth 2.0 flow for Google Calendar and Gmail APIs.
"""

import os
from pathlib import Path
from typing import Tuple, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from src.config import GOOGLE_SCOPES, get_credentials_path, get_token_path


def get_google_credentials() -> Credentials:
    """
    Get or refresh Google OAuth credentials.
    
    This function handles the OAuth 2.0 flow:
    1. If valid credentials exist in token.json, use them
    2. If credentials are expired but refreshable, refresh them
    3. Otherwise, start the OAuth flow to get new credentials
    
    Returns:
        Valid Google OAuth credentials.
        
    Raises:
        FileNotFoundError: If credentials.json is not found.
    """
    creds = None
    token_path = get_token_path()
    credentials_path = get_credentials_path()
    
    # Check if we have saved credentials
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), GOOGLE_SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            # Start OAuth flow
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}. "
                    "Please download it from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Create a project or select an existing one\n"
                    "3. Enable Calendar API and Gmail API\n"
                    "4. Create OAuth 2.0 credentials (Desktop application)\n"
                    "5. Download and save as 'credentials.json' in the project root"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    return creds


def get_google_services() -> Tuple[Resource, Resource]:
    """
    Get authenticated Google Calendar and Gmail service instances.
    
    Returns:
        Tuple of (calendar_service, gmail_service).
        
    Example:
        >>> calendar, gmail = get_google_services()
        >>> events = calendar.events().list(calendarId='primary').execute()
    """
    creds = get_google_credentials()
    
    calendar_service = build("calendar", "v3", credentials=creds)
    gmail_service = build("gmail", "v1", credentials=creds)
    
    return calendar_service, gmail_service


def get_calendar_service() -> Resource:
    """Get authenticated Google Calendar service."""
    creds = get_google_credentials()
    return build("calendar", "v3", credentials=creds)


def get_gmail_service() -> Resource:
    """Get authenticated Gmail service."""
    creds = get_google_credentials()
    return build("gmail", "v1", credentials=creds)


# Cached service instances
_calendar_service: Optional[Resource] = None
_gmail_service: Optional[Resource] = None


def get_cached_calendar_service() -> Resource:
    """Get cached Google Calendar service (creates on first call)."""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = get_calendar_service()
    return _calendar_service


def get_cached_gmail_service() -> Resource:
    """Get cached Gmail service (creates on first call)."""
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = get_gmail_service()
    return _gmail_service
