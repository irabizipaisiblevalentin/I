# mobile/ubatse.i — MOBILE core framework
# UBATSE (U-BA-TSE: "it is built") ni urwego nyamukuru rwa MOBILE
# Rikubiyemo ibintu byose by'ibanze byo kubaka porogaramu za mobile

shyiramo "json"
shyiramo "time"
shyiramo "device"

shyira_ko MOBILE_VERSION = "0.1.0"
shyira_ko NI_ANDROID = device.ubwoko() == "android"
shyira_ko NI_IOS = device.ubwoko() == "ios"
shyira_ko NI_TABLET = device.ubwoko() == "tablet"
shyira_ko NI_FOLDABLE = device.ubwoko() == "foldable"
shyira_ko NI_TV = device.ubwoko() == "tv"
shyira_ko NI_WEARABLE = device.ubwoko() == "wearable"

urwego PorogaramuConfig kora
    umurimo __init__(self, izina, ubuvandimwe, debug)
        self.izina = izina
        self.ubuvandimwe = ubuvandimwe
        self.debug = debug
        self.ibiro_kubika = {}
        self.amakuru = []
    iherezo

    umurimo shakisha_config(self, izina, igiciro)
        self.ibiro_kubika[izina] = igiciro
    iherezo

    umurimo igiciro(self, izina)
        subira self.ibiro_kubika.get(izina, none)
    iherezo

    umurimo andika_amakuru(self, ubwoko, inkuru)
        shyira entry = {"ubwoko": ubwoko, "inkuru": inkuru, "igihe": time.now()}
        self.amakuru.append(entry)
        andika("[" + ubwoko + "] " + inkuru)
    iherezo
iherezo

urwego UrwegoMobileApplication kora
    umurimo __init__(self, config)
        self.config = config
        self.amakuru = config.amakuru
        self.ibikorwa = []
        self.ikiganiro_ikirangwa = none
        self.navigator = none
        self.ubuzima = "ntangiriwe"
    iherezo

    umurimo shyira_ikiganiro(self, izina, ikiganiro)
        self.ibikorwa.append({"izina": izina, "ikiganiro": ikiganiro})
    iherezo

    umurimo shakisha_ikiganiro(self, izina_kiganiro)
        buri ikiganiro muri self.ibikorwa kora
            niba ikiganiro["izina"] == izina_kiganiro kora
                subira ikiganiro["ikiganiro"]
            iherezo
        iherezo
        subira none
    iherezo

    umurimo tangira(self)
        self.ubuzima = "gutangira"
        self.amakuru.andika_amakuru("info", "Porogaramu " + self.config.izina + " itangira")
        andika("=== " + self.config.izina + " v" + MOBILE_VERSION + " ===")
        andika("Ikoresha urubuga: " + self.config.ubuvandimwe)
        andika("Platform: " + device.ubwoko())
    iherezo

    umurimo gukora(self)
        self.tangira()
        niba self.navigator != none kora
            self.navigator.genda()
        cyangwa
            andika("Ikosa: Nta navigator yashizwe")
        iherezo
    iherezo

    umurimo gufungura(self)
        self.ubuzima = "gufunga"
        self.amakuru.andika_amakuru("info", "Porogaramu irafunga")
    iherezo
iherezo

umurimo tangiza_porogaramu(izina, ubuvandimwe, debug)
    shyira config = PorogaramuConfig.nshya(izina, ubuvandimwe, debug)
    shyira app = UrwegoMobileApplication.nshya(config)
    subira app
iherezo

umurimo shyira_ikiganiro(app, izina, ikiganiro)
    app.shyira_ikiganiro(izina, ikiganiro)
iherezo

umurimo genda(app)
    app.gukora()
iherezo
