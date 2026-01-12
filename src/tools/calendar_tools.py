"""
Google Calendar Tools.

LangChain tools for interacting with Google Calendar API.
"""

from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from langchain_core.tools import tool

from src.tools.google_auth import get_cached_calendar_service


def get_local_timezone() -> ZoneInfo:
    """Get the local timezone."""
    # Default to IST for India, adjust as needed
    return ZoneInfo("Asia/Kolkata")


def parse_datetime_to_iso(dt_str: str, default_time: str = "09:00:00") -> str:
    """
    Parse various datetime formats to ISO format.
    
    Args:
        dt_str: Datetime string in various formats.
        default_time: Default time if only date is provided.
        
    Returns:
        ISO formatted datetime string.
    """
    tz = get_local_timezone()
    
    # Try different formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            if fmt == "%Y-%m-%d":
                # Only date provided, add default time
                time_parts = default_time.split(":")
                dt = dt.replace(
                    hour=int(time_parts[0]),
                    minute=int(time_parts[1]) if len(time_parts) > 1 else 0,
                    second=int(time_parts[2]) if len(time_parts) > 2 else 0,
                )
            dt = dt.replace(tzinfo=tz)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If parsing fails, return as-is (let API handle errors)
    return dt_str


@tool
def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    attendees: list[str] = [],
    location: str = "",
    description: str = "",
) -> str:
    """
    Create a new calendar event in Google Calendar.
    
    Args:
        title: Title of the event (e.g., "Team Meeting").
        start_time: Start time in ISO format (e.g., "2024-01-15T14:00:00").
        end_time: End time in ISO format (e.g., "2024-01-15T15:00:00").
        attendees: List of attendee email addresses.
        location: Optional location for the event.
        description: Optional description for the event.
        
    Returns:
        Confirmation message with event details and link.
    """
    try:
        service = get_cached_calendar_service()
        
        # Parse datetimes
        start_iso = parse_datetime_to_iso(start_time)
        end_iso = parse_datetime_to_iso(end_time)
        
        # Build event body
        event = {
            "summary": title,
            "start": {
                "dateTime": start_iso,
                "timeZone": str(get_local_timezone()),
            },
            "end": {
                "dateTime": end_iso,
                "timeZone": str(get_local_timezone()),
            },
        }
        
        if attendees:
            event["attendees"] = [{"email": email.strip()} for email in attendees]
        
        if location:
            event["location"] = location
            
        if description:
            event["description"] = description
        
        # Create the event
        created_event = service.events().insert(
            calendarId="primary",
            body=event,
            sendUpdates="all" if attendees else "none",
        ).execute()
        
        event_link = created_event.get("htmlLink", "")
        attendee_count = len(attendees)
        
        result = f"✅ Event created successfully!\n"
        result += f"📅 Title: {title}\n"
        result += f"🕐 Start: {start_time}\n"
        result += f"🕑 End: {end_time}\n"
        
        if attendees:
            result += f"👥 Attendees: {', '.join(attendees)}\n"
        if location:
            result += f"📍 Location: {location}\n"
        if event_link:
            result += f"🔗 Link: {event_link}\n"
            
        return result
        
    except Exception as e:
        return f"❌ Failed to create event: {str(e)}"


