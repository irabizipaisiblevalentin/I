"""Ibizamini by'Ibishushanyo — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.ibishushanyo.ibara import Ibara, Amabara
from ibiro.ibishushanyo.ingingo import Ingingo, UyoboreIngingo, IngingoZubatswe


class TestIbara:
    def test_kuva_hex(self):
        c = Ibara.kuva_hex("#ff0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0

    def test_kuva_rgb(self):
        c = Ibara.kuva_rgb(255, 0, 0)
        assert c.kuri_hex() == "#ff0000"

    def test_cyera(self):
        c = Amabara.CYERA
        assert c.r == 255 and c.g == 255 and c.b == 255

    def test_umukara(self):
        c = Amabara.UMUKARA
        assert c.r == 0 and c.g == 0 and c.b == 0

    def test_kuri_tuple(self):
        c = Ibara.kuva_rgb(10, 20, 30)
        t = c.kuri_tuple()
        assert t == (10, 20, 30)


class TestIngingo:
    def test_kora_urumuri(self):
        ing = UyoboreIngingo.ingingo_zubatswe(IngingoZubatswe.URUMURI)
        assert ing.izina == "urumuri"

    def test_kora_umwijima(self):
        ing = UyoboreIngingo.ingingo_zubatswe(IngingoZubatswe.UMIJIMA)
        assert ing.izina == "umijima"

    def test_shira_kiriho(self):
        ing = UyoboreIngingo.ingingo_zubatswe(IngingoZubatswe.URUMURI)
        UyoboreIngingo.shira_kiriho(ing)
        ikiriho = UyoboreIngingo.kiriho()
        assert ikiriho.izina == "urumuri"
