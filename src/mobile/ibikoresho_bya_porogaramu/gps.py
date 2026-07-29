"""gps — Location services for the I mobile platform.

Provides GPS tracking, geocoding, distance calculation, and
location-based services for mobile applications.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class Location:
    """A geographical location fix.

    Attributes:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        altitude: Altitude in meters above sea level.
        accuracy: Horizontal accuracy radius in meters.
        speed: Speed in meters per second.
        bearing: Bearing in degrees clockwise from true north.
        timestamp: Time when the location was recorded.
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        altitude: float = 0.0,
        accuracy: float = 0.0,
        speed: float = 0.0,
        bearing: float = 0.0,
        timestamp: Optional[datetime] = None,
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.accuracy = accuracy
        self.speed = speed
        self.bearing = bearing
        self.timestamp: datetime = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this location to a dictionary.

        Returns:
            Dictionary representation of the location.
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "accuracy": self.accuracy,
            "speed": self.speed,
            "bearing": self.bearing,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Location:
        """Create a Location from a dictionary.

        Args:
            data: Dictionary with location fields.

        Returns:
            A new Location instance.
        """
        ts = data.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data.get("altitude", 0.0),
            accuracy=data.get("accuracy", 0.0),
            speed=data.get("speed", 0.0),
            bearing=data.get("bearing", 0.0),
            timestamp=ts or datetime.now(),
        )

    def __repr__(self) -> str:
        return (
            f"Location(lat={self.latitude:.6f}, "
            f"lng={self.longitude:.6f}, "
            f"acc={self.accuracy:.1f}m)"
        )


class GPSManager:
    """Location / GPS services manager.

    Provides high-level APIs for obtaining device location, configuring
    update frequency and accuracy, geocoding addresses, and calculating
    distances between coordinates.
    """

    def __init__(self) -> None:
        self._last_known: Optional[Location] = None
        self._updating: bool = False
        self._accuracy: float = 10.0
        self._interval: float = 5.0
        self._permission: bool = False

    # -- Properties -----------------------------------------------------------

    @property
    def last_known_location(self) -> Optional[Location]:
        """The most recently obtained location fix."""
        return self._last_known

    @property
    def is_updating(self) -> bool:
        """Whether location updates are active."""
        return self._updating

    @property
    def accuracy(self) -> float:
        """Desired location accuracy in meters."""
        return self._accuracy

    @accuracy.setter
    def accuracy(self, value: float) -> None:
        self._accuracy = max(1.0, value)

    @property
    def interval(self) -> float:
        """Update interval in seconds."""
        return self._interval

    @interval.setter
    def interval(self, value: float) -> None:
        self._interval = max(0.5, value)

    # -- Location Updates -----------------------------------------------------

    def start_updates(self) -> bool:
        """Begin periodic location updates.

        Returns:
            True if updates started successfully.
        """
        if not self._permission or self._updating:
            return False
        self._updating = True
        return True

    def stop_updates(self) -> bool:
        """Stop periodic location updates.

        Returns:
            True if updates were stopped.
        """
        if not self._updating:
            return False
        self._updating = False
        return True

    def get_current_location(self) -> Optional[Location]:
        """Request a single current location fix.

        Returns:
            A Location object if available, None otherwise.
        """
        if not self._permission:
            return None
        location = Location(
            latitude=-1.9441,
            longitude=30.0619,
            altitude=1567.0,
            accuracy=8.0,
        )
        self._last_known = location
        return location

    # -- Permissions ----------------------------------------------------------

    def request_permission(self) -> bool:
        """Request location permission from the user.

        Returns:
            True if permission was granted.
        """
        self._permission = True
        return True

    # -- Query Methods --------------------------------------------------------

    def get_last_known(self) -> Optional[Location]:
        """Get the last known location without a fresh fix.

        Returns:
            The cached Location or None.
        """
        return self._last_known

    @staticmethod
    def calculate_distance(
        loc1: Location, loc2: Location, unit: str = "km"
    ) -> float:
        """Calculate the great-circle distance between two locations.

        Uses the haversine formula.

        Args:
            loc1: First location.
            loc2: Second location.
            unit: Unit of distance — "km" (default) or "mi".

        Returns:
            Distance in the requested unit.
        """
        R = 6371.0  # Earth radius in km
        lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
        lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = R * c

        if unit == "mi":
            return distance_km * 0.621371
        return distance_km

    def geocode_address(self, address: str) -> Optional[Location]:
        """Convert a human-readable address to coordinates.

        Args:
            address: The address string to geocode.

        Returns:
            A Location if the address was resolved, None otherwise.
        """
        return None

    def reverse_geocode(self, location: Location) -> Optional[str]:
        """Convert coordinates to a human-readable address.

        Args:
            location: The Location to reverse-geocode.

        Returns:
            An address string if resolved, None otherwise.
        """
        return None

    def __repr__(self) -> str:
        return (
            f"GPSManager(updating={self._updating}, "
            f"permission={self._permission})"
        )
