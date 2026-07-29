"""Ibizamini bya Muyoboro — IBIRO."""

from __future__ import annotations

import pytest

from ibiro.urwego.muyoboro import Muyoboro
from ibiro.urwego.itara import Itara
from ibiro.ibikoresho.buto import Buto


class TestMuyoboro:
    def test_kora(self):
        itara = Itara()
        buto = Buto("Kanda", indangamuntu="buto_1")
        muyoboro = Muyoboro(itara, buto)
        assert muyoboro is not None

    def test_inzira_mbere_yo_kutangiza(self):
        itara = Itara()
        buto = Buto("Kanda", indangamuntu="buto_1")
        muyoboro = Muyoboro(itara, buto)
        assert muyoboro.inzira == ""

    def test_tangiza_hagarika(self):
        itara = Itara()
        buto = Buto("Kanda", indangamuntu="buto_1")
        muyoboro = Muyoboro(itara, buto)
        igisubizo = muyoboro.tangiza()
        assert igisubizo is True
        assert muyoboro.inzira != ""
        assert "localhost" in muyoboro.inzira
        muyoboro.hagarika()

    def test_inzira_nyuma_yo_kutangiza(self):
        itara = Itara()
        buto = Buto("Kanda", indangamuntu="buto_1")
        muyoboro = Muyoboro(itara, buto)
        muyoboro.tangiza()
        inzira = muyoboro.inzira
        assert inzira.startswith("http://localhost:")
        assert inzira.endswith("/")
        muyoboro.hagarika()

    def test_rirarika_garura_int(self):
        itara = Itara()
        buto = Buto("Kanda", indangamuntu="buto_1")
        muyoboro = Muyoboro(itara, buto)
        muyoboro._irimo_gukora = False
        igisubizo = muyoboro.rirarika()
        assert isinstance(igisubizo, int)
