"""push — Push notifications for the I mobile platform.

Provides remote and local notification management, including
registration, scheduling, notification channels (Android),
and deep-link handling.
"""

from __future__ import annotations

import enum
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional


class NotificationPriority(enum.Enum):
    """Priority levels for push notifications."""

    DEFAULT = "default"
    HIGH = "high"
    LOW = "low"
    MAX = "max"
    MIN = "min"


class PushNotification:
    """Represents a push or local notification.

    Attributes:
        title: Notification title.
        body: Notification body text.
        data: Custom key-value payload.
        sound: Sound file to play.
        badge: Badge count to display.
        priority: Notification priority level.
        channel_id: Android notification channel ID.
    """

    def __init__(
        self,
        title: str,
        body: str = "",
        data: Optional[Dict[str, Any]] = None,
        sound: Optional[str] = None,
        badge: int = 0,
        priority: NotificationPriority = NotificationPriority.DEFAULT,
        channel_id: str = "default",
    ) -> None:
        self.title = title
        self.body = body
        self.data: Dict[str, Any] = data or {}
        self.sound = sound
        self.badge = badge
        self.priority = priority
        self.channel_id = channel_id


class NotificationChannel:
    """An Android notification channel for grouping notifications.

    Attributes:
        channel_id: Unique channel identifier.
        name: Human-readable channel name.
        description: Channel description.
        importance: Importance level.
    """

    def __init__(
        self,
        channel_id: str,
        name: str,
        description: str = "",
        importance: int = 3,
    ) -> None:
        self.channel_id = channel_id
        self.name = name
        self.description = description
        self.importance = importance


class PushManager:
    """Push notification manager.

    Handles remote push registration, token refresh, local notification
    scheduling, and Android notification channel management.
    """

    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._permission: bool = False
        self._channels: Dict[str, NotificationChannel] = {}
        self._on_token_refresh_callback: Optional[Callable[[str], None]] = None
        self._on_notification_opened_callback: Optional[
            Callable[[PushNotification], None]
        ] = None

    # -- Properties -----------------------------------------------------------

    @property
    def token(self) -> Optional[str]:
        """The current push notification registration token."""
        return self._token

    @property
    def has_permission(self) -> bool:
        """Whether push notification permission has been granted."""
        return self._permission

    @property
    def notification_channels(self) -> Dict[str, NotificationChannel]:
        """Registered notification channels keyed by channel ID."""
        return dict(self._channels)

    # -- Permissions ----------------------------------------------------------

    def request_permission(self) -> bool:
        """Request notification permission from the user.

        Returns:
            True if permission was granted.
        """
        self._permission = True
        self.create_channel(
            NotificationChannel("default", "Default", "General notifications")
        )
        return True

    # -- Remote Push ----------------------------------------------------------

    def register(self) -> Optional[str]:
        """Register the device for remote push notifications.

        Returns:
            The registration token, or None on failure.
        """
        if not self._permission:
            return None
        self._token = "sample-push-token-abc123"
        return self._token

    def unregister(self) -> bool:
        """Unregister from remote push notifications.

        Returns:
            True if unregistration succeeded.
        """
        self._token = None
        return True

    def on_token_refresh(
        self, callback: Callable[[str], None]
    ) -> None:
        """Register a callback for when the push token is refreshed.

        Args:
            callback: Function receiving the new token string.
        """
        self._on_token_refresh_callback = callback

    # -- Local Notifications --------------------------------------------------

    def send_local_notification(
        self,
        notification: PushNotification,
        schedule_at: Optional[datetime] = None,
    ) -> int:
        """Display (or schedule) a local notification.

        Args:
            notification: The notification to display.
            schedule_at: Optional future time to show the notification.

        Returns:
            A notification ID that can be used to cancel it.
        """
        notification_id = hash(
            (notification.title, notification.body, datetime.now())
        )
        return notification_id

    def cancel_notification(self, notification_id: int) -> bool:
        """Cancel a pending or displayed notification by ID.

        Args:
            notification_id: The ID returned by send_local_notification.

        Returns:
            True if the notification was cancelled.
        """
        return True

    def cancel_all(self) -> bool:
        """Cancel all pending and displayed notifications.

        Returns:
            True if all notifications were cancelled.
        """
        return True

    # -- Notification Channels (Android) --------------------------------------

    def create_channel(self, channel: NotificationChannel) -> bool:
        """Create or update a notification channel.

        Args:
            channel: The NotificationChannel to create.

        Returns:
            True if the channel was created.
        """
        self._channels[channel.channel_id] = channel
        return True

    def delete_channel(self, channel_id: str) -> bool:
        """Delete a notification channel.

        Args:
            channel_id: The ID of the channel to delete.

        Returns:
            True if the channel was deleted.
        """
        return self._channels.pop(channel_id, None) is not None

    # -- Deep Link Handling ---------------------------------------------------

    def handle_notification_opened(
        self, callback: Callable[[PushNotification], None]
    ) -> None:
        """Register a callback for when a notification opens the app.

        Args:
            callback: Function receiving the notification that was tapped.
        """
        self._on_notification_opened_callback = callback

    def __repr__(self) -> str:
        return (
            f"PushManager(permission={self._permission}, "
            f"token={'set' if self._token else 'unset'})"
        )
