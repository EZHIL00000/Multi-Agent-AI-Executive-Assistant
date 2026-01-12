"""
Human-in-the-Loop Review Middleware.

Provides functionality to pause execution for human review of sensitive actions
like sending emails or creating calendar events.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from datetime import datetime


class ReviewDecision(Enum):
    """Possible decisions for a pending review."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


@dataclass
class PendingAction:
    """Represents an action pending human review."""
    id: str
    action_type: str  # "email" or "calendar"
    tool_name: str
    arguments: dict
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    decision: ReviewDecision = ReviewDecision.PENDING
    edited_arguments: Optional[dict] = None
    rejection_reason: Optional[str] = None
    
    def to_display_dict(self) -> dict:
        """Convert to a dictionary for display purposes."""
        return {
            "id": self.id,
            "type": self.action_type,
            "tool": self.tool_name,
            "arguments": self.arguments,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "status": self.decision.value,
        }
    
    def format_for_review(self) -> str:
        """Format the action for human review."""
        lines = [
            f"📋 Pending Action Review",
            f"{'='*50}",
            f"ID: {self.id}",
            f"Type: {self.action_type.title()}",
            f"Tool: {self.tool_name}",
            f"",
            f"Arguments:",
        ]
        
        for key, value in self.arguments.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            
            # Truncate long values
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
                
            lines.append(f"  • {key}: {value_str}")
        
        lines.extend([
            "",
            f"Description: {self.description}",
            f"{'='*50}",
        ])
        
        return "\n".join(lines)


class HumanReviewMiddleware:
    """
    Middleware for human-in-the-loop review of sensitive actions.
    
    This middleware intercepts tool calls that require human approval
    before execution.
    
    Example:
        middleware = HumanReviewMiddleware()
        
        # Register tools that need review
        middleware.register_tool("send_email", "email", "Sending an email")
        middleware.register_tool("create_calendar_event", "calendar", "Creating calendar event")
        
        # Check if a tool needs review
        if middleware.needs_review("send_email"):
            action = middleware.create_pending_action("send_email", args)
            # Present to user for review
            # ...
            middleware.approve(action.id)
    """
    
    def __init__(self):
        """Initialize the middleware."""
        self._registered_tools: dict[str, dict] = {}
        self._pending_actions: dict[str, PendingAction] = {}
        self._action_counter = 0
    
    def register_tool(
        self,
        tool_name: str,
        action_type: str,
        description_template: str,
    ):
        """
        Register a tool that requires human review.
        
        Args:
            tool_name: Name of the tool to register.
            action_type: Type of action (e.g., "email", "calendar").
            description_template: Template for describing the action.
        """
        self._registered_tools[tool_name] = {
            "action_type": action_type,
            "description_template": description_template,
        }
    
    def needs_review(self, tool_name: str) -> bool:
        """Check if a tool requires human review."""
        return tool_name in self._registered_tools
    
    def create_pending_action(
        self,
        tool_name: str,
        arguments: dict,
        custom_description: Optional[str] = None,
    ) -> PendingAction:
        """
        Create a pending action for human review.
        
        Args:
            tool_name: Name of the tool being called.
            arguments: Arguments for the tool call.
            custom_description: Optional custom description.
            
        Returns:
            PendingAction object.
        """
        self._action_counter += 1
        action_id = f"action_{self._action_counter}"
        
        tool_info = self._registered_tools.get(tool_name, {})
        action_type = tool_info.get("action_type", "unknown")
        
        # Generate description
        if custom_description:
            description = custom_description
        else:
            description = tool_info.get("description_template", f"Executing {tool_name}")
        
        action = PendingAction(
            id=action_id,
            action_type=action_type,
            tool_name=tool_name,
            arguments=arguments,
            description=description,
        )
        
        self._pending_actions[action_id] = action
        return action
    
    def get_pending_actions(self) -> list[PendingAction]:
        """Get all pending actions."""
        return [
            action for action in self._pending_actions.values()
            if action.decision == ReviewDecision.PENDING
        ]
    
    def get_action(self, action_id: str) -> Optional[PendingAction]:
        """Get a specific action by ID."""
        return self._pending_actions.get(action_id)
    
    def approve(self, action_id: str) -> bool:
        """
        Approve a pending action.
        
        Args:
            action_id: ID of the action to approve.
            
        Returns:
            True if approved successfully.
        """
        action = self._pending_actions.get(action_id)
        if action and action.decision == ReviewDecision.PENDING:
            action.decision = ReviewDecision.APPROVED
            return True
        return False
    
    def reject(self, action_id: str, reason: str = "") -> bool:
        """
        Reject a pending action.
        
        Args:
            action_id: ID of the action to reject.
            reason: Optional reason for rejection.
            
        Returns:
            True if rejected successfully.
        """
        action = self._pending_actions.get(action_id)
        if action and action.decision == ReviewDecision.PENDING:
            action.decision = ReviewDecision.REJECTED
            action.rejection_reason = reason
            return True
        return False
    
    def edit(self, action_id: str, edited_arguments: dict) -> bool:
        """
        Edit a pending action's arguments before approving.
        
        Args:
            action_id: ID of the action to edit.
            edited_arguments: New arguments for the action.
            
        Returns:
            True if edited successfully.
        """
        action = self._pending_actions.get(action_id)
        if action and action.decision == ReviewDecision.PENDING:
            action.decision = ReviewDecision.EDITED
            action.edited_arguments = edited_arguments
            return True
        return False
    
    def get_final_arguments(self, action_id: str) -> Optional[dict]:
        """
        Get the final arguments for an action (edited or original).
        
        Args:
            action_id: ID of the action.
            
        Returns:
            The arguments to use, or None if action not found or rejected.
        """
        action = self._pending_actions.get(action_id)
        if not action:
            return None
        
        if action.decision == ReviewDecision.REJECTED:
            return None
        
        if action.decision == ReviewDecision.EDITED and action.edited_arguments:
            return action.edited_arguments
        
        return action.arguments
    
    def clear_completed(self):
        """Remove all completed (non-pending) actions."""
        self._pending_actions = {
            action_id: action
            for action_id, action in self._pending_actions.items()
            if action.decision == ReviewDecision.PENDING
        }


# Global middleware instance
_review_middleware: Optional[HumanReviewMiddleware] = None


def get_review_middleware() -> HumanReviewMiddleware:
    """Get the global review middleware instance."""
    global _review_middleware
    if _review_middleware is None:
        _review_middleware = HumanReviewMiddleware()
        
        # Register sensitive tools
        _review_middleware.register_tool(
            "send_email",
            "email",
            "Sending an email",
        )
        _review_middleware.register_tool(
            "create_calendar_event",
            "calendar",
            "Creating a calendar event",
        )
    
    return _review_middleware
