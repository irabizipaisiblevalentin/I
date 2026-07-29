"""Desktop entry point — sets up ibiro platform with UAM shared modules."""

# Import shared modules
kuva "../shared/logic/counter.i"  injiza Kubara
kuva "../shared/models/user.i"  injiza Umukoresha, Urutonde_Ruhagarikira, Umwirondoro_Wa_Umukoresha
kuva "../shared/services/api.i"  injiza API_Serivisi
kuva "../shared/state/app_state.i"  injiza Leta_ya_Porogaramu, Ibikorwa, Ikindi, gabanya_ibikorwa

# Import UI
kuva "../ui/screens/home.i"  injiza Ekrani_Nyubaki

# Import ibiro platform
kuva "ibiro.porogaramu"  injiza Porogaramu
kuva "ibiro.idirishya"  injiza Idirishya

igiceri Porogaramu_ya_Desktop
    porogaramu: Porogaramu
    idirishya: Idirishya
    ekrani: Ekrani_Nyubaki
    api: API_Serivisi
    leta: Leta_ya_Porogaramu
iherezo

    umurimo nshya() -> Porogaramu_ya_Desktop
        shyira iki = Porogaramu_ya_Desktop()
        iki.porogaramu = Porogaramu("my-cross-platform-app-desktop", "ikigo")
        iki.idirishya = iki.porogaramu.uyobore_idirishya.kora_idirishya("nyamukuru", umutwe="I Application", ubugari=800, uburebure=600)
        iki.ekrani = Ekrani_Nyubaki.nshya()
        iki.api = API_Serivisi.nshya("https://api.example.com")
        iki.leta = Leta_ya_Porogaramu.nshya()
        subira iki
    iherezo

    umurimo tangira(iki: iki) -> void
        andika "Tangira porogaramu ya desktop..."
        iki.ekrani.kwiyandikisha()
        shyira ekrani = iki.ekrani.kubaka()
        iki.idirishya.shyira_ikoresho_nyamukuru(ekrani)
        iki.idirishya.kwerekana()
        iki.porogaramu.genda()
    iherezo

    umurimo genda(iki: iki) -> void
        andika "Genda porogaramu ya desktop"
        iki.tangira()
    iherezo

iherezo

shyira porogaramu = Porogaramu_ya_Desktop.nshya()
porogaramu.genda()
