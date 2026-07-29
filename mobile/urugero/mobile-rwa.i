# mobile/urugero/mobile-rwa.i — Urugero: Porogaramu ya MOBILE
# Ikiganiro nyinshi, ubugenzuzi, GPS, kamera, network

shyiramo "mobile.ubatse"
shyiramo "mobile.navigation"
shyiramo "mobile.ui"
shyiramo "mobile.layout"
shyiramo "mobile.media"
shyiramo "mobile.network"
shyiramo "mobile.device"
shyiramo "mobile.ai"
shyiramo "mobile.security"

urwego IkiganiroNyumbani kora
    umurimo __init__(self)
        self.indangamuntu = "ikiganiro_nyumbani"
        self.ibara_ikinyabiziga = ibara_rgb(52, 152, 219)
    iherezo

    umurimo gukora(self, ibiciro)
        shyira umutwe = Umutwe.nshya("Muraho neza!", 1, "umutwe_nyumbani", none)
        shyira ikimenyetso = Ikimenyetso.nshya("Iki ni urugero rwa MOBILE", "ikimenyetso_nyumbani", none)
        shyira buto = Buto.nshya("Reba GPS", "buto_gps", none, lambda: self.gps_kanda())
        shyira buto_kamera = Buto.nshya("Fata ishusho", "buto_kamera", none, lambda: self.kamera_kanda())

        shyira inkingi = Inkingi.nshya([umutwe, ikimenyetso, buto, buto_kamera], "inkingi_nyumbani", 16, ukuri)
        inkingi.ibara_ikinyabiziga()

        andika("IkiganiroNyumbani: Gukora")
    iherezo

    umurimo gps_kanda(self)
        shyira gps = GPS.nshya()
        gps.saba_uruhushya()
        gps.tangira_kurikirana()
        shyira place = gps.umwanya()
        andika("GPS: Latitude=" + shobora_umuntu(place["latitude"]) + ", Longitude=" + shobora_umuntu(place["longitude"]))
        gps.guhagarika_kurikirana()
    iherezo

    umurimo kamera_kanda(self)
        shyira kamera = Kamera.nshya()
        kamera.fungura()
        shyira ishusho = kamera.fata_ishusho()
        niba ishusho != none kora
            andika("Kamera: Ishusho yafashwe (" + ishusho["ubwoko"] + ")")
        iherezo
        kamera.gufunga()
    iherezo
iherezo

urwego IkiganiroAmakuru kora
    umurimo __init__(self)
        self.indangamuntu = "ikiganiro_amakuru"
    iherezo

    umurimo gukora(self, ibiciro)
        shyira umutwe = Umutwe.nshya("Amakuru", 2, "umutwe_amakuru", none)
        shyira client = HTTPClient.nshya("https://api.example.com")
        shyira response = client.GET("/amakuru")
        niba response["status"] == 200 kora
            shyira urutonde = Urutonde.nshya([], "urutonde_amakuru")
            shyira i = 0
            wihuse i < 5 kora
                urutonde.ongeza("Amakuru " + shobora_umuntu(i))
                i = i + 1
            iherezo
            andika("Amakuru: Yapakiwe neza")
        cyangwa
            andika("Amakuru: Ikosa ryapakiwe")
        iherezo
    iherezo
iherezo

urwego IkiganiroIbijijwe kora
    umurimo __init__(self)
        self.indangamuntu = "ikiganiro_ibijijwe"
    iherezo

    umurimo gukora(self, ibiciro)
        shyira umutwe = Umutwe.nshya("Ibijijwe", 2, "umutwe_ibijijwe", none)
        shyira AI = Kumenya ijwi.nshya()
        AI.ku_bivuzwe(lambda text: andika("Wavuze: " + text))
        AI.tangira_gutega_amatwi()
        andika("Ibijijwe: AI iratega amatwi...")
        shyira ubundi = AI.kora_transcribe("ijwi_data")
        andika("Ibijijwe: " + ubundi)
        AI.guhagarika_gutega_amatwi()

        shyira hindura = Guhindura ururimi.nshya()
        shyira translated = hindura.hindura("Muraho", "rw", "en")
        andika("Translation: " + translated)
    iherezo
iherezo

