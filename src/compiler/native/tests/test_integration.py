from __future__ import annotations

import unittest
from pathlib import Path

from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.instructions import (
    Add,
    Return,
)
from compiler.ir.module import IRModule
from compiler.ir.types import (
    IR_I64,
    IR_VOID,
    IRFunctionType,
)
from compiler.ir.values import IntConstant
from compiler.native.backend.base import BackendKind
from compiler.native.backend.manager import BackendManager
from compiler.native.backend.registry import BackendRegistry
from compiler.native.compiler import NativeCompiler, NativeCompilerResult
from compiler.native.debug.dwarf import DWARFAbbreviationTable, DWARFDebugInfo, DWARFLineTable
from compiler.native.debug.symbols import Linkage, Symbol, SymbolGenerator, SymbolType
from compiler.native.emit.llvm import LLVMEmitter
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind
from compiler.native.validate.validator import BackendValidator, ValidationResult


class TestDWARFDebugInfo(unittest.TestCase):
    def test_generate_compile_unit(self) -> None:
        dwarf = DWARFDebugInfo()
        module = IRModule("test")
        data = dwarf.generate_compile_unit(module, "test.i")
        self.assertGreater(len(data), 0)
        str_sec = dwarf.get_str_section()
        self.assertIn(b"test.i", str_sec.data)

    def test_generate_subprogram(self) -> None:
        dwarf = DWARFDebugInfo()
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("my_func", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())
        data = dwarf.generate_subprogram(func)
        self.assertGreater(len(data), 0)

    def test_generate_variable(self) -> None:
        dwarf = DWARFDebugInfo()
        var = IntConstant(42, IR_I64)
        data = dwarf.generate_variable(var, {"fbreg": -8})
        self.assertGreater(len(data), 0)

    def test_generate_line_table(self) -> None:
        dwarf = DWARFDebugInfo()
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())
        data = dwarf.generate_line_table(func)
        self.assertGreater(len(data), 0)

    def test_get_sections(self) -> None:
        dwarf = DWARFDebugInfo()
        module = IRModule("test")
        dwarf.generate_compile_unit(module, "test.i")
        sections = dwarf.get_sections()
        names = [s.name for s in sections]
        self.assertIn(".debug_info", names)
        self.assertIn(".debug_abbrev", names)
        self.assertIn(".debug_line", names)
        self.assertIn(".debug_str", names)

    def test_dwarf_abbrev_table(self) -> None:
        tab = DWARFAbbreviationTable()
        code = tab.add(0x11, 0x01, [(0x03, 0x0E)])
        self.assertEqual(code, 1)
        data = tab.serialize()
        self.assertGreater(len(data), 0)

    def test_dwarf_line_table(self) -> None:
        tab = DWARFLineTable()
        tab.set_files(["test.i"])
        tab.add_entry(0, 1)
        tab.add_entry(4, 2)
        data = tab.serialize()
        self.assertGreater(len(data), 0)


class TestSymbolGenerator(unittest.TestCase):
    def test_generate_symbol_table(self) -> None:
        gen = SymbolGenerator()
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("main", func_type)
        symbols = gen.generate_symbol_table([func], [])
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].name, "main")
        self.assertEqual(symbols[0].sym_type, SymbolType.FUNCTION)

    def test_generate_global_symbols(self) -> None:
        gen = SymbolGenerator()
        from compiler.ir.types import IR_I64
        from compiler.ir.values import GlobalVariable
        gv = GlobalVariable("my_global", IR_I64, is_constant=False, linkage="external")
        symbols = gen.generate_symbol_table([], [gv])
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].name, "my_global")
        self.assertEqual(symbols[0].sym_type, SymbolType.OBJECT)
        self.assertTrue(symbols[0].is_global())

    def test_local_vs_global(self) -> None:
        gen = SymbolGenerator()
        func_type = IRFunctionType((), IR_VOID)
        pub = IRFunction("pub_fn", func_type)
        priv = IRFunction("_private", func_type)
        gen.generate_symbol_table([pub, priv], [])
        pub_sym = gen.get_symbol("pub_fn")
        priv_sym = gen.get_symbol("_private")
        self.assertIsNotNone(pub_sym)
        self.assertIsNotNone(priv_sym)
        if pub_sym:
            self.assertTrue(pub_sym.is_global())
        if priv_sym:
            self.assertTrue(priv_sym.is_local())

    def test_to_dict(self) -> None:
        gen = SymbolGenerator()
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        gen.generate_symbol_table([func], [])
        d = gen.to_dict()
        self.assertIn("test", d)
        self.assertEqual(d["test"]["type"], 2)

    def test_relocations_to_dict(self) -> None:
        gen = SymbolGenerator()
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())
        gen.generate_relocations(func, 0)
        relocs = gen.relocations_to_dict()
        self.assertIsInstance(relocs, list)

    def test_add_symbol(self) -> None:
        gen = SymbolGenerator()
        sym = Symbol("extra", linkage=Linkage.WEAK, sym_type=SymbolType.NOTYPE)
        gen.add_symbol(sym)
        self.assertIsNotNone(gen.get_symbol("extra"))

    def test_symbol_properties(self) -> None:
        fsym = Symbol("f", linkage=Linkage.GLOBAL, sym_type=SymbolType.FUNCTION)
        self.assertTrue(fsym.is_function())
        self.assertTrue(fsym.is_global())
        osym = Symbol("o", linkage=Linkage.LOCAL, sym_type=SymbolType.OBJECT)
        self.assertTrue(osym.is_object())
        self.assertTrue(osym.is_local())


