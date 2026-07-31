"""mobile — Mobile platform for the I Programming Language.

Provides mobile application lifecycle, activity management, navigation,
and device integration built on the UFA foundation.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = [
    "MobileApplication",
    "Ikiganiro",
    "ActivityState",
    "Ubugenzuzi",
    "NavigationEvent",
    "NavigationRoute",
]

from mobile.porogaramu import MobileApplication
from mobile.ikiganiro import Ikiganiro, ActivityState
from mobile.ubugenzuzi import Ubugenzuzi, NavigationEvent, NavigationRoute
