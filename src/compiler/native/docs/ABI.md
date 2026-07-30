# ABI Documentation

## System V AMD64 ABI

Used on Linux, macOS (Intel), and other Unix-like x86-64 systems.

### Argument Passing

Integer and pointer arguments are passed in registers. Floating-point arguments use SSE registers.

| Argument Position | Integer/Pointer Register | Float Register |
|-------------------|-------------------------|----------------|
| 1st               | `rdi`                   | `xmm0`        |
| 2nd               | `rsi`                   | `xmm1`        |
| 3rd               | `rdx`                   | `xmm2`        |
| 4th               | `rcx`                   | `xmm3`        |
| 5th               | `r8`                    | `xmm4`        |
| 6th               | `r9`                    | `xmm5`        |
| 7th               | `xmm6`                  | `xmm6`        |
| 8th               | `xmm7`                  | `xmm7`        |
| 9th+              | Stack (`[rsp+8*n]`)     | Stack         |

### Return Values

| Type              | Register        |
|-------------------|-----------------|
| Integer/pointer   | `rax`           |
| 64-bit float      | `xmm0`          |
| 128-bit (2 words) | `rax` + `rdx`   |
| Struct (by value) | Stack pointer   |

### Register Usage

| Register  | Type    | Role                          | Save   |
|-----------|---------|-------------------------------|--------|
| `rax`     | GPR     | Return value, scratch         | Caller |
| `rbx`     | GPR     | Callee-saved                  | Callee |
| `rcx`     | GPR     | 4th argument, scratch         | Caller |
| `rdx`     | GPR     | 3rd argument, 2nd return      | Caller |
| `rsi`     | GPR     | 2nd argument                  | Caller |
| `rdi`     | GPR     | 1st argument                  | Caller |
| `rsp`     | GPR     | Stack pointer                 | Special|
| `rbp`     | GPR     | Frame pointer (optional)      | Callee |
| `r8`      | GPR     | 5th argument                  | Caller |
| `r9`      | GPR     | 6th argument                  | Caller |
| `r10`     | GPR     | Scratch                       | Caller |
| `r11`     | GPR     | Scratch                       | Caller |
| `r12`     | GPR     | Callee-saved                  | Callee |
| `r13`     | GPR     | Callee-saved                  | Callee |
| `r14`     | GPR     | Callee-saved                  | Callee |
| `r15`     | GPR     | Callee-saved                  | Callee |
| `xmm0-7`  | XMM     | Arguments and return value    | Caller |
| `xmm8-15` | XMM     | Temporary/scratch             | Caller |

### Stack Frame Layout

```
       High addresses
       +------------------+
       | Argument 8+n     |  (caller's stack, 8 bytes each)
       | ...              |
       | Argument 7       |
       +------------------+ <- rsp+8 on entry (after call pushes return addr)
       | Return address   |  (8 bytes, pushed by call)
       +------------------+ <- rbp (frame pointer)
       | Saved rbp        |  (8 bytes, pushed by prologue)
       +------------------+
       | Callee-saved regs|  (push rbx, r12-r15)
       +------------------+
       | Spill slots      |  (register spills)
       +------------------+
       | Local variables  |  (aligned to 16 bytes)
       +------------------+ <- rsp (after prologue sub rsp, N)
       Low addresses
```

### Red Zone

The 128-byte area below the stack pointer (`[rsp-128]` to `[rsp-1]`) is reserved for leaf functions on x86-64. Leaf functions that do not call other functions may use this area without adjusting `rsp`.

---

## Microsoft x64 ABI

Used on Windows x86-64.

### Argument Passing

| Argument Position | Integer/Pointer Register | Float Register |
|-------------------|-------------------------|----------------|
| 1st               | `rcx`                   | `xmm0`        |
| 2nd               | `rdx`                   | `xmm1`        |
| 3rd               | `r8`                    | `xmm2`        |
| 4th               | `r9`                    | `xmm3`        |
| 5th+              | Stack (`[rsp+32+8*n]`)  | Stack         |

