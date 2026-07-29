"""komponenti — UAM component registry for cross-platform UI components."""

shyiramo "json"

shyira_ko KOMPONENTI_VERSION = "1.0.0"

shyira_ko URUBUGA = "urubuga"
shyira_ko IBIRO = "ibiro"
shyira_ko MOBILE = "mobile"
shyira_ko DESKTOP = "desktop"

urwego KomponentiDefinition kora
    umurimo __init__(self, izina, imiterere, platform)
        self.izina = izina
        self.imiterere = imiterere
        self.platform = platform
        self.ibintu = {}
        self.ibikorwa = []
        self.umubiri = none
    iherezo

    umurimo shyira_ibintu(self, izina, igiciro)
        self.ibintu[izina] = igiciro
        subira self
    iherezo

    umurimo shaka_ibintu(self, izina)
        subira self.ibintu.get(izina, none)
    iherezo

    umurimo shyira_umubiri(self, handler)
        self.umubiri = handler
        subira self
    iherezo

    umurimo tanga(self, ibiciro)
        shyira merged = {}
        buri key muri self.ibintu
            merged[key] = self.ibintu[key]
        iherezo
        buri key muri ibiciro
            merged[key] = ibiciro[key]
        iherezo
        niba self.umubiri != none
            subira self.umubiri(merged)
        iherezo
        subira merged
    iherezo

    umurimo __str__(self)
        subira "KomponentiDefinition(" + self.izina + ", " + self.platform + ")"
    iherezo
iherezo

urwego KomponentiRegistry kora
    umurimo __init__(self)
        self.ikinyabupfura = {}
        self.ikurikiranya = {}
        self.impuzandengo = {}
    iherezo

    umurimo iyandikisha(self, izina, definition)
        shyira platform = definition.platform
        niba platform not in self.ikinyabupfura
            self.ikinyabupfura[platform] = {}
        iherezo
        self.ikinyabupfura[platform][izina] = definition
        self.impuzandengo[izina] = definition
        subira self
    iherezo

    umurimo iyandikisha_ikurikiranya(self, izina, platform, definition)
        niba platform not in self.ikurikiranya
            self.ikurikiranya[platform] = {}
        iherezo
        niba izina not in self.ikurikiranya[platform]
            self.ikurikiranya[platform][izina] = []
        iherezo
        self.ikurikiranya[platform][izina].append(definition)
        subira self
    iherezo

    umurimo shaka(self, izina, platform)
        niba platform in self.ikinyabupfura
            niba izina in self.ikinyabupfura[platform]
                subira self.ikinyabupfura[platform][izina]
            iherezo
        iherezo
        subira self.impuzandengo.get(izina, none)
    iherezo

    umurimo shaka_ikurikiranya(self, izina, platform)
        niba platform in self.ikurikiranya
            niba izina in self.ikurikiranya[platform]
                subira self.ikurikiranya[platform][izina]
            iherezo
        iherezo
        subira []
    iherezo

    umurimo siba(self, izina, platform)
        niba platform in self.ikinyabupfura
            niba izina in self.ikinyabupfura[platform]
                shyiramo _ = self.ikinyabupfura[platform].pop(izina)
            iherezo
        iherezo
        niba izina in self.impuzandengo
            shyiramo _ = self.impuzandengo.pop(izina)
        iherezo
    iherezo

    umurimo list(self, platform)
        shyira result = {}
        niba platform in self.ikinyabupfura
            buri izina muri self.ikinyabupfura[platform]
                result[izina] = self.ikinyabupfura[platform][izina]
            iherezo
        iherezo
        buri izina muri self.impuzandengo
            niba izina not in result
                result[izina] = self.impuzandengo[izina]
            iherezo
        iherezo
        subira result
    iherezo

    umurimo uburengero(self)
        subira uburengero(self.impuzandengo)
    iherezo
iherezo

ikinyabupfura_komponenti = KomponentiRegistry.nshya()

umurimo iyandikisha_komponenti(izina, imiterere, platform)
    shyira defi = KomponentiDefinition.nshya(izina, imiterere, platform)
    ikinyabupfura_komponenti.iyandikisha(izina, defi)
    subira defi
iherezo

umurimo shaka_komponenti(izina, platform)
    subira ikinyabupfura_komponenti.shaka(izina, platform)
iherezo

umurimo iyandikisha_ikurikiranya(izina, platform, definition)
    ikinyabupfura_komponenti.iyandikisha_ikurikiranya(izina, platform, definition)
    subira definition
iherezo

umurimo list_komponenti(platform)
    subira ikinyabupfura_komponenti.list(platform)
iherezo

