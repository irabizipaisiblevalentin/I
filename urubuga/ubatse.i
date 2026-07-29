shyiramo "httpserver"
shyiramo "json"
shyiramo "database"
shyiramo "time"
shyiramo "security"
shyiramo "text"

shyira_ko URUBUGA_VERSION = "0.1.0"
shyira_ko IKOSA_404 = 404
shyira_ko IKOSA_405 = 405
shyira_ko IKOSA_500 = 500
shyira_ko STATUS_OK = 200
shyira_ko STATUS_REDIRECT = 302

urwego UrubugaIkosa kora
    umurimo __init__(self, inkuru, icyiciro)
        self.inkuru = inkuru
        self.icyiciro = icyiciro
    iherezo

    umurimo __str__(self) -> umuntu
        subira "UrubugaIkosa(" + shobora_umuntu(self.icyiciro) + "): " + self.inkuru
    iherezo
iherezo

urwego UrubugaAmakuru kora
    umurimo __init__(self, izina, debug)
        self.izina = izina
        self.debug = debug
        self.history = []
    iherezo

    umurimo info_(self, inkuru)
        shyiramo entry = {"ubwoko": "info", "inkuru": inkuru, "time": time.now()}
        self.history.append(entry)
        andika("[INFO] " + inkuru)
    iherezo

    umurimo ikosa_(self, inkuru)
        shyiramo entry = {"ubwoko": "error", "inkuru": inkuru, "time": time.now()}
        self.history.append(entry)
        andika("[ERROR] " + inkuru)
    iherezo

    umurimo debug_(self, inkuru)
        niba self.debug kora
            shyiramo entry = {"ubwoko": "debug", "inkuru": inkuru, "time": time.now()}
            self.history.append(entry)
            andika("[DEBUG] " + inkuru)
        iherezo
    iherezo
iherezo

urwego UrubugaIbiciro kora
    umurimo __init__(self, igihe_cyo_gutangira)
        self.data = {}
        self.igihe_cyo_gutangira = igihe_cyo_gutangira
    iherezo

    umurimo shakisha(self, uruhushya, data, igihe)
        self.data[uruhushya] = {"data": data, "igiciro": time.now() + igihe}
    iherezo

    umurimo shakisha_kuri(self, uruhushya)
        niba uruhushya in self.data kora
            shyiramo entry = self.data[uruhushya]
            niba time.now() < entry["igiciro"] kora
                subira entry["data"]
            cyangwa
                shyiramo _ = self.data.pop(uruhushya)
                subira none
            iherezo
        cyangwa
            subira none
        iherezo
    iherezo

    umurimo siba(self, uruhushya)
        niba uruhushya in self.data kora
            shyiramo _ = self.data.pop(uruhushya)
        iherezo
    iherezo
iherezo

urwego UrubugaUmuyoboro kora
    umurimo __init__(self)
        self.inzira = []
    iherezo

    umurimo ongeza(self, uburyo, inzira, handler)
        self.inzira.append({"uburyo": uburyo, "inzira": inzira, "handler": handler})
    iherezo

    umurimo shakisha(self, uburyo, inzira)
        buri route muri self.inzira kora
            niba route["uburyo"] == uburyo kora
                niba self._uhambaye(route["inzira"], inzira) kora
                    subira route
                iherezo
            iherezo
        iherezo
        subira none
    iherezo

    umurimo _uhambaye(self, template, inzira)
        shyiramo template_parts = template.split("/")
        shyiramo inzira_parts = inzira.split("/")
        niba uburengero(template_parts) != uburengero(inzira_parts) kora
            subira ubusa
        iherezo
        shyiramo i = 0
        wihuse i < uburengero(template_parts) kora
            niba template_parts[i].startswith("{") kora
                # Dynamic segment - always matches
            cyangwa niba template_parts[i] != inzira_parts[i] kora
                subira ubusa
            iherezo
            i = i + 1
        iherezo
        subira ukuri
    iherezo

    umurimo gukora_params(self, template, inzira)
        shyiramo params = {}
        shyiramo template_parts = template.split("/")
        shyiramo inzira_parts = inzira.split("/")
        shyiramo i = 0
        wihuse i < uburengero(template_parts) kora
            niba template_parts[i].startswith("{") kora
                shyiramo key = template_parts[i].slice(1, -1)
                params[key] = inzira_parts[i]
            iherezo
            i = i + 1
        iherezo
        subira params
    iherezo
iherezo

urwego UrubugaAmategeko kora
    umurimo __init__(self)
        self.data = {}
    iherezo

    umurimo shakisha(self, izina, igiciro)
        self.data[izina] = igiciro
    iherezo

    umurimo igiciro(self, izina)
        subira self.data[izina]
    iherezo
iherezo

urwego UrubugaIcamba kora
    umurimo __init__(self, app, prefix)
        self.app = app
        self.prefix = prefix
    iherezo

    umurimo GET(self, inzira, handler)
        self.app.GET(self.prefix + inzira, handler)
    iherezo

    umurimo POST(self, inzira, handler)
        self.app.POST(self.prefix + inzira, handler)
    iherezo

    umurimo PUT(self, inzira, handler)
        self.app.PUT(self.prefix + inzira, handler)
    iherezo

    umurimo DELETE(self, inzira, handler)
        self.app.DELETE(self.prefix + inzira, handler)
    iherezo
