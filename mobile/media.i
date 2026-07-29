# mobile/media.i — Media support
# Camera, Image, Video, Audio, Streaming, Recording

shyiramo "json"
shyiramo "time"
shyiramo "device"

shyira_ko MEDIA_TYPE_IMAGE = "ishusho"
shyira_ko MEDIA_TYPE_VIDEO = "amashusho"
shyira_ko MEDIA_TYPE_AUDIO = "ijwi"

urwego Kamera kora
    umurimo __init__(self)
        self.ikora = ubusa
        self.ubwoko = MEDIA_TYPE_IMAGE
        self.inyuma = ukuri
    iherezo

    umurimo fungura(self)
        self.ikora = ukuri
        andika("Kamera: Ifunguye")
    iherezo

    umurimo gufunga(self)
        self.ikora = ubusa
        andika("Kamera: Irafunze")
    iherezo

    umurimo fata_ishusho(self)
        niba self.ikora == ubusa kora
            subira none
        iherezo
        shyira ishusho = {
            "ubwoko": MEDIA_TYPE_IMAGE,
            "igihe": time.now(),
            "inyuma": self.inyuma,
            "data": "data:ishusho;base64,",
        }
        andika("Kamera: Ishusho ifashwe")
        subira ishusho
    iherezo

    umurimo fata_amashusho(self, uburebure)
        niba self.ikora == ubusa kora
            subira none
        iherezo
        shyira amashusho = {
            "ubwoko": MEDIA_TYPE_VIDEO,
            "uburebure": uburebure,
            "igihe": time.now(),
            "data": "data:amashusho;base64,",
        }
        andika("Kamera: Amashusho afashwe (" + shobora_umuntu(uburebure) + "s)")
        subira amashusho
    iherezo
iherezo

urwego Ishusho itunganya kora
    umurimo __init__(self, inzira)
        self.inzira = inzira
        self.data = none
        self.uburebure = 0
        self.ubugari = 0
    iherezo

    umurimo gupakira(self)
        self.data = "ishusho_data"
        self.uburebure = 1920
        self.ubugari = 1080
        andika("Ishusho: Yapakirwa kuva " + self.inzira)
    iherezo

    umurimo guhindura_ubunini(self, ubugari, uburebure)
        niba self.data != none kora
            self.ubugari = ubugari
            self.uburebure = uburebure
            andika("Ishusho: Ihinduye ubunini kuri " + shobora_umuntu(ubugari) + "x" + shobora_umuntu(uburebure))
        iherezo
    iherezo
iherezo

urwego Amajwi kora
    umurimo __init__(self)
        self.ikina = ubusa
        self.uburebure = 0.0
    iherezo

    umurimo pakira(self, inzira)
        self.inzira = inzira
        self.ikina = ubusa
        self.uburebure = 180.0
        andika("Amajwi: Yapakirwa kuva " + inzira)
    iherezo

    umurimo kina(self)
        self.ikina = ukuri
        andika("Amajwi: Aratunganywa")
    iherezo

    umurimo guhagarika(self)
        self.ikina = ubusa
        andika("Amajwi: Arahagarijwe")
    iherezo
iherezo

urwego Streaming kora
    umurimo __init__(self, url)
        self.url = url
        self.ikora = ubusa
        self.protocol = "hls"
    iherezo

    umurimo tangira(self)
        self.ikora = ukuri
        andika("Streaming: Yatangiye kuri " + self.url)
    iherezo

    umurimo guhagarika(self)
        self.ikora = ubusa
        andika("Streaming: Yahagarijwe")
    iherezo
iherezo

urwego Gufata amajwi kora
    umurimo __init__(self)
        self.ikora = ubusa
        self.inzira_yandika = none
    iherezo

    umurimo tangira_gufata(self)
        self.ikora = ukuri
        shyira izina = "recording_" + shobora_umuntu(time.now()) + ".wav"
        self.inzira_yandika = izina
        andika("Gufata amajwi: Byatangiye -> " + izina)
    iherezo

    umurimo guhagarika_gufata(self)
        self.ikora = ubusa
        andika("Gufata amajwi: Byahagarijwe")
        subira self.inzira_yandika
    iherezo
iherezo
