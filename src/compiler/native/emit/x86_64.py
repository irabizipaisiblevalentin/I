"""
x86-64 Native Binary Emitter (Pure Python)

Emits raw x86-64 machine code bytes with full ModRM, SIB, and REX prefix
handling. Uses bytes/bytearray for the output buffer.
"""

from __future__ import annotations

import struct

# ── Register encodings ─────────────────────────────────────────────

RAX, RCX, RDX, RBX, RSP, RBP, RSI, RDI = range(8)
R8, R9, R10, R11, R12, R13, R14, R15 = range(8, 16)

XMM0, XMM1, XMM2, XMM3, XMM4, XMM5, XMM6, XMM7 = range(8)
XMM8, XMM9, XMM10, XMM11, XMM12, XMM13, XMM14, XMM15 = range(8, 16)

REG_NAMES = {
    0: "rax", 1: "rcx", 2: "rdx", 3: "rbx",
    4: "rsp", 5: "rbp", 6: "rsi", 7: "rdi",
    8: "r8", 9: "r9", 10: "r10", 11: "r11",
    12: "r12", 13: "r13", 14: "r14", 15: "r15",
}

# ── Addressing mode helpers ────────────────────────────────────────

Address = tuple[int, int, int]  # (base_reg, index_reg, displacement)


def abs_addr(disp: int) -> Address:
    return (-1, -1, disp)


def reg_addr(base: int, disp: int = 0) -> Address:
    return (base, -1, disp)


def index_addr(base: int, index: int, scale: int = 1, disp: int = 0) -> Address:
    return (base, (index << 2) | (scale & 3), disp)


# ── REX helpers ────────────────────────────────────────────────────

def _rex(w: int = 0, r: int = 0, x: int = 0, b: int = 0) -> int:
    return 0x40 | (w << 3) | (r << 2) | (x << 1) | b


def _need_rex(reg: int) -> bool:
    return reg >= 8


def _rex_r(reg: int) -> tuple[int, int]:
    """Return (rex_byte, reg_low3) for a register used as ModRM.reg."""
    if reg >= 8:
        return _rex(r=1), reg & 7
    return 0, reg


def _rex_b(reg: int) -> tuple[int, int]:
    """Return (rex_byte, reg_low3) for a register used as ModRM.rm."""
    if reg >= 8:
        return _rex(b=1), reg & 7
    return 0, reg


def _rex_rb(reg_dst: int, reg_src: int) -> tuple[int, int, int]:
    """Return (rex_byte, dst_low3, src_low3) for reg-to-reg."""
    rex = 0
    if reg_dst >= 8:
        rex |= 1 << 2  # R
    if reg_src >= 8:
        rex |= 1      # B
    return rex, reg_dst & 7, reg_src & 7


def _modrm(mod: int, reg: int, rm: int) -> int:
    return ((mod & 3) << 6) | ((reg & 7) << 3) | (rm & 7)


def _sib(scale: int, index: int, base: int) -> int:
    return ((scale & 3) << 6) | ((index & 7) << 3) | (base & 7)


# ── Condition codes ────────────────────────────────────────────────

JO, JNO, JB, JAE, JE, JNE, JBE, JA = range(0, 8)
JS, JNS, JP, JNP, JL, JGE, JLE, JG = range(8, 16)


