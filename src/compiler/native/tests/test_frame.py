from __future__ import annotations

import unittest

from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.instructions import Call, Return
from compiler.ir.types import IR_VOID, IRFunctionType
from compiler.native.frame.manager import (
    FrameManager,
    FrameOption,
    FrameOptions,
    StackFrame,
    _align_down,
    _align_up,
)
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


def _make_void_func(name: str) -> IRFunction:
    ft = IRFunctionType((), IR_VOID)
    return IRFunction(name, ft)


class TestAlignHelpers(unittest.TestCase):
    def test_align_up(self) -> None:
        self.assertEqual(_align_up(0, 16), 0)
        self.assertEqual(_align_up(1, 16), 16)
        self.assertEqual(_align_up(15, 16), 16)
        self.assertEqual(_align_up(16, 16), 16)
        self.assertEqual(_align_up(17, 16), 32)

    def test_align_down(self) -> None:
        self.assertEqual(_align_down(0, 16), 0)
        self.assertEqual(_align_down(15, 16), 0)
        self.assertEqual(_align_down(16, 16), 16)
        self.assertEqual(_align_down(17, 16), 16)


class TestFrameOptions(unittest.TestCase):
    def test_default(self) -> None:
        opts = FrameOptions.default()
        self.assertFalse(opts.red_zone)
        self.assertFalse(opts.stack_canary)
        self.assertFalse(opts.guard_page)
        self.assertFalse(opts.omit_frame_pointer)

    def test_optimized(self) -> None:
        opts = FrameOptions.optimized()
        self.assertTrue(opts.omit_frame_pointer)

    def test_secure(self) -> None:
        opts = FrameOptions.secure()
        self.assertTrue(opts.stack_canary)

    def test_red_zone_flag(self) -> None:
        opts = FrameOptions(frozenset({FrameOption.RED_ZONE}))
        self.assertTrue(opts.red_zone)


class TestStackFrame(unittest.TestCase):
    def test_default_frame(self) -> None:
        frame = StackFrame()
        self.assertEqual(frame.local_size, 0)
        self.assertEqual(frame.aligned_frame_size, 0)
        self.assertEqual(frame.frame_size, 0)

    def test_frame_size_calculation(self) -> None:
        frame = StackFrame(
            local_size=16,
            spill_size=8,
            saved_regs_size=8,
            shadow_space=32,
            alignment=16,
        )
        self.assertEqual(frame.frame_size, 64)
        self.assertEqual(frame.aligned_frame_size, 64)

    def test_aligned_frame_size_rounds_up(self) -> None:
        frame = StackFrame(local_size=10, alignment=16)
        self.assertEqual(frame.aligned_frame_size, 16)

    def test_total_frame_size(self) -> None:
        frame = StackFrame(local_size=8, alignment=16, has_return_address=True)
        self.assertEqual(frame.aligned_frame_size, 16)
        self.assertEqual(frame.total_frame_size, 24)

    def test_no_return_address(self) -> None:
        frame = StackFrame(local_size=8, alignment=16, has_return_address=False)
        self.assertEqual(frame.total_frame_size, 16)

    def test_red_zone_size(self) -> None:
        frame = StackFrame(
            leaf_function=True,
            options=FrameOptions(frozenset({FrameOption.RED_ZONE})),
        )
        self.assertEqual(frame.red_zone_size, 128)

    def test_red_zone_non_leaf(self) -> None:
        frame = StackFrame(leaf_function=False, options=FrameOptions.default())
        self.assertEqual(frame.red_zone_size, 0)

    def test_local_offset(self) -> None:
        frame = StackFrame()
        frame._local_offsets[0] = -8
        self.assertEqual(frame.local_offset(0), -8)
        self.assertEqual(frame.local_offset(99), 0)


