"""websocket — WebSocket utilities for the I language.

Provides basic WebSocket framing and echo client.
Full implementation requires asyncio (available in Python 3.4+).
"""

from __future__ import annotations

import hashlib
import os
import struct
from typing import Any, BinaryIO, Optional


# WebSocket magic key for handshake
_WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketFrame:
    """A single WebSocket frame."""

    __slots__ = ("fin", "opcode", "mask", "payload")

    OPCODE_TEXT = 0x1
    OPCODE_BINARY = 0x2
    OPCODE_CLOSE = 0x8
    OPCODE_PING = 0x9
    OPCODE_PONG = 0xA

    def __init__(self, opcode: int = OPCODE_TEXT, payload: bytes = b"",
                 fin: bool = True, mask: Optional[bytes] = None) -> None:
        self.fin = fin
        self.opcode = opcode
        self.mask = mask
        self.payload = payload

    def encode(self) -> bytes:
        """Encode frame to bytes."""
        header = bytes([0x80 | self.opcode if self.fin else self.opcode])
        length = len(self.payload)
        if length < 126:
            header += bytes([length])
        elif length < 65536:
            header += struct.pack("!BH", 126, length)
        else:
            header += struct.pack("!BQ", 127, length)
        if self.mask:
            header += self.mask
            masked = bytearray(self.payload)
            for i, b in enumerate(self.payload):
                masked[i] = b ^ self.mask[i % 4]
            return header + bytes(masked)
        return header + self.payload

    @classmethod
    def decode(cls, data: bytes) -> Optional[WebSocketFrame]:
        """Decode frame from bytes. Returns None if insufficient data."""
        if len(data) < 2:
            return None
        byte0 = data[0]
        byte1 = data[1]
        fin = bool(byte0 & 0x80)
        opcode = byte0 & 0x0F
        masked = bool(byte1 & 0x80)
        length = byte1 & 0x7F
        offset = 2
        if length == 126:
            if len(data) < 4:
                return None
            length = struct.unpack("!H", data[2:4])[0]
            offset = 4
        elif length == 127:
            if len(data) < 10:
                return None
            length = struct.unpack("!Q", data[2:10])[0]
            offset = 10
        mask_bytes = None
        if masked:
            if len(data) < offset + 4:
                return None
            mask_bytes = data[offset:offset + 4]
            offset += 4
        if len(data) < offset + length:
            return None
        payload = bytearray(data[offset:offset + length])
        if mask_bytes:
            for i in range(length):
                payload[i] ^= mask_bytes[i % 4]
        return cls(opcode=opcode, payload=bytes(payload), fin=fin, mask=mask_bytes)

    @classmethod
    def text(cls, message: str) -> WebSocketFrame:
        return cls(opcode=cls.OPCODE_TEXT, payload=message.encode("utf-8"))

    @classmethod
    def binary(cls, data: bytes) -> WebSocketFrame:
        return cls(opcode=cls.OPCODE_BINARY, payload=data)

    @classmethod
    def close(cls, code: int = 1000) -> WebSocketFrame:
        return cls(opcode=cls.OPCODE_CLOSE, payload=struct.pack("!H", code))

    @classmethod
    def ping(cls, data: bytes = b"") -> WebSocketFrame:
        return cls(opcode=cls.OPCODE_PING, payload=data)


def generate_accept_key(key: str) -> str:
    """Generate WebSocket accept key for handshake."""
    import base64
    return base64.b64encode(
        hashlib.sha1((key + _WS_MAGIC).encode()).digest()
    ).decode()
