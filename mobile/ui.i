# mobile/ui.i — UI Components
# Ibikoresho byose bya UI: Buto, Ikimenyetso, Umutwe, Ishusho, ...

shyiramo "json"
shyiramo "text"

urwego Buto kora
    umurimo __init__(self, umwandiko, indangamuntu, ibara, rikora)
        self.umwandiko = umwandiko
        self.indangamuntu = indangamuntu
        self.ibara = ibara
        self.rikora = rikora
        self.ikoranabuhanga = ubusa
    iherezo

    umurimo kanda(self)
        niba self.rikora != none kora
            self.rikora()
        iherezo
    iherezo
iherezo

urwego Ikimenyetso kora
    umurimo __init__(self, umwandiko, indangamuntu, ibara)
        self.umwandiko = umwandiko
        self.indangamuntu = indangamuntu
        self.ibara = ibara
    iherezo

    umurimo hindura_umwandiko(self, umwandiko_mushya)
        self.umwandiko = umwandiko_mushya
    iherezo
iherezo

urwego Umutwe kora
    umurimo __init__(self, umwandiko, urwego, indangamuntu, ibara)
        self.umwandiko = umwandiko
        self.urwego = urwego
        self.indangamuntu = indangamuntu
        self.ibara = ibara
    iherezo
iherezo

urwego Ibara kora
    umurimo __init__(self, igiciro, indangamuntu)
        self.igiciro = igiciro
        self.indangamuntu = indangamuntu
    iherezo

    umurimo cyijimye(self)
        subira "#" + self.igiciro
    iherezo
iherezo

urwego Ishusho kora
    umurimo __init__(self, inzira, uburebure, ubugari, indangamuntu)
        self.inzira = inzira
        self.uburebure = uburebure
        self.ubugari = ubugari
        self.indangamuntu = indangamuntu
        self.ikozwe = ubusa
    iherezo

    umurimo gupakira(self)
        self.ikozwe = ukuri
    iherezo
iherezo

urwego Urutonde kora
    umurimo __init__(self, ibintu, indangamuntu)
        self.ibintu = ibintu
        self.indangamuntu = indangamuntu
        self.umwijekuru = none
    iherezo

    umurimo ongeza(self, ikintu)
        self.ibintu.append(ikintu)
    iherezo

    umurimo kura_ku(self, index)
        niba index < uburengero(self.ibintu) kora
            self.ibintu.pop(index)
        iherezo
    iherezo
iherezo

urwego Ikarita kora
    umurimo __init__(self, umutwe, ibice, indangamuntu)
        self.umutwe = umutwe
        self.ibice = ibice
        self.indangamuntu = indangamuntu
        self.igicucu = ukuri
    iherezo

    umurimo kongera_ikintu(self, ikintu)
        self.ibice.append(ikintu)
    iherezo
iherezo

urwego Ifishi kora
    umurimo __init__(self, indangamuntu)
        self.indangamuntu = indangamuntu
        self.amashami = {}
        self.kubereka = none
    iherezo

    umurimo ongeza_ishami(self, izina, ubwoko, ikimenyetso)
        self.amashami[izina] = {
            "ubwoko": ubwoko,
            "ikimenyetso": ikimenyetso,
            "igiciro": "",
        }
    iherezo

    umurimo igiciro_ishami(self, izina)
        subira self.amashami.get(izina, {}).get("igiciro", "")
    iherezo

    umurimo shakisha_igiciro(self, izina, igiciro)
        niba izina in self.amashami kora
            self.amashami[izina]["igiciro"] = igiciro
        iherezo
    iherezo

    umurimo kohereza(self)
        niba self.kubereka != none kora
            self.kubereka(self.amashami)
        iherezo
    iherezo
iherezo

urwego Ikadiri kora
    umurimo __init__(self, umutwe, ibice, indangamuntu)
        self.umutwe = umutwe
        self.ibice = ibice
        self.indangamuntu = indangamuntu
        self.onekana = ubusa
    iherezo

    umurimo kwerekana(self)
        self.onekana = ukuri
    iherezo

    umurimo guhisha(self)
        self.onekana = ubusa
    iherezo
iherezo

urwego Ikubaza kora
    umurimo __init__(self, icumbi, amacumbi, indangamuntu)
        self.icumbi = icumbi
        self.amacumbi = amacumbi
        self.indangamuntu = indangamuntu
    iherezo

    umurimo hindura_icumbi(self, izina)
        self.icumbi = izina
    iherezo
iherezo

urwego Umubare kora
    umurimo __init__(self, igiciro, ubwoko, indangamuntu)
        self.igiciro = igiciro
        self.ubwoko = ubwoko
        self.indangamuntu = indangamuntu
    iherezo

    umurimo hindura_igiciro(self, igiciro_gishya)
        self.igiciro = igiciro_gishya
    iherezo
iherezo

umurimo ubaka_buto(umwandiko, rikora, ibara)
    subira Buto.nshya(umwandiko, "buto_" + text.lower(umwandiko), ibara, rikora)
iherezo

umurimo ubaka_umutwe(umwandiko, urwego)
    subira Umutwe.nshya(umwandiko, urwego, "umutwe_" + text.lower(umwandiko), none)
iherezo

umurimo ubaka_ikarita(umutwe, ibice)
    subira Ikarita.nshya(umutwe, ibice, "ikarita_" + text.lower(umutwe))
iherezo
