"""API service — HTTP client abstraction shared across all platforms."""

igiceri API_Serivisi
    urubuga: string
    ikirangantego: string
    umutwe: urutonde
iherezo

    umurimo nshya(urubuga: string) -> API_Serivisi
        shyira iki = API_Serivisi()
        iki.urubuga = urubuga
        iki.ikirangantego = ""
        iki.umutwe = []
        subira iki
    iherezo

    umurimo shyira_ikirangantego(iki: iki, kirangantego: string) -> void
        iki.ikirangantego = kirangantego
        iki.umutwe.kubika({"izina": "Authorization", "igiciro": "Bearer " + kirangantego})
    iherezo

    umurimo gukora_inzira(iki: iki, inzira: string) -> string
        subira iki.urubuga + inzira
    iherezo

    umurimo kubona(iki: iki, inzira: string) -> umuntu
        shyira url = iki.gukora_inzira(inzira)
        andika "GET " + url
        subira {"imikorerere": 200, "amakuru": {"ibisubizo": []}}
    iherezo

    umurimo kohereza(iki: iki, inzira: string, amakuru: umuntu) -> umuntu
        shyira url = iki.gukora_inzira(inzira)
        andika "POST " + url
        subira {"imikorerere": 201, "amakuru": amakuru}
    iherezo

    umurimo shyiraho(iki: iki, inzira: string, amakuru: umuntu) -> umuntu
        shyira url = iki.gukora_inzira(inzira)
        andika "PUT " + url
        subira {"imikorerere": 200, "amakuru": amakuru}
    iherezo

    umurimo siba(iki: iki, inzira: string) -> umuntu
        shyira url = iki.gukora_inzira(inzira)
        andika "DELETE " + url
        subira {"imikorerere": 204, "amakuru": {}}
    iherezo

    umurimo gukora_ikosa(iki: iki, imikorerere: int) -> void
        igihe imikorerere >= 400
            igihe imikorerere == 401
                andika "Ikosa: nta bushobozi - Injiza ikirangantego"
            nanone igihe imikorerere == 403
                andika "Ikosa: ntibyemewe"
            nanone igihe imikorerere == 404
                andika "Ikosa: inzira ntaboneka"
            nanone igihe imikorerere >= 500
                andika "Ikosa: seriveri ikosa - " + imikorerere
            nanone
                andika "Ikosa: itazwi - " + imikorerere
            iherezo
        iherezo
    iherezo

iherezo
