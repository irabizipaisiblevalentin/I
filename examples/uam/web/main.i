"""Web entry point — sets up urubuga platform with UAM shared modules."""

# Import shared modules
kuva "../shared/logic/counter.i"  injiza Kubara
kuva "../shared/models/user.i"  injiza Umukoresha, Urutonde_Ruhagarikira, Umwirondoro_Wa_Umukoresha
kuva "../shared/services/api.i"  injiza API_Serivisi
kuva "../shared/state/app_state.i"  injiza Leta_ya_Porogaramu, Ibikorwa, Ikindi, gabanya_ibikorwa

# Import UI
kuva "../ui/screens/home.i"  injiza Ekrani_Nyubaki

# Import urubuga platform
kuva "urubuga"  injiza Urubuga, Seriveri

igiceri Porogaramu_ya_Urubuga
    porogaramu: umuntu
    ekrani: Ekrani_Nyubaki
    seriveri: Seriveri
    api: API_Serivisi
    leta: Leta_ya_Porogaramu
iherezo

    umurimo nshya() -> Porogaramu_ya_Urubuga
        shyira iki = Porogaramu_ya_Urubuga()
        iki.porogaramu = Urubuga("my-cross-platform-app-web", "urubuga")
        iki.ekrani = Ekrani_Nyubaki.nshya()
        iki.api = API_Serivisi.nshya("https://api.example.com")
        iki.leta = Leta_ya_Porogaramu.nshya()
        subira iki
    iherezo

    umurimo tangira(iki: iki) -> void
        andika "Tangira porogaramu ya urubuga..."
        iki.ekrani.kwiyandikisha()
        shyira ekrani = iki.ekrani.kubaka()
        andika "Ekrani yubatswe: " + ekrani
        iki.porogaramu.genda()
    iherezo

    umurimo genda(iki: iki) -> void
        andika "Genda porogaramu ya urubuga"
        iki.tangira()
    iherezo

iherezo

shyira porogaramu = Porogaramu_ya_Urubuga.nshya()
porogaramu.genda()
