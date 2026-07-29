# mobile/layout.i — Layout system
# Inkingi, Umurongo, Urusobete, Itemba, Ikinyabiziga

shyiramo "json"
shyiramo "device"

shyira_ko SAFE_AREA_TOP = device.safe_area_top()
shyira_ko SAFE_AREA_BOTTOM = device.safe_area_bottom()
shyira_ko SAFE_AREA_LEFT = device.safe_area_left()
shyira_ko SAFE_AREA_RIGHT = device.safe_area_right()

shyira_ko INKINGI = "inkingi"
shyira_ko UMURONGO = "umurongo"
shyira_ko URUSOBETE = "urusobete"
shyira_ko ITEMBA = "itemba"
shyira_ko IKINYABIZIGA = "ikinyabiziga"

urwego Inkingi kora
    umurimo __init__(self, ibice, indangamuntu, intera, ikinyabiziga)
        self.ibice = ibice
        self.indangamuntu = indangamuntu
        self.intera = intera
        self.ikinyabiziga = ikinyabiziga
        self.ubwoko = INKINGI
    iherezo

    umurimo kongera(self, ikintu)
        self.ibice.append(ikintu)
    iherezo

    umurimo kuraho(self, ikintu)
        shyira index = self.ibice.index(ikintu)
        niba index != -1 kora
            self.ibice.pop(index)
        iherezo
    iherezo

    umurimo ibara_ikinyabiziga(self)
        andika("Inkingi: " + self.indangamuntu + " ifite ibice " + shobora_umuntu(uburengero(self.ibice)))
    iherezo
iherezo

urwego Umurongo kora
    umurimo __init__(self, ibice, indangamuntu, intera, ikinyabiziga)
        self.ibice = ibice
        self.indangamuntu = indangamuntu
        self.intera = intera
        self.ikinyabiziga = ikinyabiziga
        self.ubwoko = UMURONGO
    iherezo

    umurimo kongera(self, ikintu)
        self.ibice.append(ikintu)
    iherezo

    umurimo kuraho(self, ikintu)
        shyira index = self.ibice.index(ikintu)
        niba index != -1 kora
            self.ibice.pop(index)
        iherezo
    iherezo

    umurimo ibara_ikinyabiziga(self)
        andika("Umurongo: " + self.indangamuntu + " ufite ibice " + shobora_umuntu(uburengero(self.ibice)))
    iherezo
iherezo

urwego Urusobete kora
    umurimo __init__(self, ibice, inkingi, indangamuntu, intera)
        self.ibice = ibice
        self.inkingi = inkingi
        self.indangamuntu = indangamuntu
        self.intera = intera
        self.ubwoko = URUSOBETE
    iherezo

    umurimo kongera(self, ikintu)
        self.ibice.append(ikintu)
    iherezo

    umurimo ibara_ikinyabiziga(self)
        andika("Urusobete: " + self.indangamuntu + " (" + shobora_umuntu(self.inkingi) + " inkingi)")
    iherezo
iherezo

urwego Itemba kora
    umurimo __init__(self, ibice, indangamuntu, alignment)
        self.ibice = ibice
        self.indangamuntu = indangamuntu
        self.alignment = alignment
        self.ubwoko = ITEMBA
    iherezo

    umurimo kongera(self, ikintu)
        self.ibice.append(ikintu)
    iherezo

    umurimo ibara_ikinyabiziga(self)
        andika("Itemba: " + self.indangamuntu + " ifite ibice " + shobora_umuntu(uburengero(self.ibice)))
    iherezo
iherezo

urwego Ikinyabiziga kora
    umurimo __init__(self, ibice, indangamuntu, inzira, intera)
        self.ibice = ibice
        self.indangamuntu = indangamuntu
        self.inzira = inzira
        self.intera = intera
        self.ubwoko = IKINYABIZIGA
    iherezo

    umurimo kongera(self, ikintu)
        self.ibice.append(ikintu)
    iherezo

    umurimo ibara_ikinyabiziga(self)
        andika("Ikinyabiziga: " + self.indangamuntu + " (" + self.inzira + " inzira)")
    iherezo
iherezo

umurimo inkingi_nshya(ibice, indangamuntu, intera)
    subira Inkingi.nshya(ibice, indangamuntu, intera, ukuri)
iherezo

umurimo umurongo_nshya(ibice, indangamuntu, intera)
    subira Umurongo.nshya(ibice, indangamuntu, intera, ukuri)
iherezo

umurimo urusobete_nshya(ibice, inkingi, indangamuntu)
    subira Urusobete.nshya(ibice, inkingi, indangamuntu, 8)
iherezo

umurimo koresha_safe_area(igiciro, urwego)
    niba urwego == "hejuru" kora
        subira igiciro + SAFE_AREA_TOP
    cyangwa niba urwego == "hasi" kora
        subira igiciro + SAFE_AREA_BOTTOM
    cyangwa
        subira igiciro
    iherezo
iherezo
