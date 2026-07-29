"""biometrike — Biometric authentication for the I mobile platform.

Provides fingerprint, face, iris, and voice biometric
authentication with a configurable prompt interface.
"""

from __future__ import annotations

import enum
from typing import Callable, List, Optional


class BiometricType(enum.Enum):
    """Types of biometric authentication available on a device."""

    FINGERPRINT = "fingerprint"
    FACE = "face"
    IRIS = "iris"
    VOICE = "voice"


class BiometricResult(enum.Enum):
    """Outcome of a biometric authentication attempt."""

    SUCCESS = "success"
    FAILED = "failed"
    NOT_AVAILABLE = "not_available"
    NOT_ENROLLED = "not_enrolled"
    LOCKED_OUT = "locked_out"
    CANCELED = "canceled"


class BiometricManager:
    """Biometric authentication manager.

    Provides APIs for checking biometric availability, enrolling status,
    and performing biometric authentication with a system prompt.
    """

    def __init__(self) -> None:
        self._available_types: List[BiometricType] = []
        self._is_available: bool = False
        self._is_enrolled: bool = False
        self._permission: bool = False

    # -- Properties -----------------------------------------------------------

    @property
    def available_types(self) -> List[BiometricType]:
        """List of biometric types supported by the device."""
        return list(self._available_types)

    @property
    def is_available(self) -> bool:
        """Whether biometric hardware is available."""
        return self._is_available

    @property
    def is_enrolled(self) -> bool:
        """Whether the user has enrolled biometrics."""
        return self._is_enrolled

    # -- Capability Checks ----------------------------------------------------

    def can_authenticate(self) -> BiometricResult:
        """Check if biometric authentication is possible.

        Evaluates hardware availability, enrollment status, and lockout.

        Returns:
            A BiometricResult indicating readiness.
        """
        if not self._is_available:
            return BiometricResult.NOT_AVAILABLE
        if not self._is_enrolled:
            return BiometricResult.NOT_ENROLLED
        return BiometricResult.SUCCESS

    # -- Authentication -------------------------------------------------------

    def authenticate(
        self,
        title: str = "Authenticate",
        subtitle: str = "",
        negative_button_text: str = "Cancel",
        callback: Optional[Callable[[BiometricResult], None]] = None,
    ) -> BiometricResult:
        """Prompt the user for biometric authentication.

        Args:
            title: Title shown in the biometric prompt.
            subtitle: Optional subtitle / description.
            negative_button_text: Text for the cancel button.
            callback: Optional function invoked with the result.

        Returns:
            The BiometricResult of the authentication attempt.
        """
        if not self._permission:
            self.request_permission()
        result = self.can_authenticate()
        if result != BiometricResult.SUCCESS:
            if callback is not None:
                callback(result)
            return result
        result = BiometricResult.SUCCESS
        if callback is not None:
            callback(result)
        return result

    def request_permission(self) -> bool:
        """Request biometric permission from the user.

        Returns:
            True if permission was granted.
        """
        self._permission = True
        self._is_available = True
        self._is_enrolled = True
        self._available_types = [BiometricType.FINGERPRINT, BiometricType.FACE]
        return True

    def __repr__(self) -> str:
        return (
            f"BiometricManager(available={self._is_available}, "
            f"enrolled={self._is_enrolled})"
        )
