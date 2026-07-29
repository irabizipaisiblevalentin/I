"""imisemburo — Platform service abstractions and implementations."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from uam import PlatformTarget


class PlatformService(ABC):
    """Abstract base for platform-specific service implementations.

    All platforms must implement these methods to provide a consistent
    interface for filesystem, clipboard, screen, storage, and notifications.
    """

    @abstractmethod
    def read_file(self, path: str) -> str:
        """Read file contents from the platform filesystem.

        Args:
            path: Path to the file.

        Returns:
            File contents as a string.
        """

    @abstractmethod
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file on the platform filesystem.

        Args:
            path: Path to the file.
            content: Content to write.

        Returns:
            True if successful.
        """

    @abstractmethod
    def clipboard_copy(self, text: str) -> bool:
        """Copy text to the platform clipboard.

        Args:
            text: Text to copy.

        Returns:
            True if successful.
        """

    @abstractmethod
    def screen_width(self) -> int:
        """Get the screen width in pixels.

        Returns:
            Screen width.
        """

    @abstractmethod
    def screen_height(self) -> int:
        """Get the screen height in pixels.

        Returns:
            Screen height.
        """

    @abstractmethod
    def storage_set(self, key: str, value: str) -> bool:
        """Persist a key-value pair to platform storage.

        Args:
            key: Storage key.
            value: Value to store.

        Returns:
            True if successful.
        """

    @abstractmethod
    def storage_get(self, key: str) -> Optional[str]:
        """Retrieve a value from platform storage.

        Args:
            key: Storage key.

        Returns:
            Stored value, or None if not found.
        """

    @abstractmethod
    def notify(self, title: str, message: str) -> bool:
        """Show a platform notification.

        Args:
            title: Notification title.
            message: Notification body.

        Returns:
            True if successful.
        """

    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name string.

        Returns:
            Platform name.
        """

    @abstractmethod
    def platform_version(self) -> str:
        """Return the platform version string.

        Returns:
            Platform version.
        """


class WebPlatformService(PlatformService):
    """Platform service implementation for web (urubuga)."""

    def read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IOError):
            return ""

    def write_file(self, path: str, content: str) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except IOError:
            return False

    def clipboard_copy(self, text: str) -> bool:
        try:
            import pyperclip as _pc
            _pc.copy(text)
            return True
        except ImportError:
            return False

    def screen_width(self) -> int:
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except (ImportError, ValueError):
            return 1024

    def screen_height(self) -> int:
        try:
            import shutil
            return shutil.get_terminal_size().lines
        except (ImportError, ValueError):
            return 768

    def storage_set(self, key: str, value: str) -> bool:
        try:
            import json
            data: Dict[str, str] = {}
            if os.path.isfile("_uam_storage.json"):
                with open("_uam_storage.json", "r") as f:
                    data = json.load(f)
            data[key] = value
            with open("_uam_storage.json", "w") as f:
                json.dump(data, f)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def storage_get(self, key: str) -> Optional[str]:
        try:
            import json
            if not os.path.isfile("_uam_storage.json"):
                return None
            with open("_uam_storage.json", "r") as f:
                data = json.load(f)
            return data.get(key)
        except (IOError, json.JSONDecodeError):
            return None

    def notify(self, title: str, message: str) -> bool:
        print(f"[Notification] {title}: {message}")
        return True

    def platform_name(self) -> str:
        return "web"

    def platform_version(self) -> str:
        return "0.1.0"


class DesktopPlatformService(PlatformService):
    """Platform service implementation for desktop (ibiro)."""

    def read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IOError):
            return ""

    def write_file(self, path: str, content: str) -> bool:
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except IOError:
            return False

    def clipboard_copy(self, text: str) -> bool:
        try:
            import pyperclip as _pc
            _pc.copy(text)
            return True
        except ImportError:
            try:
                import subprocess
                proc = subprocess.run(
                    ["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
                    capture_output=True, timeout=5,
                )
                return proc.returncode == 0
            except (FileNotFoundError, subprocess.SubprocessError):
                return False

    def screen_width(self) -> int:
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except (ImportError, ValueError):
            return 1920

    def screen_height(self) -> int:
        try:
            import shutil
            return shutil.get_terminal_size().lines
        except (ImportError, ValueError):
            return 1080

    def storage_set(self, key: str, value: str) -> bool:
        try:
            import json
            import platform
            app_dir = os.path.join("~", ".uam")
            if platform.system() == "Windows":
                app_dir = os.environ.get("APPDATA", "~")
            app_dir = os.path.expanduser(os.path.join(app_dir, ".uam"))
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "storage.json")
            data: Dict[str, str] = {}
            if os.path.isfile(db_path):
                with open(db_path, "r") as f:
                    data = json.load(f)
            data[key] = value
            with open(db_path, "w") as f:
                json.dump(data, f)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def storage_get(self, key: str) -> Optional[str]:
        try:
            import json
            import platform
            app_dir = os.path.join("~", ".uam")
            if platform.system() == "Windows":
                app_dir = os.environ.get("APPDATA", "~")
            app_dir = os.path.expanduser(os.path.join(app_dir, ".uam"))
            db_path = os.path.join(app_dir, "storage.json")
            if not os.path.isfile(db_path):
                return None
            with open(db_path, "r") as f:
                data = json.load(f)
            return data.get(key)
        except (IOError, json.JSONDecodeError):
            return None

    def notify(self, title: str, message: str) -> bool:
        try:
            import platform
            system = platform.system()
            if system == "Windows":
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, message, title, 0)
                return True
            elif system == "Darwin":
                import subprocess
                subprocess.run(
                    ["osascript", "-e",
                     f'display notification "{message}" with title "{title}"'],
                    capture_output=True, timeout=5,
                )
                return True
            else:
                import subprocess
                subprocess.run(
                    ["notify-send", title, message],
                    capture_output=True, timeout=5,
                )
                return True
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            print(f"[Notification] {title}: {message}")
            return True

    def platform_name(self) -> str:
        return "desktop"

    def platform_version(self) -> str:
        import platform as _platform
        return _platform.version() or "0.0.0"


class MobilePlatformService(PlatformService):
    """Platform service implementation for mobile (MOBILE)."""

    def read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IOError):
            return ""

    def write_file(self, path: str, content: str) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except IOError:
            return False

    def clipboard_copy(self, text: str) -> bool:
        try:
            import pyperclip as _pc
            _pc.copy(text)
            return True
        except ImportError:
            return False

    def screen_width(self) -> int:
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except (ImportError, ValueError):
            return 390

    def screen_height(self) -> int:
        try:
            import shutil
            return shutil.get_terminal_size().lines
        except (ImportError, ValueError):
            return 844

    def storage_set(self, key: str, value: str) -> bool:
        try:
            import json
            db_path = os.path.join(os.path.expanduser("~"), ".uam_mobile_storage.json")
            data: Dict[str, str] = {}
            if os.path.isfile(db_path):
                with open(db_path, "r") as f:
                    data = json.load(f)
            data[key] = value
            with open(db_path, "w") as f:
                json.dump(data, f)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def storage_get(self, key: str) -> Optional[str]:
        try:
            import json
            db_path = os.path.join(os.path.expanduser("~"), ".uam_mobile_storage.json")
            if not os.path.isfile(db_path):
                return None
            with open(db_path, "r") as f:
                data = json.load(f)
            return data.get(key)
        except (IOError, json.JSONDecodeError):
            return None

    def notify(self, title: str, message: str) -> bool:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=5)
            return True
        except ImportError:
            print(f"[Notification] {title}: {message}")
            return True

    def platform_name(self) -> str:
        return "mobile"

    def platform_version(self) -> str:
        try:
            import platform as _platform
            return f"{_platform.system()} {_platform.release()}"
        except ImportError:
            return "0.0.0"


_SERVICE_MAP: Dict[PlatformTarget, type] = {
    PlatformTarget.URUBUGA: WebPlatformService,
    PlatformTarget.IBIRO: DesktopPlatformService,
    PlatformTarget.MOBILE: MobilePlatformService,
}


def register_default_services(platform: Optional[PlatformTarget] = None) -> Dict[str, Any]:
    """Create and register default service implementations for a platform.

    Args:
        platform: Target platform. Detected automatically if None.

    Returns:
        Dictionary of service names to service instances.
    """
    from uam import detect_platform
    target = platform or detect_platform()
    service_class = _SERVICE_MAP.get(target, WebPlatformService)
    instance = service_class()

    services: Dict[str, Any] = {}
    for name in ("filesystem", "clipboard", "display", "storage", "notification"):
        services[name] = instance
    services["platform_info"] = instance

    return services