shyira_ko URUBUGA_BUTTON = KomponentiDefinition.nshya("button", {"ubwoko": "urubuga", "tag": "button"}, URUBUGA)
shyira_ko URUBUGA_INPUT = KomponentiDefinition.nshya("input", {"ubwoko": "urubuga", "tag": "input"}, URUBUGA)
shyira_ko URUBUGA_TEXT = KomponentiDefinition.nshya("text", {"ubwoko": "urubuga", "tag": "span"}, URUBUGA)
shyira_ko URUBUGA_LIST = KomponentiDefinition.nshya("list", {"ubwoko": "urubuga", "tag": "ul"}, URUBUGA)
shyira_ko URUBUGA_IMAGE = KomponentiDefinition.nshya("image", {"ubwoko": "urubuga", "tag": "img"}, URUBUGA)
shyira_ko URUBUGA_FORM = KomponentiDefinition.nshya("form", {"ubwoko": "urubuga", "tag": "form"}, URUBUGA)

shyira_ko MOBILE_BUTTON = KomponentiDefinition.nshya("button", {"ubwoko": "mobile", "material": "raised"}, MOBILE)
shyira_ko MOBILE_INPUT = KomponentiDefinition.nshya("input", {"ubwoko": "mobile", "material": "outlined"}, MOBILE)
shyira_ko MOBILE_TEXT = KomponentiDefinition.nshya("text", {"ubwoko": "mobile", "font": "body"}, MOBILE)
shyira_ko MOBILE_LIST = KomponentiDefinition.nshya("list", {"ubwoko": "mobile", "scroll": ukuri}, MOBILE)
shyira_ko MOBILE_IMAGE = KomponentiDefinition.nshya("image", {"ubwoko": "mobile", "fit": "cover"}, MOBILE)
shyira_ko MOBILE_CARD = KomponentiDefinition.nshya("card", {"ubwoko": "mobile", "elevation": 2}, MOBILE)

shyira_ko IBIRO_BUTTON = KomponentiDefinition.nshya("button", {"ubwoko": "ibiro", "style": "modern"}, IBIRO)
shyira_ko IBIRO_INPUT = KomponentiDefinition.nshya("input", {"ubwoko": "ibiro", "style": "modern"}, IBIRO)
shyira_ko IBIRO_TEXT = KomponentiDefinition.nshya("text", {"ubwoko": "ibiro", "font": "system"}, IBIRO)
shyira_ko IBIRO_LIST = KomponentiDefinition.nshya("list", {"ubwoko": "ibiro", "scroll": ukuri}, IBIRO)
shyira_ko IBIRO_TABLE = KomponentiDefinition.nshya("table", {"ubwoko": "ibiro", "resizable": ukuri}, IBIRO)
shyira_ko IBIRO_TREE = KomponentiDefinition.nshya("tree", {"ubwoko": "ibiro", "expandable": ukuri}, IBIRO)

ikinyabupfura_komponenti.iyandikisha(URUBUGA_BUTTON.izina, URUBUGA_BUTTON)
ikinyabupfura_komponenti.iyandikisha(URUBUGA_INPUT.izina, URUBUGA_INPUT)
ikinyabupfura_komponenti.iyandikisha(URUBUGA_TEXT.izina, URUBUGA_TEXT)
ikinyabupfura_komponenti.iyandikisha(URUBUGA_LIST.izina, URUBUGA_LIST)
ikinyabupfura_komponenti.iyandikisha(URUBUGA_IMAGE.izina, URUBUGA_IMAGE)
ikinyabupfura_komponenti.iyandikisha(URUBUGA_FORM.izina, URUBUGA_FORM)

ikinyabupfura_komponenti.iyandikisha(MOBILE_BUTTON.izina, MOBILE_BUTTON)
ikinyabupfura_komponenti.iyandikisha(MOBILE_INPUT.izina, MOBILE_INPUT)
ikinyabupfura_komponenti.iyandikisha(MOBILE_TEXT.izina, MOBILE_TEXT)
ikinyabupfura_komponenti.iyandikisha(MOBILE_LIST.izina, MOBILE_LIST)
ikinyabupfura_komponenti.iyandikisha(MOBILE_IMAGE.izina, MOBILE_IMAGE)
ikinyabupfura_komponenti.iyandikisha(MOBILE_CARD.izina, MOBILE_CARD)

ikinyabupfura_komponenti.iyandikisha(IBIRO_BUTTON.izina, IBIRO_BUTTON)
ikinyabupfura_komponenti.iyandikisha(IBIRO_INPUT.izina, IBIRO_INPUT)
ikinyabupfura_komponenti.iyandikisha(IBIRO_TEXT.izina, IBIRO_TEXT)
ikinyabupfura_komponenti.iyandikisha(IBIRO_LIST.izina, IBIRO_LIST)
ikinyabupfura_komponenti.iyandikisha(IBIRO_TABLE.izina, IBIRO_TABLE)
ikinyabupfura_komponenti.iyandikisha(IBIRO_TREE.izina, IBIRO_TREE)
