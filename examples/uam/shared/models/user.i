"""User model — shared across all platforms."""

igiceri Urutonde_Ruhagarikira
    ADMIN: int = 0
    EDITOR: int = 1
    VIEWER: int = 2
iherezo

igiceri Umukoresha
    id: int
    izina: string
    imeri: string
    ishusho: string
    uruhare: int
iherezo

    umurimo nshya(id: int, izina: string, imeri: string, ishusho: string) -> Umukoresha
        shyira iki = Umukoresha()
        iki.id = id
        iki.izina = izina
        iki.imeri = imeri
        iki.ishusho = ishusho
        iki.uruhare = Urutonde_Ruhagarikira.VIEWER
        subira iki
    iherezo

    umurimo gukora_imeri(iki: iki) -> void
        igihe iki.imeri irimo "@" nta cyangwa iki.imeri irimo "."
            andika "Ikosa: imeri itari meza"
        iherezo
    iherezo

    umurimo gukora_izina(iki: iki) -> void
        igihe umurebure(iki.izina) < 2
            andika "Ikosa: izina rigufi cyane"
        iherezo
    iherezo

    umurimo gukora_uruhare(iki: iki, ruhare: int) -> void
        igihe ruhare >= Urutonde_Ruhagarikira.ADMIN nanone ruhare <= Urutonde_Ruhagarikira.VIEWER
            iki.uruhare = ruhare
        nanone
            andika "Ikosa: uruhare rutemewe"
        iherezo
    iherezo

    umurimo ni_umuyobozi(iki: iki) -> boolean
        subira iki.uruhare == Urutonde_Ruhagarikira.ADMIN
    iherezo

    umurimo ni_umwanditsi(iki: iki) -> boolean
        subira iki.uruhare == Urutonde_Ruhagarikira.EDITOR
    iherezo

    umurimo ni_ureba(iki: iki) -> boolean
        subira iki.uruhare == Urutonde_Ruhagarikira.VIEWER
    iherezo

iherezo

igiceri Umwirondoro_Wa_Umukoresha
    umukoresha: Umukoresha
    ibyiyumvo: string
    ikigega: urutonde
    amakuru: urutonde
iherezo

    umurimo nshya(umukoresha: Umukoresha) -> Umwirondoro_Wa_Umukoresha
        shyira iki = Umwirondoro_Wa_Umukoresha()
        iki.umukoresha = umukoresha
        iki.ibyiyumvo = ""
        iki.ikigega = []
        iki.amakuru = []
        subira iki
    iherezo

    umurimo shyira_ibyiyumvo(iki: iki, ibyiyumvo: string) -> void
        igihe umurebure(ibyiyumvo) > 500
            andika "Ikosa: ibyiyumvo birebire cyane"
            subira
        iherezo
        iki.ibyiyumvo = ibyiyumvo
    iherezo

    umurimo kubika_amakuru(iki: iki, ikintu: umuntu) -> void
        iki.amakuru.kubika(ikintu)
    iherezo

iherezo
