# urubuga/realtime.i — Real-time Platform
# WebSocket, SSE, Live Updates, Presence

shyiramo "json"
shyiramo "httpserver"
shyiramo "random"

# ── UrubugaWebSocket — WebSocket Server ──────────────────────────

urwego UrubugaWebSocket
    host: umuntu
    port: int
    ibiciro: {}
    handlers: {}
    connections: {}
    rooms: {}

    umurimo __init__(self, host: umuntu, port: int)
        self.host = host
        self.port = port
        self.ibiciro = {}
        self.handlers = {}
        self.connections = {}
        self.rooms = {}
    iherezo

    umurimo on(self, event: umuntu, handler: ubusa) -> ubusa
        self.handlers[event] = handler
    iherezo

    umurimo gukora(self) -> ubusa
        shyira server = httpserver.UrubugaWebSocketServer.nshya(self.host, self.port)
        
        server.on_connect(lambda conn_id: self._on_connect(conn_id))
        server.on_disconnect(lambda conn_id: self._on_disconnect(conn_id))
        server.on_message(lambda conn_id, msg: self._on_message(conn_id, msg))
        
        self._server = server
        andika "WebSocket server: ws://" + self.host + ":" + str(self.port)
    iherezo

    umurimo _on_connect(self, conn_id: umuntu) -> ubusa
        self.connections[conn_id] = {"id": conn_id, "rooms": []}
        niba "connect" in self.handlers
            self.handlers["connect"](conn_id)
        iherezo
    iherezo

    umurimo _on_disconnect(self, conn_id: umuntu) -> ubusa
        # Remove from all rooms
        buri room in self.connections.get(conn_id, {}).get("rooms", [])
            niba room in self.rooms
                self.rooms[room] = [c for c in self.rooms[room] if c != conn_id]
            iherezo
        iherezo
        self.connections.pop(conn_id, ubusa)
        niba "disconnect" in self.handlers
            self.handlers["disconnect"](conn_id)
        iherezo
    iherezo

    umurimo _on_message(self, conn_id: umuntu, message: umuntu) -> ubusa
        shyira data = json.json_loads(message)
        shyira event = data.get("event", "message")
        
        niba event == "join_room"
            self.join_room(conn_id, data.get("room", "default"))
        cyangwa niba event == "leave_room"
            self.leave_room(conn_id, data.get("room", "default"))
        cyangwa
            niba event in self.handlers
                self.handlers[event](conn_id, data.get("payload", {}))
            iherezo
        iherezo
    iherezo

    umurimo send_to(self, conn_id: umuntu, event: umuntu, payload: ubusa) -> ukuri
        niba self._server == ubusa
            subira ubusa
        iherezo
        
        shyira message = json.json_dumps({"event": event, "payload": payload})
        subira self._server.send_to(conn_id, message)
    iherezo

    umurimo broadcast(self, event: umuntu, payload: ubusa, room: umuntu) -> ubusa
        niba self._server == ubusa
            subira ubusa
        iherezo
        
        shyira message = json.json_dumps({"event": event, "payload": payload})
        
        niba room != ""
            buri conn_id in self.rooms.get(room, [])
                self._server.send_to(conn_id, message)
            iherezo
        cyangwa
            self._server.broadcast(message)
        iherezo
    iherezo

    umurimo join_room(self, conn_id: umuntu, room: umuntu) -> ubusa
        niba room not in self.rooms
            self.rooms[room] = []
        iherezo
        
        niba conn_id not in self.rooms[room]
            self.rooms[room].append(conn_id)
        iherezo
        
        niba conn_id in self.connections
            self.connections[conn_id]["rooms"].append(room)
        iherezo
    iherezo

    umurimo leave_room(self, conn_id: umuntu, room: umuntu) -> ubusa
        niba room in self.rooms
            self.rooms[room] = [c for c in self.rooms[room] if c != conn_id]
        iherezo
        
        niba conn_id in self.connections
            self.connections[conn_id]["rooms"] = [
                r for r in self.connections[conn_id]["rooms"] if r != room
            ]
        iherezo
    iherezo

    umurimo connections_in_room(self, room: umuntu) -> int
        subira len(self.rooms.get(room, []))
    iherezo

    umurimo connection_count(self) -> int
        subira len(self.connections)
    iherezo
iherezo


# ── UrubugaSSE — Server-Sent Events ──────────────────────────────

urwego UrubugaSSE
    clients: {}

    umurimo __init__(self)
        self.clients = {}
    iherezo

    umurimo connect(self, client_id: umuntu) -> ubusa
        self.clients[client_id] = {"id": client_id, "events": []}
    iherezo

    umurimo disconnect(self, client_id: umuntu) -> ubusa
        self.clients.pop(client_id, ubusa)
    iherezo

    umurimo send_event(self, client_id: umuntu, event: umuntu, data: umuntu) -> ubusa
        niba client_id in self.clients
            self.clients[client_id]["events"].append({
                "event": event,
                "data": data,
            })
        iherezo
    iherezo

    umurimo broadcast(self, event: umuntu, data: umuntu) -> ubusa
        buri client in self.clients.values()
            client["events"].append({
                "event": event,
                "data": data,
            })
        iherezo
    iherezo

    umurimo get_events(self, client_id: umuntu) -> []
        niba client_id in self.clients
            events = self.clients[client_id]["events"]
            self.clients[client_id]["events"] = []
            subira events
        iherezo
        subira []
    iherezo

    umurimo client_count(self) -> int
        subira len(self.clients)
    iherezo
iherezo


# ── UrubugaPresence — Presence System ────────────────────────────

urwego UrubugaPresence
    abantu: {}

    umurimo __init__(self)
        self.abantu = {}
    iherezo

    umurimo presence(self, user_id: umuntu, metadata: {}) -> ubusa
        self.abantu[user_id] = {
            "id": user_id,
            "online": ukuri,
            "last_seen": time.time(),
            "metadata": metadata,
        }
    iherezo

    umurimo absence(self, user_id: umuntu) -> ubusa
        niba user_id in self.abantu
            self.abantu[user_id]["online"] = ubusa
            self.abantu[user_id]["last_seen"] = time.time()
        iherezo
    iherezo

    umurimo online(self) -> []
        ibiciro = []
        buri user in self.abantu.values()
            niba user["online"] == ukuri
                ibiciro.append(user)
            iherezo
        iherezo
        subira ibiciro
    iherezo

    umurimo ubwoko(self, user_id: umuntu) -> ukuri
        niba user_id in self.abantu
            subira self.abantu[user_id]["online"]
        iherezo
        subira ubusa
    iherezo
iherezo
