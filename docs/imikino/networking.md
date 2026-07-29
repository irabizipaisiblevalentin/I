# Networking Guide

## Server
```python
from imikino.gukoreshana import get_network

net = get_network()
net.start_server(port=7777, max_players=16)
net.broadcast(NetworkMessage(msg_type="server_started"))
```

## Client
```python
net = get_network()
net.start_client(host="localhost", port=7777)
```

## Handlers
```python
def on_message(msg):
    print(f"Received: {msg.msg_type} from {msg.sender_id}")

net.register_handler("chat", on_message)
```

## Replicated Objects
```python
obj_id = net.create_replicated_object("Player", {
    "position": [0, 0, 0],
    "health": 100,
})
```