Shadow space (32 bytes) is always allocated by the caller above the return address.

### Return Values

| Type              | Register  |
|-------------------|-----------|
| Integer/pointer   | `rax`     |
| Float/double      | `xmm0`    |

### Register Usage

| Register  | Type    | Role                    | Save     |
|-----------|---------|-------------------------|----------|
| `rax`     | GPR     | Return value, scratch   | Caller   |
| `rbx`     | GPR     | Callee-saved            | Callee   |
| `rcx`     | GPR     | 1st argument            | Caller   |
| `rdx`     | GPR     | 2nd argument            | Caller   |
| `rsi`     | GPR     | Callee-saved            | Callee   |
| `rdi`     | GPR     | Callee-saved            | Callee   |
| `r8`      | GPR     | 3rd argument            | Caller   |
| `r9`      | GPR     | 4th argument            | Caller   |
| `r10`     | GPR     | Scratch                 | Caller   |
| `r11`     | GPR     | Scratch                 | Caller   |
| `r12`     | GPR     | Callee-saved            | Callee   |
| `r13`     | GPR     | Callee-saved            | Callee   |
| `r14`     | GPR     | Callee-saved            | Callee   |
| `r15`     | GPR     | Callee-saved            | Callee   |
| `rbp`     | GPR     | Callee-saved (optional) | Callee   |
| `xmm0-3`  | XMM     | Arguments               | Caller   |
| `xmm4-5`  | XMM     | Scratch                 | Caller   |
| `xmm6-15` | XMM     | Callee-saved            | Callee   |

### Stack Frame Layout

```
       High addresses
       +------------------+
       | Argument 5+n     |  (caller-defined, 8 bytes each)
       | ...              |
       | Argument 5       |
       +------------------+
       | Return address   |  (8 bytes, pushed by call)
       +------------------+
       | Shadow space     |  (32 bytes, allocated by caller)
       +------------------+ <- entry rsp
       | Saved rbp        |  (optional, 8 bytes)
       +------------------+
       | Callee-saved regs|  (rbx, rsi, rdi, r12-r15)
       +------------------+
       | Spill slots      |
       +------------------+
       | Local variables  |
       +------------------+ <- rsp (after sub rsp, N)
       Low addresses
```

### Shadow Space

The caller must allocate 32 bytes of shadow space on the stack before every call. This space can be used by the callee to spill the four register arguments. The callee owns the shadow space and may use it for temporary storage.

### Stack Alignment

The stack must be 16-byte aligned before any `call` instruction. The `call` itself pushes 8 bytes (return address), so the callee sees `rsp % 16 == 8` on entry. The prologue must adjust `rsp` to maintain 16-byte alignment for subsequent calls.

---

## ARM64 ABI

Used on macOS ARM64, Linux ARM64, and other AArch64 systems.

### Argument Passing

| Argument Position | Integer/Pointer Register | Float Register |
|-------------------|-------------------------|----------------|
| 1st               | `x0`                    | `v0`          |
| 2nd               | `x1`                    | `v1`          |
| 3rd               | `x2`                    | `v2`          |
| 4th               | `x3`                    | `v3`          |
| 5th               | `x4`                    | `v4`          |
| 6th               | `x5`                    | `v5`          |
| 7th               | `x6`                    | `v6`          |
| 8th               | `x7`                    | `v7`          |
| 9th+              | Stack (`[sp+8*n]`)      | Stack         |

### Return Values

| Type        | Register  |
|-------------|-----------|
| Integer     | `x0`      |
| Float/double| `v0`      |

### Register Usage

