# urubuga/api.i — REST API Platform
# Uburyo bwo Gukora REST API

shyiramo "json"

# ── UrubugaAPI — REST API Helpers ─────────────────────────────────

urwego UrubugaAPI
    app: ubusa

    umurimo __init__(self, app: ubusa)
        self.app = app
    iherezo

    umurimo CRUD(self, inzira: umuntu, icyumba: umuntu) -> ubusa
        # GET / — List all
        self.app.GET(inzira, lambda req: self._list(req, icyumba))
        
        # GET /{id} — Get one
        self.app.GET(inzira + "/{id}", lambda req: self._get(req, icyumba))
        
        # POST / — Create
        self.app.POST(inzira, lambda req: self._create(req, icyumba))
        
        # PUT /{id} — Update
        self.app.PUT(inzira + "/{id}", lambda req: self._update(req, icyumba))
        
        # DELETE /{id} — Delete
        self.app.DELETE(inzira + "/{id}", lambda req: self._delete(req, icyumba))
        
        subira self
    iherezo

    umurimo _list(self, request: ubusa, icyumba: umuntu) -> {}
        niba self.app.ububiko == ubusa
            subira {"items": [], "total": 0}
        iherezo
        
        shyira items = self.app.ububiko.shakisha(icyumba, {})
        subira {"items": items, "total": len(items)}
    iherezo

    umurimo _get(self, request: ubusa, icyumba: umuntu) -> {}
        shyira id = int(request.path_params.get("id", 0))
        niba self.app.ububiko == ubusa
            subira {"error": "Database not configured"}
        iherezo
        
        shyira item = self.app.ububiko.shakisha_id(icyumba, id)
        niba item == ubusa
            subira {"error": "Not found"}
        iherezo
        subira item
    iherezo

    umurimo _create(self, request: ubusa, icyumba: umuntu) -> {}
        niba self.app.ububiko == ubusa
            subira {"error": "Database not configured"}
        iherezo
        
        shyira data = request.json_data
        niba data == ubusa
            data = {}
        iherezo
        
        shyira id = self.app.ububiko.injiza(icyumba, data)
        subira {"id": id, "message": "Yakorewe neza"}
    iherezo

    umurimo _update(self, request: ubusa, icyumba: umuntu) -> {}
        niba self.app.ububiko == ubusa
            subira {"error": "Database not configured"}
        iherezo
        
        shyira id = int(request.path_params.get("id", 0))
        shyira data = request.json_data
        niba data == ubusa
            data = {}
        iherezo
        
        self.app.ububiko.hindura(icyumba, data, "id = ?", [id])
        subira {"id": id, "message": "Yahinduwe neza"}
    iherezo

    umurimo _delete(self, request: ubusa, icyumba: umuntu) -> {}
        niba self.app.ububiko == ubusa
            subira {"error": "Database not configured"}
        iherezo
        
        shyira id = int(request.path_params.get("id", 0))
        self.app.ububiko.siba(icyumba, "id = ?", [id])
        subira {"id": id, "message": "Yaburwe neza"}
    iherezo
iherezo


# ── UrubugaPagination — API Pagination ───────────────────────────
urwego UrubugaPagination
    umurimo paginate(self, items: [], page: int, per_page: int) -> {}
        shyira total = len(items)
        shyira start = (page - 1) * per_page
        shyira end = start + per_page
        shyira items_y' = items[start:end]
        shyira total_pages = math.ceil(total / per_page)
        
        subira {
            "items": items_y',
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    iherezo
iherezo


# ── UrubugaValidation — Request Validation ───────────────────────
urwego UrubugaValidation
    ibiciro: {}

    umurimo __init__(self)
        self.ibiciro = {}
    iherezo

    umurimo shakisha(self, izina: umuntu, imiterere: {}) -> ubusa
        self.ibiciro[izina] = imiterere
    iherezo

    umurimo kugenzura(self, izina: umuntu, ibiciro: {}) -> {}
        imiterere = self.ibiciro.get(izina, {})
        amakosa = []
        
        buri izina in imiterere.keys()
            ibintu = imiterere[izina]
            niba ibintu.get("birakenewe", ubusa) == ukuri
                niba izina not in ibiciro
                    amakosa.append(izina + " birakenewe")
                iherezo
            iherezo
            
            niba ibiciro.get(izina, ubusa) != ubusa
                agaciro = ibiciro[izina]
                ubwoko = ibintu.get("ubwoko", "umuntu")
                
                niba ubwoko == "int" kandi type(agaciro) != type(1)
                    amakosa.append(izina + " igomba kuba int")
                iherezo
                
                niba ubwoko == "umuntu" kandi type(agaciro) != type("")
                    amakosa.append(izina + " igomba kuba umubare")
                iherezo
                
                niba ibintu.get("min", ubusa) != ubusa
                    niba len(str(agaciro)) < ibintu["min"]
                        amakosa.append(izina + " igomba kuba runini cyane")
                    iherezo
                iherezo
                
                niba ibintu.get("max", ubusa) != ubusa
                    niba len(str(agaciro)) > ibintu["max"]
                        amakosa.append(izina + " igomba kuba gito")
                    iherezo
                iherezo
            iherezo
        iherezo
        
        niba len(amakosa) > 0
            subira {"valid": ubusa, "errors": amakosa}
        iherezo
        
        subira {"valid": ukuri, "data": ibiciro}
    iherezo
iherezo


# ── UrubugaRateLimit — Rate Limiting ──────────────────────────────
urwego UrubugaRateLimit
    ubushobozi: int
    isaha: int
    abantu: {}

    umurimo __init__(self, ubushobozi: int, isaha: int)
        self.ubushobozi = ubushobozi
        self.isaha = isaha
        self.abantu = {}
    iherezo

    umurimo kugenzura(self, request: ubusa) -> ubusa
        shyira key = request.client_ip
        shyira now = time.time()
        
        niba key not in self.abantu
            self.abantu[key] = []
        iherezo
        
        # Remove old timestamps
        self.abantu[key] = [t for t in self.abantu[key] if t > now - self.isaha]
        
        niba len(self.abantu[key]) >= self.ubushobozi
            subira {"_type": "json", "data": {"error": {"status": 429, "message": "Rate limit exceeded"}}, "status": 429}
        iherezo
        
        self.abantu[key].append(now)
        subira ubusa
    iherezo
iherezo


# ── UrubugaCORS — CORS Support ───────────────────────────────────
urwego UrubugaCORS
    allow_origins: []
    allow_methods: []
    allow_headers: []

    umurimo __init__(self)
        self.allow_origins = ["*"]
        self.allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        self.allow_headers = ["content-type", "authorization", "x-requested-with"]
    iherezo

    umurimo kugenzura(self, request: ubusa) -> ubusa
        niba request.method == "OPTIONS"
            subira {
                "_type": "empty",
                "status": 204,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                    "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
                    "Access-Control-Max-Age": "86400",
                }
            }
        iherezo
        subira ubusa
    iherezo
iherezo
