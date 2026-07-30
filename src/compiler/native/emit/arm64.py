"""
ARM64 Native Binary Emitter (Stub)

Emits ARM64 machine code bytes. Currently a stub implementation with
basic operations — sufficient for testing and incremental development.
"""

from __future__ import annotations

import struct

# ── Register constants ─────────────────────────────────────────────

X0, X1, X2, X3, X4, X5, X6, X7 = range(8)
X8, X9, X10, X11, X12, X13, X14, X15 = range(8, 16)
X16, X17, X18, X19, X20, X21, X22, X23 = range(16, 24)
X24, X25, X26, X27, X28, X29, X30 = range(24, 31)
SP = 31

W0, W1, W2, W3, W4, W5, W6, W7 = range(8)
W8, W9, W10, W11, W12, W13, W14, W15 = range(8, 16)
W16, W17, W18, W19, W20, W21, W22, W23 = range(16, 24)
W24, W25, W26, W27, W28, W29, W30 = range(24, 31)
WSP = 31

V0, V1, V2, V3, V4, V5, V6, V7 = range(8)
V8, V9, V10, V11, V12, V13, V14, V15 = range(8, 16)
V16, V17, V18, V19, V20, V21, V22, V23 = range(16, 24)
V24, V25, V26, V27, V28, V29, V30, V31 = range(24, 32)

# Condition codes
EQ, NE, CS, CC, MI, PL, VS, VC = range(8)
HI, LS, GE, LT, GT, LE, AL, NV = range(8, 16)


