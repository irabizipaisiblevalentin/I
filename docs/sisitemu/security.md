# Systems Security Guide

## Overview

The `umutekano_sisitemu` module provides memory protection, sandboxing,
cryptography, secure IPC, stack protection, and audit logging for systems
programming.

## Memory Protection

```python
from sisitemu.umutekano_sisitemu import MemoryProtectionUnit, MPURegion

mpu = MemoryProtectionUnit()
region = MPURegion(base=0x20000000, size=4096, permissions="rw-", enabled=True)
mpu.configure_region(0, region)
mpu.enable()
```

## Sandboxing

```python
from sisitemu.umutekano_sisitemu import Sandbox

sandbox = Sandbox(name="untrusted_code")
sandbox.add_permission("fs.read", ["/tmp/"])
sandbox.add_permission("net.connect", ["*.example.com:443"])
sandbox.run(lambda: print("Running in sandbox"))
```

## Cryptography

```python
from sisitemu.umutekano_sisitemu import CryptographicEngine

crypto = CryptographicEngine()
key = crypto.generate_key("aes-256-gcm")
encrypted = crypto.encrypt("aes-256-gcm", key, b"secret data")
decrypted = crypto.decrypt("aes-256-gcm", key, encrypted)
hash_val = crypto.hash("sha-256", b"data")
signature = crypto.sign(private_key, b"message")
```

## Secure IPC

```python
from sisitemu.umutekano_sisitemu import SecureIPCChannel

channel = SecureIPCChannel(name="trusted_channel")
channel.bind()
channel.send(b"authenticated message")
data = channel.recv()
```

## Audit Logging

```python
from sisitemu.umutekano_sisitemu import AuditLog

log = AuditLog()
log.record(event="process_create", pid=1234, user="root")
log.export("syslog.json")
```
