"""IBIRO — Urwego rwa Porogaramu za Desktop.

IBIRO (I-BI-RO: "kureba") ni urwego rwa porogaramu za desktop
rwubatswe ku rurimi rwa I. Ritanga ibikoresho byo kubaka porogaramu
za desktop zikoresha amadirishya, ibikoresho, n'imiterere.
"""

from __future__ import annotations

import importlib.machinery
if '.i' not in importlib.machinery.SOURCE_SUFFIXES:
    importlib.machinery.SOURCE_SUFFIXES.append('.i')

from ibiro.porogaramu import Porogaramu
from ibiro.idirishya import Idirishya, UyoboreIdirishya, ImiterereIdirishya, UburyoIdirishya

umubare_verisiyo = "0.1.0"

ibyoherezwa = ["Porogaramu", "Idirishya", "UyoboreIdirishya"]
