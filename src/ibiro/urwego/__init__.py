"""Urwego — Urwego rwa porogaramu (platform).

Iki modulu gikubiyemo inyuma ya porogaramu
(platform backends), itara (HTML renderer),
na muyoboro (main loop bridge).
"""

from ibiro.urwego.shingiro import Inyuma
from ibiro.urwego.menya import menya_urwego, kora_inyuma
from ibiro.urwego.windows import InyumaWindows
from ibiro.urwego.linux import InyumaLinux
from ibiro.urwego.darwin import InyumaDarwin
from ibiro.urwego.umutwe import InyumaUmutwe
from ibiro.urwego.itara import Itara
from ibiro.urwego.muyoboro import Muyoboro
