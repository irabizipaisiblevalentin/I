"""Counter logic — shared across all platforms."""

igiceri Abantu_Biteze
    indangamuntu: umuntu
    imirimo: urutonde
iherezo

igiceri Kubika
    indangamuntu: umuntu
    imirimo: urutonde
iherezo

igiceri Indangagaciro
    indangamuntu: umuntu
    igiciro: int
iherezo

igiceri Ikubitiro
    abantu_biteze: urutonde
iherezo

    umurimo nshya() -> Ikubitiro
        shyira iki = Ikubitiro()
        iki.abantu_biteze = []
        subira iki
    iherezo

    umurimo kwiyandikisha(iki: iki, uwiteze: umuntu) -> void
        shyira kubika = Kubika()
        kubika.indangamuntu = uwiteze
        kubika.imirimo = []
        iki.abantu_biteze.kubika(kubika)
    iherezo

    umurimo gukwiza(iki: iki, igiciro: int) -> void
        kuri buri muntu in iki.abantu_biteze
            kuri buri murimo in muntu.imirimo
                murimo(muntu.indangamuntu, igiciro)
            iherezo
        iherezo
    iherezo

iherezo

igiceri Kubara
    igiciro: int
    ikubitiro: Ikubitiro
iherezo

    umurimo nshya() -> Kubara
        shyira iki = Kubara()
        iki.igiciro = 0
        iki.ikubitiro = Ikubitiro.nshya()
        subira iki
    iherezo

    umurimo ongera(iki: iki) -> int
        iki.igiciro = iki.igiciro + 1
        iki.ikubitiro.gukwiza(iki.igiciro)
        subira iki.igiciro
    iherezo

    umurimo gabanya(iki: iki) -> int
        iki.igiciro = iki.igiciro - 1
        iki.ikubitiro.gukwiza(iki.igiciro)
        subira iki.igiciro
    iherezo

    umurimo kubika_kuri_zero(iki: iki) -> int
        iki.igiciro = 0
        iki.ikubitiro.gukwiza(iki.igiciro)
        subira iki.igiciro
    iherezo

    umurimo indangagaciro(iki: iki) -> int
        subira iki.igiciro
    iherezo

    umurimo kwiyandikisha(iki: iki, uwiteze: umuntu) -> void
        iki.ikubitiro.kwiyandikisha(uwiteze)
    iherezo

iherezo
