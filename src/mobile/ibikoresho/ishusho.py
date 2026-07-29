from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from .ikoresho import Ikoresho


class ImageFit(Enum):
    COVER = "cover"
    CONTAIN = "contain"
    FILL = "fill"
    NONE = "none"


class LoadingState(Enum):
    IDLE = "idle"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"


class Ishusho(Ikoresho):
    """Image component for displaying raster images.

    Supports loading from URLs, local file paths, or asset keys.
    Provides caching, placeholder rendering, and loading-state
    tracking.

    Attributes:
        source: Image source — URL string, local path, or file key.
        width: Desired display width in pixels.
        height: Desired display height in pixels.
        fit: How the image should be fitted into its box.
        border_radius: Corner radius in pixels.
        placeholder: Placeholder source or colour while loading.
        loading_state: Current state of the image loader.
    """

    _cache: dict[str, Any] = {}

    def __init__(
        self,
        source: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fit: ImageFit = ImageFit.COVER,
        border_radius: Optional[int] = None,
        placeholder: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._source: Optional[str] = source
        self._width: Optional[int] = width
        self._height: Optional[int] = height
        self._fit: ImageFit = fit
        self._border_radius: Optional[int] = border_radius
        self._placeholder: Optional[str] = placeholder
        self._loading_state: LoadingState = LoadingState.IDLE

    # --- Properties ---

    @property
    def source(self) -> Optional[str]:
        return self._source

    @source.setter
    def source(self, value: Optional[str]) -> None:
        self._source = value

    @property
    def width(self) -> Optional[int]:
        return self._width

    @width.setter
    def width(self, value: Optional[int]) -> None:
        self._width = value

    @property
    def height(self) -> Optional[int]:
        return self._height

    @height.setter
    def height(self, value: Optional[int]) -> None:
        self._height = value

    @property
    def fit(self) -> ImageFit:
        return self._fit

    @fit.setter
    def fit(self, value: ImageFit) -> None:
        self._fit = value

    @property
    def border_radius(self) -> Optional[int]:
        return self._border_radius

    @border_radius.setter
    def border_radius(self, value: Optional[int]) -> None:
        self._border_radius = value

    @property
    def placeholder(self) -> Optional[str]:
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]) -> None:
        self._placeholder = value

    @property
    def loading_state(self) -> LoadingState:
        return self._loading_state

    @loading_state.setter
    def loading_state(self, value: LoadingState) -> None:
        self._loading_state = value

    # --- Methods ---

    def load(self) -> None:
        if self._source is None:
            self._loading_state = LoadingState.ERROR
            return

        cached = self._load_from_cache(self._source)
        if cached is not None:
            self._loading_state = LoadingState.LOADED
            return

        self._loading_state = LoadingState.LOADING
        try:
            _data = self._fetch_source(self._source)
            self._store_in_cache(self._source, _data)
            self._loading_state = LoadingState.LOADED
        except Exception:
            self._loading_state = LoadingState.ERROR

    def set_source(self, source: str) -> None:
        self._source = source
        self.load()

    def get_native_bitmap(self) -> Optional[Any]:
        if self._loading_state != LoadingState.LOADED or self._source is None:
            return None
        return self._load_from_cache(self._source)

    @classmethod
    def _load_from_cache(cls, key: str) -> Optional[Any]:
        return cls._cache.get(key)

    @classmethod
    def _store_in_cache(cls, key: str, data: Any) -> None:
        cls._cache[key] = data

    @staticmethod
    def _fetch_source(source: str) -> bytes:
        if source.startswith(("http://", "https://", "file://")):
            return b"<simulated-remote-image-data>"
        return b"<simulated-local-image-data>"

    def render(self) -> dict[str, Any]:
        return {
            "type": "Ishusho",
            "source": self._source,
            "width": self._width,
            "height": self._height,
            "fit": self._fit.value,
            "border_radius": self._border_radius,
            "placeholder": self._placeholder,
            "loading_state": self._loading_state.value,
            "visible": self._visible,
        }

    def measure(self) -> tuple[int, int]:
        return (self._width or 100, self._height or 100)
