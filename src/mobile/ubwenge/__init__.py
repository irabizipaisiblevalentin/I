"""ubwenge — AI / Intelligence modules for the I mobile platform.

Provides on-device AI capabilities: speech recognition,
text-to-speech, translation, computer vision, and offline
ML model inference.
"""

from __future__ import annotations

from mobile.ubwenge.ijwi import (
    AIStream,
    OfflineModel,
    SpeechRecognizer,
    TextToSpeech,
    TranslationManager,
    VisionManager,
)

__all__ = [
    "AIStream",
    "OfflineModel",
    "SpeechRecognizer",
    "TextToSpeech",
    "TranslationManager",
    "VisionManager",
]