iherezo

urwego UrubugaPorogaramu kora
    umurimo __init__(self)
        self.liste = []
    iherezo

    umurimo ongeza(self, handler)
        self.liste.append(handler)
    iherezo

    umurimo gukora(self, req)
        buri handler muri self.liste kora
            shyiramo result = handler(req)
            niba result != none kora
                subira result
            iherezo
        iherezo
        subira none
    iherezo
iherezo

urwego UrubugaInyandikorumurongo kora
    umurimo __init__(self)
        self.amayandiko = {}
    iherezo

    umurimo shakisha(self, izina, inyandiko)
        self.amayandiko[izina] = inyandiko
    iherezo

    umurimo dorera(self, izina, data)
        niba izina in self.amayandiko kora
            shyiramo inyandiko = self.amayandiko[izina]
            buri key muri data ibiciro kora
                shyiramo umugereka = "{{ " + key + " }}"
                shyiramo igiciro = data[key]
                inyandiko = inyandiko.replace(umugereka, shobora_umuntu(igiciro))
            iherezo
            subira inyandiko
        iherezo
        subira "Template not found: " + izina
    iherezo
iherezo

urwego UrubugaUburinzi kora
    umurimo __init__(self, jwt_secret, jwt_expires)
        self.jwt_secret = jwt_secret
        self.jwt_expires = jwt_expires
    iherezo

    umurimo hash_password(self, password)
        subira security.sha256(password + self.jwt_secret)
    iherezo

    umurimo check_password(self, password, hashed)
        subira self.hash_password(password) == hashed
    iherezo

    umurimo generate_token(self, data)
        shyiramo payload = shobora_umuntu(data) + ":" + shobora_umuntu(time.now() + self.jwt_expires)
        subira security.hmac_sha256(payload, self.jwt_secret)
    iherezo

    umurimo validate_token(self, token)
        # Basic validation - in production use proper JWT
        subira token != none and uburengero(token) > 0
    iherezo
iherezo

urwego UrubugaUbubiko kora
    umurimo __init__(self, db_path)
        self.db_path = db_path
        self.db = database.kwinjira(db_path)
    iherezo

    umurimo gukora_icyumba(self, izina, columns)
        shyiramo sql = "CREATE TABLE IF NOT EXISTS " + izina + " (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        shyiramo parts = []
        buri col_name muri columns ibiciro kora
            shyiramo col = columns[col_name]
            parts.append(col_name + " " + col["ubwoko"])
        iherezo
        sql = sql + ", ".join(parts) + ")"
        self.db.gukora(sql)
    iherezo

    umurimo injiza(self, icyumba, data)
        shyiramo keys = []
        shyiramo values = []
        buri key muri data ibiciro kora
            keys.append(key)
            values.append(shobora_umuntu(data[key]))
        iherezo
        shyiramo sql = "INSERT INTO " + icyumba + " (" + ", ".join(keys) + ") VALUES (" + ", ".join(values) + ")"
        self.db.gukora(sql)
    iherezo

    umurimo shakisha(self, icyumba, data)
        shyiramo parts = []
        buri key muri data ibiciro kora
            parts.append(key + " = '" + shobora_umuntu(data[key]) + "'")
        iherezo
        shyiramo sql = "SELECT * FROM " + cyumba + " WHERE " + ", ".join(parts)
        subira self.db.guharura(sql)
    iherezo

    umurimo shakisha_id(self, icyumba, id)
        shyiramo sql = "SELECT * FROM " + icyumba + " WHERE id = " + shobora_umuntu(id)
        subira self.db.guharura(sql)
    iherezo

    umurimo hindura(self, icyumba, data, clause, params)
        shyiramo parts = []
        buri key muri data ibiciro kora
            parts.append(key + " = '" + shobora_umuntu(data[key]) + "'")
        iherezo
        shyiramo sql = "UPDATE " + icyumba + " SET " + ", ".join(parts) + " WHERE " + clause
        self.db.gukora(sql)
    iherezo

    umurimo siba(self, icyumba, clause, params)
        shyiramo sql = "DELETE FROM " + icyumba + " WHERE " + clause
        self.db.gukora(sql)
    iherezo

    umurimo guharura(self, sql)
        subira self.db.guharura(sql)
    iherezo

    umurimo gufungura(self)
        self.db.close()
    iherezo
iherezo

urwego UrubugaAmakuru_ kora
    umurimo __init__(self)
        self.amakuru = {}
    iherezo

    umurimo shakisha(self, izina, ibiciro)
        self.amakuru[izina] = ibiciro
    iherezo

    umurimo giye(self, izina)
        subira self.amakuru[izina]
    iherezo

    umurimo uburengero_(self)
        subira uburengero(self.amakuru)
    iherezo
iherezo

