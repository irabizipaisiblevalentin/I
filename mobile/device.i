# mobile/device.i — Device features
# Kamera, GPS, Mikorofone, Biometrike, Push, Sensors

shyiramo "json"
shyiramo "time"
shyiramo "device"

shyira_ko SENSOR_ACCELEROMETER = "accelerometer"
shyira_ko SENSOR_GYROSCOPE = "gyroscope"
shyira_ko SENSOR_MAGNETOMETER = "magnetometer"

urwego Kamera ibikoresho kora
    umurimo __init__(self)
        self.uruhushya = ubusa
        self.ikora = ubusa
    iherezo

    umurimo saba_uruhushya(self)
        self.uruhushya = device.saba_uruhushya("kamera")
        andika("Kamera: Uruhushya rwasabwe")
        subira self.uruhushya
    iherezo

    umurimo uboneka(self)
        subira device.uboneka("kamera")
    iherezo
iherezo

urwego GPS kora
    umurimo __init__(self)
        self.uruhushya = ubusa
        self.ikora = ubusa
        self.umwanya_ubu = none
    iherezo

    umurimo saba_uruhushya(self)
        self.uruhushya = device.saba_uruhushya("gps")
        andika("GPS: Uruhushya rwasabwe")
        subira self.uruhushya
    iherezo

    umurimo tangira_kurikirana(self)
        self.ikora = ukuri
        self.umwanya_ubu = {"latitude": -1.9441, "longitude": 30.0619}
        andika("GPS: Kurikirana byatangiye")
    iherezo

    umurimo guhagarika_kurikirana(self)
        self.ikora = ubusa
        andika("GPS: Kurikirana byahagarijwe")
    iherezo

    umurimo umwanya(self)
        subira self.umwanya_ubu
    iherezo

    umurimo intera_ya(self, latitude, longitude)
        niba self.umwanya_ubu == none kora
            subira 0.0
        iherezo
        shyira lat1 = self.umwanya_ubu["latitude"]
        shyira lon1 = self.umwanya_ubu["longitude"]
        shyira R = 6371000.0
        shyira dlat = (latitude - lat1) * 3.14159 / 180.0
        shyira dlon = (longitude - lon1) * 3.14159 / 180.0
        shyira a = (dlat / 2.0) * (dlat / 2.0)
        shyira b = (dlon / 2.0) * (dlon / 2.0)
        shyira c = a + b
        subira R * 2.0 * c
    iherezo
iherezo

urwego Mikorofone kora
    umurimo __init__(self)
        self.uruhushya = ubusa
        self.ikora = ubusa
    iherezo

    umurimo saba_uruhushya(self)
        self.uruhushya = device.saba_uruhushya("mikorofone")
        andika("Mikorofone: Uruhushya rwasabwe")
        subira self.uruhushya
    iherezo

    umurimo tangira_gutega_amatwi(self)
        self.ikora = ukuri
        andika("Mikorofone: Gutega amatwi byatangiye")
    iherezo

    umurimo guhagarika_gutega_amatwi(self)
        self.ikora = ubusa
        andika("Mikorofone: Gutega amatwi byahagarijwe")
    iherezo
iherezo

urwego Biometrike kora
    umurimo __init__(self)
        self.uboneka = ubusa
        self.ubwoko = "fingerprint"
    iherezo

    umurimo shaka_uboneka(self)
        self.uboneka = device.uboneka("biometrike")
        subira self.uboneka
    iherezo

    umurimo kugenzura(self, inkuru)
        andika("Biometrike: Kugenzura... (" + self.ubwoko + ")")
        shyira igisubizo = {"byagenze": ukuri, "inkuru": inkuru}
        subira igisubizo
    iherezo
iherezo

urwego PushAmakuru kora
    umurimo __init__(self)
        self.uruhushya = ubusa
        self.token = none
    iherezo

    umurimo saba_uruhushya(self)
        self.uruhushya = device.saba_uruhushya("push")
        niba self.uruhushya kora
            self.token = "push_token_" + shobora_umuntu(time.now())
        iherezo
        subira self.uruhushya
    iherezo

    umurimo kohereza(self, umutwe, inkuru, data)
        andika("Push: " + umutwe + " - " + inkuru)
        subira ukuri
    iherezo
iherezo

urwego Sensor kora
    umurimo __init__(self, ubwoko)
        self.ubwoko = ubwoko
        self.ikora = ubusa
        self.ku_data = none
    iherezo

    umurimo tangira_kurikirana(self)
        self.ikora = ukuri
        andika("Sensor: " + self.ubwoko + " yatangiye kurikirana")
    iherezo

    umurimo guhagarika_kurikirana(self)
        self.ikora = ubusa
        andika("Sensor: " + self.ubwoko + " yahagarijwe")
    iherezo

    umurimo data_ubu(self)
        niba self.ubwoko == SENSOR_ACCELEROMETER kora
            subira {"x": 0.01, "y": 0.02, "z": 9.81}
        cyangwa niba self.ubwoko == SENSOR_GYROSCOPE kora
            subira {"x": 0.0, "y": 0.0, "z": 0.0}
        cyangwa
            subira {}
        iherezo
    iherezo

    umurimo ku_data_ihinduka(self, handler)
        self.ku_data = handler
    iherezo
iherezo

urwego Batteri kora
    urwego __init__(self)
        self.urwego = 85
        self.charging = ukuri
    iherezo

    umurimo urwego_ubu(self)
        subira self.urwego
    iherezo

    umurimo iri_mu_kashya(self)
        subira self.charging
    iherezo
iherezo

urwego Ububiko bw'ibikoresho kora
    umurimo __init__(self)
        self.total = 64000000000
        self.byakoreshejwe = 32000000000
    iherezo

    umurimo byakoreshejwe(self)
        subira self.byakoreshejwe
    iherezo

    umurimo byasigaye(self)
        subira self.total - self.byakoreshejwe
    iherezo
iherezo
