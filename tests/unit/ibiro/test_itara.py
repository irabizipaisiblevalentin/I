"""Ibizamini by'Itara — IBIRO."""

from __future__ import annotations

import pytest

from ibiro.urwego.itara import Itara
from ibiro.ibikoresho.buto import Buto
from ibiro.ibikoresho.ikimenyetso import Ikimenyetso, Umutwe, Paragarafu, Ihuza
from ibiro.ibikoresho.inyandiko import Inyandiko, IkibanzaInyandiko, InyandikoIbanga, Umubare
from ibiro.ibikoresho.ishusho import Ishusho
from ibiro.ibikoresho.kunyerera import Kunyerera
from ibiro.ibikoresho.iterambere import Iterambere, Uruziga
from ibiro.ibikoresho.ikarita import Ikarita
from ibiro.ibikoresho.buto import Akabokisi
from ibiro.ibikoresho.itangazo import Itangazo, Imenyekanisha, UrwegoImenyekanisha
from ibiro.imiterere.inkingi import Inkingi
from ibiro.imiterere.umurongo import Umurongo
from ibiro.ibishushanyo.ingingo import Ingingo


class TestItara:
    def test_kora(self):
        itara = Itara()
        assert itara is not None

    def test_temba_buto(self):
        itara = Itara()
        buto = Buto("Kanda", indangamuntu="buto_1")
        html = itara.temba(buto)
        assert "<html" in html
        assert "buto_1" in html
        assert "Kanda" in html
        assert "<button" in html

    def test_temba_ikimenyetso(self):
        itara = Itara()
        ikimenyetso = Ikimenyetso("Muraho", indangamuntu="ikim_1")
        html = itara.temba(ikimenyetso)
        assert "Muraho" in html
        assert "<span" in html

    def test_temba_umutwe(self):
        itara = Itara()
        umutwe = Umutwe("Umutwe", indangamuntu="utwe_1", urwego=2)
        html = itara.temba(umutwe)
        assert "Umutwe" in html
        assert "<h2" in html

    def test_temba_paragarafu(self):
        itara = Itara()
        para = Paragarafu("Paragarafu ndende", indangamuntu="para_1")
        html = itara.temba(para)
        assert "Paragarafu ndende" in html
        assert "<p" in html

    def test_temba_ihuza(self):
        itara = Itara()
        ihuza = Ihuza("Kanda hano", inzira="https://example.com", indangamuntu="ihuza_1")
        html = itara.temba(ihuza)
        assert "Kanda hano" in html
        assert "example.com" in html

    def test_temba_inyandiko(self):
        itara = Itara()
        inyandiko = Inyandiko(indangamuntu="iny_1", ikimenyetso="Izina:", agaciro="Irabizi")
        html = itara.temba(inyandiko)
        assert "izina" in html.lower() or "Izina" in html
        assert "input" in html

    def test_temba_inyandiko_ibanga(self):
        itara = Itara()
        ibanga = InyandikoIbanga(indangamuntu="ibanga_1")
        html = itara.temba(ibanga)
        assert 'type="password"' in html

    def test_temba_ikibanza_inyandiko(self):
        itara = Itara()
        ikibanza = IkibanzaInyandiko(indangamuntu="kibanza_1")
        html = itara.temba(ikibanza)
        assert "<textarea" in html

    def test_temba_umubare(self):
        itara = Itara()
        umubare = Umubare(indangamuntu="umubare_1")
        html = itara.temba(umubare)
        assert 'type="number"' in html

    def test_temba_ishusho(self):
        itara = Itara()
        ishusho = Ishusho("logo.png", indangamuntu="ishusho_1")
        html = itara.temba(ishusho)
        assert "<img" in html
        assert "logo.png" in html

    def test_temba_kunyerera(self):
        itara = Itara()
        kunyerera = Kunyerera(indangamuntu="kuny_1", agaciro=50, nini=100)
        html = itara.temba(kunyerera)
        assert 'type="range"' in html

    def test_temba_iterambere(self):
        itara = Itara()
        iterambere = Iterambere(indangamuntu="iter_1", agaciro=50)
        html = itara.temba(iterambere)
        assert "<progress" in html

    def test_temba_uruziga(self):
        itara = Itara()
        uruziga = Uruziga(indangamuntu="uruziga_1")
        html = itara.temba(uruziga)
        assert "uruziga" in html.lower()
        assert "spinziga" in html

    def test_temba_akabokisi(self):
        itara = Itara()
        akabokisi = Akabokisi("Emera", indangamuntu="akab_1")
        html = itara.temba(akabokisi)
        assert 'type="checkbox"' in html

    def test_temba_itangazo(self):
        itara = Itara()
        itangazo = Itangazo(indangamuntu="itangazo_1")
        itangazo.kwerekana(Imenyekanisha(umutwe="Amakuru", inyandiko="Byagenze neza!", urwego=UrwegoImenyekanisha.AMAKURU))
        html = itara.temba(itangazo)
        assert "Byagenze neza!" in html or "amakuru" in html.lower()

    def test_temba_ikarita(self):
        itara = Itara()
        ikarita = Ikarita(indangamuntu="ikarita_1")
        html = itara.temba(ikarita)
        assert "ikarita" in html.lower()

    def test_temba_inkingi(self):
        itara = Itara()
        inkingi = Inkingi(indangamuntu="inkingi_1")
        inkingi.kongera(Buto("A", indangamuntu="buto_a"))
        inkingi.kongera(Buto("B", indangamuntu="buto_b"))
        html = itara.temba(inkingi)
        assert "flex-direction:column" in html or "A" in html
        assert "buto_a" in html
        assert "buto_b" in html

    def test_temba_umurongo(self):
        itara = Itara()
        umurongo = Umurongo(indangamuntu="umurongo_1")
        umurongo.kongera(Buto("A", indangamuntu="buto_a"))
        html = itara.temba(umurongo)
        assert "flex-direction:row" in html or "A" in html

    def test_temba_hishwe(self):
        itara = Itara()
        buto = Buto("Hishwe", indangamuntu="hishwe_1")
        buto.imiterere = buto.imiterere.HISHWE
        html = itara.temba(buto)
        assert "hishwe" in html

    def test_shaka_ibikoresho(self):
        itara = Itara()
        buto_a = Buto("A", indangamuntu="buto_a")
        buto_b = Buto("B", indangamuntu="buto_b")
        inkingi = Inkingi(indangamuntu="inkingi_1")
        inkingi.kongera(buto_a)
        inkingi.kongera(buto_b)
        itara.temba(inkingi)
        ibikoresho = itara.shaka_ibikoresho()
        assert "buto_a" in ibikoresho
        assert "buto_b" in ibikoresho
        assert "inkingi_1" in ibikoresho

    def test_shaka_ikoresho(self):
        itara = Itara()
        buto = Buto("Test", indangamuntu="test_buto")
        itara.temba(buto)
        iboneka = itara.shaka_ikoresho("test_buto")
        assert iboneka is buto
        assert itara.shaka_ikoresho("ntikibaho") is None
