"""ibikoresho_sisitemu — Systems core: memory model, allocators, low-level primitives, bit manipulation, atomics."""

from __future__ import annotations

import ctypes
import math
import mmap
import os
import struct
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class MemoryRegion(Enum):
    STACK = "stack"
    HEAP = "heap"
    ARENA = "arena"
    POOL = "pool"
    REGION = "region"
    MMAP = "mmap"
    SHARED = "shared"
    PINNED = "pinned"
    DMA = "dma"


class Alignment(Enum):
    BYTE = 1
    WORD = 2
    DWORD = 4
    QWORD = 8
    PARAGRAPH = 16
    CACHE_LINE = 64
    PAGE = 4096


@dataclass
class MemoryBlock:
    address: int = 0
    size: int = 0
    used: bool = False
    region: MemoryRegion = MemoryRegion.HEAP
    alignment: int = 8
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def end(self) -> int:
        return self.address + self.size

    def contains(self, addr: int) -> bool:
        return self.address <= addr < self.end

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": hex(self.address),
            "size": self.size,
            "used": self.used,
            "region": self.region.value,
        }


class Allocator:
    def __init__(self, name: str = "default", total_size: int = 1048576):
        self.name = name
        self.total_size = total_size
        self.blocks: List[MemoryBlock] = [
            MemoryBlock(address=0, size=total_size, used=False)
        ]
        self._allocations: int = 0
        self._frees: int = 0

    def allocate(self, size: int, alignment: int = 8) -> Optional[MemoryBlock]:
        for i, block in enumerate(self.blocks):
            if block.used:
                continue
            if block.size < size:
                continue
            aligned_addr = self._align_up(block.address, alignment)
            padding = aligned_addr - block.address
            if block.size < size + padding:
                continue
            if padding > 0:
                self.blocks.insert(i, MemoryBlock(
                    address=block.address, size=padding, used=False
                ))
                i += 1
                block = self.blocks[i]
            used_block = MemoryBlock(
                address=aligned_addr, size=size, used=True,
                alignment=alignment,
            )
            remainder = block.size - size - padding
            if remainder > 0:
                self.blocks.insert(i + 1, MemoryBlock(
                    address=aligned_addr + size, size=remainder, used=False
                ))
            self.blocks[i] = used_block
            self._allocations += 1
            return used_block
        return None

    def free(self, block: MemoryBlock) -> bool:
        for i, b in enumerate(self.blocks):
            if b.address == block.address and b.used:
                self.blocks[i].used = False
                self._merge_adjacent()
                self._frees += 1
                return True
        return False

    def _align_up(self, addr: int, alignment: int) -> int:
        return (addr + alignment - 1) & ~(alignment - 1)

    def _merge_adjacent(self) -> None:
        i = 0
        while i < len(self.blocks) - 1:
            curr = self.blocks[i]
            next_b = self.blocks[i + 1]
            if not curr.used and not next_b.used:
                self.blocks[i] = MemoryBlock(
                    address=curr.address,
                    size=curr.size + next_b.size,
                    used=False,
                )
                self.blocks.pop(i + 1)
            else:
                i += 1

    @property
    def used_memory(self) -> int:
        return sum(b.size for b in self.blocks if b.used)

    @property
    def free_memory(self) -> int:
        return sum(b.size for b in self.blocks if not b.used)

    @property
    def fragmentation(self) -> float:
        free_blocks = [b for b in self.blocks if not b.used]
        if not free_blocks:
            return 0.0
        largest = max(b.size for b in free_blocks)
        total_free = sum(b.size for b in free_blocks)
        return 1.0 - (largest / total_free) if total_free > 0 else 0.0

    def reset(self) -> None:
        self.blocks = [MemoryBlock(address=0, size=self.total_size, used=False)]
        self._allocations = 0
        self._frees = 0

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "total": self.total_size,
            "used": self.used_memory,
            "free": self.free_memory,
            "fragmentation": round(self.fragmentation, 4),
            "blocks": len(self.blocks),
            "allocations": self._allocations,
            "frees": self._frees,
        }


class ArenaAllocator:
    def __init__(self, name: str = "arena", size: int = 65536):
        self.name = name
        self.size = size
        self._offset = 0
        self._regions: List[Tuple[int, int, str]] = []

    def allocate(self, size: int, tag: str = "") -> Optional[MemoryBlock]:
        aligned = (self._offset + 7) & ~7
        if aligned + size > self.size:
            return None
        block = MemoryBlock(address=aligned, size=size, used=True,
                            region=MemoryRegion.ARENA)
        self._regions.append((aligned, size, tag))
        self._offset = aligned + size
        return block

    def reset(self) -> None:
        self._offset = 0
        self._regions.clear()

    @property
    def used(self) -> int:
        return self._offset

    @property
    def free(self) -> int:
        return self.size - self._offset

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
            "used": self.used,
            "free": self.free,
            "utilization": round(self.used / self.size, 4) if self.size > 0 else 0,
        }


