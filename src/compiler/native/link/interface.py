"""
Linker interface — abstracts system linker invocation across platforms.
"""

from __future__ import annotations

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from compiler.native.link.result import CompileResult

if TYPE_CHECKING:
    from collections.abc import Sequence

    from compiler.native.target.desc import TargetDescription


class LinkError(Exception):
    """Raised when linking fails."""

    __slots__ = ("message", "returncode", "stderr")

    def __init__(self, message: str, returncode: int = -1, stderr: str = "") -> None:
        self.message = message
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"{message} (code={returncode})")


class LinkerInterface(ABC):
    """Abstract base for system linker wrappers."""

    __slots__ = ()

    @abstractmethod
    def link(
        self,
        object_files: Sequence[Path],
        output: Path,
        target: TargetDescription,
    ) -> CompileResult:
        ...

    @abstractmethod
    def link_executable(
        self,
        object_files: Sequence[Path],
        output: Path,
        target: TargetDescription,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
        entry: str | None = None,
    ) -> CompileResult:
        ...

    @abstractmethod
    def link_shared_library(
        self,
        object_files: Sequence[Path],
        output: Path,
        target: TargetDescription,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
    ) -> CompileResult:
        ...

    def _check_paths(self, object_files: Sequence[Path]) -> None:
        for p in object_files:
            if not p.exists():
                raise LinkError(f"Object file not found: {p}")


