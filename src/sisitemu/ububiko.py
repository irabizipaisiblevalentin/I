"""ububiko — File systems: VFS, FAT, EXT, memory file systems, and I/O abstractions."""

from __future__ import annotations

import io
import os
import struct
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, List, Optional, Tuple


class FileType(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    BLOCK = "block"
    CHARACTER = "character"
    PIPE = "pipe"
    SOCKET = "socket"


class FilePermission(Enum):
    READ = 4
    WRITE = 2
    EXECUTE = 1

    @staticmethod
    def mask(owner: int = 6, group: int = 4, other: int = 4) -> int:
        return (owner << 6) | (group << 3) | other


class OpenMode(Enum):
    READ = "r"
    WRITE = "w"
    APPEND = "a"
    READ_WRITE = "r+"
    WRITE_READ = "w+"
    APPEND_READ = "a+"


@dataclass
class FileStat:
    file_type: FileType = FileType.FILE
    size: int = 0
    blocks: int = 0
    permissions: int = 0o644
    created: float = 0.0
    modified: float = 0.0
    accessed: float = 0.0
    owner: str = "root"
    group: str = "root"
    inode: int = 0
    hard_links: int = 1
    device_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.file_type.value,
            "size": self.size,
            "blocks": self.blocks,
            "permissions": oct(self.permissions),
            "inode": self.inode,
            "owner": self.owner,
        }


@dataclass
class DirEntry:
    name: str = ""
    file_type: FileType = FileType.FILE
    inode: int = 0
    size: int = 0

    def is_file(self) -> bool:
        return self.file_type == FileType.FILE

    def is_directory(self) -> bool:
        return self.file_type == FileType.DIRECTORY

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.file_type.value, "size": self.size}


class VirtualFileSystem:
    def __init__(self, name: str = "vfs"):
        self.name = name
        self.mounts: Dict[str, FileSystem] = {}
        self._current_dir: str = "/"

    def mount(self, path: str, fs: FileSystem) -> bool:
        self.mounts[path] = fs
        return True

    def unmount(self, path: str) -> bool:
        if path in self.mounts:
            del self.mounts[path]
            return True
        return False

    def _resolve(self, path: str) -> Tuple[FileSystem, str]:
        for mount_point in sorted(self.mounts.keys(), reverse=True):
            if path.startswith(mount_point):
                rel_path = path[len(mount_point):] or "/"
                return self.mounts[mount_point], rel_path
        return self.mounts.get("/", NullFS()), path

    def open(self, path: str, mode: OpenMode = OpenMode.READ) -> Optional[FileHandle]:
        fs, rel = self._resolve(path)
        return fs.open(rel, mode)

    def read(self, path: str) -> Optional[bytes]:
        fh = self.open(path, OpenMode.READ)
        if fh:
            data = fh.read()
            fh.close()
            return data
        return None

    def write(self, path: str, data: bytes) -> bool:
        fh = self.open(path, OpenMode.WRITE)
        if fh:
            fh.write(data)
            fh.close()
            return True
        return False

    def stat(self, path: str) -> Optional[FileStat]:
        fs, rel = self._resolve(path)
        return fs.stat(rel)

    def listdir(self, path: str) -> List[DirEntry]:
        fs, rel = self._resolve(path)
        return fs.listdir(rel)

    def mkdir(self, path: str) -> bool:
        fs, rel = self._resolve(path)
        return fs.mkdir(rel)

    def remove(self, path: str) -> bool:
        fs, rel = self._resolve(path)
        return fs.remove(rel)

    def exists(self, path: str) -> bool:
        return self.stat(path) is not None

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "mounts": list(self.mounts.keys()),
            "current_dir": self._current_dir,
        }


class FileHandle:
    def __init__(self, name: str = "", data: Optional[bytearray] = None):
        self.name = name
        self._data = data or bytearray()
        self._pos = 0
        self._closed = False

    def read(self, size: int = -1) -> bytes:
        if self._closed:
            return b""
        if size < 0:
            result = bytes(self._data[self._pos:])
            self._pos = len(self._data)
        else:
            result = bytes(self._data[self._pos:self._pos + size])
            self._pos += len(result)
        return result

    def write(self, data: bytes) -> int:
        if self._closed:
            return 0
        end = self._pos + len(data)
        if end > len(self._data):
            self._data.extend(b'\x00' * (end - len(self._data)))
        self._data[self._pos:end] = data
        self._pos = end
        return len(data)

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        elif whence == 2:
            self._pos = len(self._data) + offset
        self._pos = max(0, min(self._pos, len(self._data)))
        return self._pos

    def tell(self) -> int:
        return self._pos

    def truncate(self, size: Optional[int] = None) -> None:
        if size is not None:
            self._data = self._data[:size]
        else:
            self._data = self._data[:self._pos]

    def close(self) -> None:
        self._closed = True

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def closed(self) -> bool:
        return self._closed


