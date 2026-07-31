"""archive — Archive operations for the I language.

Provides ZIP and TAR archive creation and extraction.
"""

from __future__ import annotations

import os
import tarfile
import zipfile
from typing import List, Optional


# ---------------------------------------------------------------------------
# ZIP
# ---------------------------------------------------------------------------

def zip_create(path: str, files: List[str], compression: int = zipfile.ZIP_DEFLATED) -> None:
    """Create a ZIP archive from a list of file paths."""
    with zipfile.ZipFile(path, "w", compression=compression) as zf:
        for f in files:
            zf.write(f, os.path.basename(f))


def zip_extract(path: str, dest: str = ".") -> None:
    """Extract a ZIP archive safely (rejects path traversal members)."""
    dest_abs = os.path.abspath(dest)
    with zipfile.ZipFile(path, "r") as zf:
        for member in zf.infolist():
            name = member.filename.replace("\\", "/")
            target = os.path.abspath(os.path.join(dest_abs, name))
            if not (target == dest_abs or target.startswith(dest_abs + os.sep)):
                raise ValueError(f"unsafe archive member: {member.filename}")
            zf.extract(member, dest)


def zip_list(path: str) -> List[str]:
    """List contents of a ZIP archive."""
    with zipfile.ZipFile(path, "r") as zf:
        return zf.namelist()


def zip_add(archive: str, file: str, arcname: Optional[str] = None) -> None:
    """Add a file to an existing ZIP archive."""
    with zipfile.ZipFile(archive, "a") as zf:
        zf.write(file, arcname or os.path.basename(file))


# ---------------------------------------------------------------------------
# TAR
# ---------------------------------------------------------------------------

def tar_create(path: str, files: List[str], mode: str = "w:gz") -> None:
    """Create a tar archive."""
    with tarfile.open(path, mode) as tf:
        for f in files:
            tf.add(f, arcname=os.path.basename(f))


def tar_extract(path: str, dest: str = ".") -> None:
    """Extract a tar archive safely (rejects path traversal and links)."""
    dest_abs = os.path.abspath(dest)
    with tarfile.open(path, "r:*") as tf:
        members = []
        for member in tf.getmembers():
            name = member.name.replace("\\", "/")
            target = os.path.abspath(os.path.join(dest_abs, name))
            if not (target == dest_abs or target.startswith(dest_abs + os.sep)):
                raise ValueError(f"unsafe archive member: {member.name}")
            if member.issym() or member.islnk():
                raise ValueError(f"unsafe archive link: {member.name}")
            members.append(member)
        tf.extractall(dest, members=members)


def tar_list(path: str) -> List[str]:
    """List contents of a tar archive."""
    with tarfile.open(path, "r:*") as tf:
        return tf.getnames()
