# Code Generation Guide

## IR to LLVM IR Lowering

The `LLVMEmitter` in `emit/llvm.py` converts the I language `IRModule` into textual LLVM IR (.ll format). This output can be compiled to object files using LLVM's `llc` tool.

### Type Mapping

| I IR Type            | LLVM IR Type        |
|----------------------|---------------------|
| `VoidType`           | `void`              |
| `IntegerType(n)`     | `i1`, `i8`, `i32`, `i64`, etc. |
| `FloatType(16)`      | `half`              |
| `FloatType(32)`      | `float`             |
| `FloatType(64)`      | `double`            |
| `FloatType(128)`     | `fp128`             |
| `PointerType(t)`     | `t*`                |
| `ArrayType(n, t)`    | `[n x t]`           |
| `StructType(fields)` | `{ t1, t2, ... }`   |
| `VectorType(n, t)`   | `<n x t>`           |

### Opcode Mapping

| I IR Opcode          | LLVM IR Instruction      |
|----------------------|--------------------------|
| `ADD`                | `add`                    |
| `SUB`                | `sub`                    |
| `MUL`                | `mul`                    |
| `SDIV`               | `sdiv`                   |
| `UDIV`               | `udiv`                   |
| `FADD`               | `fadd`                   |
| `FSUB`               | `fsub`                   |
| `FMUL`               | `fmul`                   |
| `FDIV`               | `fdiv`                   |
| `AND`                | `and`                    |
| `OR`                 | `or`                     |
| `XOR`                | `xor`                    |
| `SHL`                | `shl`                    |
| `LSHR`               | `lshr`                   |
| `ASHR`               | `ashr`                   |
| `ICMP`               | `icmp {pred}`            |
| `FCMP`               | `fcmp {pred}`            |
| `ALLOCA`             | `alloca`                 |
| `LOAD`               | `load`                   |
| `STORE`              | `store`                  |
| `GEP`                | `getelementptr`          |
| `TRUNC`              | `trunc`                  |
| `ZEXT`               | `zext`                   |
| `SEXT`               | `sext`                   |
| `FPTOUI`             | `fptoui`                 |
| `FPTOSI`             | `fptosi`                 |
| `UITOFP`             | `uitofp`                 |
| `SITOFP`             | `sitofp`                 |
| `BITCAST`            | `bitcast`                |
| `CALL`               | `call`                   |
| `PHI`                | `phi`                    |
| `BRANCH`             | `br`                     |
| `COND_BRANCH`        | `br cond, label, label`  |
| `RETURN`             | `ret`                    |
| `SWITCH`             | `switch`                 |
| `MEMCPY`             | `call @llvm.memcpy`      |
| `MEMSET`             | `call @llvm.memset`      |

### Compilation to Object

```python
emitter = LLVMEmitter()
ll_ir = emitter.emit_module(module)
# Then invoke llc:
obj_bytes = emitter.compile_to_object(
    ll_ir,
    target_triple="x86_64-unknown-linux-gnu",
    opt_level=2,
)
```

The `llc` invocation uses:
```bash
llc -filetype=obj -mtriple=<triple> -O<level>
```

---

## IR to x86-64 Machine Code Lowering

The `X86_64InstructionSelector` in `ir_lower/selector.py` maps LIR instructions to x86-64 `MachineInst` sequences.

### LIR to MachineOp Mapping

Integer arithmetic:

| LIR InstKind | MachineOp(s)           | Notes                       |
|--------------|------------------------|-----------------------------|
| `IADD`       | `ADD dst, src`         |                             |
| `ISUB`       | `SUB dst, src`         |                             |
| `IMUL`       | `IMUL dst, src`        | 2-operand form              |
| `IDIV`       | `MOV rax, lhs; CDQ; IDIV rhs; MOV dst, rax` | Signed division |
| `IMOD`       | `MOV rax, lhs; CDQ; IDIV rhs; MOV dst, rdx` | Remainder in rdx |
| `IAND`       | `AND dst, src`         |                             |
| `IOR`        | `OR dst, src`          |                             |
| `IXOR`       | `XOR dst, src`         |                             |
| `ISHL`       | `SHL dst, src`         |                             |
| `ISHR`       | `SHR dst, src`         |                             |

Floating-point (SSE2):

| LIR InstKind | MachineOp(s)           |
|--------------|------------------------|
| `FADD`       | `ADDSD dst, src`       |
| `FSUB`       | `SUBSD dst, src`       |
| `FMUL`       | `MULSD dst, src`       |
| `FDIV`       | `DIVSD dst, src`       |

