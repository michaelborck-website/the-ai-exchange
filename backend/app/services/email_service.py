"""Email notification service with flexible provider support."""

import logging
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.models import Resource, User
from app.services.email_provider import get_email_provider

logger = logging.getLogger(__name__)

# In-memory store for mocked emails (for testing)
_email_log: list[dict[str, Any]] = []


class EmailNotification:
    """Email notification data structure."""

    def __init__(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        notification_type: str,
    ):
        """Initialize email notification.

        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body
            notification_type: Type of notification (new_request, new_solution, etc)
        """
        self.recipient_email = recipient_email
        self.subject = subject
        self.body = body
        self.notification_type = notification_type
        self.timestamp = datetime.now()


def send_email(notification: EmailNotification) -> bool:
    """Send email notification using configured provider.

    Args:
        notification: Email notification to send

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the configured email provider
        provider = get_email_provider()

        # Send via provider
        success = provider.send_email(
            to_email=notification.recipient_email,
            subject=notification.subject,
            body=notification.body,
            from_email=settings.mail_from,
            from_name=settings.mail_from_name,
        )

        if success:
            # Store in memory log for testing
            _email_log.append(
                {
                    "to": notification.recipient_email,
                    "subject": notification.subject,
                    "body": notification.body,
                    "type": notification.notification_type,
                    "timestamp": notification.timestamp,
                }
            )

            logger.info(
                f"Email sent ({settings.email_provider}): "
                f"{notification.notification_type} to {notification.recipient_email}"
            )
        else:
            logger.error(
                f"Failed to send email via {settings.email_provider}: "
                f"{notification.notification_type} to {notification.recipient_email}"
            )

        return success
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def notify_new_request(
    resource: Resource,
    subscribers: list[User],
) -> int:
    """Notify subscribers when a new request is posted.

    Args:
        resource: The new request resource
        subscribers: List of users subscribed to matching tags

    Returns:
        Number of emails sent
    """
    if not subscribers:
        return 0

    emails_sent = 0
    tags_str = ", ".join(resource.system_tags[:3]) if resource.system_tags else "General"

    for subscriber in subscribers:
        # Skip if subscriber has disabled request notifications
        if not subscriber.notification_prefs.get("notify_requests", True):
            continue

        subject = f"New AI Request: {resource.title}"
        body = f"""Hi {subscriber.full_name},

A new request has been posted on The AI Exchange that matches your interests:

Title: {resource.title}
Tags: {tags_str}
Posted by: {"Anonymous" if resource.is_anonymous else "Faculty Member"}

View the request and submit your solution:
{settings.api_v1_str}/resources/{resource.id}

You're receiving this because you're subscribed to tags related to this request.
You can adjust your notification preferences in your account settings.

Best regards,
The AI Exchange Team
"""

        notification = EmailNotification(
            recipient_email=subscriber.email,
            subject=subject,
            body=body,
            notification_type="new_request",
        )

        if send_email(notification):
            emails_sent += 1

    return emails_sent


def notify_new_solution(
    solution: Resource,
    requester: User,
) -> bool:
    """Notify requester when a solution is posted to their request.

    Args:
        solution: The new solution resource
        requester: The user who posted the original request

    Returns:
        True if email sent successfully
    """
    # Skip if requester has disabled solution notifications
    if not requester.notification_prefs.get("notify_solutions", True):
        return False

    subject = f"New Solution to Your Request: {solution.title}"
    body = f"""Hi {requester.full_name},

Someone has posted a solution to your request!

Solution: {solution.title}
Posted by: {"Anonymous" if solution.is_anonymous else "Faculty Member"}

View the solution and other responses:
{settings.api_v1_str}/resources/{solution.parent_id}

You're receiving this because you posted a request on The AI Exchange.
You can adjust your notification preferences in your account settings.

Best regards,
The AI Exchange Team
"""

    notification = EmailNotification(
        recipient_email=requester.email,
        subject=subject,
        body=body,
        notification_type="new_solution",
    )

    return send_email(notification)


def get_email_log() -> list[dict[str, Any]]:
    """Get log of all mocked emails sent (for testing).

    Returns:
        List of email records
    """
    return _email_log


def clear_email_log() -> None:
    """Clear email log (for testing).

    Used to reset state between tests.
    """
    global _email_log
    _email_log = []


def send_verification_email(user: User, verification_code: str) -> bool:
    """Send email verification code to user.

    Args:
        user: User who registered
        verification_code: 6-digit verification code

    Returns:
        True if email sent successfully
    """
    subject = "Verify Your Email - The AI Exchange"
    body = f"""Hi {user.full_name},

Welcome to The AI Exchange! Please verify your email address to complete your registration.

Your verification code is: {verification_code}

This code will expire in 60 minutes.

Enter this code on the verification page to activate your account.

If you did not create this account, please ignore this email.

Do not share this code with anyone.

Best regards,
The AI Exchange Team
"""

    notification = EmailNotification(
        recipient_email=user.email,
        subject=subject,
        body=body,
        notification_type="email_verification",
    )

    return send_email(notification)


def send_password_reset_email(user: User, reset_code: str) -> bool:
    """Send password reset code to user via email.

    Args:
        user: User requesting password reset
        reset_code: 6-digit reset code

    Returns:
        True if email sent successfully
    """
    subject = "Password Reset Code for The AI Exchange"
    body = f"""Hi {user.full_name},

You requested a password reset for your The AI Exchange account.

Your password reset code is: {reset_code}

This code will expire in 30 minutes.

If you did not request a password reset, please ignore this email and your password will remain unchanged.

Do not share this code with anyone. The AI Exchange team will never ask you for your reset code.

Best regards,
The AI Exchange Team
"""

    notification = EmailNotification(
        recipient_email=user.email,
        subject=subject,
        body=body,
        notification_type="password_reset",
    )

    return send_email(notification)