class FileSystem:
    def open(self, path: str, mode: OpenMode = OpenMode.READ) -> Optional[FileHandle]:
        raise NotImplementedError

    def stat(self, path: str) -> Optional[FileStat]:
        raise NotImplementedError

    def listdir(self, path: str) -> List[DirEntry]:
        raise NotImplementedError

    def mkdir(self, path: str) -> bool:
        raise NotImplementedError

    def remove(self, path: str) -> bool:
        raise NotImplementedError


class NullFS(FileSystem):
    def open(self, path: str, mode: OpenMode = OpenMode.READ) -> Optional[FileHandle]:
        return None

    def stat(self, path: str) -> Optional[FileStat]:
        return None

    def listdir(self, path: str) -> List[DirEntry]:
        return []

    def mkdir(self, path: str) -> bool:
        return False

    def remove(self, path: str) -> bool:
        return False


class MemoryFileSystem(FileSystem):
    def __init__(self):
        self.files: Dict[str, bytearray] = {}
        self.dirs: Dict[str, List[str]] = {"/": []}
        self.stats: Dict[str, FileStat] = {}
        self._inode_counter = 1

    def open(self, path: str, mode: OpenMode = OpenMode.READ) -> Optional[FileHandle]:
        if mode in (OpenMode.READ, OpenMode.READ_WRITE) and path not in self.files:
            return None
        if mode in (OpenMode.WRITE, OpenMode.WRITE_READ):
            self.files[path] = bytearray()
        if path not in self.files:
            self.files[path] = bytearray()
        fh = FileHandle(name=path, data=self.files[path])
        stat = self.stats.get(path, FileStat())
        stat.accessed = time.time()
        self.stats[path] = stat
        return fh

    def stat(self, path: str) -> Optional[FileStat]:
        if path in self.stats:
            return self.stats[path]
        if path in self.files:
            stat = FileStat(inode=self._inode_counter, size=len(self.files[path]))
            self._inode_counter += 1
            self.stats[path] = stat
            return stat
        parent, name = self._split(path)
        if parent in self.dirs and name in self.dirs[parent]:
            stat = FileStat(file_type=FileType.DIRECTORY, inode=self._inode_counter)
            self._inode_counter += 1
            self.stats[path] = stat
            return stat
        return None

    def listdir(self, path: str) -> List[DirEntry]:
        path = path.rstrip("/") or "/"
        entries = []
        if path in self.dirs:
            for name in self.dirs[path]:
                full = f"{path}/{name}" if path != "/" else f"/{name}"
                if full in self.files:
                    entries.append(DirEntry(name=name, file_type=FileType.FILE,
                                            size=len(self.files[full])))
                else:
                    entries.append(DirEntry(name=name, file_type=FileType.DIRECTORY))
        for fpath in self.files:
            if fpath.startswith(path + "/"):
                rest = fpath[len(path) + 1:]
                if "/" not in rest:
                    entries.append(DirEntry(name=rest, file_type=FileType.FILE,
                                            size=len(self.files[fpath])))
        seen = set()
        unique = []
        for e in entries:
            if e.name not in seen:
                seen.add(e.name)
                unique.append(e)
        return unique

    def mkdir(self, path: str) -> bool:
        path = path.rstrip("/")
        if path in self.dirs:
            return False
        parent, name = self._split(path)
        if parent not in self.dirs:
            return False
        self.dirs[path] = []
        self.dirs[parent].append(name)
        stat = FileStat(file_type=FileType.DIRECTORY, inode=self._inode_counter)
        self._inode_counter += 1
        self.stats[path] = stat
        return True

    def remove(self, path: str) -> bool:
        if path in self.files:
            del self.files[path]
            if path in self.stats:
                del self.stats[path]
            parent, name = self._split(path)
            if parent in self.dirs and name in self.dirs[parent]:
                self.dirs[parent].remove(name)
            return True
        return False

    def write_file(self, path: str, data: bytes) -> None:
        self.files[path] = bytearray(data)
        parent, name = self._split(path)
        if parent not in self.dirs:
            self._ensure_parents(parent)
        if parent in self.dirs and name not in self.dirs.get(parent, []):
            self.dirs[parent].append(name)

    def _split(self, path: str) -> Tuple[str, str]:
        path = path.rstrip("/") or "/"
        parent = str(Path(path).parent)
        name = Path(path).name
        return parent or "/", name

    def _ensure_parents(self, path: str) -> None:
        parts = [p for p in path.split("/") if p]
        current = "/"
        for part in parts:
            current = f"{current}/{part}" if current != "/" else f"/{part}"
            if current not in self.dirs:
                self.dirs[current] = []


