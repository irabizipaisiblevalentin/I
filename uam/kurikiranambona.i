"""kurikiranambona — UAM cross-platform navigation system."""

shyiramo "json"

shyira_ko KURIKIRANAMBONA_VERSION = "1.0.0"

shyira_ko PUSH = "push"
shyira_ko POP = "pop"
shyira_ko REPLACE = "replace"
shyira_ko TAB = "tab"
shyira_ko DRAWER = "drawer"
shyira_ko MODAL = "modal"

urwego Inzira kora
    umurimo __init__(self, izina, komponenti, ibiciro)
        self.izina = izina
        self.komponenti = komponenti
        self.ibiciro = ibiciro
        self.uburinzi = none
        self.meta = {}
    iherezo

    umurimo shyira_uburinzi(self, handler)
        self.uburinzi = handler
        subira self
    iherezo

    umurimo shyira_meta(self, izina, igiciro)
        self.meta[izina] = igiciro
        subira self
    iherezo

    umurimo shaka_meta(self, izina)
        subira self.meta.get(izina, none)
    iherezo

    umurimo rahindura(self, ibiciro)
        shyira merged = {}
        buri key muri self.ibiciro
            merged[key] = self.ibiciro[key]
        iherezo
        buri key muri ibiciro
            merged[key] = ibiciro[key]
        iherezo
        subira merged
    iherezo

    umurimo reba_ubushobozi(self, context)
        niba self.uburinzi != none
            subira self.uburinzi(context)
        iherezo
        subira ukuri
    iherezo

    umurimo __str__(self)
        subira "Inzira(" + self.izina + ")"
    iherezo
iherezo

urwego InziraGroup kora
    umurimo __init__(self, izina)
        self.izina = izina
        self.inzira = {}
        self.ikirangwa = none
    iherezo

    umurimo ongeza(self, inzira)
        self.inzira[inzira.izina] = inzira
        niba self.ikirangwa == none
            self.ikirangwa = inzira.izina
        iherezo
        subira self
    iherezo

    umurimo shaka(self, izina)
        subira self.inzira.get(izina, none)
    iherezo

    umurimo siba(self, izina)
        niba izina in self.inzira
            shyiramo _ = self.inzira.pop(izina)
        iherezo
    iherezo

    umurimo list(self)
        shyira result = []
        buri izina muri self.inzira
            result.append(self.inzira[izina])
        iherezo
        subira result
    iherezo

    umurimo uburengero(self)
        subira uburengero(self.inzira)
    iherezo
iherezo