urwego UrubugaKubohora kora
    umurimo __init__(self)
        self.amakeneye = []
    iherezo

    umurimo ongeza(self, izina, umurimo_wa_handler)
        self.amakeneye.append({"izina": izina, "handler": umurimo_wa_handler})
    iherezo

    umurimo gukora(self, req)
        buri kubohora muri self.amakeneye kora
            shyiramo result = kubohora["handler"](req)
            niba result != none kora
                subira result
            iherezo
        iherezo
        subira none
    iherezo
iherezo

urwego UrubugaApplication kora
    umurimo __init__(self, izina, ubuvandimwe)
        self.izina = izina
        self.ubuvandimwe = ubuvandimwe
        self.umuyoboro = UrubugaUmuyoboro.nshya()
        self.amategeko = UrubugaAmategeko.nshya()
        self.porogaramu = UrubugaPorogaramu.nshya()
        self.inyandikorumurongo = UrubugaInyandikorumurongo.nshya()
        self.amakuru = UrubugaAmakuru.nshya(self.izina, ukuri)
        self.ibiciro = UrubugaIbiciro.nshya(300)
        self.uburinzi_ = none
        self.ububiko = none
        self.debug = ubusa
    iherezo

    umurimo GET(self, inzira, handler)
        self.umuyoboro.ongeza("GET", inzira, handler)
    iherezo

    umurimo POST(self, inzira, handler)
        self.umuyoboro.ongeza("POST", inzira, handler)
    iherezo

    umurimo PUT(self, inzira, handler)
        self.umuyoboro.ongeza("PUT", inzira, handler)
    iherezo

    umurimo DELETE(self, inzira, handler)
        self.umuyoboro.ongeza("DELETE", inzira, handler)
    iherezo

    umurimo PATCH(self, inzira, handler)
        self.umuyoboro.ongeza("PATCH", inzira, handler)
    iherezo

    umurimo shakisha_porogaramu(self, handler)
        self.porogaramu.ongeza(handler)
    iherezo

    umurimo shakisha_ububiko(self, db_path)
        self.ububiko = UrubugaUbubiko.nshya(db_path)
    iherezo

    umurimo shakisha_amategeko(self, izina, igiciro)
        self.amategeko.shakisha(izina, igiciro)
    iherezo

    umurimo shakisha_jwt(self, secret, expires)
        self.uburinzi_ = UrubugaUburinzi.nshya(secret, expires)
    iherezo

    umurimo gukora_icyumba(self, izina, columns)
        niba self.ububiko != none kora
            self.ububiko.gukora_icyumba(izina, columns)
        iherezo
    iherezo

    umurimo json_(self, data, status)
        subira {
            "status": status,
            "headers": {"Content-Type": "application/json"},
            "body": json.stringify(data),
        }
    iherezo

    umurimo html_(self, html, status)
        subira {
            "status": status,
            "headers": {"Content-Type": "text/html"},
            "body": html,
        }
    iherezo

    umurimo redirect(self, url, status)
        niba status == none kora
            status = STATUS_REDIRECT
        iherezo
        subira {
            "status": status,
            "headers": {"Location": url},
            "body": "",
        }
    iherezo

    umurimo error_(self, status, message)
        subira {
            "status": status,
            "headers": {"Content-Type": "application/json"},
            "body": json.stringify({"error": message, "status": status}),
        }
    iherezo

    umurimo dorera(self, template, data)
        subira self.inyandikorumurongo.dorera(template, data)
    iherezo

    umurimo icamba(self, prefix)
        subira UrubugaIcamba.nshya(self, prefix)
    iherezo

    umurimo _handle_request(self, req)
        # Run middleware
        shyiramo mw_result = self.porogaramu.gukora(req)
        niba mw_result != none kora
            subira mw_result
        iherezo

        # Find route
        shyiramo route = self.umuyoboro.shakisha(req.method, req.path)
        niba route == none kora
            subira self.error_(IKOSA_404, "Inzira itabonetse: " + req.path)
        iherezo

        # Extract params
        shyiramo params = self.umuyoboro.gukora_params(route["inzira"], req.path)
        req.params = params

        # Call handler
        kora
            subira route["handler"](req)
        ikinyoma kuri e kora
            self.amakuru.ikosa_("Ikosa ryabaye: " + shobora_umuntu(e))
            subira self.error_(IKOSA_500, "Ikosa rya mbere: " + shobora_umuntu(e))
        iherezo
    iherezo

    umurimo gukora(self, port)
        andika("Ruri gufatira kuri port " + shobora_umuntu(port) + "...")
        self.amakuru.info_("Urubuga " + self.izina + " uratangira")
        httpserver.gukora_server(port, self._handle_request)
    iherezo

    umurimo gukora_threaded(self, port)
        andika("Ruri gufatira kuri port " + shobora_umuntu(port) + " (urwego rufite ibintu)...")
        self.amakuru.info_("Urubuga " + self.izina + " uratangira (urwego rufite ibintu)")
        httpserver.gukora_threaded_server(port, self._handle_request)
    iherezo
iherezo

umurimo gukora_urubuga(izina, ubuvandimwe, debug)
    subira UrubugaApplication.nshya(izina, ubuvandimwe)
iherezo
