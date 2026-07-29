"""Home screen — platform-independent UI definition."""

# Import shared logic and UI components
kuva "../shared/logic/counter.i"  injiza Kubara
kuva "../shared/state/app_state.i"  injiza Leta_ya_Porogaramu, Ibikorwa, Ikindi
kuva "../components/button.i"  injiza gukora_buto

igiceri Ekrani_Nyubaki
    kubara: Kubara
    leta: Leta_ya_Porogaramu
    ibikoresho: urutonde
iherezo

    umurimo nshya() -> Ekrani_Nyubaki
        shyira iki = Ekrani_Nyubaki()
        iki.kubara = Kubara.nshya()
        iki.leta = Leta_ya_Porogaramu.nshya()
        iki.ibikoresho = []
        subira iki
    iherezo

    umurimo kubaka(iki: iki) -> umuntu
        shyira buto_ongera = gukora_buto("ONGERA", umurimo (**_) -> void
            iki.kubara.ongera()
            iki.leta.kohereza(Ikindi.nshya(Ibikorwa.ONGERA))
        iherezo)
        shyira buto_gabanya = gukora_buto("GABANYA", umurimo (**_) -> void
            iki.kubara.gabanya()
            iki.leta.kohereza(Ikindi.nshya(Ibikorwa.GABANYA))
        iherezo)
        shyira buto_kubika_kuri_zero = gukora_buto("KUBIKA KURI ZERO", umurimo (**_) -> void
            iki.kubara.kubika_kuri_zero()
            iki.leta.kohereza(Ikindi.nshya(Ibikorwa.GABANYA))
        iherezo)

        iki.ibikoresho = [buto_ongera, buto_gabanya, buto_kubika_kuri_zero]

        subira {
            "ekrani": "Nyubaki",
            "ikigaragaza": {
                "umutwe": "Muraho, Isi!",
                "igiciro": iki.kubara.indangagaciro(),
                "ibikoresho": iki.ibikoresho
            }
        }
    iherezo

    umurimo kuvugurura(iki: iki) -> void
        shyira ekrani = iki.kubaka()
        andika "Kuvugurura ekrani: " + ekrani
    iherezo

    umurimo kwiyandikisha(iki: iki) -> void
        iki.kubara.kwiyandikisha(umurimo (igiciro: int) -> void
            andika "Kubara kuvuguruwe: " + igiciro
            iki.kuvugurura()
        iherezo)
    iherezo

iherezo
