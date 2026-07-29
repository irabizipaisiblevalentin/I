"""Ibizamini by'Ubuzimagange — IBIRO."""

from __future__ import annotations

import pytest
from ibiro.ibishushanyo.ubuzimagange import Ubuzimagange, UmurongoUbuzimagange, ItsindaUbuzimagange, MoteriUbuzimagange


class TestUbuzimagange:
    def test_kora(self):
        ubu = Ubuzimagange(
            indangamuntu_igikoresho="ikoresho1",
            umutungo="x",
            kuva=0.0,
            kugeza=100.0,
            igihe=1.0,
        )
        assert ubu.indangamuntu_igikoresho == "ikoresho1"
        assert ubu.umutungo == "x"
        assert ubu.kuva == 0.0
        assert ubu.kugeza == 100.0

    def test_umurongo_mburabura(self):
        ubu = Ubuzimagange(
            indangamuntu_igikoresho="w",
            umutungo="x",
            kuva=0.0,
            kugeza=100.0,
            igihe=1.0,
        )
        assert ubu.umurongo == UmurongoUbuzimagange.LINEARI


class TestItsindaUbuzimagange:
    def test_kongera(self):
        its = ItsindaUbuzimagange()
        ubu = Ubuzimagange(indangamuntu_igikoresho="w", umutungo="x", kuva=0.0, kugeza=100.0, igihe=1.0)
        its.kongera(ubu)
        assert len(its.ubuzimagange) == 1


class TestMoteriUbuzimagange:
    def test_kora(self):
        mot = MoteriUbuzimagange()
        assert mot is not None

    def test_gucuranga(self):
        mot = MoteriUbuzimagange()
        ubu = Ubuzimagange(indangamuntu_igikoresho="w", umutungo="x", kuva=0.0, kugeza=100.0, igihe=0.01)
        mot.gucuranga(ubu)
        assert len(mot._iruka) == 1
