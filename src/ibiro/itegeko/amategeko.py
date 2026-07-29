"""Amategeko — CLI commands for IBIRO.

Iki modulu gikubiyemo amategeko yose ya CLI
ya IBIRO: gushya, gupakira, kubaka, gukohereza, etc.
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import os
import sys
from typing import Any


def _andika_i() -> None:
    """Andika .i mu buryo bwo gukoresha Python."""
    if '.i' not in importlib.machinery.SOURCE_SUFFIXES:
        importlib.machinery.SOURCE_SUFFIXES.append('.i')


def kongera_iyobokamana(ibikorwa: Any) -> None:
    """Kongera iyobokamana rya ibiro CLI.

    Arguments:
        ibikorwa: Subparsers object from argparse
    """
    iyobokamana = ibikorwa.add_parser("ibiro", help="IBIRO — Urwego rwa porogaramu za desktop")

    amategeko = iyobokamana.add_subparsers(dest="itegeko_ibiro", help="Amategeko ya IBIRO")

    # isoko ibiro gushya <izina>
    gushya = amategeko.add_parser("gushya", help="Kora porogaramu nshya ya IBIRO mu .i")
    gushya.add_argument("izina", help="Izina rya porogaramu")
    gushya.add_argument("--umuyobozi", "-u", default=".", help="Umuyobozi wo gushyiramo porogaramu")

    # isoko ibiro genda <inzira.i>
    genda_cmd = amategeko.add_parser("genda", help="Genda porogaramu ya IBIRO (.i dosiye)")
    genda_cmd.add_argument("inzira", help="Inzira ya dosiye .i")

    # isoko ibiro kubaka [inzira]
    kubaka = amategeko.add_parser("kubaka", help="Kubaka porogaramu ya IBIRO")
    kubaka.add_argument("inzira", nargs="?", default=".", help="Inzira ya porogaramu")

    # isoko ibiro gupakira <imiterere>
    gupakira = amategeko.add_parser("gupakira", help="Gupakira porogaramu")
    gupakira.add_argument("imiterere", choices=["appdir", "appimage", "flatpak", "snap", "deb", "exe", "msi", "app", "dmg"], help="Imiterere y'iyubaka")

    # isoko ibiro kohereza <ahantu>
    kohereza = amategeko.add_parser("kohereza", help="Kohereza porogaramu")
    kohereza.add_argument("ahantu", help="Ahantu yo kohereza")

    # isoko ibiro isuzuma [inzira]
    isuzuma = amategeko.add_parser("isuzuma", help="Isuzuma ry'igiti cy'ibikoresho")
    isuzuma.add_argument("inzira", nargs="?", default=".", help="Inzira ya porogaramu")

    # isoko ibiro ingingo
    amategeko.add_parser("ingingo", help="Reba urutonde rw'ingingo ziboneka")

    # isoko ibiro gufasha
    amategeko.add_parser("gufasha", help="Gufasha kuri IBIRO CLI")

    iyobokamana.set_default(func=genda)


def genda(ibitekerezo: argparse.Namespace) -> int:
    """Genda itegeko rya IBIRO.

    Arguments:
        ibitekerezo: Arguments from argparse

    Returns:
        int: Kode y'isohoka (0 = neza)
    """
    itegeko = getattr(ibitekerezo, "itegeko_ibiro", None)
    if itegeko is None:
        print("IBIRO — Urwego rwa Porogaramu za Desktop v0.1.0")
        print("Koresha: isoko ibiro <itegeko> [amahitamo]")
        print("")
        print("Amategeko:")
        print("  gushya <izina>          Kora porogaramu nshya (.i)")
        print("  genda <inzira.i>        Genda porogaramu .i")
        print("  kubaka [inzira]         Kubaka porogaramu")
        print("  gupakira <imiterere>    Gupakira porogaramu")
        print("  kohereza <ahantu>       Kohereza porogaramu")
        print("  isuzuma [inzira]        Isuzuma ry'igiti")
        print("  ingingo                Reba ingingo")
        print("  gufasha                Gufasha")
        return 0

    if itegeko == "gushya":
        return _gushya(ibitekerezo.izina, ibitekerezo.umuyobozi)
    elif itegeko == "genda":
        return _genda(ibitekerezo.inzira)
    elif itegeko == "kubaka":
        print(f"Kubaka porogaramu: {ibitekerezo.inzira}")
    elif itegeko == "gupakira":
        print(f"Gupakira porogaramu nka: {ibitekerezo.imiterere}")
    elif itegeko == "kohereza":
        print(f"Kohereza porogaramu: {ibitekerezo.ahantu}")
    elif itegeko == "isuzuma":
        print(f"Isuzuma porogaramu: {ibitekerezo.inzira}")
    elif itegeko == "ingingo":
        print("Ingingo ziboneka:")
        print("  - urumuri (Light)")
        print("  - umwijima (Dark)")
        print("  - imweru_nini (High Contrast)")
    elif itegeko == "gufasha":
        print("IBIRO CLI Gufasha")
        print("Reba: isoko ibiro --help")

    return 0


def _gushya(izina: str, umuyobozi: str) -> int:
    """Kora dosiye nshya .i ya porogaramu."""
    inzira = os.path.join(umuyobozi, f"{izina}.i")
    if os.path.exists(inzira):
        print(f"Ikosa: {inzira} isanzwe ihari!")
        return 1
    try:
        os.makedirs(umuyobozi, exist_ok=True)
        with open(inzira, "w", encoding="utf-8") as f:
            f.write(f'''"""Porogaramu: {izina} — IBIRO."""

from ibiro.porogaramu import Porogaramu
from ibiro.idirishya import Idirishya
from ibiro.ibikoresho.buto import Buto
from ibiro.ibikoresho.ikimenyetso import Ikimenyetso, Umutwe
from ibiro.imiterere.inkingi import Inkingi


porogaramu = Porogaramu("{izina}", "ikigo")

idirishya = porogaramu.uyobore_idirishya.kora_idirishya(
    "nyamukuru", umutwe="{izina}",
    ubugari=800, uburebure=600
)

imiterere = Inkingi(indangamuntu="imiterere_nyamukuru")
imiterere.kongera(Umutwe("Muraho Isi!", urwego=1))
imiterere.kongera(Ikimenyetso("Iyi ni porogaramu ya {izina}"))
imiterere.kongera(Buto("Kanda", indangamuntu="buto_1",
    rikora=lambda **_: print("Buto yakandijwe!")))

idirishya.shyira_ikoresho_nyamukuru(imiterere)
idirishya.kwerekana()

porogaramu.genda()
''')
        print(f"Porogaramu {izina} yaremwe neza! -> {inzira}")
        print(f"Genda: isoko ibiro genda {inzira}")
        return 0
    except Exception as e:
        print(f"Ikosa: {e}")
        return 1


def _genda(inzira: str) -> int:
    """Genda dosiye .i ya porogaramu."""
    if not os.path.exists(inzira):
        print(f"Ikosa: {inzira} ntaboneka!")
        return 1
    if not inzira.endswith(".i"):
        print(f"Ikosa: {inzira} ntabwo ari dosiye .i!")
        return 1
    try:
        _andika_i()
        inzira_yuzuye = os.path.abspath(inzira)
        umuyobozi = os.path.dirname(inzira_yuzuye)
        if umuyobozi:
            sys.path.insert(0, umuyobozi)
        izina_modulu = os.path.splitext(os.path.basename(inzira))[0]
        spec = importlib.util.spec_from_file_location(izina_modulu, inzira_yuzuye)
        if spec is None or spec.loader is None:
            print(f"Ikosa: ntabwo shobora gutwikura {inzira}")
            return 1
        modulu = importlib.util.module_from_spec(spec)
        sys.modules[izina_modulu] = modulu
        spec.loader.exec_module(modulu)
        return 0
    except Exception as e:
        print(f"Ikosa: {e}")
        return 1
