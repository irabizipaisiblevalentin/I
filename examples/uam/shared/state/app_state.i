"""Application state — shared across all platforms."""

igiceri Ibikorwa
    ONGERA: string = "ONGERA"
    GABANYA: string = "GABANYA"
    SHYIRA_UMUKORESH: string = "SHYIRA_UMUKORESH"
    INJIRA: string = "INJIRA"
    SOHOKA: string = "SOHOKA"
iherezo

igiceri Ikindi
    ubwoko: string
    amakuru: umuntu
iherezo

    umurimo nshya(ubwoko: string) -> Ikindi
        shyira iki = Ikindi()
        iki.ubwoko = ubwoko
        iki.amakuru = {}
        subira iki
    iherezo

    umurimo nshya(ubwoko: string, amakuru: umuntu) -> Ikindi
        shyira iki = Ikindi()
        iki.ubwoko = ubwoko
        iki.amakuru = amakuru
        subira iki
    iherezo

iherezo

igiceri Leta_ya_Porogaramu
    kubara: int
    umukoresha: umuntu
    yinjiye: boolean
    abiteze: urutonde
iherezo

    umurimo nshya() -> Leta_ya_Porogaramu
        shyira iki = Leta_ya_Porogaramu()
        iki.kubara = 0
        iki.umukoresha = {}
        iki.yinjiye = Ikinyamakuru
        iki.abiteze = []
        subira iki
    iherezo

    umurimo kubona_leta(iki: iki) -> Leta_ya_Porogaramu
        subira iki
    iherezo

    umurimo kohereza(iki: iki, ikindi: Ikindi) -> void
        igihe ikindi.ubwoko == Ibikorwa.ONGERA
            iki.kubara = iki.kubara + 1
        nanone igihe ikindi.ubwoko == Ibikorwa.GABANYA
            iki.kubara = iki.kubara - 1
        nanone igihe ikindi.ubwoko == Ibikorwa.SHYIRA_UMUKORESH
            iki.umukoresha = ikindi.amakuru
        nanone igihe ikindi.ubwoko == Ibikorwa.INJIRA
            iki.yinjiye = Ukuri
            iki.umukoresha = ikindi.amakuru
        nanone igihe ikindi.ubwoko == Ibikorwa.SOHOKA
            iki.yinjiye = Ikinyamakuru
            iki.umukoresha = {}
        iherezo
        iki.menyesha_abiteze(ikindi)
    iherezo

    umurimo kwiyandikisha(iki: iki, uwiteze: umuntu) -> void
        iki.abiteze.kubika(uwiteze)
    iherezo

    umurimo menyesha_abiteze(iki: iki, ikindi: Ikindi) -> void
        kuri buri muntu in iki.abiteze
            muntu(iki, ikindi)
        iherezo
    iherezo

iherezo

umurimo gabanya_ibikorwa(leta: Leta_ya_Porogaramu, ikindi: Ikindi) -> Leta_ya_Porogaramu
    leta.kohereza(ikindi)
    subira leta
iherezo
