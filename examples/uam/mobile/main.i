"""Mobile entry point — sets up MOBILE platform with UAM shared modules."""

# Import shared modules
kuva "../shared/logic/counter.i"  injiza Kubara
kuva "../shared/models/user.i"  injiza Umukoresha, Urutonde_Ruhagarikira, Umwirondoro_Wa_Umukoresha
kuva "../shared/services/api.i"  injiza API_Serivisi
kuva "../shared/state/app_state.i"  injiza Leta_ya_Porogaramu, Ibikorwa, Ikindi, gabanya_ibikorwa

# Import UI
kuva "../ui/screens/home.i"  injiza Ekrani_Nyubaki

# Import mobile platform
kuva "mobile.porogaramu"  injiza Porogaramu_ya_Mobu
kuva "mobile.idirishya"  injiza Idirishya_rya_Mobu

igiceri Porogaramu_ya_Mobile
    porogaramu: Porogaramu_ya_Mobu
    idirishya: Idirishya_rya_Mobu
    ekrani: Ekrani_Nyubaki
    api: API_Serivisi
    leta: Leta_ya_Porogaramu
iherezo

    umurimo nshya() -> Porogaramu_ya_Mobile
        shyira iki = Porogaramu_ya_Mobile()
        iki.porogaramu = Porogaramu_ya_Mobu("my-cross-platform-app-mobile", "mobu")
        iki.idirishya = iki.porogaramu.kora_idirishya("nyamukuru", umutwe="I Application")
        iki.ekrani = Ekrani_Nyubaki.nshya()
        iki.api = API_Serivisi.nshya("https://api.example.com")
        iki.leta = Leta_ya_Porogaramu.nshya()
        subira iki
    iherezo

    umurimo tangira(iki: iki) -> void
        andika "Tangira porogaramu ya mobile..."
        iki.ekrani.kwiyandikisha()
        shyira ekrani = iki.ekrani.kubaka()
        iki.idirishya.shyira_ikoresho_nyamukuru(ekrani)
        iki.idirishya.kwerekana()
        iki.porogaramu.genda()
    iherezo

    umurimo genda(iki: iki) -> void
        andika "Genda porogaramu ya mobile"
        iki.tangira()
    iherezo

iherezo

shyira porogaramu = Porogaramu_ya_Mobile.nshya()
porogaramu.genda()