class ARM64Emitter:
    """Emits raw ARM64 machine code bytes into a bytearray buffer.

    This is a stub implementation covering basic operations.
    """

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._labels: dict[str, int] = {}
        self._fixups: list[tuple[int, str]] = []

    # ── Buffer access ──────────────────────────────────────────────

    @property
    def buffer(self) -> bytearray:
        return self._buffer

    @property
    def size(self) -> int:
        return len(self._buffer)

    def get_bytes(self) -> bytes:
        return bytes(self._buffer)

    # ── Data emission helpers ──────────────────────────────────────

    def emit_byte(self, b: int) -> None:
        self._buffer.append(b & 0xFF)

    def emit_dword(self, d: int) -> None:
        self._buffer.extend(struct.pack("<I", d & 0xFFFFFFFF))

    def emit_qword(self, q: int) -> None:
        self._buffer.extend(struct.pack("<q", q))

    def emit_bytes(self, data: bytes) -> None:
        self._buffer.extend(data)

    def emit_insn(self, insn: int) -> None:
        """Emit a 32-bit ARM64 instruction."""
        self.emit_dword(insn)

    # ── Label management ───────────────────────────────────────────

    def emit_label(self, name: str) -> int:
        """Mark current position with a label. Returns position."""
        pos = self.size
        self._labels[name] = pos
        return pos

    def resolve_labels(self) -> bytes:
        """Patch all forward references and return final bytes."""
        for offset, label in self._fixups:
            if label not in self._labels:
                raise ValueError(f"Undefined label: {label}")
            target = self._labels[label]
            rel = target - offset
            # Patch the 26-bit or 19-bit immediate
            insn_bytes = self._buffer[offset:offset + 4]
            if len(insn_bytes) < 4:
                raise ValueError(f"Fixup at {offset} out of range")
            insn = struct.unpack_from("<I", self._buffer, offset)[0]
            if (insn & 0xFC000000) == 0x14000000:
                # B / BL — 26-bit immediate
                imm26 = (rel >> 2) & 0x03FFFFFF
                insn = (insn & 0xFC000000) | imm26
            elif (insn & 0x7C000000) >> 26 == 5:
                # B.cond — 19-bit immediate (cond branch)
                imm19 = (rel >> 2) & 0x7FFFF
                insn = (insn & 0xFF00001F) | (imm19 << 5)
            else:
                # CBZ/CBNZ or TBZ/TBNZ — 19-bit or 14-bit; fallback
                imm19 = (rel >> 2) & 0x7FFFF
                insn = (insn & 0xFF00001F) | (imm19 << 5)
            struct.pack_into("<I", self._buffer, offset, insn)
        return bytes(self._buffer)

    def _add_fixup(self, offset: int, label: str) -> None:
        self._fixups.append((offset, label))

    # ── Arithmetic ─────────────────────────────────────────────────

    def emit_mov(self, reg_dst: int, reg_src: int) -> bytes:
        """mov Xd, Xm  (alias for ORR Xd, XZR, Xm)"""
        insn = 0xAA0003E0 | (reg_src & 0x1F) | ((reg_dst & 0x1F) << 0)
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_add(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """add Xd, Xn, Xm"""
        insn = (0x8B000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_sub(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """sub Xd, Xn, Xm"""
        insn = (0xCB000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_mul(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """mul Xd, Xn, Xm"""
        insn = (0x9B007C00 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_sdiv(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """sdiv Xd, Xn, Xm"""
        insn = (0x9AC00C00 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_udiv(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """udiv Xd, Xn, Xm"""
        insn = (0x9AC00800 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Add immediate ──────────────────────────────────────────────

    def emit_add_imm(self, reg_dst: int, reg_src: int, imm: int) -> bytes:
        """add Xd, Xn, #imm  (12-bit unsigned immediate)"""
        if imm < 0 or imm > 0xFFF:
            raise ValueError(f"add immediate out of range: {imm}")
        insn = (0x91000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                (imm << 10))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_sub_imm(self, reg_dst: int, reg_src: int, imm: int) -> bytes:
        """sub Xd, Xn, #imm  (12-bit unsigned immediate)"""
        if imm < 0 or imm > 0xFFF:
            raise ValueError(f"sub immediate out of range: {imm}")
        insn = (0xD1000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                (imm << 10))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Mov immediate ──────────────────────────────────────────────

    def emit_mov_imm(self, reg: int, imm: int) -> bytes:
        """mov Xd, #imm  (16-bit immediate via MOVZ)"""
        if imm < 0 or imm > 0xFFFF:
            raise ValueError(f"mov immediate out of 16-bit range: {imm}")
        insn = (0xD2800000 |
                ((reg & 0x1F) << 0) |
                (imm << 5))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_movk(self, reg: int, imm: int, shift: int = 0) -> bytes:
        """movk Xd, #imm, lsl #shift  (16-bit immediate into register)"""
        if imm < 0 or imm > 0xFFFF:
            raise ValueError(f"movk immediate out of 16-bit range: {imm}")
        if shift not in (0, 16, 32, 48):
            raise ValueError(f"movk shift must be 0, 16, 32, or 48: {shift}")
        hw = shift // 16
        insn = (0xF2800000 |
                ((reg & 0x1F) << 0) |
                (imm << 5) |
                (hw << 21))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Comparison ─────────────────────────────────────────────────

    def emit_cmp(self, reg_src: int, reg_op: int) -> bytes:
        """cmp Xn, Xm  (alias for SUBS XZR, Xn, Xm)"""
        insn = (0xEB00001F |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_cmp_imm(self, reg_src: int, imm: int) -> bytes:
        """cmp Xn, #imm  (12-bit unsigned immediate)"""
        if imm < 0 or imm > 0xFFF:
            raise ValueError(f"cmp immediate out of range: {imm}")
        insn = (0xF100001F |
                ((reg_src & 0x1F) << 5) |
                (imm << 10))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Logical ────────────────────────────────────────────────────

    def emit_and(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """and Xd, Xn, Xm"""
        insn = (0x8A000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_orr(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """orr Xd, Xn, Xm"""
        insn = (0xAA000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_eor(self, reg_dst: int, reg_src: int, reg_op: int) -> bytes:
        """eor Xd, Xn, Xm"""
        insn = (0xCA000000 |
                ((reg_dst & 0x1F) << 0) |
                ((reg_src & 0x1F) << 5) |
                ((reg_op & 0x1F) << 16))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Memory ─────────────────────────────────────────────────────

    def emit_ldr(self, reg: int, address: tuple[int, int]) -> bytes:
        """ldr Xt, [Xn, #imm]  (64-bit, unsigned offset)"""
        base, imm = address
        if imm < 0 or imm > 32760 or imm % 8 != 0:
            raise ValueError(f"ldr offset out of range or not 8-aligned: {imm}")
        insn = (0xF9400000 |
                ((reg & 0x1F) << 0) |
                ((base & 0x1F) << 5) |
                ((imm // 8) << 10))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_str(self, address: tuple[int, int], reg: int) -> bytes:
        """str Xt, [Xn, #imm]  (64-bit, unsigned offset)"""
        base, imm = address
        if imm < 0 or imm > 32760 or imm % 8 != 0:
            raise ValueError(f"str offset out of range or not 8-aligned: {imm}")
        insn = (0xF9000000 |
                ((reg & 0x1F) << 0) |
                ((base & 0x1F) << 5) |
                ((imm // 8) << 10))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_ldr_literal(self, reg: int, label: str) -> bytes:
        """ldr Xt, label  (literal pool load — requires fixup)"""
        insn = 0x58000000 | (reg & 0x1F)
        pos = self.size
        self.emit_insn(insn)
        self._add_fixup(pos, label)
        return bytes(self._buffer[-4:])

    def emit_adr(self, reg: int, label: str) -> bytes:
        """adr Xd, label"""
        insn = 0x10000000 | ((reg & 0x1F) << 0)
        pos = self.size
        self.emit_insn(insn)
        self._add_fixup(pos, label)
        return bytes(self._buffer[-4:])

    def emit_adrp(self, reg: int, label: str) -> bytes:
        """adrp Xd, label"""
        insn = 0x90000000 | ((reg & 0x1F) << 0)
        pos = self.size
        self.emit_insn(insn)
        self._add_fixup(pos, label)
        return bytes(self._buffer[-4:])

    # ── Stack ──────────────────────────────────────────────────────

    def emit_stp(self, reg1: int, reg2: int, address: tuple[int, int]) -> bytes:
        """stp Xt1, Xt2, [Xn, #imm]  (store pair, pre-index)"""
        base, imm = address
        if imm < -512 or imm > 504 or imm % 8 != 0:
            raise ValueError(f"stp offset out of range or not 8-aligned: {imm}")
        imm_val = (imm // 8) & 0x7F
        insn = (0xA9000000 |
                ((reg1 & 0x1F) << 0) |
                ((reg2 & 0x1F) << 10) |
                ((base & 0x1F) << 5) |
                (imm_val << 15))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_ldp(self, reg1: int, reg2: int, address: tuple[int, int]) -> bytes:
        """ldp Xt1, Xt2, [Xn, #imm]  (load pair, post-index)"""
        base, imm = address
        if imm < -512 or imm > 504 or imm % 8 != 0:
            raise ValueError(f"ldp offset out of range or not 8-aligned: {imm}")
        imm_val = (imm // 8) & 0x7F
        insn = (0xA9400000 |
                ((reg1 & 0x1F) << 0) |
                ((reg2 & 0x1F) << 10) |
                ((base & 0x1F) << 5) |
                (imm_val << 15))
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Control flow ───────────────────────────────────────────────

    def emit_b(self, target) -> bytes:
        """b label/offset  (unconditional branch)"""
        if isinstance(target, str):
            insn = 0x14000000
            pos = self.size
            self.emit_insn(insn)
            self._add_fixup(pos, target)
        else:
            # Direct offset (used after fixup)
            imm26 = (target >> 2) & 0x03FFFFFF
            insn = 0x14000000 | imm26
            self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_bl(self, target) -> bytes:
        """bl label/offset  (branch and link)"""
        if isinstance(target, str):
            insn = 0x94000000
            pos = self.size
            self.emit_insn(insn)
            self._add_fixup(pos, target)
        else:
            imm26 = (target >> 2) & 0x03FFFFFF
            insn = 0x94000000 | imm26
            self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_br(self, reg: int) -> bytes:
        """br Xn  (branch to register)"""
        insn = 0xD61F0000 | ((reg & 0x1F) << 5)
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_blr(self, reg: int) -> bytes:
        """blr Xn  (branch with link to register)"""
        insn = 0xD63F0000 | ((reg & 0x1F) << 5)
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_ret(self, reg: int = X30) -> bytes:
        """ret Xn  (return from subroutine, default LR)"""
        insn = 0xD65F0000 | ((reg & 0x1F) << 5)
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_bcond(self, cond: int, label: str) -> bytes:
        """b.{cond} label  (conditional branch)"""
        insn = 0x54000000 | (cond & 0xF)
        pos = self.size
        self.emit_insn(insn)
        self._add_fixup(pos, label)
        return bytes(self._buffer[-4:])

    def emit_beq(self, label: str) -> bytes:
        return self.emit_bcond(EQ, label)

    def emit_bne(self, label: str) -> bytes:
        return self.emit_bcond(NE, label)

    def emit_blt(self, label: str) -> bytes:
        return self.emit_bcond(LT, label)

    def emit_bge(self, label: str) -> bytes:
        return self.emit_bcond(GE, label)

    def emit_ble(self, label: str) -> bytes:
        return self.emit_bcond(LE, label)

    def emit_bgt(self, label: str) -> bytes:
        return self.emit_bcond(GT, label)

    def emit_cbz(self, reg: int, label: str) -> bytes:
        """cbz Xt, label  (compare and branch if zero)"""
        insn = 0x34000000 | ((reg & 0x1F) << 0)
        pos = self.size
        self.emit_insn(insn)
        self._add_fixup(pos, label)
        return bytes(self._buffer[-4:])

    def emit_cbnz(self, reg: int, label: str) -> bytes:
        """cbnz Xt, label  (compare and branch if non-zero)"""
        insn = 0x35000000 | ((reg & 0x1F) << 0)
        pos = self.size
        self.emit_insn(insn)
        self._add_fixup(pos, label)
        return bytes(self._buffer[-4:])

    # ── Nop / Debug ────────────────────────────────────────────────

    def emit_nop(self) -> bytes:
        """nop"""
        self.emit_insn(0xD503201F)
        return bytes(self._buffer[-4:])

    def emit_brk(self, imm: int = 0) -> bytes:
        """brk #imm  (debug breakpoint)"""
        if imm < 0 or imm > 0xFFFF:
            raise ValueError(f"brk immediate out of 16-bit range: {imm}")
        insn = 0xD4200000 | (imm << 5)
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    def emit_hlt(self, imm: int = 0) -> bytes:
        """hlt #imm  (halt)"""
        if imm < 0 or imm > 0xFFFF:
            raise ValueError(f"hlt immediate out of 16-bit range: {imm}")
        insn = 0xD4400000 | (imm << 5)
        self.emit_insn(insn)
        return bytes(self._buffer[-4:])

    # ── Utility ────────────────────────────────────────────────────

    def emit_align(self, alignment: int, fill: int = 0x00) -> None:
        """Emit padding bytes to align to the given boundary."""
        pad = (alignment - (self.size % alignment)) % alignment
        for _ in range(pad):
            self.emit_byte(fill)

    def emit_bytes_raw(self, data: bytes) -> None:
        """Emit raw bytes directly into the buffer."""
        self._buffer.extend(data)