@tool
def get_available_time_slots(
    date: str,
    duration_minutes: int = 60,
    attendees: list[str] = [],
    working_hours_start: int = 9,
    working_hours_end: int = 18,
) -> str:
    """
    Get available time slots on a specific date.
    
    Args:
        date: Date to check in ISO format (e.g., "2024-01-15").
        duration_minutes: Duration of the meeting in minutes.
        attendees: List of attendee emails to check availability for.
        working_hours_start: Start of working hours (default: 9 AM).
        working_hours_end: End of working hours (default: 6 PM).
        
    Returns:
        List of available time slots.
    """
    try:
        service = get_cached_calendar_service()
        tz = get_local_timezone()
        
        # Parse the date
        try:
            check_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=tz)
        except ValueError:
            return f"❌ Invalid date format. Please use YYYY-MM-DD format."
        
        # Define time range
        time_min = check_date.replace(hour=working_hours_start, minute=0, second=0)
        time_max = check_date.replace(hour=working_hours_end, minute=0, second=0)
        
        # Get events for the day
        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        
        events = events_result.get("items", [])
        
        # Build list of busy periods
        busy_periods = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                busy_periods.append((start_dt, end_dt))
            except:
                continue
        
        # Find available slots
        available_slots = []
        current_time = time_min
        slot_duration = timedelta(minutes=duration_minutes)
        
        while current_time + slot_duration <= time_max:
            slot_end = current_time + slot_duration
            
            # Check if this slot conflicts with any busy period
            is_available = True
            for busy_start, busy_end in busy_periods:
                if not (slot_end <= busy_start or current_time >= busy_end):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current_time.strftime("%H:%M"))
            
            # Move to next slot (30-minute increments)
            current_time += timedelta(minutes=30)
        
        if available_slots:
            result = f"📅 Available {duration_minutes}-minute slots on {date}:\n"
            result += "\n".join([f"  • {slot}" for slot in available_slots])
            return result
        else:
            return f"❌ No available {duration_minutes}-minute slots on {date} during working hours."
            
    except Exception as e:
        return f"❌ Failed to check availability: {str(e)}"


@tool
def list_upcoming_events(days: int = 7, max_results: int = 10) -> str:
    """
    List upcoming calendar events.
    
    Args:
        days: Number of days to look ahead (default: 7).
        max_results: Maximum number of events to return (default: 10).
        
    Returns:
        List of upcoming events with details.
    """
    try:
        service = get_cached_calendar_service()
        tz = get_local_timezone()
        
        now = datetime.now(tz)
        time_max = now + timedelta(days=days)
        
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=time_max.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            return f"📅 No upcoming events in the next {days} days."
        
        result = f"📅 Upcoming events (next {days} days):\n\n"
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No title")
            
            # Parse and format the start time
            try:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                formatted_start = start_dt.strftime("%a, %b %d at %I:%M %p")
            except:
                formatted_start = start
            
            result += f"• **{summary}**\n"
            result += f"  📆 {formatted_start}\n"
            
            if event.get("location"):
                result += f"  📍 {event['location']}\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ Failed to list events: {str(e)}"


@tool
def delete_calendar_event(event_id: str) -> str:
    """
    Delete a calendar event by its ID.
    
    Args:
        event_id: The ID of the event to delete.
        
    Returns:
        Confirmation message.
    """
    try:
        service = get_cached_calendar_service()
        
        # First, get the event to confirm it exists
        try:
            event = service.events().get(calendarId="primary", eventId=event_id).execute()
            event_title = event.get("summary", "Untitled Event")
        except:
            return f"❌ Event with ID '{event_id}' not found."
        
        # Delete the event
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        
        return f"✅ Event '{event_title}' has been deleted successfully."
        
    except Exception as e:
        return f"❌ Failed to delete event: {str(e)}"


@tool
def update_calendar_event(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """
    Update an existing calendar event.
    
    Args:
        event_id: The ID of the event to update.
        title: New title for the event (optional).
        start_time: New start time in ISO format (optional).
        end_time: New end time in ISO format (optional).
        location: New location (optional).
        description: New description (optional).
        
    Returns:
        Confirmation message with updated details.
    """
    try:
        service = get_cached_calendar_service()
        
        # Get existing event
        try:
            event = service.events().get(calendarId="primary", eventId=event_id).execute()
        except:
            return f"❌ Event with ID '{event_id}' not found."
        
        # Update fields
        if title is not None:
            event["summary"] = title
        
        if start_time is not None:
            event["start"] = {
                "dateTime": parse_datetime_to_iso(start_time),
                "timeZone": str(get_local_timezone()),
            }
        
        if end_time is not None:
            event["end"] = {
                "dateTime": parse_datetime_to_iso(end_time),
                "timeZone": str(get_local_timezone()),
            }
        
        if location is not None:
            event["location"] = location
            
        if description is not None:
            event["description"] = description
        
        # Update the event
        updated_event = service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event,
        ).execute()
        
        return f"✅ Event updated successfully!\n📅 Title: {updated_event.get('summary', 'N/A')}"
        
    except Exception as e:
        return f"❌ Failed to update event: {str(e)}"