urwego UrugendoNavigator kora
    umurimo __init__(self)
        self.amatsiko = {}
        self.amateka = []
        self.ikirangwa_ikirangwa = none
        self.ikurikiranya = {}
        self.ikinyabupfura = {}
    iherezo

    umurimo shyira_inzira(self, izina, inzira)
        self.amatsiko[izina] = inzira
        niba self.ikirangwa_ikirangwa == none
            self.ikirangwa_ikirangwa = izina
        iherezo
        subira self
    iherezo

    umurimo shyira_group(self, group)
        buri inzira_name muri group.inzira
            self.amatsiko[inzira_name] = group.inzira[inzira_name]
        iherezo
        subira self
    iherezo

    umurimo shaka_inzira(self, izina)
        subira self.amatsiko.get(izina, none)
    iherezo

    umurimo genda(self, izina, ibiciro)
        shyira inzira = self.shaka_inzira(izina)
        niba inzira == none
            andika("Navigator: Inzira " + izina + " ntabonetse")
            subira ubusa
        iherezo
        niba inzira.reba_ubushobozi({"icyitso": izina}) == ubusa
            andika("Navigator: Ntabwo uremewe kugera kuri " + izina)
            subira ubusa
        iherezo
        shyira merged = inzira.rahindura(ibiciro)
        shyira entry = {"icyitso": izina, "ibiciro": merged, "ubwoko": PUSH}
        self.amateka.append(entry)
        self.ikirangwa_ikirangwa = izina
        andika("Navigator: Genda kuri " + izina)
        self._hamagara_ikurikiranya("genda", entry)
        subira ukuri
    iherezo

    umurimo subira(self)
        niba uburengero(self.amateka) > 1
            shyiramo _ = self.amateka.pop()
            shyira ibyo = self.amateka[uburengero(self.amateka) - 1]
            self.ikirangwa_ikirangwa = ibyo["icyitso"]
            andika("Navigator: Subira kuri " + ibyo["icyitso"])
            self._hamagara_ikurikiranya("subira", ibyo)
            subira ukuri
        iherezo
        andika("Navigator: Nta mateka asigaye")
        subira ubusa
    iherezo

    umurimo gusimbura(self, izina, ibiciro)
        shyira inzira = self.shaka_inzira(izina)
        niba inzira == none
            andika("Navigator: Inzira " + izina + " ntabonetse")
            subira ubusa
        iherezo
        shyira merged = inzira.rahindura(ibiciro)
        niba uburengero(self.amateka) > 0
            self.amateka[uburengero(self.amateka) - 1] = {"icyitso": izina, "ibiciro": merged, "ubwoko": REPLACE}
        cyangwa
            self.amateka.append({"icyitso": izina, "ibiciro": merged, "ubwoko": REPLACE})
        iherezo
        self.ikirangwa_ikirangwa = izina
        andika("Navigator: Gusimbura kuri " + izina)
        self._hamagara_ikurikiranya("gusimbura", {"icyitso": izina, "ibiciro": merged})
        subira ukuri
    iherezo

    umurimo genda_tab(self, izina, ibiciro)
        shyira inzira = self.shaka_inzira(izina)
        niba inzira == none
            andika("Navigator: Tab " + izina + " ntabonetse")
            subira ubusa
        iherezo
        shyira merged = inzira.rahindura(ibiciro)
        shyira entry = {"icyitso": izina, "ibiciro": merged, "ubwoko": TAB}
        self.amateka.append(entry)
        self.ikirangwa_ikirangwa = izina
        andika("Navigator: Tab kuri " + izina)
        self._hamagara_ikurikiranya("tab", entry)
        subira ukuri
    iherezo

    umurimo genda_drawer(self, izina, ibiciro)
        shyira inzira = self.shaka_inzira(izina)
        niba inzira == none
            andika("Navigator: Drawer " + izina + " ntabonetse")
            subira ubusa
        iherezo
        shyira merged = inzira.rahindura(ibiciro)
        shyira entry = {"icyitso": izina, "ibiciro": merged, "ubwoko": DRAWER}
        self.amateka.append(entry)
        self.ikirangwa_ikirangwa = izina
        andika("Navigator: Drawer kuri " + izina)
        self._hamagara_ikurikiranya("drawer", entry)
        subira ukuri
    iherezo

    umurimo genda_modal(self, izina, ibiciro)
        shyira inzira = self.shaka_inzira(izina)
        niba inzira == none
            andika("Navigator: Modal " + izina + " ntabonetse")
            subira ubusa
        iherezo
        shyira merged = inzira.rahindura(ibiciro)
        shyira entry = {"icyitso": izina, "ibiciro": merged, "ubwoko": MODAL}
        self.amateka.append(entry)
        self.ikirangwa_ikirangwa = izina
        andika("Navigator: Modal kuri " + izina)
        self._hamagara_ikurikiranya("modal", entry)
        subira ukuri
    iherezo

    umurimo genda_kubanza(self)
        niba uburengero(self.amateka) > 0
            shyira ibyo = self.amateka[0]
            self.ikirangwa_ikirangwa = ibyo["icyitso"]
            andika("Navigator: Genda kubanza kuri " + ibyo["icyitso"])
            subira ukuri
        iherezo
        subira ubusa
    iherezo

    umurimo ikirangwa(self)
        subira self.ikirangwa_ikirangwa
    iherezo

    umurimo ibiriho(self)
        niba uburengero(self.amateka) > 0
            subira self.amateka[uburengero(self.amateka) - 1]
        iherezo
        subira none
    iherezo

    umurimo amateka_yose(self)
        subira self.amateka
    iherezo

    umurimo uburengero(self)
        subira uburengero(self.amateka)
    iherezo

    umurimo siba_amateka(self)
        self.amateka = []
        self.ikirangwa_ikirangwa = none
    iherezo

    umurimo gukurikirana(self, icyitso, handler)
        niba icyitso not in self.ikurikiranya
            self.ikurikiranya[icyitso] = []
        iherezo
        self.ikurikiranya[icyitso].append(handler)
        subira self
    iherezo

    umurimo _hamagara_ikurikiranya(self, icyitso, data)
        niba icyitso in self.ikurikiranya
            buri handler muri self.ikurikiranya[icyitso]
                handler(data)
            iherezo
        iherezo
    iherezo

    umurimo shyira_ikinyabupfura(self, izina, igiciro)
        self.ikinyabupfura[izina] = igiciro
        subira self
    iherezo

    umurimo shaka_ikinyabupfura(self, izina)
        subira self.ikinyabupfura.get(izina, none)
    iherezo

    umurimo __str__(self)
        subira "UrugendoNavigator(" + shobora_umuntu(uburengero(self.amateka)) + " inzira)"
    iherezo
iherezo

umurimo shyira_inzira(navigator, izina, komponenti, ibiciro)
    shyira inzira = Inzira.nshya(izina, komponenti, ibiciro)
    navigator.shyira_inzira(izina, inzira)
    subira inzira
iherezo

umurimo gera(navigator, izina, ibiciro)
    subira navigator.genda(izina, ibiciro)
iherezo

umurimo tangiza_navigator()
    subira UrugendoNavigator.nshya()
iherezo
