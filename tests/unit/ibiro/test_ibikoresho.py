"""Ibizamini by'Ibikoresho — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.ibikoresho.ikoresho import Ikoresho, ImiterereIkoresho, IkirangaIkoresho, ImiterereshingiroIkoresho
from ibiro.ibikoresho.buto import Buto, ButoGucunga
from ibiro.ibikoresho.ikimenyetso import Ikimenyetso
from ibiro.ibikoresho.inyandiko import Inyandiko
from ibiro.ibikoresho.ishusho import Ishusho


class TestIkoresho:
    def test_kora(self):
        ik = Ikoresho("ikizamini")
        assert ik.indangamuntu == "ikizamini"
        assert ik.imiterere == ImiterereIkoresho.KUREMWE

    def test_kongera_umwana(self):
        umubyeyi = Ikoresho("umubyeyi")
        umwana = Ikoresho("umwana")
        umubyeyi.kongera(umwana)
        assert umwana in umubyeyi.abana
        assert umwana.umubyeyi is umubyeyi

    def test_kuraho_umwana(self):
        umubyeyi = Ikoresho("umubyeyi")
        umwana = Ikoresho("umwana")
        umubyeyi.kongera(umwana)
        umubyeyi.kuraho(umwana)
        assert umwana not in umubyeyi.abana
        assert umwana.umubyeyi is None

    def test_shaka_kubw_indangamuntu(self):
        umubyeyi = Ikoresho("umubyeyi")
        umwana = Ikoresho("umwana")
        umubyeyi.kongera(umwana)
        assert umubyeyi.shaka_kubw_indangamuntu("umwana") is umwana
        assert umubyeyi.shaka_kubw_indangamuntu("ntibaho") is None


class TestButo:
    def test_kora(self):
        buto = Buto("kanda hano", indangamuntu="b1")
        assert buto.inyandiko == "kanda hano"
        assert buto.indangamuntu == "b1"

    def test_basha(self):
        buto = Buto("ikizamini")
        buto.basha()
        assert IkirangaIkoresho.NTIBISHOBOKA not in buto.ibiranga

    def test_basha_ntibishoboka(self):
        buto = Buto("ikizamini")
        buto.basha_ntibishoboka()
        assert IkirangaIkoresho.NTIBISHOBOKA in buto.ibiranga


class TestButoGucunga:
    def test_gucunga(self):
        tb = ButoGucunga("gucunga")
        assert not tb.iri_ku_mwanya
        tb.gucunga()
        assert tb.iri_ku_mwanya


class TestIkimenyetso:
    def test_kora(self):
        ik = Ikimenyetso("muraho")
        assert ik.inyandiko == "muraho"


class TestInyandiko:
    def test_kora(self):
        inv = Inyandiko("izina")
        assert inv.agaciro == ""


class TestIshusho:
    def test_kora(self):
        ish = Ishusho("ifoto.jpg")
        assert ish.inkomoko == "ifoto.jpg"
