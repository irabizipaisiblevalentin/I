"""Urugero: Porogaramu y'inyandiko mu .i dosiye."""

from ibiro.porogaramu import Porogaramu
from ibiro.idirishya import Idirishya
from ibiro.ibikoresho.buto import Buto
from ibiro.ibikoresho.ikimenyetso import Ikimenyetso, Umutwe
from ibiro.ibikoresho.inyandiko import Inyandiko
from ibiro.imiterere.inkingi import Inkingi
from ibiro.imiterere.umurongo import Umurongo


porogaramu = Porogaramu("InyandikoYanjye", "ikizamini.rw")

idirishya = porogaramu.uyobore_idirishya.kora_idirishya(
    "nyamukuru", umutwe="InyandikoYanjye",
    ubugari=800, uburebure=600
)

imiterere = Inkingi(indangamuntu="imiterere_nyamukuru")

umutwe = Umutwe("Muraho Neza!", urwego=1)
imiterere.kongera(umutwe)

ikimenyetso = Ikimenyetso("Iyi ni porogaramu y'inyandiko ya IBIRO mu .i dosiye")
imiterere.kongera(ikimenyetso)

umurongo_buto = Umurongo(indangamuntu="imirongo_buto")

buto_kubika = Buto("Kubika", indangamuntu="kubika",
    rikora=lambda **_: print("Porogaramu irabikwa!"))
umurongo_buto.kongera(buto_kubika)

imiterere.kongera(umurongo_buto)

idirishya.shyira_ikoresho_nyamukuru(imiterere)
idirishya.kwerekana()

porogaramu.genda()