class X86_64Emitter:  # noqa: N801
    """Emits raw x86-64 machine code bytes into a bytearray buffer."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._labels: dict[str, int] = {}
        self._fixups: list[tuple[int, int, int, str]] = []
        self._label_counter: int = 0

    # ── Buffer access ──────────────────────────────────────────────

    @property
    def buffer(self) -> bytearray:
        return self._buffer

    @property
    def size(self) -> int:
        return len(self._buffer)

    def get_bytes(self) -> bytes:
        return bytes(self._buffer)

    # ── Data emission ──────────────────────────────────────────────

    def emit_byte(self, b: int) -> None:
        self._buffer.append(b & 0xFF)

    def emit_word(self, w: int) -> None:
        self._buffer.extend(struct.pack("<H", w & 0xFFFF))

    def emit_dword(self, d: int) -> None:
        self._buffer.extend(struct.pack("<I", d & 0xFFFFFFFF))

    def emit_qword(self, q: int) -> None:
        self._buffer.extend(struct.pack("<q", q))

    def emit_bytes(self, data: bytes) -> None:
        self._buffer.extend(data)

    # ── Label management ───────────────────────────────────────────

    def emit_label(self, name: str) -> int:
        """Mark current position with a label. Returns position."""
        pos = self.size
        self._labels[name] = pos
        return pos

    def _fresh_label(self, prefix: str = "L") -> str:
        self._label_counter += 1
        return f"{prefix}{self._label_counter}"

    def _add_fixup(self, fixup_type: int, offset: int, label: str) -> None:
        """Record a fixup to be patched later.
        fixup_type: 0 = rel32, 1 = rel8
        """
        self._fixups.append((fixup_type, offset, self.size, label))
        self.emit_dword(0)  # placeholder

    def resolve_labels(self) -> bytes:
        """Patch all forward references and return final bytes."""
        for fixup_type, fixup_offset, placeholder_offset, label in self._fixups:
            if label not in self._labels:
                raise ValueError(f"Undefined label: {label}")
            target = self._labels[label]
            if fixup_type == 0:
                rel = target - (placeholder_offset + 4)
                struct.pack_into("<i", self._buffer, placeholder_offset, rel)
            elif fixup_type == 1:
                rel = target - (placeholder_offset + 1)
                if rel < -128 or rel > 127:
                    raise ValueError(
                        f"rel8 overflow for label {label}: {rel}"
                    )
                self._buffer[placeholder_offset] = rel & 0xFF
            else:
                raise ValueError(f"Unknown fixup type: {fixup_type}")
        return bytes(self._buffer)

    def _here(self) -> int:
        return self.size

    # ── REX prefix emission ────────────────────────────────────────

    def _emit_rex(self, w: int = 0, r: int = 0, x: int = 0, b: int = 0) -> None:
        val = _rex(w, r, x, b)
        if val != 0x40:
            self.emit_byte(val)

    def _emit_vex(self, pp: int, mmmmm: int, w: int = 0, r: int = 0, x: int = 0, b: int = 0) -> None:
        if mmmmm < 0 or mmmmm > 31:
            raise ValueError("VEX mmmmm out of range")
        self.emit_byte(0xC5)
        self.emit_byte(((not r) << 7) | ((mmmmm & 1) << 6) | (pp & 3))
        # 2-byte VEX simplified — sufficient for 128-bit SSE/AVX

    # ── Mov (register to register) ─────────────────────────────────

    def emit_mov(self, reg_dst: int, reg_src: int) -> bytes:
        """mov reg_dst, reg_src  (reg-to-reg, 64-bit)"""
        self._emit_rex(w=1, r=reg_src >= 8, b=reg_dst >= 8)
        self.emit_byte(0x89)
        self.emit_byte(_modrm(3, reg_src & 7, reg_dst & 7))
        return bytes(self._buffer[-3:])

    # ── Arithmetic (reg to reg) ────────────────────────────────────

    def emit_add(self, reg_dst: int, reg_src: int) -> bytes:
        """add reg_dst, reg_src  (64-bit)"""
        self._emit_rex(w=1, r=reg_src >= 8, b=reg_dst >= 8)
        self.emit_byte(0x01)
        self.emit_byte(_modrm(3, reg_src & 7, reg_dst & 7))
        return bytes(self._buffer[-3:])

    def emit_sub(self, reg_dst: int, reg_src: int) -> bytes:
        """sub reg_dst, reg_src  (64-bit)"""
        self._emit_rex(w=1, r=reg_src >= 8, b=reg_dst >= 8)
        self.emit_byte(0x29)
        self.emit_byte(_modrm(3, reg_src & 7, reg_dst & 7))
        return bytes(self._buffer[-3:])

    def emit_imul(self, reg_dst: int, reg_src: int) -> bytes:
        """imul reg_dst, reg_src  (64-bit, two-operand form)"""
        self._emit_rex(w=1, r=reg_dst >= 8, b=reg_src >= 8)
        self.emit_byte(0x0F)
        self.emit_byte(0xAF)
        self.emit_byte(_modrm(3, reg_dst & 7, reg_src & 7))
        return bytes(self._buffer[-4:])

    def emit_xor(self, reg_dst: int, reg_src: int) -> bytes:
        """xor reg_dst, reg_src  (64-bit)"""
        self._emit_rex(w=1, r=reg_src >= 8, b=reg_dst >= 8)
        self.emit_byte(0x31)
        self.emit_byte(_modrm(3, reg_src & 7, reg_dst & 7))
        return bytes(self._buffer[-3:])

    # ── Comparison ─────────────────────────────────────────────────

    def emit_cmp(self, reg_dst: int, reg_src: int) -> bytes:
        """cmp reg_dst, reg_src  (64-bit)"""
        self._emit_rex(w=1, r=reg_src >= 8, b=reg_dst >= 8)
        self.emit_byte(0x39)
        self.emit_byte(_modrm(3, reg_src & 7, reg_dst & 7))
        return bytes(self._buffer[-3:])

    def emit_test(self, reg_dst: int, reg_src: int) -> bytes:
        """test reg_dst, reg_src  (64-bit)"""
        self._emit_rex(w=1, r=reg_src >= 8, b=reg_dst >= 8)
        self.emit_byte(0x85)
        self.emit_byte(_modrm(3, reg_src & 7, reg_dst & 7))
        return bytes(self._buffer[-3:])

    # ── Unary ──────────────────────────────────────────────────────

    def emit_neg(self, reg: int) -> bytes:
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xF7)
        self.emit_byte(_modrm(3, 3, rm))
        return bytes(self._buffer[-3:])

    def emit_not(self, reg: int) -> bytes:
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xF7)
        self.emit_byte(_modrm(3, 2, rm))
        return bytes(self._buffer[-3:])

    # ── Shifts ─────────────────────────────────────────────────────

    def emit_shl(self, reg: int, imm: int) -> bytes:
        """shl reg, imm8"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xC1)
        self.emit_byte(_modrm(3, 4, rm))
        self.emit_byte(imm & 0xFF)
        return bytes(self._buffer[-4:])

    def emit_shr(self, reg: int, imm: int) -> bytes:
        """shr reg, imm8"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xC1)
        self.emit_byte(_modrm(3, 5, rm))
        self.emit_byte(imm & 0xFF)
        return bytes(self._buffer[-4:])

    def emit_sar(self, reg: int, imm: int) -> bytes:
        """sar reg, imm8"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xC1)
        self.emit_byte(_modrm(3, 7, rm))
        self.emit_byte(imm & 0xFF)
        return bytes(self._buffer[-4:])

    # ── Mov immediate ──────────────────────────────────────────────

    def emit_mov_ri(self, reg: int, imm: int) -> bytes:
        """mov reg, imm64  (64-bit immediate)"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xB8 | rm)
        self.emit_qword(imm)
        return bytes(self._buffer[-10:])

    def emit_mov_ri32(self, reg: int, imm: int) -> bytes:
        """mov reg, imm32  (sign-extended 32-bit immediate)"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=(rm != reg))
        self.emit_byte(0xC7)
        self.emit_byte(_modrm(3, 0, rm))
        self.emit_dword(imm)
        return bytes(self._buffer[-7:])

    # ── Memory operations ──────────────────────────────────────────

    def emit_mov_rm(self, reg: int, address: Address) -> bytes:
        """mov reg, [address]  (load from memory)"""
        return self._emit_mov_mem(reg, address, is_load=True, size=64)

    def emit_mov_mr(self, address: Address, reg: int) -> bytes:
        """mov [address], reg  (store to memory)"""
        return self._emit_mov_mem(reg, address, is_load=False, size=64)

    def _emit_mov_mem(self, reg: int, address: Address, is_load: bool, size: int = 64) -> bytes:
        base, index_scale, disp = address
        rex_r, reg_low = _rex_r(reg)
        w = 1 if size == 64 else 0

        if base < 0 and index_scale < 0:
            # Absolute address (disp32)
            self._emit_rex(w=w, r=rex_r >> 2)
            self.emit_byte(0x8B if is_load else 0x89)
            self.emit_byte(_modrm(0, reg_low, 5))
            self.emit_dword(disp)
        elif index_scale >= 0:
            # SIB addressing
            index = index_scale >> 2
            scale = index_scale & 3
            sib_rex_x = 1 if index >= 8 else 0
            rex_b, base_low = _rex_b(base)
            self._emit_rex(w=w, r=rex_r >> 2, x=sib_rex_x, b=rex_b >> 2 if base >= 8 else 0)
            self.emit_byte(0x8B if is_load else 0x89)
            if disp == 0 and base != RBP:
                mod = 0
            elif -128 <= disp <= 127:
                mod = 1
            else:
                mod = 2
            self.emit_byte(_modrm(mod, reg_low, 4))
            self.emit_byte(_sib(scale, index & 7, base_low))
            if mod == 1:
                self.emit_byte(disp & 0xFF)
            elif mod == 2:
                self.emit_dword(disp)
        else:
            # Base + disp
            rex_b, base_low = _rex_b(base)
            self._emit_rex(w=w, r=rex_r >> 2, b=rex_b >> 2)
            self.emit_byte(0x8B if is_load else 0x89)
            if disp == 0 and base != RBP:
                mod = 0
            elif -128 <= disp <= 127:
                mod = 1
            else:
                mod = 2
            self.emit_byte(_modrm(mod, reg_low, base_low))
            if mod == 1:
                self.emit_byte(disp & 0xFF)
            elif mod == 2:
                self.emit_dword(disp)
        return bytes(self._buffer[-16:]) if self._buffer else b""

    def emit_mov_rm8(self, reg: int, address: Address) -> bytes:
        """mov reg, [address]  (8-bit load)"""
        return self._emit_mov_mem(reg, address, is_load=True, size=8)

    def emit_mov_mr8(self, address: Address, reg: int) -> bytes:
        """mov [address], reg  (8-bit store)"""
        return self._emit_mov_mem(reg, address, is_load=False, size=8)

    def emit_mov_rm32(self, reg: int, address: Address) -> bytes:
        """mov reg, [address]  (32-bit load, zero-extend)"""
        return self._emit_mov_mem(reg, address, is_load=True, size=32)

    def emit_mov_mr32(self, address: Address, reg: int) -> bytes:
        """mov [address], reg  (32-bit store)"""
        return self._emit_mov_mem(reg, address, is_load=False, size=32)

    def emit_lea(self, reg: int, address: Address) -> bytes:
        """lea reg, [address]"""
        base, index_scale, disp = address
        rex_r, reg_low = _rex_r(reg)

        if index_scale >= 0:
            index = index_scale >> 2
            scale = index_scale & 3
            sib_rex_x = 1 if index >= 8 else 0
            rex_b, base_low = _rex_b(base)
            self._emit_rex(w=1, r=rex_r >> 2, x=sib_rex_x, b=rex_b >> 2 if base >= 8 else 0)
            self.emit_byte(0x8D)
            if disp == 0 and base != RBP:
                mod = 0
            elif -128 <= disp <= 127:
                mod = 1
            else:
                mod = 2
            self.emit_byte(_modrm(mod, reg_low, 4))
            self.emit_byte(_sib(scale, index & 7, base_low))
            if mod == 1:
                self.emit_byte(disp & 0xFF)
            elif mod == 2:
                self.emit_dword(disp)
        else:
            rex_b, base_low = _rex_b(base)
            self._emit_rex(w=1, r=rex_r >> 2, b=rex_b >> 2)
            self.emit_byte(0x8D)
            if disp == 0 and base != RBP:
                mod = 0
            elif -128 <= disp <= 127:
                mod = 1
            else:
                mod = 2
            self.emit_byte(_modrm(mod, reg_low, base_low))
            if mod == 1:
                self.emit_byte(disp & 0xFF)
            elif mod == 2:
                self.emit_dword(disp)
        return bytes(self._buffer[-16:]) if self._buffer else b""

    # ── Stack operations ───────────────────────────────────────────

    def emit_push(self, reg: int) -> bytes:
        """push reg"""
        start = len(self._buffer)
        rex_byte, rm = _rex_b(reg)
        if rex_byte:
            self.emit_byte(rex_byte)
        self.emit_byte(0x50 | rm)
        return bytes(self._buffer[start:])

    def emit_pop(self, reg: int) -> bytes:
        """pop reg"""
        start = len(self._buffer)
        rex_byte, rm = _rex_b(reg)
        if rex_byte:
            self.emit_byte(rex_byte)
        self.emit_byte(0x58 | rm)
        return bytes(self._buffer[start:])

    # ── Control flow ───────────────────────────────────────────────

    def emit_ret(self) -> bytes:
        """ret"""
        self.emit_byte(0xC3)
        return b"\xC3"

    def emit_call(self, target) -> bytes:
        """call target  (register or relative offset)"""
        start = len(self._buffer)
        if isinstance(target, int) and target > 15:
            # Relative call (offsets > 15 to avoid conflicting with registers)
            self.emit_byte(0xE8)
            self.emit_dword(target & 0xFFFFFFFF)
            return bytes(self._buffer[start:])
        # Register indirect call (target is a register number 0-15)
        rex_byte, rm = _rex_b(target)
        if rex_byte:
            self.emit_byte(rex_byte)
        self.emit_byte(0xFF)
        self.emit_byte(_modrm(3, 2, rm))
        return bytes(self._buffer[start:])

    def emit_jmp(self, offset: int) -> bytes:
        """jmp rel32"""
        self.emit_byte(0xE9)
        self.emit_dword(offset & 0xFFFFFFFF)
        return bytes(self._buffer[-5:])

    def emit_jmp_short(self, offset: int) -> bytes:
        """jmp rel8"""
        self.emit_byte(0xEB)
        self.emit_byte(offset & 0xFF)
        return bytes(self._buffer[-2:])

    def _emit_jcc(self, cc: int, offset: int, long_form: bool = False) -> bytes:
        if long_form or offset < -128 or offset > 127:
            self.emit_byte(0x0F)
            self.emit_byte(0x80 | cc)
            self.emit_dword(offset & 0xFFFFFFFF)
            return bytes(self._buffer[-6:])
        self.emit_byte(0x70 | cc)
        self.emit_byte(offset & 0xFF)
        return bytes(self._buffer[-2:])

    def emit_je(self, offset: int) -> bytes:
        return self._emit_jcc(JE, offset)

    def emit_jne(self, offset: int) -> bytes:
        return self._emit_jcc(JNE, offset)

    def emit_jl(self, offset: int) -> bytes:
        return self._emit_jcc(JL, offset)

    def emit_jge(self, offset: int) -> bytes:
        return self._emit_jcc(JGE, offset)

    def emit_jle(self, offset: int) -> bytes:
        return self._emit_jcc(JLE, offset)

    def emit_jg(self, offset: int) -> bytes:
        return self._emit_jcc(JG, offset)

    def emit_jb(self, offset: int) -> bytes:
        return self._emit_jcc(JB, offset)

    def emit_jae(self, offset: int) -> bytes:
        return self._emit_jcc(JAE, offset)

    def emit_jbe(self, offset: int) -> bytes:
        return self._emit_jcc(JBE, offset)

    def emit_ja(self, offset: int) -> bytes:
        return self._emit_jcc(JA, offset)

    def emit_js(self, offset: int) -> bytes:
        return self._emit_jcc(JS, offset)

    def emit_jns(self, offset: int) -> bytes:
        return self._emit_jcc(JNS, offset)

    def emit_jp(self, offset: int) -> bytes:
        return self._emit_jcc(JP, offset)

    def emit_jnp(self, offset: int) -> bytes:
        return self._emit_jcc(JNP, offset)

    # ── Label-based jumps (auto-patched) ───────────────────────────

    def emit_jmp_to_label(self, label: str) -> None:
        """Emit a jmp that gets patched to the label later."""
        self._add_fixup(0, 0, label)
        self.emit_byte(0xE9)
        # placeholder — _add_fixup already wrote 4 bytes

    def emit_je_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)
        self.emit_byte(0x0F)
        self.emit_byte(0x84)
        self.emit_dword(0)

    def emit_jne_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)
        self.emit_byte(0x0F)
        self.emit_byte(0x85)
        self.emit_dword(0)

    def emit_jl_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)
        self.emit_byte(0x0F)
        self.emit_byte(0x8C)
        self.emit_dword(0)

    def emit_jge_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)
        self.emit_byte(0x0F)
        self.emit_byte(0x8D)
        self.emit_dword(0)

    def emit_jle_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)
        self.emit_byte(0x0F)
        self.emit_byte(0x8E)
        self.emit_dword(0)

    def emit_jg_to_label(self, label: str) -> None:
        self._add_fixup(0, 0, label)
        self.emit_byte(0x0F)
        self.emit_byte(0x8F)
        self.emit_dword(0)

    # ── Division ───────────────────────────────────────────────────

    def emit_cdq(self) -> bytes:
        """cdq  (sign-extend rax into rdx:rax)"""
        self.emit_byte(0x48)  # REX.W
        self.emit_byte(0x99)
        return b"\x48\x99"

    def emit_idiv(self, reg: int) -> bytes:
        """idiv reg  (signed divide rdx:rax by reg)"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=rex_byte >> 2)
        self.emit_byte(0xF7)
        self.emit_byte(_modrm(3, 7, rm))
        return bytes(self._buffer[-3:])

    def emit_div(self, reg: int) -> bytes:
        """div reg  (unsigned divide rdx:rax by reg)"""
        rex_byte, rm = _rex_b(reg)
        self._emit_rex(w=1, b=rex_byte >> 2)
        self.emit_byte(0xF7)
        self.emit_byte(_modrm(3, 6, rm))
        return bytes(self._buffer[-3:])

    # ── Nop / Debug ────────────────────────────────────────────────

    def emit_nop(self) -> bytes:
        """nop"""
        self.emit_byte(0x90)
        return b"\x90"

    def emit_int3(self) -> bytes:
        """int3"""
        self.emit_byte(0xCC)
        return b"\xCC"

    # ── Floating point (SSE2) ──────────────────────────────────────

    def emit_movsd(self, reg_dst: int, reg_src: int) -> bytes:
        """movsd reg_dst, reg_src  (scalar double, reg-to-reg)"""
        rex, dst, src = _rex_rb(reg_dst, reg_src)
        self._emit_rex(r=dst != reg_dst, b=src != reg_src)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x10)
        self.emit_byte(_modrm(3, dst, src))
        return bytes(self._buffer[-5:])

    def emit_addsd(self, reg_dst: int, reg_src: int) -> bytes:
        """addsd reg_dst, reg_src"""
        rex, dst, src = _rex_rb(reg_dst, reg_src)
        self._emit_rex(r=dst != reg_dst, b=src != reg_src)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x58)
        self.emit_byte(_modrm(3, dst, src))
        return bytes(self._buffer[-5:])

    def emit_subsd(self, reg_dst: int, reg_src: int) -> bytes:
        """subsd reg_dst, reg_src"""
        rex, dst, src = _rex_rb(reg_dst, reg_src)
        self._emit_rex(r=dst != reg_dst, b=src != reg_src)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x5C)
        self.emit_byte(_modrm(3, dst, src))
        return bytes(self._buffer[-5:])

    def emit_mulsd(self, reg_dst: int, reg_src: int) -> bytes:
        """mulsd reg_dst, reg_src"""
        rex, dst, src = _rex_rb(reg_dst, reg_src)
        self._emit_rex(r=dst != reg_dst, b=src != reg_src)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x59)
        self.emit_byte(_modrm(3, dst, src))
        return bytes(self._buffer[-5:])

    def emit_divsd(self, reg_dst: int, reg_src: int) -> bytes:
        """divsd reg_dst, reg_src"""
        rex, dst, src = _rex_rb(reg_dst, reg_src)
        self._emit_rex(r=dst != reg_dst, b=src != reg_src)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x5E)
        self.emit_byte(_modrm(3, dst, src))
        return bytes(self._buffer[-5:])

    # ── SSE2 memory ops ────────────────────────────────────────────

    def emit_movsd_load(self, reg: int, address: Address) -> bytes:
        """movsd reg, [address]  (load scalar double from memory)"""
        base, index_scale, disp = address
        rex_r, reg_low = _rex_r(reg)
        self.emit_byte(0xF2)
        self._emit_movsd_mem(reg_low, rex_r, base, index_scale, disp, is_load=True)
        return bytes(self._buffer[-16:]) if self._buffer else b""

    def emit_movsd_store(self, address: Address, reg: int) -> bytes:
        """movsd [address], reg  (store scalar double to memory)"""
        base, index_scale, disp = address
        rex_r, reg_low = _rex_r(reg)
        self.emit_byte(0xF2)
        self._emit_movsd_mem(reg_low, rex_r, base, index_scale, disp, is_load=False)
        return bytes(self._buffer[-16:]) if self._buffer else b""

    def _emit_movsd_mem(self, reg_low: int, rex_r: int, base: int, index_scale: int, disp: int, is_load: bool) -> None:
        op = 0x10 if is_load else 0x11
        if index_scale >= 0:
            index = index_scale >> 2
            scale = index_scale & 3
            sib_rex_x = 1 if index >= 8 else 0
            rex_b, base_low = _rex_b(base)
            self._emit_rex(r=rex_r >> 2, x=sib_rex_x, b=rex_b >> 2 if base >= 8 else 0)
            self.emit_byte(0x0F)
            self.emit_byte(op)
            if disp == 0 and base != RBP:
                mod = 0
            elif -128 <= disp <= 127:
                mod = 1
            else:
                mod = 2
            self.emit_byte(_modrm(mod, reg_low, 4))
            self.emit_byte(_sib(scale, index & 7, base_low))
            if mod == 1:
                self.emit_byte(disp & 0xFF)
            elif mod == 2:
                self.emit_dword(disp)
        else:
            rex_b, base_low = _rex_b(base)
            self._emit_rex(r=rex_r >> 2, b=rex_b >> 2)
            self.emit_byte(0x0F)
            self.emit_byte(op)
            if disp == 0 and base != RBP:
                mod = 0
            elif -128 <= disp <= 127:
                mod = 1
            else:
                mod = 2
            self.emit_byte(_modrm(mod, reg_low, base_low))
            if mod == 1:
                self.emit_byte(disp & 0xFF)
            elif mod == 2:
                self.emit_dword(disp)

    # ── SSE2 convert instructions ──────────────────────────────────

    def emit_cvtsi2sd(self, xmm_reg: int, gp_reg: int) -> bytes:
        """cvtsi2sd xmm_reg, gp_reg  (convert int64 to double)"""
        rex_r, dst_low = _rex_r(xmm_reg)
        rex_b, src_low = _rex_b(gp_reg)
        self._emit_rex(w=1, r=rex_r >> 2, b=rex_b >> 2)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x2A)
        self.emit_byte(_modrm(3, dst_low, src_low))
        return bytes(self._buffer[-5:])

    def emit_cvttsd2si(self, gp_reg: int, xmm_reg: int) -> bytes:
        """cvttsd2si gp_reg, xmm_reg  (convert double to int64)"""
        rex_r, dst_low = _rex_r(gp_reg)
        rex_b, src_low = _rex_b(xmm_reg)
        self._emit_rex(w=1, r=rex_r >> 2, b=rex_b >> 2)
        self.emit_byte(0xF2)
        self.emit_byte(0x0F)
        self.emit_byte(0x2C)
        self.emit_byte(_modrm(3, dst_low, src_low))
        return bytes(self._buffer[-5:])

    def emit_ucomisd(self, reg_dst: int, reg_src: int) -> bytes:
        """ucomisd reg_dst, reg_src  (compare doubles, set flags)"""
        rex, dst, src = _rex_rb(reg_dst, reg_src)
        self._emit_rex(r=dst != reg_dst, b=src != reg_src)
        self.emit_byte(0x66)
        self.emit_byte(0x0F)
        self.emit_byte(0x2E)
        self.emit_byte(_modrm(3, dst, src))
        return bytes(self._buffer[-5:])

    # ── Utility ────────────────────────────────────────────────────

    def emit_align(self, alignment: int, fill: int = 0x90) -> None:
        """Emit padding bytes to align to the given boundary."""
        pad = (alignment - (self.size % alignment)) % alignment
        for _ in range(pad):
            self.emit_byte(fill)

    def emit_bytes_raw(self, data: bytes) -> None:
        """Emit raw bytes directly into the buffer."""
        self._buffer.extend(data)