class FATFileSystem(FileSystem):
    SECTOR_SIZE = 512
    FAT_ENTRY_SIZE = 4

    def __init__(self, total_sectors: int = 65536):
        self.total_sectors = total_sectors
        self.fat: List[int] = [0] * total_sectors
        self.data: Dict[int, bytearray] = {}
        self.root: Dict[str, int] = {}
        self.dirs: Dict[str, Dict[str, int]] = {"/": {}}
        self._created = time.time()

    def _alloc_cluster(self) -> int:
        for i in range(2, len(self.fat)):
            if self.fat[i] == 0:
                self.fat[i] = 0xFFFFFFFF
                return i
        return -1

    def open(self, path: str, mode: OpenMode = OpenMode.READ) -> Optional[FileHandle]:
        name = path.strip("/")
        if name not in self.root and mode in (OpenMode.WRITE, OpenMode.WRITE_READ):
            cluster = self._alloc_cluster()
            if cluster < 0:
                return None
            self.root[name] = cluster
        if name not in self.root:
            return None
        cluster = self.root[name]
        data = bytearray()
        while cluster < 0xFFFFFFF0:
            sector_data = self.data.get(cluster, bytearray(self.SECTOR_SIZE))
            data.extend(sector_data)
            cluster = self.fat[cluster] if cluster < len(self.fat) else 0xFFFFFFF
        fh = FileHandle(name=name, data=data)
        return fh

    def stat(self, path: str) -> Optional[FileStat]:
        name = path.strip("/")
        if name not in self.root:
            return None
        cluster = self.root[name]
        size = 0
        while cluster < 0xFFFFFFF0:
            size += self.SECTOR_SIZE
            cluster = self.fat[cluster] if cluster < len(self.fat) else 0xFFFFFFF
        return FileStat(size=size, created=self._created)

    def listdir(self, path: str) -> List[DirEntry]:
        return [DirEntry(name=n, file_type=FileType.FILE) for n in self.root]

    def mkdir(self, path: str) -> bool:
        return True

    def remove(self, path: str) -> bool:
        name = path.strip("/")
        if name in self.root:
            cluster = self.root[name]
            while cluster < 0xFFFFFFF0:
                self.fat[cluster] = 0
                cluster = self.fat[cluster] if cluster < len(self.fat) else 0xFFFFFFF
            del self.root[name]
            return True
        return False


class NativeFileSystem(FileSystem):
    def __init__(self, root: str = "/"):
        self.root = root

    def _resolve(self, path: str) -> str:
        return os.path.join(self.root, path.lstrip("/"))

    def open(self, path: str, mode: OpenMode = OpenMode.READ) -> Optional[FileHandle]:
        try:
            native_path = self._resolve(path)
            with open(native_path, mode.value + "b") as f:
                data = bytearray(f.read())
            return FileHandle(name=path, data=data)
        except Exception:
            return None

    def stat(self, path: str) -> Optional[FileStat]:
        try:
            s = os.stat(self._resolve(path))
            ft = FileType.FILE
            if os.path.isdir(self._resolve(path)):
                ft = FileType.DIRECTORY
            return FileStat(
                file_type=ft, size=s.st_size, blocks=s.st_blocks,
                permissions=s.st_mode, created=s.st_ctime,
                modified=s.st_mtime, accessed=s.st_atime,
                inode=s.st_ino,
            )
        except Exception:
            return None

    def listdir(self, path: str) -> List[DirEntry]:
        try:
            entries = []
            for name in os.listdir(self._resolve(path)):
                full = os.path.join(self._resolve(path), name)
                ft = FileType.DIRECTORY if os.path.isdir(full) else FileType.FILE
                size = os.path.getsize(full) if ft == FileType.FILE else 0
                entries.append(DirEntry(name=name, file_type=ft, size=size))
            return entries
        except Exception:
            return []

    def mkdir(self, path: str) -> bool:
        try:
            os.makedirs(self._resolve(path), exist_ok=True)
            return True
        except Exception:
            return False

    def remove(self, path: str) -> bool:
        try:
            os.remove(self._resolve(path))
            return True
        except Exception:
            return False


# ─── Memory-Mapped I/O ──────────────────────────────────────────────────────