| Register | Type | Role                        | Save     |
|----------|------|-----------------------------|----------|
| `x0`     | GPR  | 1st arg, return value       | Caller   |
| `x1`     | GPR  | 2nd arg                     | Caller   |
| `x2`     | GPR  | 3rd arg                     | Caller   |
| `x3`     | GPR  | 4th arg                     | Caller   |
| `x4`     | GPR  | 5th arg                     | Caller   |
| `x5`     | GPR  | 6th arg                     | Caller   |
| `x6`     | GPR  | 7th arg                     | Caller   |
| `x7`     | GPR  | 8th arg                     | Caller   |
| `x8`     | GPR  | Indirect result location    | Caller   |
| `x9`     | GPR  | Scratch                     | Caller   |
| `x10`    | GPR  | Scratch                     | Caller   |
| `x11`    | GPR  | Scratch                     | Caller   |
| `x12`    | GPR  | Scratch                     | Caller   |
| `x13`    | GPR  | Scratch                     | Caller   |
| `x14`    | GPR  | Scratch                     | Caller   |
| `x15`    | GPR  | Scratch                     | Caller   |
| `x16`    | GPR  | IP0 (scratch, used by stubs)| Caller   |
| `x17`    | GPR  | IP1 (scratch, used by stubs)| Caller   |
| `x18`    | GPR  | Platform register           | Special  |
| `x19`    | GPR  | Callee-saved                | Callee   |
| `x20`    | GPR  | Callee-saved                | Callee   |
| `x21`    | GPR  | Callee-saved                | Callee   |
| `x22`    | GPR  | Callee-saved                | Callee   |
| `x23`    | GPR  | Callee-saved                | Callee   |
| `x24`    | GPR  | Callee-saved                | Callee   |
| `x25`    | GPR  | Callee-saved                | Callee   |
| `x26`    | GPR  | Callee-saved                | Callee   |
| `x27`    | GPR  | Callee-saved                | Callee   |
| `x28`    | GPR  | Callee-saved                | Callee   |
| `x29`    | GPR  | Frame pointer               | Callee   |
| `x30`    | GPR  | Link register (LR)          | Caller   |
| `sp`     | GPR  | Stack pointer               | Special  |
| `xzr`    | GPR  | Zero register               | Special  |
| `v0-v7`  | SIMD | Args and return value       | Caller   |
| `v8-v15` | SIMD | Callee-saved (lower 64 bits)| Callee   |
| `v16-v31`| SIMD | Scratch                     | Caller   |

### Stack Frame Layout

```
       High addresses
       +------------------+
       | Argument 9+n     |  (caller's stack, 8 bytes each)
       | ...              |
       | Argument 9       |
       +------------------+
       | Return address   |  (stored in x30, saved by callee if needed)
       +------------------+
       | Frame record     |  (optional: saved x29, saved x30)
       +------------------+ <- sp (if frame record is absent)
       | Callee-saved regs|  (x19-x28, v8-v15 saved by stp/ldp)
       +------------------+
       | Spill slots      |
       +------------------+
       | Local variables  |
       +------------------+ <- sp (after sub sp, sp, #N)
       Low addresses
```

### Key Differences from x86-64

- Return address is stored in `x30` (link register), not on the stack
- Frame record pairs `x29` (frame pointer) and `x30` (LR) are saved together using `stp x29, x30, [sp, #-16]!`
- No push/pop instructions; stack adjustment uses `sub sp, sp, #N` / `add sp, sp, #N`
- No dedicated flags register; comparisons set `xzr` and condition flags implicitly
- `str/ldr` require immediates that are multiples of the access size
- No red zone in the ARM64 ABI

---

## Parameter Passing Rules Summary

| Convention          | Int Regs | Float Regs | Shadow Space | Stack Alignment |
|---------------------|----------|------------|--------------|-----------------|
| System V AMD64      | `rdi, rsi, rdx, rcx, r8, r9` | `xmm0-xmm7` | 0   | 16-byte  |
| Microsoft x64       | `rcx, rdx, r8, r9` | `xmm0-xmm3` | 32 bytes | 16-byte |
| ARM64 AAPCS         | `x0-x7`  | `v0-v7`    | 0           | 16-byte  |

For all conventions:
- Arguments beyond the register count are passed on the stack in 8-byte slots
- The stack pointer must be 16-byte aligned at the point of each call
- The return value is in `rax`/`xmm0` (System V), `rax`/`xmm0` (Microsoft), or `x0`/`v0` (ARM64)
