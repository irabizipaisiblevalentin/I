"""ubatse — UAM core framework for cross-platform applications."""

shyiramo "json"
shyiramo "time"

shyira_ko UAM_VERSION = "1.0.0"
shyira_ko UAM_BUILD = 1

shyira_ko URUBUGA = "urubuga"
shyira_ko IBIRO = "ibiro"
shyira_ko MOBILE = "mobile"
shyira_ko DESKTOP = "desktop"
shyira_ko TV = "tv"
shyira_ko WEARABLE = "wearable"

shyira_ko PLATFORM_ALL = [URUBUGA, IBIRO, MOBILE, DESKTOP, TV, WEARABLE]

shyira_ko IBIRO_VERSION = "0.1.0"
shyira_ko URUBUGA_VERSION = "0.1.0"
shyira_ko MOBILE_VERSION = "0.1.0"

ikoranabugari = URUBUGA

urwego PlatformTarget kora
    umurimo __init__(self, izina)
        self.izina = izina
        self.ibarurishya = 0
    iherezo

    umurimo ni_urubuga(self)
        subira self.izina == URUBUGA
    iherezo

    umurimo ni_ibiro(self)
        subira self.izina == IBIRO
    iherezo

    umurimo ni_mobile(self)
        subira self.izina == MOBILE
    iherezo

    umurimo ni_desktop(self)
        subira self.izina == DESKTOP
    iherezo

    umurimo ni_tv(self)
        subira self.izina == TV
    iherezo

    umurimo ni_wearable(self)
        subira self.izina == WEARABLE
    iherezo

    umurimo __str__(self)
        subira "PlatformTarget(" + self.izina + ")"
    iherezo
iherezo

shyira_ko URUBUGA_TARGET = PlatformTarget.nshya(URUBUGA)
shyira_ko IBIRO_TARGET = PlatformTarget.nshya(IBIRO)
shyira_ko MOBILE_TARGET = PlatformTarget.nshya(MOBILE)
shyira_ko DESKTOP_TARGET = PlatformTarget.nshya(DESKTOP)
shyira_ko TV_TARGET = PlatformTarget.nshya(TV)
shyira_ko WEARABLE_TARGET = PlatformTarget.nshya(WEARABLE)

urwego UAMApplication kora
    umurimo __init__(self, izina, target)
        self.izina = izina
        self.target = target
        self.ikiganiro_ikirangwa = none
        self.komponenti = {}
        self.ububiko = {}
        self.serivisi = {}
        self.inzira = []
        self.navigator = none
        self.theme = none
        self.ubuzima = "ntangiriwe"
        self.ibikorwa = []
        self.amasoko = {}
        self.config = {}
    iherezo

    umurimo shyira_ikiganiro(self, izina, ikiganiro)
        self.ibikorwa.append({"izina": izina, "ikiganiro": ikiganiro})
        niba self.ikiganiro_ikirangwa == none
            self.ikiganiro_ikirangwa = izina
        iherezo
        subira self
    iherezo

    umurimo shyira_komponenti(self, izina, komponenti)
        self.komponenti[izina] = komponenti
        subira self
    iherezo

    umurimo shyira_serivisi(self, izina, serivisi)
        self.serivisi[izina] = serivisi
        subira self
    iherezo

    umurimo shaka_komponenti(self, izina)
        subira self.komponenti.get(izina, none)
    iherezo

    umurimo shaka_serivisi(self, izina)
        subira self.serivisi.get(izina, none)
    iherezo

    umurimo shyira_config(self, izina, igiciro)
        self.config[izina] = igiciro
        subira self
    iherezo

    umurimo igiciro(self, izina)
        subira self.config.get(izina, none)
    iherezo

    umurimo shyira_amasoko(self, izina, soko)
        self.amasoko[izina] = soko
        subira self
    iherezo

    umurimo shaka_amasoko(self, izina)
        subira self.amasoko.get(izina, none)
    iherezo

    umurimo genda(self)
        self.ubuzima = "gutangira"
        andika("=== " + self.izina + " v" + UAM_VERSION + " ===")
        andika("Urwego: " + self.target.izina)
        buri serivisi_izina muri self.serivisi
            shyira serivisi = self.serivisi[serivisi_izina]
            niba serivisi has_member "tangira"
                serivisi.tangira()
            iherezo
        iherezo
        self.ubuzima = "gutunganye"
        andika(self.izina + " yatangiye neza")
        subira self
    iherezo

    umurimo gufungura(self)
        self.ubuzima = "gufunga"
        buri serivisi_izina muri self.serivisi
            shyira serivisi = self.serivisi[serivisi_izina]
            niba serivisi has_member "gufungura"
                serivisi.gufungura()
            iherezo
        iherezo
        self.ubuzima = "gufunze"
        andika(self.izina + " yafunze")
    iherezo

    umurimo __str__(self)
        subira "UAMApplication(" + self.izina + ", " + self.target.izina + ")"
    iherezo
iherezo

umurimo tangiza_uam(izina, target_izina)
    shyira target = PlatformTarget.nshya(target_izina)
    shyira app = UAMApplication.nshya(izina, target)
    ikoranabugari = target_izina
    subira app
iherezo

umurimo shyira_platform_target(target_izina)
    ikoranabugari = target_izina
    subira PlatformTarget.nshya(target_izina)
iherezo

umurimo ni_urubuga()
    subira ikoranabugari == URUBUGA
iherezo

umurimo ni_ibiro()
    subira ikoranabugari == IBIRO
iherezo

umurimo ni_mobile()
    subira ikoranabugari == MOBILE
iherezo

umurimo ni_desktop()
    subira ikoranabugari == DESKTOP
iherezo
