"""
Feature Flag System

Manages experimental feature flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from ..config.types import FeatureFlags


class FeatureFlagManager:
    """
    Manages feature flags with runtime toggling.
    """
    
    def __init__(self, flags: Optional[FeatureFlags] = None) -> None:
        """
        Initialize manager.
        
        Args:
            flags: Initial feature flags
        """
        self._flags = flags or FeatureFlags()
        self._overrides: Dict[str, bool] = {}
    
    @property
    def flags(self) -> FeatureFlags:
        """Current feature flags."""
        return self._flags
    
    def is_enabled(self, feature: str) -> bool:
        """
        Check if feature is enabled.
        
        Args:
            feature: Feature name
            
        Returns:
            True if enabled
        """
        # Check overrides first
        if feature in self._overrides:
            return self._overrides[feature]
        
        # Check flags object
        return getattr(self._flags, feature, False)
    
    def enable(self, feature: str) -> None:
        """
        Enable a feature.
        
        Args:
            feature: Feature name
        """
        self._overrides[feature] = True
    
    def disable(self, feature: str) -> None:
        """
        Disable a feature.
        
        Args:
            feature: Feature name
        """
        self._overrides[feature] = False
    
    def reset(self) -> None:
        """Reset all overrides."""
        self._overrides.clear()
    
    def get_enabled(self) -> Set[str]:
        """Get all enabled features."""
        result = set()
        
        # Get features from flags object
        for attr in dir(self._flags):
            if attr.startswith("experimental_"):
                if getattr(self._flags, attr, False):
                    result.add(attr)
        
        # Apply overrides
        for feature, enabled in self._overrides.items():
            if enabled:
                result.add(feature)
            else:
                result.discard(feature)
        
        return result
