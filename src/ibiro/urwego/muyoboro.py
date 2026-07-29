"""Muyoboro — Main loop bridge (HTTP server + browser).

Itangiza seriveri ya HTTP, ifungura urupapuro mu mushakisha,
kandi igakora mainloop ya porogaramu.
"""

from __future__ import annotations

import json
import webbrowser
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional, Callable

from ibiro.urwego.itara import Itara
from ibiro.ibikoresho.ikoresho import Ikoresho


class _UbutumwaBwItara(BaseHTTPRequestHandler):
    """Ubutumwa bw'itara — HTTP handler for IBIRO."""

    _itara: Itara = None
    _ku_ikintu: Optional[Callable] = None

    def do_HEAD(ibi):
        ibi.send_response(200)
        ibi.send_header("Content-Type", "text/html; charset=utf-8")
        ibi.end_headers()

    def do_GET(ibi):
        ibi.send_response(200)
        ibi.send_header("Content-Type", "text/html; charset=utf-8")
        ibi.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        ibi.end_headers()
        if ibi._itara:
            html = ibi._itara.temba(ibi._itara._ikoresho_nyamukuru)
            ibi.wfile.write(html.encode("utf-8"))
        else:
            ibi.wfile.write(b"<html><body><p>Itara ntiratangijwe</p></body></html>")

    def do_POST(ibi):
        uburebure = int(ibi.headers.get("Content-Length", 0))
        amakuru = {}
        if uburebure > 0:
            amakuru = json.loads(ibi.rfile.read(uburebure))
        indangamuntu = amakuru.get("indangamuntu", "")
        ubwoko = amakuru.get("ubwoko", "")
        data = amakuru.get("amakuru", {})

        igisubizo = {"kibyemejwe": False, "kuvuguruza": False}
        if ibi._ku_ikintu and indangamuntu and ubwoko:
            igisubizo = ibi._ku_ikintu(indangamuntu, ubwoko, data)

        ibi.send_response(200)
        ibi.send_header("Content-Type", "application/json")
        ibi.end_headers()
        ibi.wfile.write(json.dumps(igisubizo).encode("utf-8"))

    def log_message(ibi, umurongo: str, *amakuru: Any):
        pass


class Muyoboro:
    """Muyoboro — Main loop bridge.

    Itangiza seriveri HTTP, ifungura urupapuro mu mushakisha,
    kandi igakora mainloop ya porogaramu.
    """

    _itara: Itara
    _ikoresho_nyamukuru: Ikoresho
    _seriveri: Optional[HTTPServer]
    _urugori: Optional[threading.Thread]
    _irimo_gukora: bool
    _ipaki: int

    def __init__(ibi: "Muyoboro", itara: Itara, ikoresho: Ikoresho, ipaki: int = 0):
        ibi._itara = itara
        ibi._ikoresho_nyamukuru = ikoresho
        ibi._seriveri = None
        ibi._urugori = None
        ibi._irimo_gukora = False
        ibi._ipaki = ipaki
        itara._ikoresho_nyamukuru = ikoresho

    @property
    def inzira(ibi: "Muyoboro") -> str:
        """Shaka URL ya seriveri."""
        if ibi._seriveri:
            return f"http://localhost:{ibi._seriveri.server_port}/"
        return ""

    def tangiza(ibi: "Muyoboro") -> bool:
        """Tangiza seriveri ya HTTP."""
        if ibi._seriveri:
            return True
        try:
            _UbutumwaBwItara._itara = ibi._itara
            _UbutumwaBwItara._ku_ikintu = ibi._ku_ikintu

            ibi._seriveri = HTTPServer(("127.0.0.1", ibi._ipaki or 0), _UbutumwaBwItara)
            if ibi._ipaki == 0:
                ibi._ipaki = ibi._seriveri.server_port

            ibi._urugori = threading.Thread(target=ibi._seriveri.serve_forever, daemon=True)
            ibi._urugori.start()
            ibi._irimo_gukora = True

            webbrowser.open(ibi.inzira)
            return True
        except Exception:
            ibi._seriveri = None
            ibi._urugori = None
            ibi._irimo_gukora = False
            return False

    def _ku_ikintu(ibi: "Muyoboro", indangamuntu: str, ubwoko: str, amakuru: Dict[str, Any]) -> Dict[str, Any]:
        """Kora ikintu cyatererejwe na JavaScript."""
        ikoresho = ibi._itara.shaka_ikoresho(indangamuntu)
        if ikoresho:
            ikoresho.tereza(ubwoko, **amakuru)
            return {"kibyemejwe": True, "kuvuguruza": True}
        return {"kibyemejwe": False, "kuvuguruza": False}

    def rirarika(ibi: "Muyoboro") -> int:
        """Rirarika mainloop — garagara kugeza seriveri ihagaze."""
        try:
            while ibi._irimo_gukora:
                threading.Event().wait(0.1)
        except KeyboardInterrupt:
            pass
        return 0

    def hagarika(ibi: "Muyoboro") -> None:
        """Hagarika seriveri."""
        ibi._irimo_gukora = False
        if ibi._seriveri:
            ibi._seriveri.shutdown()
            ibi._seriveri.server_close()
            ibi._seriveri = None