class TestBackendValidator(unittest.TestCase):
    def test_validate_module_empty(self) -> None:
        validator = BackendValidator()
        module = IRModule("empty")
        result = validator.validate_module(module)
        self.assertTrue(result.success)

    def test_validate_elf_empty(self) -> None:
        validator = BackendValidator()
        result = validator.validate_object(b"", "elf")
        self.assertFalse(result.success)
        self.assertIn("empty", result.errors[0])

    def test_validate_elf_invalid_magic(self) -> None:
        validator = BackendValidator()
        result = validator.validate_object(b"\x00" * 128, "elf")
        self.assertFalse(result.success)
        self.assertIn("magic", result.errors[0])

    def test_validate_elf_valid_header(self) -> None:
        from compiler.native.object.elf import ELFWriter
        writer = ELFWriter()
        data = writer.write_object({".text": b"\xc3"}, {}, [])
        validator = BackendValidator()
        result = validator.validate_object(data, "elf")
        self.assertTrue(result.success, msg=f"errors: {result.errors}")

    def test_validate_pe_invalid(self) -> None:
        validator = BackendValidator()
        result = validator.validate_object(b"\x00" * 64, "pe")
        self.assertFalse(result.success)
        self.assertIn("magic", result.errors[0])

    def test_validate_macho_invalid(self) -> None:
        validator = BackendValidator()
        result = validator.validate_object(b"\x00" * 32, "macho")
        self.assertFalse(result.success)
        self.assertIn("magic", result.errors[0])

    def test_validate_unsupported_format(self) -> None:
        validator = BackendValidator()
        result = validator.validate_object(b"data", "unknown")
        self.assertFalse(result.success)

    def test_validate_executable_not_found(self) -> None:
        validator = BackendValidator()
        result = validator.validate_executable(Path("/nonexistent/file.exe"))
        self.assertFalse(result.success)

    def test_validation_result(self) -> None:
        r = ValidationResult()
        self.assertTrue(r.success)
        r.add_error("something broke")
        self.assertFalse(r.success)
        self.assertEqual(len(r.errors), 1)
        r.add_warning("be careful")
        self.assertEqual(len(r.warnings), 1)

    def test_validation_result_merge(self) -> None:
        a = ValidationResult()
        b = ValidationResult()
        b.add_error("err1")
        a.merge(b)
        self.assertFalse(a.success)
        self.assertIn("err1", a.errors)

    def test_validate_elf_with_real_data(self) -> None:
        elf_bytes = (
            b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x01\x00\x3e\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00"
            b"\x00\x00\x40\x00\x07\x00\x00\x00\x00\x00\x00\x00"
        ).ljust(128, b"\x00")
        validator = BackendValidator()
        result = validator.validate_object(elf_bytes, "elf")
        self.assertTrue(result.success)


class TestBackendManager(unittest.TestCase):
    def test_detect_target(self) -> None:
        mgr = BackendManager()
        target = mgr.detect_target()
        self.assertIsInstance(target, TargetDescription)
        self.assertIn(target.kind, (TargetKind.X86_64, TargetKind.ARM64))

    def test_host_os(self) -> None:
        os_str = BackendManager._host_os()
        self.assertIn(os_str, ("windows-msvc", "macosx", "linux-gnu"))


class TestNativeCompilerIntegration(unittest.TestCase):
    def test_native_compiler_no_backend(self) -> None:
        registry = BackendRegistry()
        compiler = NativeCompiler(registry=registry)
        module = IRModule("test")
        result = compiler.compile(module, TargetKind.X86_64, BackendKind.LLVM)
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0 or not result.success)

    def test_native_compiler_result(self) -> None:
        result = NativeCompilerResult(success=True)
        self.assertTrue(result.success)
        result = NativeCompilerResult(success=False, errors=["fail"])
        self.assertFalse(result.success)
        self.assertIn("fail", result.errors)

    def test_llvm_emitter_basic(self) -> None:
        emitter = LLVMEmitter()
        module = IRModule("test_mod")
        result = emitter.emit_module(module)
        self.assertIn("test_mod", result)

    def test_llvm_emitter_with_function(self) -> None:
        emitter = LLVMEmitter()
        module = IRModule("llvm_mod")
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("foo", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())
        module.add_function(func)
        result = emitter.emit_module(module)
        self.assertIn("@foo", result)

    def test_full_ir_to_llvm_roundtrip(self) -> None:
        emitter = LLVMEmitter()
        module = IRModule("roundtrip")

        ft = IRFunctionType((IR_I64, IR_I64), IR_I64)
        func = IRFunction("add", ft)
        entry = BasicBlock("entry")
        func.append_block(entry)

        result = Add("sum", func.args[0], func.args[1])
        entry.append(result)
        entry.append(Return(result))
        module.add_function(func)

        llvm_ir = emitter.emit_module(module)
        self.assertIn("@add", llvm_ir)
        self.assertIn("add", llvm_ir)
        self.assertIn("ret i64", llvm_ir)