class MMapFile:
    def __init__(self, path: str = "", size: int = 0):
        self.path = path
        self.size = size
        self._data = bytearray(size) if size > 0 else bytearray()
        self._offset = 0

    def map(self, path: str, offset: int = 0, size: Optional[int] = None) -> bool:
        try:
            with open(path, "rb") as f:
                if size:
                    f.seek(offset)
                    self._data = bytearray(f.read(size))
                else:
                    self._data = bytearray(f.read())
            self.path = path
            self.size = len(self._data)
            self._offset = 0
            return True
        except (OSError, IOError):
            return False

    def sync(self) -> bool:
        try:
            if self.path:
                with open(self.path, "wb") as f:
                    f.write(self._data)
            return True
        except (OSError, IOError):
            return False

    def read(self, offset: int, size: int) -> bytes:
        return bytes(self._data[offset:offset + size])

    def write(self, offset: int, data: bytes) -> int:
        end = offset + len(data)
        if end > len(self._data):
            self._data.extend(b"\x00" * (end - len(self._data)))
        self._data[offset:end] = data
        return len(data)

    def resize(self, new_size: int) -> bool:
        if new_size > len(self._data):
            self._data.extend(b"\x00" * (new_size - len(self._data)))
        elif new_size < len(self._data):
            self._data = self._data[:new_size]
        self.size = new_size
        return True

    def close(self) -> None:
        self._data = bytearray()
        self.size = 0


# ─── Asynchronous I/O ───────────────────────────────────────────────────────

class AIORequest:
    def __init__(self, fd: int = 0, operation: str = "read",
                 offset: int = 0, size: int = 0, data: bytes = b""):
        self.fd = fd
        self.operation = operation
        self.offset = offset
        self.size = size
        self.data = data
        self.completed: bool = False
        self.result: bytes = b""
        self.error: Optional[str] = None


class AIOManager:
    def __init__(self, max_requests: int = 256):
        self.max_requests = max_requests
        self._pending: List[AIORequest] = []
        self._completed: List[AIORequest] = []
        self._lock = threading.Lock()

    def submit(self, req: AIORequest) -> bool:
        with self._lock:
            if len(self._pending) >= self.max_requests:
                return False
            self._pending.append(req)
            return True

    def poll(self) -> List[AIORequest]:
        with self._lock:
            results = list(self._completed)
            self._completed.clear()
            return results

    def process(self) -> int:
        with self._lock:
            count = 0
            for req in self._pending:
                req.completed = True
                req.result = b"\x00" * req.size
                self._completed.append(req)
                count += 1
            self._pending.clear()
            return count

    def summary(self) -> Dict[str, Any]:
        return {"pending": len(self._pending), "completed": len(self._completed)}


# ─── io_uring Emulation ─────────────────────────────────────────────────────

class IOURingSQE:
    def __init__(self, opcode: str = "read", fd: int = 0,
                 offset: int = 0, size: int = 0, data: bytes = b""):
        self.opcode = opcode
        self.fd = fd
        self.offset = offset
        self.size = size
        self.data = data
        self.user_data: int = 0


class IOURingCQE:
    def __init__(self, user_data: int = 0, result: int = 0, flags: int = 0):
        self.user_data = user_data
        self.result = result
        self.flags = flags


class IOURing:
    def __init__(self, queue_depth: int = 128):
        self.queue_depth = queue_depth
        self._sq: List[IOURingSQE] = []
        self._cq: List[IOURingCQE] = []
        self._lock = threading.Lock()
        self._next_user_data: int = 1

    def get_sqe(self) -> Optional[IOURingSQE]:
        with self._lock:
            if len(self._sq) >= self.queue_depth:
                return None
            sqe = IOURingSQE()
            sqe.user_data = self._next_user_data
            self._next_user_data += 1
            return sqe

    def submit(self, sqe: IOURingSQE) -> bool:
        with self._lock:
            if len(self._sq) >= self.queue_depth:
                return False
            self._sq.append(sqe)
            return True

    def submit_and_wait(self, count: int = 1) -> int:
        with self._lock:
            submitted = len(self._sq)
            for sqe in self._sq:
                result = sqe.size if sqe.opcode == "read" else len(sqe.data)
                self._cq.append(IOURingCQE(
                    user_data=sqe.user_data, result=result,
                ))
            self._sq.clear()
            return submitted

    def reap(self) -> List[IOURingCQE]:
        with self._lock:
            entries = list(self._cq)
            self._cq.clear()
            return entries

    @property
    def sq_depth(self) -> int:
        return len(self._sq)

    @property
    def cq_depth(self) -> int:
        return len(self._cq)

    def summary(self) -> Dict[str, Any]:
        return {
            "queue_depth": self.queue_depth,
            "sq_pending": len(self._sq),
            "cq_ready": len(self._cq),
        }


_vfs = VirtualFileSystem()


def get_vfs() -> VirtualFileSystem:
    return _vfs
