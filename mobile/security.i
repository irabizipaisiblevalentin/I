# mobile/security.i — Security
# Biometric authentication, secure storage, app integrity, permissions

shyiramo "json"
shyiramo "time"
shyiramo "device"
shyiramo "security"

shyira_ko PERMISSION_CAMERA = "kamera"
shyira_ko PERMISSION_GPS = "gps"
shyira_ko PERMISSION_MICROPHONE = "mikorofone"
shyira_ko PERMISSION_STORAGE = "ububiko"
shyira_ko PERMISSION_PUSH = "push"

shyira_ko AUTH_BIOMETRIC = "biometrike"
shyira_ko AUTH_PIN = "pin"
shyira_ko AUTH_PASSWORD = "ijambo_ibanga"
shyira_ko AUTH_PATTERN = "ikimenyetso"

urwego Kugenzura biometrike kora
    umurimo __init__(self)
        self.uboneka = ubusa
        self.ubwoko = AUTH_BIOMETRIC
    iherezo

    umurimo shaka_uboneka(self)
        self.uboneka = device.uboneka("biometrike")
        niba self.uboneka kora
            shyira sensors = device.sensors_biometrike()
            niba uburengero(sensors) > 0 kora
                self.ubwoko = sensors[0]
            iherezo
        iherezo
        subira self.uboneka
    iherezo

    umurimo kugenzura(self, inkuru)
        andika("Kugenzura biometrike: " + inkuru + " (" + self.ubwoko + ")")
        shyira result = device.kugenzura_biometrike(inkuru)
        niba result["byagenze"] kora
            andika("Kugenzura biometrike: Byagenze neza")
        cyangwa
            andika("Kugenzura biometrike: Ntibyagenze")
        iherezo
        subira result
    iherezo
iherezo

urwego Kubika mu mutekano kora
    umurimo __init__(self)
        self.data = {}
        self.ubutabire = ukuri
    iherezo

    umurimo kubika(self, izina, igiciro)
        niba self.ubutabire kora
            shyira igiciro_kibishwe = security.butabire(shobora_umuntu(igiciro))
            self.data[izina] = igiciro_kibishwe
        cyangwa
            self.data[izina] = igiciro
        iherezo
        andika("Kubika mu mutekano: " + izina + " byabitswe")
    iherezo

    umurimo kura(self, izina)
        niba izina in self.data kora
            niba self.ubutabire kora
                shyira igiciro_kibishwe = self.data[izina]
                subira security.bohora(igiciro_kibishwe)
            cyangwa
                subira self.data[izina]
            iherezo
        iherezo
        subira none
    iherezo

    umurimo siba(self, izina)
        niba izina in self.data kora
            shyira _ = self.data.pop(izina)
            andika("Kubika mu mutekano: " + izina + " byakuwemo")
        iherezo
    iherezo

    umurimo isukuye(self)
        self.data = {}
        andika("Kubika mu mutekano: Byose byakuweho")
    iherezo
iherezo

urwego Kugenzura porogaramu kora
    umurimo __init__(self)
        self.amacode = {}
    iherezo

    umurimo kugenzura_intego(self)
        shyira result = device.kugenzura_root()
        niba result kora
            andika("Kugenzura porogaramu: Root/detected!")
        cyangwa
            andika("Kugenzura porogaramu: Nta root")
        iherezo
        subira result
    iherezo

    umurimo kugenzura_uwanyere(self)
        shyira result = device.kugenzura_uwanyere()
        niba result kora
            andika("Kugenzura porogaramu: Uwanyere yahindutse!")
        iherezo
        subira result
    iherezo

    umurimo kugenzura_signature(self)
        shyira expected = "signature_123"
        shyira actual = device.signature_ porogaramu()
        niba expected == actual kora
            subira ukuri
        iherezo
        andika("Kugenzura porogaramu: Signature nti ihuye!")
        subira ubusa
    iherezo
iherezo

urwego Igenzura ry'uruhushya kora
    umurimo __init__(self)
        self.uruhushya_rwatanzwe = {}
    iherezo

    umurimo saba(self, izina, impamvu)
        niba izina in self.uruhushya_rwatanzwe kora
            shyira igisubizo = self.uruhushya_rwatanzwe[izina]
            andika("Igenzura ry'uruhushya: " + izina + " = " + shobora_umuntu(igisubizo) + " (byakozwe mbere)")
            subira igisubizo
        iherezo
        shyira result = device.saba_uruhushya(izina)
        self.uruhushya_rwatanzwe[izina] = result
        andika("Igenzura ry'uruhushya: " + izina + " = " + shobora_umuntu(result))
        subira result
    iherezo

    umurimo saba_nyinshi(self, uruhushya_list, impamvu)
        shyira results = {}
        buri izina muri uruhushya_list kora
            results[izina] = self.saba(izina, impamvu)
        iherezo
        subira results
    iherezo

    umurimo rahushya_rwatanzwe(self, izina)
        subira self.uruhushya_rwatanzwe.get(izina, ubusa)
    iherezo

    umurimo kura_uruhushya(self, izina)
        niba izina in self.uruhushya_rwatanzwe kora
            shyira _ = self.uruhushya_rwatanzwe.pop(izina)
        iherezo
    iherezo
iherezo

umurimo umutekano_nshya()
    shyira biometrike = Kugenzura biometrike.nshya()
    shyira kubika = Kubika mu mutekano.nshya()
    shyira kugenzura = Kugenzura porogaramu.nshya()
    shyira uruhushya = Igenzura ry'uruhushya.nshya()
    subira {
        "biometrike": biometrike,
        "kubika": kubika,
        "kugenzura": kugenzura,
        "uruhushya": uruhushya,
    }
iherezo