class SystemLinker(LinkerInterface):
    """Invokes the system linker (ld, gcc, clang, or link.exe)."""

    __slots__ = ("_linker_path", "_linker_type", "_use_gcc_frontend")

    def __init__(
        self,
        linker_path: str | None = None,
        use_gcc_frontend: bool = False,
    ) -> None:
        self._linker_path = linker_path
        self._linker_type = self._detect_linker_type(linker_path)
        self._use_gcc_frontend = use_gcc_frontend

    @property
    def linker_path(self) -> str:
        if self._linker_path:
            return self._linker_path
        if self._linker_type == "msvc":
            return "link.exe"
        if self._linker_type == "macos":
            return "ld"
        return "ld"

    @property
    def linker_type(self) -> str:
        return self._linker_type

    def link(
        self,
        object_files: Sequence[Path],
        output: Path,
        target: TargetDescription,
    ) -> CompileResult:
        return self.link_executable(object_files, output, target)

    def link_executable(
        self,
        object_files: Sequence[Path],
        output: Path,
        target: TargetDescription,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
        entry: str | None = None,
    ) -> CompileResult:
        self._check_paths(object_files)

        if self._linker_type == "msvc":
            return self._link_msvc(object_files, output, libraries, lib_paths, entry)
        if self._linker_type == "macos":
            return self._link_macos(object_files, output, libraries, lib_paths, entry)
        return self._link_linux(object_files, output, libraries, lib_paths, entry)

    def link_shared_library(
        self,
        object_files: Sequence[Path],
        output: Path,
        target: TargetDescription,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
    ) -> CompileResult:
        self._check_paths(object_files)

        if self._linker_type == "msvc":
            return self._link_msvc_shared(object_files, output, libraries, lib_paths)
        if self._linker_type == "macos":
            return self._link_macos_shared(object_files, output, libraries, lib_paths)
        return self._link_linux_shared(object_files, output, libraries, lib_paths)

    def _link_linux(
        self,
        object_files: Sequence[Path],
        output: Path,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
        entry: str | None = None,
    ) -> CompileResult:
        cmd: list[str] = []
        if self._use_gcc_frontend:
            cmd.append("gcc")
        else:
            cmd.append("ld")

        if not self._use_gcc_frontend:
            cmd.extend(["-o", str(output)])
            cmd.extend(["-m", "elf_x86_64"])
            if entry:
                cmd.extend(["-e", entry])
            else:
                cmd.extend(["-e", "main"])
            cmd.extend(["-dynamic-linker", "/lib64/ld-linux-x86-64.so.2"])
            cmd.extend(["-L/usr/lib", "-L/lib"])
        else:
            cmd.extend(["-o", str(output)])

        cmd.extend(str(p) for p in object_files)

        if self._use_gcc_frontend:
            if libraries:
                for lib in libraries:
                    cmd.append(f"-l{lib}")
            if lib_paths:
                for p in lib_paths:
                    cmd.append(f"-L{str(p)}")
        else:
            if libraries:
                for lib in libraries:
                    cmd.append(f"-l{lib}")
            if lib_paths:
                for p in lib_paths:
                    cmd.append(f"-L{str(p)}")
            cmd.extend(["-lc", "-lgcc"])

        return self._run(cmd)

    def _link_macos(
        self,
        object_files: Sequence[Path],
        output: Path,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
        entry: str | None = None,
    ) -> CompileResult:
        cmd: list[str] = []
        if self._use_gcc_frontend or True:
            cmd.append("clang")
        else:
            cmd.append("ld")

        cmd.extend(["-o", str(output)])

        cmd.extend(str(p) for p in object_files)

        if libraries:
            for lib in libraries:
                cmd.append(f"-l{lib}")
        if lib_paths:
            for p in lib_paths:
                cmd.append(f"-L{str(p)}")

        if entry:
            cmd.extend(["-e", entry])
        else:
            cmd.append("-lSystem")

        return self._run(cmd)

    def _link_msvc(
        self,
        object_files: Sequence[Path],
        output: Path,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
        entry: str | None = None,
    ) -> CompileResult:
        cmd = ["link.exe", "/NOLOGO", "/MACHINE:X64"]

        if output.suffix in (".exe", ".dll"):
            cmd.append(f"/OUT:{output}")
        else:
            cmd.append(f"/OUT:{output}")

        cmd.extend(str(p) for p in object_files)

        if libraries:
            for lib in libraries:
                cmd.append(f"{lib}.lib")
        else:
            cmd.append("kernel32.lib")
            cmd.append("user32.lib")

        if lib_paths:
            for p in lib_paths:
                cmd.append(f"/LIBPATH:{p}")

        if entry:
            cmd.append(f"/ENTRY:{entry}")

        cmd.append("/DEFAULTLIB:msvcrt")

        return self._run(cmd)

    def _link_linux_shared(
        self,
        object_files: Sequence[Path],
        output: Path,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
    ) -> CompileResult:
        cmd: list[str] = []
        if self._use_gcc_frontend:
            cmd.append("gcc")
            cmd.append("-shared")
        else:
            cmd.append("ld")
            cmd.append("-shared")

        cmd.extend(["-o", str(output)])
        cmd.extend(str(p) for p in object_files)

        if libraries:
            for lib in libraries:
                cmd.append(f"-l{lib}")
        if lib_paths:
            for p in lib_paths:
                cmd.append(f"-L{str(p)}")
        if not self._use_gcc_frontend:
            cmd.extend(["-lc"])

        return self._run(cmd)

    def _link_macos_shared(
        self,
        object_files: Sequence[Path],
        output: Path,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
    ) -> CompileResult:
        cmd = ["clang", "-shared", "-o", str(output)]
        cmd.extend(str(p) for p in object_files)

        if libraries:
            for lib in libraries:
                cmd.append(f"-l{lib}")
        if lib_paths:
            for p in lib_paths:
                cmd.append(f"-L{str(p)}")

        return self._run(cmd)

    def _link_msvc_shared(
        self,
        object_files: Sequence[Path],
        output: Path,
        libraries: Sequence[str] | None = None,
        lib_paths: Sequence[Path] | None = None,
    ) -> CompileResult:
        cmd = ["link.exe", "/NOLOGO", "/MACHINE:X64", "/DLL"]
        cmd.append(f"/OUT:{output}")
        cmd.extend(str(p) for p in object_files)

        if libraries:
            for lib in libraries:
                cmd.append(f"{lib}.lib")
        else:
            cmd.append("kernel32.lib")

        if lib_paths:
            for p in lib_paths:
                cmd.append(f"/LIBPATH:{p}")

        cmd.append("/DEFAULTLIB:msvcrt")

        return self._run(cmd)

    def _run(self, cmd: list[str]) -> CompileResult:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError:
            return CompileResult(
                success=False,
                errors=[f"Linker not found: {cmd[0]}. Is it installed?"],
            )
        except subprocess.TimeoutExpired:
            return CompileResult(
                success=False,
                errors=["Linker timed out after 120 seconds"],
            )

        if result.returncode != 0:
            stderr = result.stderr or ""
            stdout = result.stdout or ""
            return CompileResult(
                success=False,
                errors=[stderr.strip() or stdout.strip() or f"Linker failed with code {result.returncode}"],
            )

        return CompileResult(
            success=True,
            output_path=Path(cmd[cmd.index("-o") + 1]) if "-o" in cmd else None,
        )

    def _detect_linker_type(self, linker_path: str | None) -> str:
        if linker_path and "link" in linker_path.lower():
            return "msvc"
        import platform
        system = platform.system().lower()
        if system == "windows":
            return "msvc"
        if system == "darwin":
            return "macos"
        return "linux"


def detect_system_linker() -> SystemLinker:
    """Detect and return the appropriate system linker for the host platform."""
    import platform

    system = platform.system().lower()

    if system == "windows":
        msvc_path = _find_msvc_linker()
        if msvc_path:
            return SystemLinker(linker_path=msvc_path)
        return SystemLinker(linker_path="link.exe")

    if system == "darwin":
        if _find_on_path("clang"):
            return SystemLinker(linker_path="clang", use_gcc_frontend=True)
        return SystemLinker(linker_path="ld")

    if _find_on_path("gcc"):
        return SystemLinker(linker_path="gcc", use_gcc_frontend=True)
    return SystemLinker(linker_path="ld")


def _find_msvc_linker() -> str | None:
    vs_paths = [
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Tools\MSVC",
    ]

    for base in vs_paths:
        if os.path.isdir(base):
            for entry in os.listdir(base):
                link_exe = os.path.join(base, entry, "bin", "Hostx64", "x64", "link.exe")
                if os.path.isfile(link_exe):
                    return link_exe
    return None


def _find_on_path(name: str) -> bool:
    try:
        import shutil
        return shutil.which(name) is not None
    except Exception:
        return False