Comparison:

| LIR InstKind | MachineOp(s)                    |
|--------------|---------------------------------|
| `ICMP_EQ`    | `CMP lhs, rhs; SETE dst`        |
| `ICMP_NE`    | `CMP lhs, rhs; SETNE dst`       |
| `ICMP_LT`    | `CMP lhs, rhs; SETL dst`        |
| `ICMP_GT`    | `CMP lhs, rhs; SETG dst`        |
| `FCMP_EQ`    | `UCOMISD a, b; SETE dst`        |
| `FCMP_LT`    | `UCOMISD a, b; SETB dst`        |

Memory:

| LIR InstKind | MachineOp(s)                    |
|--------------|---------------------------------|
| `LOAD_VAR`   | `MOV reg, [address]`            |
| `STORE_VAR`  | `MOV [address], reg`            |
| `LOAD_CONST` | `MOV reg, imm`                  |
| `MOVE`       | `MOV dst, src`                  |
| `ALLOCA`     | `SUB rsp, size`                 |

Control flow:

| LIR InstKind | MachineOp(s)                    |
|--------------|---------------------------------|
| `CALL`       | `CALL target; MOV dst, rax`     |
| `RETURN`     | `MOV rax, val; RET`             |
| `BR`         | `JMP label`                     |
| `BREQ`       | `CMP reg, 0; JE label`          |
| `BRNE`       | `CMP reg, 0; JNE label`         |

Conversions:

| LIR InstKind | MachineOp(s)                    |
|--------------|---------------------------------|
| `I2F`        | `CVTSI2SD xmm, reg`             |
| `F2I`        | `CVTTSD2SI reg, xmm`            |
| `I2I`        | `MOV dst, src` (truncate/extend via register size) |

### ARM64 Lowering

Similar mapping with ARM64-specific opcodes:

| LIR InstKind | ARM64 MachineOp(s)      |
|--------------|-------------------------|
| `IADD`       | `ADD_K Xd, Xn, Xm`      |
| `ISUB`       | `SUB_K Xd, Xn, Xm`      |
| `IMUL`       | `MUL_K Xd, Xn, Xm`      |
| `IDIV`       | `SDIV_K Xd, Xn, Xm`     |
| `LOAD_VAR`   | `LDR Xt, [address]`     |
| `STORE_VAR`  | `STR Xt, [address]`     |
| `CALL`       | `BL target; MOV_K dst, x0` |
| `RETURN`     | `MOV_K x0, val; RET`    |
| `BR`         | `B label`               |
| `BREQ`       | `CMP_K Xn, 0; B_EQ`    |
| `I2F`        | `SCVTF Xd, Xn`          |
| `F2I`        | `FCVTZS Xd, Xn`         |

---

## Instruction Encoding

### x86-64 Encoding

The `X86_64Emitter` in `emit/x86_64.py` handles full x86-64 instruction encoding including REX prefixes, ModRM bytes, SIB bytes, and displacement/immediate fields.

**REX Prefix Format:**
```
Byte: 0100WRXB
  W = 1 for 64-bit operand size
  R = extends ModRM.reg
  X = extends SIB.index
  B = extends ModRM.rm or SIB.base
```

**ModRM Byte:**
```
Bits: mod[2] | reg[3] | rm[3]
  mod = 3 for register, 0/1/2 for memory
  reg = opcode extension or register operand
  rm  = register or addressing mode
```

**SIB Byte (Scale-Index-Base):**
```
Bits: scale[2] | index[3] | base[3]
  scale = 1, 2, 4, or 8
  index = index register
  base  = base register
```

**Memory Addressing Forms:**
```python
# Absolute address (disp32)
mov rax, [0x12345678]   # 48 8B 04 25 78 56 34 12

# Base + displacement
mov rax, [rbp + 16]     # 48 8B 45 10

# Base + index * scale + displacement
mov rax, [rbx + rcx*4 + 8]  # 48 8B 44 8B 08
```

**Instruction Encoding Examples:**
```python
# mov rax, rbx   -> 48 89 D8
# 0x48 = REX.W, 0x89 = MOV r/m, r, ModRM(3, 3, 3)

# add rax, rcx   -> 48 01 C8
# 0x48 = REX.W, 0x01 = ADD r/m, r, ModRM(3, 0, 1)

# cmp rsi, rdi   -> 48 39 FE
# 0x48 = REX.W, 0x39 = CMP r/m, r, ModRM(3, 7, 6)
```

