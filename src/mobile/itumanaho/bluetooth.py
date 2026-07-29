"""Bluetooth manager supporting BLE and classic Bluetooth."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set

DeviceDiscoveredCallback = Callable[["BluetoothDevice"], None]
DataReceivedCallback = Callable[[str, bytes], None]


class BluetoothState(Enum):
    """Bluetooth adapter states."""

    DISABLED = auto()
    """Bluetooth is powered off."""
    ENABLING = auto()
    """Bluetooth is being powered on."""
    ENABLED = auto()
    """Bluetooth is powered on and ready."""
    DISABLING = auto()
    """Bluetooth is being powered off."""
    SCANNING = auto()
    """Bluetooth is scanning for devices."""
    CONNECTING = auto()
    """Attempting to connect to a device."""
    CONNECTED = auto()
    """Connected to a device."""
    DISCONNECTING = auto()
    """Disconnecting from a device."""
    ERROR = auto()
    """An error occurred."""


class BluetoothTransport(Enum):
    """Bluetooth transport type."""

    BLE = "ble"
    CLASSIC = "classic"
    DUAL = "dual"


@dataclass
class BluetoothDevice:
    """Represents a discovered Bluetooth device.

    Args:
        name: Human-readable device name.
        address: MAC address of the device.
        rssi: Received signal strength indicator.
        services: List of service UUIDs.
        transport: Transport type (BLE/classic).
        paired: Whether the device is paired.
    """

    name: str = ""
    address: str = ""
    rssi: int = -100
    services: List[str] = field(default_factory=list)
    transport: BluetoothTransport = BluetoothTransport.BLE
    paired: bool = False


class BluetoothManager:
    """Manages Bluetooth operations including scanning, connecting, and data transfer.

    Supports both BLE (Bluetooth Low Energy) and classic Bluetooth.

    Args:
        adapter_name: Name of the Bluetooth adapter to use.
    """

    def __init__(self, adapter_name: str = "hci0") -> None:
        self._adapter_name: str = adapter_name
        self._state: BluetoothState = BluetoothState.DISABLED
        self._discovered_devices: Dict[str, BluetoothDevice] = {}
        self._connected_devices: Dict[str, BluetoothDevice] = {}
        self._device_discovered_callbacks: List[DeviceDiscoveredCallback] = []
        self._data_received_callbacks: Dict[str, List[DataReceivedCallback]] = {}
        self._state_change_callbacks: List[Callable[[BluetoothState], None]] = []

    @property
    def state(self) -> BluetoothState:
        """Current Bluetooth adapter state."""
        return self._state

    async def enable(self) -> bool:
        """Enable the Bluetooth adapter.

        Returns:
            True if enabled successfully, False otherwise.
        """
        if self._state == BluetoothState.ENABLED:
            return True
        self._state = BluetoothState.ENABLING
        try:
            # Simulate enabling Bluetooth
            self._state = BluetoothState.ENABLED
            self._notify_state_change()
            return True
        except Exception:
            self._state = BluetoothState.ERROR
            self._notify_state_change()
            return False

    async def disable(self) -> bool:
        """Disable the Bluetooth adapter.

        Returns:
            True if disabled successfully, False otherwise.
        """
        if self._state == BluetoothState.DISABLED:
            return True
        self._state = BluetoothState.DISABLING
        try:
            # Disconnect all connected devices
            for address in list(self._connected_devices.keys()):
                await self.disconnect(address)
            self._state = BluetoothState.DISABLED
            self._notify_state_change()
            return True
        except Exception:
            self._state = BluetoothState.ERROR
            self._notify_state_change()
            return False

    async def start_scan(self, duration: float = 10.0) -> None:
        """Start scanning for nearby Bluetooth devices.

        Args:
            duration: Scan duration in seconds.

        Raises:
            RuntimeError: If Bluetooth is not enabled.
        """
        if self._state != BluetoothState.ENABLED:
            raise RuntimeError("Bluetooth is not enabled")
        self._state = BluetoothState.SCANNING
        self._notify_state_change()
        # Simulate scanning
        self._discovered_devices.clear()

    async def stop_scan(self) -> None:
        """Stop an active device scan."""
        if self._state == BluetoothState.SCANNING:
            self._state = BluetoothState.ENABLED
            self._notify_state_change()

    async def connect(
        self, address: str, transport: BluetoothTransport = BluetoothTransport.BLE
    ) -> bool:
        """Connect to a Bluetooth device.

        Args:
            address: MAC address of the device.
            transport: Transport type to use.

        Returns:
            True if connected successfully, False otherwise.

        Raises:
            RuntimeError: If Bluetooth is not enabled.
        """
        if self._state != BluetoothState.ENABLED:
            raise RuntimeError("Bluetooth is not enabled")
        if address in self._connected_devices:
            return True

        device = self._discovered_devices.get(address)
        if device is None:
            device = BluetoothDevice(address=address, transport=transport)

        self._state = BluetoothState.CONNECTING
        self._notify_state_change()

        try:
            # Simulate connection
            device.transport = transport
            self._connected_devices[address] = device
            self._state = BluetoothState.CONNECTED
            self._notify_state_change()
            return True
        except Exception:
            self._state = BluetoothState.ERROR
            self._notify_state_change()
            return False

    async def disconnect(self, address: str) -> bool:
        """Disconnect from a Bluetooth device.

        Args:
            address: MAC address of the device.

        Returns:
            True if disconnected successfully, False otherwise.
        """
        if address not in self._connected_devices:
            return True

        self._state = BluetoothState.DISCONNECTING
        self._notify_state_change()

        try:
            self._connected_devices.pop(address, None)
            self._state = BluetoothState.ENABLED
            self._notify_state_change()
            return True
        except Exception:
            self._state = BluetoothState.ERROR
            self._notify_state_change()
            return False

    async def send_data(self, address: str, data: bytes) -> bool:
        """Send data to a connected device.

        Args:
            address: MAC address of the device.
            data: Byte data to send.

        Returns:
            True if sent successfully, False otherwise.

        Raises:
            ConnectionError: If not connected to the device.
        """
        if address not in self._connected_devices:
            raise ConnectionError(f"Not connected to device {address}")
        # Simulated send
        return True

    async def receive_data(
        self, address: str, callback: DataReceivedCallback
    ) -> None:
        """Register a callback for incoming data from a device.

        Args:
            address: MAC address of the device.
            callback: Called with (address, data) on data receipt.
        """
        if address not in self._data_received_callbacks:
            self._data_received_callbacks[address] = []
        self._data_received_callbacks[address].append(callback)

    async def get_paired_devices(self) -> List[BluetoothDevice]:
        """Return a list of paired Bluetooth devices.

        Returns:
            List of paired BluetoothDevice objects.
        """
        return [
            device
            for device in self._discovered_devices.values()
            if device.paired
        ]

    def on_device_discovered(
        self, callback: DeviceDiscoveredCallback
    ) -> Callable[[], None]:
        """Register a callback for newly discovered devices.

        Args:
            callback: Called with the discovered BluetoothDevice.

        Returns:
            A function to unregister the callback.
        """
        self._device_discovered_callbacks.append(callback)

        def remove() -> None:
            try:
                self._device_discovered_callbacks.remove(callback)
            except ValueError:
                pass

        return remove

    def on_state_change(
        self, callback: Callable[[BluetoothState], None]
    ) -> Callable[[], None]:
        """Register a callback for Bluetooth state changes.

        Args:
            callback: Called with the new state.

        Returns:
            A function to unregister the callback.
        """
        self._state_change_callbacks.append(callback)

        def remove() -> None:
            try:
                self._state_change_callbacks.remove(callback)
            except ValueError:
                pass

        return remove

    def _notify_state_change(self) -> None:
        """Notify registered callbacks of a state change."""
        for cb in self._state_change_callbacks:
            cb(self._state)

    async def discover_services(
        self, address: str
    ) -> List[str]:
        """Discover GATT services on a connected BLE device.

        Args:
            address: MAC address of the device.

        Returns:
            List of service UUID strings.

        Raises:
            ConnectionError: If not connected to the device.
        """
        if address not in self._connected_devices:
            raise ConnectionError(f"Not connected to device {address}")
        device = self._connected_devices[address]
        return device.services

    async def discover_characteristics(
        self, address: str, service_uuid: str
    ) -> List[str]:
        """Discover characteristics for a given service.

        Args:
            address: MAC address of the device.
            service_uuid: UUID of the service.

        Returns:
            List of characteristic UUID strings.

        Raises:
            ConnectionError: If not connected to the device.
        """
        if address not in self._connected_devices:
            raise ConnectionError(f"Not connected to device {address}")
        # Simulated characteristic discovery
        return []