class TestFrameManager(unittest.TestCase):
    def test_allocate_basic_frame(self) -> None:
        func = _make_void_func("test")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target)
        self.assertIsInstance(frame, StackFrame)
        self.assertEqual(frame.local_size, 0)
        self.assertEqual(frame.spill_size, 0)

    def test_allocate_with_locals(self) -> None:
        func = _make_void_func("locals")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8, 4, 8])
        self.assertEqual(frame.local_size, 20)

    def test_allocate_with_spills(self) -> None:
        func = _make_void_func("spills")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, spill_slots=4)
        self.assertEqual(frame.spill_size, 32)

    def test_allocate_with_saved_regs(self) -> None:
        func = _make_void_func("saved")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, saved_regs=3)
        self.assertEqual(frame.saved_regs_size, 24)

    def test_allocate_shadow_space_windows(self) -> None:
        func = _make_void_func("win")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64, triple="x86_64-pc-windows-msvc")
        frame = mgr.allocate_frame(func, target)
        self.assertEqual(frame.shadow_space, 32)

    def test_allocate_shadow_space_systemv(self) -> None:
        func = _make_void_func("sysv")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64, triple="x86_64-unknown-linux-gnu")
        frame = mgr.allocate_frame(func, target)
        self.assertEqual(frame.shadow_space, 0)

    def test_leaf_function_detection(self) -> None:
        func = _make_void_func("leaf")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        self.assertTrue(mgr._is_leaf_function(func))

    def test_non_leaf_function_detection(self) -> None:
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("nonleaf", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        callee = IRFunction("other", func_type)
        call = Call("", func_type, callee, [])
        block.append(call)
        block.append(Return())

        mgr = FrameManager()
        self.assertFalse(mgr._is_leaf_function(func))

    def test_prologue_x86_64(self) -> None:
        func = _make_void_func("prologue")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[16])
        prologue = mgr.prologue_bytes(func, target, frame)
        self.assertIn(b"\x55", prologue)
        self.assertIn(b"\x48\x89\xe5", prologue)

    def test_prologue_no_frame_pointer(self) -> None:
        func = _make_void_func("no_fp")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        opts = FrameOptions.optimized()
        mgr = FrameManager(opts)
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8])
        prologue = mgr.prologue_bytes(func, target, frame)
        self.assertNotIn(b"\x55", prologue)

    def test_epilogue(self) -> None:
        func = _make_void_func("epilogue")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        epilogue = mgr.epilogue_bytes(func, target)
        self.assertIn(b"\xc3", epilogue)

    def test_epilogue_restores_frame(self) -> None:
        func = _make_void_func("restore")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8])
        epilogue = mgr.epilogue_bytes(func, target, frame)
        self.assertIn(b"\x5d", epilogue)

    def test_stack_canary_prologue(self) -> None:
        func = _make_void_func("canary")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        opts = FrameOptions.secure()
        mgr = FrameManager(opts)
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8])
        prologue = mgr.prologue_bytes(func, target, frame)
        self.assertIn(b"\x48\x8b\x04\x25", prologue)

    def test_stack_canary_epilogue(self) -> None:
        func = _make_void_func("canary_epi")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        opts = FrameOptions.secure()
        mgr = FrameManager(opts)
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8])
        epilogue = mgr.epilogue_bytes(func, target, frame)
        self.assertIn(b"\x48\x33\x04\x25", epilogue)

    def test_frame_manager_local_offset(self) -> None:
        func = _make_void_func("offsets")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8, 4])
        off = mgr.local_offset(frame, 0)
        self.assertEqual(off, -8)

    def test_stack_alignment_x86_64(self) -> None:
        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        self.assertEqual(mgr._stack_alignment(target), 16)

    def test_stack_alignment_arm64(self) -> None:
        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.ARM64)
        self.assertEqual(mgr._stack_alignment(target), 16)

    def test_stack_alignment_x86_32(self) -> None:
        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_32)
        self.assertEqual(mgr._stack_alignment(target), 4)

    def test_prologue_small_frame(self) -> None:
        func = _make_void_func("small")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[8])
        prologue = mgr.prologue_bytes(func, target, frame)
        self.assertIn(b"\x48\x83\xec", prologue)

    def test_prologue_large_frame(self) -> None:
        func = _make_void_func("large")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        mgr = FrameManager()
        target = TargetDescription(kind=TargetKind.X86_64)
        frame = mgr.allocate_frame(func, target, local_var_sizes=[256])
        prologue = mgr.prologue_bytes(func, target, frame)
        self.assertIn(b"\x48\x81\xec", prologue)