class PoolAllocator:
    def __init__(self, name: str = "pool", block_size: int = 32,
                 count: int = 1024):
        self.name = name
        self.block_size = block_size
        self.count = count
        self._free_list: List[int] = list(range(count))
        self._allocated: Dict[int, bool] = {}

    def allocate(self) -> Optional[MemoryBlock]:
        if not self._free_list:
            return None
        index = self._free_list.pop(0)
        addr = index * self.block_size
        self._allocated[index] = True
        return MemoryBlock(address=addr, size=self.block_size, used=True,
                           region=MemoryRegion.POOL)

    def free(self, block: MemoryBlock) -> bool:
        index = block.address // self.block_size
        if index in self._allocated:
            del self._allocated[index]
            self._free_list.append(index)
            return True
        return False

    @property
    def available(self) -> int:
        return len(self._free_list)

    @property
    def allocated_count(self) -> int:
        return len(self._allocated)

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "block_size": self.block_size,
            "total": self.count,
            "available": self.available,
            "allocated": self.allocated_count,
            "utilization": round(self.allocated_count / self.count, 4) if self.count > 0 else 0,
        }


class RegionAllocator:
    def __init__(self, name: str = "region"):
        self.name = name
        self.regions: Dict[str, List[MemoryBlock]] = {}

    def create_region(self, name: str, size: int,
                      region_type: MemoryRegion = MemoryRegion.REGION) -> MemoryBlock:
        block = MemoryBlock(address=0, size=size, used=False, region=region_type)
        self.regions[name] = [block]
        return block

    def allocate_in_region(self, region_name: str, size: int,
                           tag: str = "") -> Optional[MemoryBlock]:
        region = self.regions.get(region_name)
        if not region:
            return None
        alloc = Allocator(name=region_name, total_size=sum(
            b.size for b in region if not b.used))
        return alloc.allocate(size)

    def free_region(self, name: str) -> bool:
        if name in self.regions:
            del self.regions[name]
            return True
        return False

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "regions": list(self.regions.keys()),
            "region_count": len(self.regions),
        }


@dataclass
class Pointer:
    address: int = 0
    offset: int = 0
    size: int = 0
    typed: bool = False
    type_name: str = "void"

    def read(self, fmt: str = "B") -> Any:
        return struct.unpack(fmt, self._read_bytes(struct.calcsize(fmt)))[0]

    def write(self, value: Any, fmt: str = "B") -> None:
        data = struct.pack(fmt, value)
        self._write_bytes(data)

    def _read_bytes(self, size: int) -> bytes:
        return b'\x00' * size

    def _write_bytes(self, data: bytes) -> None:
        pass

    def offset_by(self, n: int) -> Pointer:
        return Pointer(address=self.address + n, size=self.size - n)

    def is_null(self) -> bool:
        return self.address == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": hex(self.address),
            "offset": self.offset,
            "size": self.size,
            "type": self.type_name,
        }


@dataclass
class Slice:
    data: List[int] = field(default_factory=list)
    offset: int = 0
    length: int = 0
    capacity: int = 0

    def __getitem__(self, index: int) -> int:
        return self.data[self.offset + index]

    def __setitem__(self, index: int, value: int) -> None:
        self.data[self.offset + index] = value

    def __len__(self) -> int:
        return self.length

    def subslice(self, start: int, end: int) -> Slice:
        return Slice(data=self.data, offset=self.offset + start,
                     length=end - start, capacity=self.capacity - start)

    def copy_to(self, dest: Slice) -> None:
        for i in range(min(self.length, dest.length)):
            dest[i] = self[i]


class BitManipulator:
    @staticmethod
    def set_bit(value: int, bit: int) -> int:
        return value | (1 << bit)

    @staticmethod
    def clear_bit(value: int, bit: int) -> int:
        return value & ~(1 << bit)

    @staticmethod
    def toggle_bit(value: int, bit: int) -> int:
        return value ^ (1 << bit)

    @staticmethod
    def test_bit(value: int, bit: int) -> bool:
        return bool(value & (1 << bit))

    @staticmethod
    def mask(value: int, bits: int) -> int:
        return value & ((1 << bits) - 1)

    @staticmethod
    def extract_bits(value: int, start: int, count: int) -> int:
        return (value >> start) & ((1 << count) - 1)

    @staticmethod
    def insert_bits(dest: int, src: int, start: int, count: int) -> int:
        mask = ((1 << count) - 1) << start
        return (dest & ~mask) | ((src << start) & mask)

    @staticmethod
    def rotate_left(value: int, shift: int, bits: int = 32) -> int:
        shift %= bits
        return ((value << shift) | (value >> (bits - shift))) & ((1 << bits) - 1)

    @staticmethod
    def rotate_right(value: int, shift: int, bits: int = 32) -> int:
        shift %= bits
        return ((value >> shift) | (value << (bits - shift))) & ((1 << bits) - 1)

    @staticmethod
    def count_ones(value: int) -> int:
        return bin(value & 0xFFFFFFFF).count('1')

    @staticmethod
    def count_zeros(value: int, bits: int = 32) -> int:
        return bits - BitManipulator.count_ones(value)

    @staticmethod
    def leading_zeros(value: int, bits: int = 32) -> int:
        v = value & ((1 << bits) - 1)
        if v == 0:
            return bits
        return bits - v.bit_length()

    @staticmethod
    def trailing_zeros(value: int, bits: int = 32) -> int:
        v = value & ((1 << bits) - 1)
        if v == 0:
            return bits
        return (v & -v).bit_length() - 1

    @staticmethod
    def reverse_bits(value: int, bits: int = 32) -> int:
        result = 0
        for i in range(bits):
            if value & (1 << i):
                result |= (1 << (bits - 1 - i))
        return result

    @staticmethod
    def byteswap16(value: int) -> int:
        return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)

    @staticmethod
    def byteswap32(value: int) -> int:
        return struct.unpack('<I', struct.pack('>I', value & 0xFFFFFFFF))[0]