**SSE2 Instruction Encoding:**
```python
# addsd xmm0, xmm1   -> F2 0F 58 C1
# 0xF2 = SSE2 prefix (scalar double)
# 0x0F 0x58 = ADDSD opcode
# ModRM(3, 0, 1) = xmm0, xmm1
```

### ARM64 Encoding

All ARM64 instructions are 32 bits wide, encoded as a single `emit_dword()`.

**R-Type (register):**
```
Bits: 31..24 | 23..21 | 20..16 | 15..10 | 9..5 | 4..0
      opcode  | 1      | Rm     | 0      | Rn   | Rd
```
Example: `add x0, x1, x2` = `0x8B020020`
```python
insn = (0x8B000000 | (0 & 0x1F) | (1 & 0x1F) << 5 | (2 & 0x1F) << 16)
```

**I-Type (immediate):**
```
Bits: 31..24 | 23..22 | 21..10 | 9..5 | 4..0
      opcode  | shift  | imm12  | Rn   | Rd
```
Example: `add x0, x1, #42` = `0x91002C20`
```python
insn = (0x91000000 | (0 & 0x1F) | (1 & 0x1F) << 5 | (42 & 0xFFF) << 10)
```

**B-Type (branch):**
```
Bits: 31..26 | 25..0
      opcode | imm26
```
Example: `b label` = `0x14000000 | (offset >> 2) & 0x03FFFFFF`

---

## Label Management and Fixup

Labels are used for branch targets and are resolved in a two-pass manner:

1. **Emission pass:** Label positions are recorded and branch instructions emit placeholders
2. **Fixup pass:** Placeholders are patched with computed relative offsets

### x86-64 Fixups

```python
class X86_64Emitter:
    def emit_label(self, name: str) -> int:
        self._labels[name] = self.size  # Record position

    def emit_jmp_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)    # fixup_type=0 (rel32)
        self.emit_byte(0xE9)            # jmp opcode
        self.emit_dword(0)              # placeholder

    def resolve_labels(self) -> bytes:
        for fixup_type, fixup_offset, placeholder_offset, label in self._fixups:
            target = self._labels[label]
            if fixup_type == 0:  # rel32
                rel = target - (placeholder_offset + 4)
                struct.pack_into("<i", self._buffer, placeholder_offset, rel)
            elif fixup_type == 1:  # rel8
                rel = target - (placeholder_offset + 1)
                self._buffer[placeholder_offset] = rel & 0xFF
```

### ARM64 Fixups

```python
class ARM64Emitter:
    def emit_label(self, name: str) -> int:
        self._labels[name] = self.size

    def emit_b(self, target: str) -> None:
        insn = 0x14000000
        pos = self.size
        self.emit_insn(insn)           # Placeholder
        self._add_fixup(pos, target)   # Record for patching

    def resolve_labels(self) -> bytes:
        for offset, label in self._fixups:
            target = self._labels[label]
            rel = target - offset
            insn = struct.unpack_from("<I", self._buffer, offset)[0]
            if (insn & 0xFC000000) == 0x14000000:  # B/BL
                imm26 = (rel >> 2) & 0x03FFFFFF
                insn = (insn & 0xFC000000) | imm26
            elif (insn & 0x7C000000) >> 26 == 5:   # B.cond
                imm19 = (rel >> 2) & 0x7FFFF
                insn = (insn & 0xFF00001F) | (imm19 << 5)
            struct.pack_into("<I", self._buffer, offset, insn)
```

### Jump Optimization

The instruction selector (`selector.py`) optimizes jumps:
- Removes unconditional branches that fall through to the next block
- Removes conditional branches that fall through to the target block
- Ensures every basic block is terminated (adding `RET` after `CALL` if needed)

---

## Code Alignment and Padding

### Function Alignment

Functions are aligned to 16-byte boundaries by default:

```python
class X86_64Emitter:
    def emit_align(self, alignment: int, fill: int = 0x90) -> None:
        pad = (alignment - (self.size % alignment)) % alignment
        for _ in range(pad):
            self.emit_byte(fill)
```

### Padding Fill Byte

- **x86-64:** Multi-byte NOP instructions (`0x90`) or longer NOP sequences for optimal performance
- **ARM64:** NOP instruction encoding (`0xD503201F`) is the standard padding

### Section Alignment

Object file sections have target-specific alignment:
- `.text`: 16-byte alignment (common for code sections)
- `.data` / `.rodata`: 8-byte or 16-byte alignment
- `.bss`: 8-byte alignment

The `ELFWriter`, `PEWriter`, and `MachOWriter` classes handle section alignment during object file generation.