urwego IkiganiroUmutekano kora
    umurimo __init__(self)
        self.indangamuntu = "ikiganiro_umutekano"
    iherezo

    umurimo gukora(self, ibiciro)
        shyira umutwe = Umutwe.nshya("Umutekano", 2, "umutwe_umutekano", none)
        shyira uruhushya = Igenzura ry'uruhushya.nshya()
        shyira camera_ok = uruhushya.saba(PERMISSION_CAMERA, "Gukoresha kamera")
        shyira gps_ok = uruhushya.saba(PERMISSION_GPS, "Gukoresha GPS")
        andika("Umutekano: Kamera=" + shobora_umuntu(camera_ok) + ", GPS=" + shobora_umuntu(gps_ok))

        shyira biometrike = Kugenzura biometrike.nshya()
        shyira bio_ok = biometrike.shaka_uboneka()
        niba bio_ok kora
            shyira result = biometrike.kugenzura("Kwinjira")
            andika("Biometrike: " + shobora_umuntu(result["byagenze"]))
        iherezo

        shyira kubika = Kubika mu mutekano.nshya()
        kubika.kubika("token", "token_y_ibanga_123")
        shyira token = kubika.kura("token")
        andika("Kubika mu mutekano: token=" + token)
    iherezo
iherezo

urwego IkiganiroNetwork kora
    umurimo __init__(self)
        self.indangamuntu = "ikiganiro_network"
    iherezo

    umurimo gukora(self, ibiciro)
        shyira umutwe = Umutwe.nshya("Network", 2, "umutwe_network", none)
        shyira ws = WebSocket.nshya("wss://example.com/chat")
        ws.ku_ibyabaye("message", lambda data: andika("WS: " + json.stringify(data)))
        ws.guhuza()
        ws.kohereza({"ubwoko": "chat", "inkuru": "Muraho!"})
        ws.kira_ibyabaye("message", {"author": "bot", "text": "Muraho neza!"})
        ws.guhuza_garuka()

        shyira offline = Guhuza hanze.nshya()
        buri i muri 0 kugeza 3 kora
            offline.ongeza_igikorwa("sync", {"id": i, "data": "data_" + shobora_umuntu(i)})
        iherezo
        offline.guhuza()
        andika("Network: Queue uburengero=" + shobora_umuntu(offline.queue_uburengero()))
    iherezo
iherezo

umurimo nyamukuru()
    shyira app = tangiza_porogaramu("UrugeroMobile", "0.1.0", ukuri)
    shyira navigator = TangizaNavigator()

    shyira nyumbani = IkiganiroNyumbani.nshya()
    shyira amakuru = IkiganiroAmakuru.nshya()
    shyira ibijijwe = IkiganiroIbijijwe.nshya()
    shyira umutekano = IkiganiroUmutekano.nshya()
    shyira network = IkiganiroNetwork.nshya()

    navigator.shakisha_inzira("/", Inzira.nshya("Nyumbani", nyumbani, {}))
    navigator.shakisha_inzira("/amakuru", Inzira.nshya("Amakuru", amakuru, {}))
    navigator.shakisha_inzira("/ibijijwe", Inzira.nshya("Ibijijwe", ibijijwe, {}))
    navigator.shakisha_inzira("/umutekano", Inzira.nshya("Umutekano", umutekano, {}))
    navigator.shakisha_inzira("/network", Inzira.nshya("Network", network, {}))

    app.navigator = navigator
    app.shyira_ikiganiro("nyumbani", nyumbani)
    app.shyira_ikiganiro("amakuru", amakuru)
    app.shyira_ikiganiro("ibijijwe", ibijijwe)
    app.shyira_ikiganiro("umutekano", umutekano)
    app.shyira_ikiganiro("network", network)

    navigator.sunika("/", {})
    navigator.sunika("/amakuru", {})

    shyira tabs = UbugenzuziTab.nshya()
    tabs.ongeza_icumbi("Nyumbani", nyumbani, "🏠")
    tabs.ongeza_icumbi("Amakuru", amakuru, "📰")
    tabs.ongeza_icumbi("Ibijijwe", ibijijwe, "🤖")
    tabs.ongeza_icumbi("Umutekano", umutekano, "🔒")
    tabs.hindura_icumbi("Nyumbani")

    shyira drawer = UbugenzuziDrawer.nshya()
    drawer.ongeza_icumbi("Nyumbani", nyumbani, "🏠")
    drawer.ongeza_icumbi("Network", network, "🌐")
    drawer.fungura()
    drawer.gukora_amaboko("Network")
    drawer.gufunga()

    shyira config = app.config
    config.andika_amakuru("info", "Porogaramu yateguye neza")

    genda(app)
iherezo

nyamukuru()