class AtomicOps:
    @staticmethod
    def compare_and_swap(target: List[int], index: int,
                         expected: int, new: int) -> bool:
        if target[index] == expected:
            target[index] = new
            return True
        return False

    @staticmethod
    def fetch_add(target: List[int], index: int, value: int) -> int:
        old = target[index]
        target[index] = old + value
        return old

    @staticmethod
    def fetch_sub(target: List[int], index: int, value: int) -> int:
        old = target[index]
        target[index] = old - value
        return old

    @staticmethod
    def fetch_and(target: List[int], index: int, value: int) -> int:
        old = target[index]
        target[index] = old & value
        return old

    @staticmethod
    def fetch_or(target: List[int], index: int, value: int) -> int:
        old = target[index]
        target[index] = old | value
        return old

    @staticmethod
    def fetch_xor(target: List[int], index: int, value: int) -> int:
        old = target[index]
        target[index] = old ^ value
        return old

    @staticmethod
    def load(target: List[int], index: int) -> int:
        return target[index]

    @staticmethod
    def store(target: List[int], index: int, value: int) -> None:
        target[index] = value

    @staticmethod
    def memory_barrier() -> None:
        pass


class Endianness:
    LITTLE = "little"
    BIG = "big"

    @staticmethod
    def host() -> str:
        return "little"

    @staticmethod
    def to_le(value: int, bits: int = 32) -> int:
        return value

    @staticmethod
    def to_be(value: int, bits: int = 32) -> int:
        return value

    @staticmethod
    def swap(value: int, bits: int = 32) -> int:
        if bits == 16:
            return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)
        elif bits == 32:
            return struct.unpack('<I', struct.pack('>I', value & 0xFFFFFFFF))[0]
        elif bits == 64:
            return struct.unpack('<Q', struct.pack('>Q', value & 0xFFFFFFFFFFFFFFFF))[0]
        return value


class CacheManager:
    @staticmethod
    def line_size() -> int:
        return 64

    @staticmethod
    def align_to_line(addr: int) -> int:
        return (addr + 63) & ~63

    @staticmethod
    def prefetch(addr: int) -> None:
        pass

    @staticmethod
    def flush(addr: int, size: int) -> None:
        pass


class SystemsCore:
    def __init__(self):
        self.allocators: Dict[str, Allocator] = {}
        self.arenas: Dict[str, ArenaAllocator] = {}
        self.pools: Dict[str, PoolAllocator] = {}
        self.regions = RegionAllocator()
        self._default_allocator = Allocator("global", 64 * 1024 * 1024)

    def create_allocator(self, name: str, size: int = 1048576) -> Allocator:
        alloc = Allocator(name, size)
        self.allocators[name] = alloc
        return alloc

    def create_arena(self, name: str, size: int = 65536) -> ArenaAllocator:
        arena = ArenaAllocator(name, size)
        self.arenas[name] = arena
        return arena

    def create_pool(self, name: str, block_size: int = 32,
                    count: int = 1024) -> PoolAllocator:
        pool = PoolAllocator(name, block_size, count)
        self.pools[name] = pool
        return pool

    def allocate(self, size: int, alignment: int = 8) -> Optional[MemoryBlock]:
        return self._default_allocator.allocate(size, alignment)

    def free(self, block: MemoryBlock) -> bool:
        return self._default_allocator.free(block)

    def summary(self) -> Dict[str, Any]:
        return {
            "allocators": {n: a.summary() for n, a in self.allocators.items()},
            "arenas": {n: a.summary() for n, a in self.arenas.items()},
            "pools": {n: p.summary() for n, p in self.pools.items()},
            "region_allocator": self.regions.summary(),
            "default_allocator": self._default_allocator.summary(),
        }


_systems_core = SystemsCore()


def get_systems_core() -> SystemsCore:
    return _systems_core
