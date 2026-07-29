# mobile/network.i — Networking
# HTTP, WebSocket, Offline sync, Background sync

shyiramo "json"
shyiramo "time"
shyiramo "device"

shyira_ko METHOD_GET = "GET"
shyira_ko METHOD_POST = "POST"
shyira_ko METHOD_PUT = "PUT"
shyira_ko METHOD_DELETE = "DELETE"

shyira_ko STATUS_OK = 200
shyira_ko STATUS_ERROR = 400
shyira_ko STATUS_SERVER_ERROR = 500

urwego HTTPClient kora
    umurimo __init__(self, base_url)
        self.base_url = base_url
        self.imitwe = {}
        self.timeout = 30
    iherezo

    umurimo shakisha_imitwe(self, izina, igiciro)
        self.imitwe[izina] = igiciro
    iherezo

    umurimo GET(self, inzira)
        andika("HTTP GET: " + self.base_url + inzira)
        subira {"status": STATUS_OK, "data": {}, "headers": self.imitwe}
    iherezo

    umurimo POST(self, inzira, data)
        andika("HTTP POST: " + self.base_url + inzira)
        subira {"status": STATUS_OK, "data": data, "headers": self.imitwe}
    iherezo

    umurimo PUT(self, inzira, data)
        andika("HTTP PUT: " + self.base_url + inzira)
        subira {"status": STATUS_OK, "data": data, "headers": self.imitwe}
    iherezo

    umurimo DELETE(self, inzira)
        andika("HTTP DELETE: " + self.base_url + inzira)
        subira {"status": STATUS_OK, "data": {}, "headers": self.imitwe}
    iherezo

    umurimo json_(self, inzira, method, data)
        andika("HTTP " + method + " JSON: " + self.base_url + inzira)
        subira {"status": STATUS_OK, "data": data}
    iherezo
iherezo

urwego WebSocket kora
    umurimo __init__(self, url)
        self.url = url
        self.ikora = ubusa
        self.ibyabaye = {}
    iherezo

    umurimo guhuza(self)
        self.ikora = ukuri
        andika("WebSocket: Guhuza kuri " + self.url)
    iherezo

    umurimo guhuza_garuka(self)
        self.ikora = ubusa
        andika("WebSocket: Guhuza garutse")
    iherezo

    umurimo kohereza(self, data)
        niba self.ikora == ukuri kora
            andika("WebSocket: Kohereza " + json.stringify(data))
        iherezo
    iherezo

    umurimo ku_ibyabaye(self, event, handler)
        self.ibyabaye[event] = handler
    iherezo

    umurimo kira_ibyabaye(self, event, data)
        niba event in self.ibyabaye kora
            self.ibyabaye[event](data)
        iherezo
    iherezo
iherezo

urwego Guhuza hanze kora
    umurimo __init__(self)
        self.queue = []
        self.sync_ikora = ubusa
    iherezo

    umurimo ongeza_igikorwa(self, ubwoko, data)
        self.queue.append({
            "ubwoko": ubwoko,
            "data": data,
            "igihe": time.now(),
            "imbaraga": 0,
        })
        andika("Offline: Igikorwa cyongewe kuri queue (" + shobora_umuntu(uburengero(self.queue)) + ")")
    iherezo

    umurimo guhuza(self)
        niba self.sync_ikora kora
            andika("Offline: Gushyira mu murongo biratunganywa")
            subira
        iherezo
        self.sync_ikora = ukuri
        buri igikorwa muri self.queue kora
            andika("Offline: Guhuza " + igikorwa["ubwoko"])
            igikorwa["imbaraga"] = igikorwa["imbaraga"] + 1
        iherezo
        self.queue = []
        self.sync_ikora = ubusa
        andika("Offline: Gushyira mu murongo birangiye")
    iherezo

    umurimo queue_uburengero(self)
        subira uburengero(self.queue)
    iherezo
iherezo

urwego Guhuza inyuma kora
    umurimo __init__(self)
        self.interval = 300
        self.ikora = ubusa
        self.handler = none
    iherezo

    umurimo tangira(self)
        self.ikora = ukuri
        andika("Background sync: Yatangiye (interval=" + shobora_umuntu(self.interval) + "s)")
    iherezo

    umurimo guhagarika(self)
        self.ikora = ubusa
        andika("Background sync: Yahagarijwe")
    iherezo

    umurimo ku_sync(self, handler)
        self.handler = handler
    iherezo

    umurimo gukora_sync(self)
        niba self.ikora kandi self.handler != none kora
            self.handler()
            andika("Background sync: Gukora sync")
        iherezo
    iherezo
iherezo

umurimo ubaka_http(base_url)
    subira HTTPClient.nshya(base_url)
iherezo

umurimo ubaka_websocket(url)
    subira WebSocket.nshya(url)
iherezo
