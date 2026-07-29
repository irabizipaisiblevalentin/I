"""Button component — platform-independent UI definition."""

igiceri Ibikorwa_bya_Buto
    kanda: umuntu
    ubwoko: string
    inyandiko: string
    yashoboye: boolean
iherezo

    umurimo nshya(inyandiko: string, kanda: umuntu) -> Ibikorwa_bya_Buto
        shyira iki = Ibikorwa_bya_Buto()
        iki.inyandiko = inyandiko
        iki.kanda = kanda
        iki.ubwoko = "cyangwa"
        iki.yashoboye = Ukuri
        subira iki
    iherezo

    umurimo gukora_buto(iki: iki) -> umuntu
        igihe iki.yashoboye
            subira {
                "ikoresho": "Buto",
                "inyandiko": iki.inyandiko,
                "ubwoko": iki.ubwoko,
                "kanda": iki.kanda,
                "yashoboye": iki.yashoboye
            }
        nanone
            subira {
                "ikoresho": "Buto",
                "inyandiko": iki.inyandiko,
                "ubwoko": "idafite",
                "kanda": {},
                "yashoboye": iki.yashoboye
            }
        iherezo
    iherezo

    umurimo shyira_ubwoko(iki: iki, ubwoko: string) -> void
        iki.ubwoko = ubwoko
    iherezo

    umurimo shobora(iki: iki) -> void
        iki.yashoboye = Ukuri
    iherezo

    umurimo buza(iki: iki) -> void
        iki.yashoboye = Ikinyamakuru
    iherezo

iherezo

igiceri Ikusanyirizo_ry_Ibikoresho
    ibikoresho: urutonde
iherezo

    umurimo nshya() -> Ikusanyirizo_ry_Ibikoresho
        shyira iki = Ikusanyirizo_ry_Ibikoresho()
        iki.ibikoresho = []
        subira iki
    iherezo

    umurimo kwiyandikisha(iki: iki, izina: string, ikoresho: umuntu) -> void
        shyira ikoresho = {"izina": izina, "ikoresho": ikoresho}
        iki.ibikoresho.kubika(ikoresho)
    iherezo

    umurimo kubona(iki: iki, izina: string) -> umuntu
        kuri buri ikoresho in iki.ibikoresho
            igihe ikoresho["izina"] == izina
                subira ikoresho["ikoresho"]
            iherezo
        iherezo
        subira {}
    iherezo

iherezo

shyira ikusanyirizo = Ikusanyirizo_ry_Ibikoresho.nshya()

umurimo gukora_buto(inyandiko: string, kanda: umuntu) -> umuntu
    shyira buto = Ibikorwa_bya_Buto.nshya(inyandiko, kanda)
    subira buto.gukora_buto()
iherezo
