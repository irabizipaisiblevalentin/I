"""gusaba — UAM cross-platform state management with actions and reducers."""

shyiramo "json"
shyiramo "time"

shyira_ko GusabaVersion = "1.0.0"

shyira_ko IKORA = "kora"
shyira_ko IHINDURA = "hindura"
shyira_ko SIBA = "siba"
shyira_ko SUBIRA_INYUMARO = "subira_inyumaro"
shyira_ko KUBIKA = "kubika"
shyira_ko GUSOMA = "gusoma"

urwego Igikorwa kora
    umurimo __init__(self, ubwoko, ibiciro)
        self.ubwoko = ubwoko
        self.ibiciro = ibiciro
        self.igihe = time.now()
        self.id = ubwoko + "_" + shobora_umuntu(self.igihe)
    iherezo

    umurimo __str__(self)
        subira "Igikorwa(" + self.ubwoko + ")"
    iherezo
iherezo

urwego IkurikiranyaIgikorwa kora
    umurimo __init__(self)
        self.abunvisi = {}
        self.amateka = []
        self.kugabanya = none
        self.igihagarikive = ubusa
    iherezo

    umurimo andika(self, abunvisi_izina, handler)
        niba abunvisi_izina not in self.abunvisi
            self.abunvisi[abunvisi_izina] = []
        iherezo
        self.abunvisi[abunvisi_izina].append(handler)
        subira self
    iherezo

    umurimo siba_abunvisi(self, abunvisi_izina, handler)
        niba abunvisi_izina in self.abunvisi
            shyira handlers = self.abunvisi[abunvisi_izina]
            shyira index = -1
            buri i muri 0 kugeza uburengero(handlers)
                niba handlers[i] == handler
                    index = i
                    iherezo
                iherezo
            iherezo
            niba index >= 0
                handlers.pop(index)
            iherezo
        iherezo
        subira self
    iherezo

    umurimo kohereza(self, igikorwa)
        niba self.igihagarikive
            subira
        iherezo
        niba self.kugabanya != none
            shyira igikorwa_cyagenzuwe = self.kugabanya(igikorwa)
            niba igikorwa_cyagenzuwe != none
                igikorwa = igikorwa_cyagenzuwe
            iherezo
        iherezo
        self.amateka.append(igikorwa)
        niba igikorwa.ubwoko in self.abunvisi
            buri handler muri self.abunvisi[igikorwa.ubwoko]
                handler(igikorwa)
            iherezo
        iherezo
        niba IKORA in self.abunvisi
            buri handler muri self.abunvisi[IKORA]
                handler(igikorwa)
            iherezo
        iherezo
        subira igikorwa
    iherezo

    umurimo shyira_kugabanya(self, kugabanya)
        self.kugabanya = kugabanya
        subira self
    iherezo

    umurimo guhagarika(self)
        self.igihagarikive = ukuri
    iherezo

    umurimo komeza(self)
        self.igihagarikive = ubusa
    iherezo

    umurimo siba_amateka(self)
        self.amateka = []
    iherezo

    umurimo uburengero_amateka(self)
        subira uburengero(self.amateka)
    iherezo
iherezo

