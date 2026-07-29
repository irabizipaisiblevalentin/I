# mobile/navigation.i — Navigation system
# Ubugenzuzi, Inzira, Ihuza, na Tab/Drawer navigation

shyiramo "json"
shyiramo "text"

shyira_ko INZIRA_YIBANZE = "/"

urwego Inzira kora
    umurimo __init__(self, izina, component, ibiciro)
        self.izina = izina
        self.component = component
        self.ibiciro = ibiciro
        self.params = {}
    iherezo

    umurimo shakisha_param(self, izina, igiciro)
        self.params[izina] = igiciro
    iherezo

    umurimo igiciro_param(self, izina)
        subira self.params.get(izina, none)
    iherezo
iherezo

urwego Ihuza kora
    umurimo __init__(self, inzira, scheme)
        self.inzira = inzira
        self.scheme = scheme
        self.amahurizo = {}
    iherezo

    umurimo shakisha_amahurizo(self, izina, param)
        self.amahurizo[izina] = param
    iherezo

    umurimo ubaka(self, params)
        shyira url = self.scheme + "://" + self.inzira
        buri izina muri params.ibiciro kora
            shyira igiciro = params.ibiciro[izina]
            url = url + "/" + izina + "=" + shobora_umuntu(igiciro)
        iherezo
        subira url
    iherezo
iherezo

urwego Ubugenzuzi kora
    umurimo __init__(self)
        self.amateka = []
        self.inzira_zose = {}
        self.ikiganiro_kigezweho = none
    iherezo

    umurimo shakisha_inzira(self, izina, inzira)
        self.inzira_zose[izina] = inzira
    iherezo

    umurimo sunika(self, izina, ibiciro)
        shyira inzira = self.inzira_zose.get(izina, none)
        niba inzira == none kora
            andika("Ikosa: Inzira " + izina + " ntabonetse")
            subira
        iherezo
        inzira.ibiciro = ibiciro
        self.amateka.append(inzira)
        self.ikiganiro_kigezweho = inzira
    iherezo

    umurimo kura(self)
        niba uburengero(self.amateka) > 1 kora
            shyira _ = self.amateka.pop()
            self.ikiganiro_kigezweho = self.amateka[-1]
        iherezo
    iherezo

    umurimo gusimbura(self, izina, ibiciro)
        shyira inzira = self.inzira_zose.get(izina, none)
        niba inzira == none kora
            andika("Ikosa: Inzira " + izina + " ntabonetse")
            subira
        iherezo
        inzira.ibiciro = ibiciro
        niba uburengero(self.amateka) > 0 kora
            self.amateka[-1] = inzira
        cyangwa
            self.amateka.append(inzira)
        iherezo
        self.ikiganiro_kigezweho = inzira
    iherezo

    umurimo genda(self)
        niba uburengero(self.amateka) > 0 kora
            shyira inzira = self.amateka[0]
            self.ikiganiro_kigezweho = inzira
            self.component_kwerekana(inzira)
        iherezo
    iherezo

    umurimo component_kwerekana(self, inzira)
        andika("Ubugenzuzi: Kwerekana " + inzira.izina)
        andika("  Ibiciro: " + json.stringify(inzira.ibiciro))
    iherezo
iherezo

urwego UbugenzuziTab kora
    umurimo __init__(self)
        self.amacumbi = {}
        self.icumbi_rikoreshwa = none
    iherezo

    umurimo ongeza_icumbi(self, izina, ikiganiro, ikimenyetso)
        self.amacumbi[izina] = {
            "ikiganiro": ikiganiro,
            "ikimenyetso": ikimenyetso,
        }
        niba self.icumbi_rikoreshwa == none kora
            self.icumbi_rikoreshwa = izina
        iherezo
    iherezo

    umurimo hindura_icumbi(self, izina)
        niba izina in self.amacumbi kora
            self.icumbi_rikoreshwa = izina
            andika("Tab: Rereka " + izina)
        iherezo
    iherezo

    umurimo icumbi_kigezweho(self)
        subira self.amacumbi.get(self.icumbi_rikoreshwa, none)
    iherezo
iherezo

urwego UbugenzuziDrawer kora
    umurimo __init__(self)
        self.amacumbi = {}
        self.icumbi_rikoreshwa = none
        self.funguye = ubusa
    iherezo

    umurimo ongeza_icumbi(self, izina, ikiganiro, ikimenyetso)
        self.amacumbi[izina] = {
            "ikiganiro": ikiganiro,
            "ikimenyetso": ikimenyetso,
        }
    iherezo

    umurimo fungura(self)
        self.funguye = ukuri
        andika("Drawer: Ifunguye")
    iherezo

    umurimo gufunga(self)
        self.funguye = ubusa
        andika("Drawer: Irafunze")
    iherezo

    umurimo gukora_amaboko(self, izina)
        niba izina in self.amacumbi kora
            self.icumbi_rikoreshwa = izina
            self.gufunga()
        iherezo
    iherezo
iherezo

umurimo TangizaNavigator()
    subira Ubugenzuzi.nshya()
iherezo
