# Networking Guide

## Overview

The `itumanaho_sisitemu` module provides TCP, UDP, HTTP, DNS, DHCP, serial, and
CAN bus networking for systems programming.

## TCP Server

```python
from sisitemu.itumanaho_sisitemu import TCPServer

server = TCPServer(host="0.0.0.0", port=8080)
server.on_connection(lambda conn: print(f"Connected: {conn.remote_addr}"))
server.start()
```

## HTTP Server

```python
from sisitemu.itumanaho_sisitemu import HTTPServer

app = HTTPServer()

@app.route("/api/status")
def status(req, res):
    res.json({"status": "ok", "uptime": 3600})

app.listen(80)
```

## DNS Resolution

```python
from sisitemu.itumanaho_sisitemu import DNSResolver

resolver = DNSResolver()
ips = resolver.resolve("example.com")
print(f"Resolved to: {ips}")
```

## CAN Bus

```python
from sisitemu.itumanaho_sisitemu import CANBus

can = CANBus(interface="can0", bitrate=500000)
can.send(0x123, b"\x01\x02\x03\x04")
message = can.recv()
```

## Network Stack

```python
from sisitemu.itumanaho_sisitemu import NetworkStack

stack = NetworkStack(config={"ip": "192.168.1.100", "subnet": "255.255.255.0"})
stack.add_route(destination="0.0.0.0/0", gateway="192.168.1.1")
result = stack.ping("8.8.8.8")
```
