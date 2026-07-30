from __future__ import annotations

import unittest

from compiler.native.target.arm64 import ARM64Features, ARM64Registers, ARM64Target
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind
from compiler.native.target.platform import Platform, detect_architecture, detect_platform, host_triple
from compiler.native.target.x86_64 import X86_64Features, X86_64Registers, X86_64Target


class TestX86_64Registers(unittest.TestCase):  # noqa: N801
    def test_caller_saved(self) -> None:
        regs = X86_64Registers.caller_saved()
        self.assertIn("rax", regs)
        self.assertIn("rcx", regs)
        self.assertIn("rdx", regs)
        self.assertIn("rsi", regs)
        self.assertIn("rdi", regs)
        self.assertIn("r8", regs)
        self.assertIn("r9", regs)
        self.assertIn("r10", regs)
        self.assertIn("r11", regs)
        for xmm in ("xmm0", "xmm1", "xmm15"):
            self.assertIn(xmm, regs)

    def test_callee_saved(self) -> None:
        regs = X86_64Registers.callee_saved()
        self.assertIn("rbx", regs)
        self.assertIn("rbp", regs)
        self.assertIn("r12", regs)
        self.assertIn("r13", regs)
        self.assertIn("r14", regs)
        self.assertIn("r15", regs)
        self.assertNotIn("rax", regs)
        self.assertNotIn("rcx", regs)

    def test_arg_registers(self) -> None:
        regs = X86_64Registers.arg_registers()
        expected_order = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")
        for i, exp in enumerate(expected_order):
            self.assertEqual(regs[i], exp)
        for xmm in ("xmm0", "xmm1", "xmm7"):
            self.assertIn(xmm, regs)

    def test_is_gpr(self) -> None:
        self.assertTrue(X86_64Registers.is_gpr("rax"))
        self.assertTrue(X86_64Registers.is_gpr("r15"))
        self.assertTrue(X86_64Registers.is_gpr("RSP"))
        self.assertFalse(X86_64Registers.is_gpr("xmm0"))
        self.assertFalse(X86_64Registers.is_gpr("invalid"))

    def test_is_xmm(self) -> None:
        self.assertTrue(X86_64Registers.is_xmm("xmm0"))
        self.assertTrue(X86_64Registers.is_xmm("XMM15"))
        self.assertFalse(X86_64Registers.is_xmm("rax"))
        self.assertFalse(X86_64Registers.is_xmm("xmm"))


class TestARM64Registers(unittest.TestCase):
    def test_caller_saved(self) -> None:
        regs = ARM64Registers.caller_saved()
        self.assertIn("x0", regs)
        self.assertIn("x18", regs)
        self.assertNotIn("x19", regs)
        self.assertIn("v0", regs)
        self.assertIn("v7", regs)
        self.assertIn("v16", regs)
        self.assertNotIn("v8", regs)
        self.assertNotIn("v15", regs)

    def test_callee_saved(self) -> None:
        regs = ARM64Registers.callee_saved()
        self.assertIn("x19", regs)
        self.assertIn("x29", regs)
        self.assertNotIn("x18", regs)
        self.assertIn("v8", regs)
        self.assertIn("v15", regs)
        self.assertNotIn("v7", regs)

    def test_arg_registers(self) -> None:
        regs = ARM64Registers.arg_registers()
        for i in range(8):
            self.assertIn(f"x{i}", regs)
            self.assertIn(f"v{i}", regs)
        self.assertNotIn("x8", regs)

    def test_is_gpr(self) -> None:
        self.assertTrue(ARM64Registers.is_gpr("x0"))
        self.assertTrue(ARM64Registers.is_gpr("X30"))
        self.assertFalse(ARM64Registers.is_gpr("x31"))
        self.assertFalse(ARM64Registers.is_gpr("v0"))

    def test_is_simd(self) -> None:
        self.assertTrue(ARM64Registers.is_simd("v0"))
        self.assertTrue(ARM64Registers.is_simd("V31"))
        self.assertFalse(ARM64Registers.is_simd("v32"))
        self.assertFalse(ARM64Registers.is_simd("x0"))


class TestTargetTargets(unittest.TestCase):
    def test_x86_64_target_default(self) -> None:
        t = X86_64Target()
        self.assertEqual(t.kind, TargetKind.X86_64)
        self.assertEqual(t.bits, 64)
        self.assertEqual(t.register_width, 64)
        self.assertEqual(t.stack_alignment, 16)
        self.assertEqual(t.endianness, "little")
        self.assertIn("rax", t.preferred_reg_order)
        self.assertIn("xmm15", t.preferred_reg_order)

    def test_x86_64_target_with_features(self) -> None:
        feats = X86_64Features(avx=True, avx512=True)
        t = X86_64Target(feats)
        self.assertIn("avx", t.target.features)
        self.assertIn("avx512", t.target.features)

    def test_arm64_target_default(self) -> None:
        t = ARM64Target()
        self.assertEqual(t.kind, TargetKind.ARM64)
        self.assertEqual(t.bits, 64)
        self.assertEqual(t.register_width, 64)
        self.assertIn("x0", t.preferred_reg_order)

    def test_arm64_target_with_features(self) -> None:
        feats = ARM64Features(sve=True)
        t = ARM64Target(feats)
        self.assertIn("sve", t.target.features)
        self.assertIn("neon", t.target.features)


class TestTargetDescription(unittest.TestCase):
    def test_create_x86_64(self) -> None:
        td = TargetDescription(kind=TargetKind.X86_64, bits=64, triple="x86_64-unknown-linux-gnu")
        self.assertEqual(td.kind, TargetKind.X86_64)
        self.assertEqual(td.triple, "x86_64-unknown-linux-gnu")

    def test_create_arm64(self) -> None:
        td = TargetDescription(kind=TargetKind.ARM64, bits=64, triple="aarch64-unknown-linux-gnu")
        self.assertEqual(td.kind, TargetKind.ARM64)

    def test_immutable(self) -> None:
        td = TargetDescription(kind=TargetKind.X86_64)
        with self.assertRaises(AttributeError):
            td.kind = TargetKind.ARM64


class TestPlatformDetection(unittest.TestCase):
    def test_detect_architecture(self) -> None:
        arch = detect_architecture()
        self.assertIsInstance(arch, str)
        self.assertTrue(len(arch) > 0)

    def test_host_triple(self) -> None:
        triple = host_triple()
        self.assertIsInstance(triple, str)
        self.assertIn("-", triple)

    def test_detect_platform(self) -> None:
        plat = detect_platform()
        self.assertIn(plat, (Platform.LINUX, Platform.WINDOWS, Platform.MACOS))