urwego UbubikoBw'Igihugu kora
    umurimo __init__(self, izina)
        self.izina = izina
        self.state = {}
        self.iyongera = {}
        self.ikurikiranya = IkurikiranyaIgikorwa.nshya()
        self.ibika = none
        self.gusoma = none
    iherezo

    umurimo iyandikisha_iyongera(self, icyitso, iyongera)
        self.iyongera[icyitso] = iyongera
        niba icyitso not in self.state
            self.state[icyitso] = {}
        iherezo
        subira self
    iherezo

    umurimo kohereza(self, igikorwa)
        niba igikorwa.ubwoko in self.iyongera
            shyira iyongera = self.iyongera[igikorwa.ubwoko]
            shyira ubufatanye = self.state[igikorwa.ubwoko]
            shyira state_nshya = iyongera(ubufatanye, igikorwa)
            self.state[igikorwa.ubwoko] = state_nshya
        iherezo
        self.ikurikiranya.kohereza(igikorwa)
        self._kubika()
        subira igikorwa
    iherezo

    umurimo shaka(self, icyitso)
        subira self.state.get(icyitso, none)
    iherezo

    umurimo shaka_byose(self)
        subira self.state
    iherezo

    umurimo shyira(self, icyitso, igiciro)
        self.state[icyitso] = igiciro
        self._hamagara_abunvisi({"ubwoko": IHINDURA, "ibiciro": {"icyitso": icyitso, "igiciro": igiciro}})
        self._kubika()
        subira self
    iherezo

    umurimo siba(self, icyitso)
        niba icyitso in self.state
            shyiramo _ = self.state.pop(icyitso)
            self._hamagara_abunvisi({"ubwoko": SIBA, "ibiciro": {"icyitso": icyitso}})
            self._kubika()
        iherezo
        subira self
    iherezo

    umurimo subira_inyumaro(self)
        bwa nyuma niba uburengero(self.ikurikiranya.amateka) > 1
            shyiramo ibyo = self.ikurikiranya.amateka.pop()
            niba ibyo.ubwoko in self.iyongera
                shyira iyongera = self.iyongera[ibyo.ubwoko]
                shyira ubufatanye = self.state[ibyo.ubwoko]
                self.state[ibyo.ubwoko] = iyongera(ubufatanye, Igikorwa.nshya(SUBIRA_INYUMARO, ibyo.ibiciro))
            iherezo
        iherezo
    iherezo

    umurimo andika(self, ubwoko_igikorwa, handler)
        self.ikurikiranya.andika(ubwoko_igikorwa, handler)
        subira self
    iherezo

    umurimo _hamagara_abunvisi(self, igikorwa)
        self.ikurikiranya.kohereza(igikorwa)
    iherezo

    umurimo shyira_ibika(self, ibika)
        self.ibika = ibika
        subira self
    iherezo

    umurimo shyira_gusoma(self, gusoma)
        self.gusoma = gusoma
        subira self
    iherezo

    umurimo _kubika(self)
        niba self.ibika != none
            self.ibika(self.izina, self.state)
        iherezo
    iherezo

    umurimo gusoma(self)
        niba self.gusoma != none
            shyira ibikubiye = self.gusoma(self.izina)
            niba ibikubiye != none
                self.state = ibikubiye
            iherezo
        iherezo
        subira self
    iherezo

    umurimo siba_byose(self)
        self.state = {}
        buri icyitso muri self.iyongera
            self.state[icyitso] = {}
        iherezo
        self.ikurikiranya.siba_amateka()
        self._kubika()
    iherezo

    umurimo uburengero(self)
        subira uburengero(self.state)
    iherezo

    umurimo __str__(self)
        subira "UbubikoBw'Igihugu(" + self.izina + ", " + shobora_umuntu(uburengero(self.state)) + " icyitso)"
    iherezo
iherezo

urwego GusabaKomatanya kora
    umurimo __init__(self)
        self.amasoko = {}
        self.ikirangwa = none
    iherezo

    umurimo ongeza(self, izina, ububiko)
        self.amasoko[izina] = ububiko
        niba self.ikirangwa == none
            self.ikirangwa = izina
        iherezo
        subira self
    iherezo

    umurimo shaka(self, izina)
        subira self.amasoko.get(izina, none)
    iherezo

    umurimo shaka_ikirangwa(self)
        subira self.amasoko.get(self.ikirangwa, none)
    iherezo

    umurimo shyira_ikirangwa(self, izina)
        niba izina in self.amasoko
            self.ikirangwa = izina
        iherezo
        subira self
    iherezo

    umurimo siba(self, izina)
        niba izina in self.amasoko
            shyiramo _ = self.amasoko.pop(izina)
        iherezo
    iherezo

    umurimo kohereza_byose(self, igikorwa)
        buri izina muri self.amasoko
            self.amasoko[izina].kohereza(igikorwa)
        iherezo
    iherezo

    umurimo kubika_byose(self)
        buri izina muri self.amasoko
            self.amasoko[izina]._kubika()
        iherezo
    iherezo

    umurimo gusoma_byose(self)
        buri izina muri self.amasoko
            self.amasoko[izina].gusoma()
        iherezo
    iherezo

    umurimo uburengero(self)
        subira uburengero(self.amasoko)
    iherezo
iherezo

umurimo tangiza_ububiko(izina)
    subira UbubikoBw'Igihugu.nshya(izina)
iherezo

umurimo tangiza_gusaba_komatanya()
    subira GusabaKomatanya.nshya()
iherezo

umurimo kora_igikorwa(ubwoko, ibiciro)
    subira Igikorwa.nshya(ubwoko, ibiciro)
iherezo

shyira_ko GUSABA_KUBIKA = "gusaba_kubika"
shyira_ko GUSABA_GUSOMA = "gusaba_gusoma"
shyira_ko GUSABA_SIBA = "gusaba_siba"
