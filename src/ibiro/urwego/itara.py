"""Itara — Widget tree → HTML renderer."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set

from ibiro.ibikoresho.ikoresho import Ikoresho, ImiterereIkoresho, IkirangaIkoresho, ImiterereshingiroIkoresho
from ibiro.ibikoresho.buto import Buto, ButoGucunga, ButoRadiyo, Akabokisi
from ibiro.ibikoresho.ikimenyetso import Ikimenyetso, Umutwe, Paragarafu, Ihuza
from ibiro.ibikoresho.inyandiko import Inyandiko, IkibanzaInyandiko, InyandikoIbanga, Umubare
from ibiro.ibikoresho.imbonerahamwe import Imbonerahamwe
from ibiro.ibikoresho.igiti import Igiti
from ibiro.ibikoresho.urutonde import Urutonde
from ibiro.ibikoresho.ishusho import Ishusho
from ibiro.ibikoresho.kunyerera import Kunyerera
from ibiro.ibikoresho.iterambere import Iterambere, Uruziga
from ibiro.ibikoresho.ikarita import Ikarita
from ibiro.ibikoresho.ikiganiro import Ikiganiro
from ibiro.ibikoresho.ifishi import Ifishi
from ibiro.ibikoresho.igikanya import Igikanya
from ibiro.ibikoresho.itangazo import Itangazo
from ibiro.ibikoresho.umweru import Umweru
from ibiro.ibikoresho.ibikoresho import UrutondeIbikoresho, Igikoresho
from ibiro.ibikoresho.ikibaho import Ikibaho
from ibiro.ibikoresho.uruhande import Uruhande
from ibiro.imiterere.shingiro import Imiterere, Guringaniza, Icyerekezo
from ibiro.imiterere.umurongo import Umurongo
from ibiro.imiterere.inkingi import Inkingi
from ibiro.imiterere.urusenya import Urusenya
from ibiro.imiterere.ikirundo import Ikirundo
from ibiro.imiterere.gufunga import Gufunga
from ibiro.imiterere.gukuza import Gukuza
from ibiro.imiterere.gutandukanya import Gutandukanya
from ibiro.ibishushanyo.ibara import Ibara, Amabara
from ibiro.ibishushanyo.ingingo import Ingingo, UyoboreIngingo, IngingoZubatswe


class Itara:
    """Itara — Renders widget tree to HTML with embedded CSS/JS.

    Transform the Igiti cy'ibikoresho into HTML.
    """

    _ingingo: Optional[Ingingo]
    _ibikoresho_byose: Dict[str, Ikoresho]
    _umubare_ibikoresho: int

    def __init__(ibi: "Itara"):
        ibi._ingingo = None
        ibi._ibikoresho_byose = {}
        ibi._umubare_ibikoresho = 0

    def shira_ingingo(ibi: "Itara", ingingo: Ingingo) -> None:
        ibi._ingingo = ingingo

    def temba(ibi: "Itara", ikoresho: Ikoresho) -> str:
        """Temba igikoresho n'abana baryo maze ubereke HTML."""
        ibi._ibikoresho_byose.clear()
        ibi._umubare_ibikoresho = 0
        indangamuntu = ikoresho.indangamuntu or "ikoresho_nyamukuru"
        html_igikoresho = ibi._temba(ikoresho)
        ingingo = ibi._ingingo or UyoboreIngingo.ingingo_zubatswe(IngingoZubatswe.URUMURI)
        ibara_ibara = "#0078d4"
        return f"""<!DOCTYPE html>
<html lang="rw">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>IBIRO — {indangamuntu}</title>
{ibi._mitere(ingingo)}
</head>
<body>
<div id="ibiro-igiti" data-indangamuntu="{indangamuntu}">
{html_igikoresho}
</div>
{ibi._inkoranyigama(ibara_ibara)}
</body>
</html>"""

    def _temba(ibi: "Itara", ikoresho: Ikoresho) -> str:
        """Temba igikoresho kimwe n'abana baryo."""
        ibi._umubare_ibikoresho += 1
        ubwoko = type(ikoresho).__name__
        indangamuntu = ikoresho.indangamuntu or f"ikoresho_{ibi._umubare_ibikoresho}"
        ibi._ibikoresho_byose[indangamuntu] = ikoresho

        nubwo = ikoresho.imiterere == ImiterereIkoresho.HISHWE
        ntibishoboka = IkirangaIkoresho.NTIBISHOBOKA in ikoresho.ibiranga
        ibiranga_klasi = "hishwe" if nubwo else ""

        klasi = f"ibiro-{ubwoko.lower()} {ibiranga_klasi}"
        mitere = ibi._mitere_igikoresho(ikoresho)
        ibintu_byihariye = ibi._ibintu_byihariye(ikoresho)

        style_attrib = f' style="{mitere}"' if mitere else ""
        disabled_attrib = ' disabled' if ntibishoboka else ""

        html = f'<div class="{klasi}" id="{indangamuntu}"{style_attrib}{disabled_attrib}>'

        ibintu = ibi._temba_ibintu(ikoresho, indangamuntu)
        html += ibintu if ibintu else ""

        if ikoresho.abana:
            for umwana in ikoresho.abana:
                html += ibi._temba(umwana)

        html += "</div>"
        return html

    def _ibintu_byihariye(ibi: "Itara", ikoresho: Ikoresho) -> Dict[str, Any]:
        """Shaka ibintu byihariye by'igikoresho (inyandiko, agaciro, etc.)."""
        ibintu = {}
        if isinstance(ikoresho, (Buto, ButoGucunga)):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
        if isinstance(ikoresho, Ikimenyetso):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
        if isinstance(ikoresho, Umutwe):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
            ibintu["urwego"] = getattr(ikoresho, "urwego", 1)
        if isinstance(ikoresho, Paragarafu):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
        if isinstance(ikoresho, Ihuza):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
            ibintu["inzira"] = getattr(ikoresho, "inzira", "")
        if isinstance(ikoresho, (Inyandiko, InyandikoIbanga)):
            ibintu["agaciro"] = getattr(ikoresho, "agaciro", "")
            ibintu["ikimenyetso"] = getattr(ikoresho, "ikimenyetso", "")
        if isinstance(ikoresho, IkibanzaInyandiko):
            ibintu["agaciro"] = getattr(ikoresho, "agaciro", "")
        if isinstance(ikoresho, Umubare):
            ibintu["agaciro"] = getattr(ikoresho, "agaciro", 0)
        if isinstance(ikoresho, Akabokisi):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
            ibintu["ikemye"] = getattr(ikoresho, "ikemye", False)
        if isinstance(ikoresho, ButoRadiyo):
            ibintu["inyandiko"] = getattr(ikoresho, "inyandiko", "")
            ibintu["ihitamo"] = getattr(ikoresho, "ihitamo", False)
        if isinstance(ikoresho, Kunyerera):
            ibintu["agaciro"] = getattr(ikoresho, "agaciro", 50)
            ibintu["nini"] = getattr(ikoresho, "nini", 100)
        if isinstance(ikoresho, Iterambere):
            ibintu["agaciro"] = getattr(ikoresho, "agaciro", 0)
        if isinstance(ikoresho, Ishusho):
            ibintu["inkomoko"] = getattr(ikoresho, "inkomoko", "")
            ibintu["ubugari"] = getattr(ikoresho, "ubugari", 0)
            ibintu["uburebure"] = getattr(ikoresho, "uburebure", 0)
        if isinstance(ikoresho, Ikarita):
            ikarita_umutwe = getattr(ikoresho, "umutwe", None)
            if ikarita_umutwe:
                ibintu["umutwe_inyandiko"] = getattr(ikarita_umutwe, "inyandiko", "") if hasattr(ikarita_umutwe, "inyandiko") else ""
        if isinstance(ikoresho, Itangazo):
            ibintu["ubwoko"] = getattr(ikoresho, "ubwoko", "amakuru")
            ibintu["ubutumwa"] = getattr(ikoresho, "ubutumwa", "")
        if isinstance(ikoresho, Umweru):
            ibintu["indangamuntu_ukurikira"] = getattr(ikoresho, "indangamuntu_ukurikira", "")
        return ibintu

    def _temba_ibintu(ibi: "Itara", ikoresho: Ikoresho, indangamuntu: str) -> str:
        """Temba ibintu byihariye by'igikoresho nk'HTML."""
        html = ""
        if isinstance(ikoresho, Buto):
            html += f"<button class=\"ibiro-buto-input\" data-indangamuntu=\"{indangamuntu}\">{ikoresho.inyandiko}</button>"
        elif isinstance(ikoresho, ButoGucunga):
            ikemye = ' checked' if ikoresho.iri_ku_mwanya else ""
            html += f"<label class=\"ibiro-gucunga\"><input type=\"checkbox\"{ikemye} data-indangamuntu=\"{indangamuntu}\"> {ikoresho.inyandiko}</label>"
        elif isinstance(ikoresho, Akabokisi):
            ikemye = ' checked' if ikoresho.ikemye else ""
            html += f"<label class=\"ibiro-akabokisi\"><input type=\"checkbox\"{ikemye} data-indangamuntu=\"{indangamuntu}\"> {ikoresho.inyandiko}</label>"
        elif isinstance(ikoresho, ButoRadiyo):
            ihitamo = ' checked' if ikoresho.ihitamo else ""
            html += f"<label class=\"ibiro-radiyo\"><input type=\"radio\"{ihitamo} data-indangamuntu=\"{indangamuntu}\"> {ikoresho.inyandiko}</label>"
        elif isinstance(ikoresho, Ikimenyetso):
            html += f"<span class=\"ibiro-ikimenyetso\">{ikoresho.inyandiko}</span>"
        elif isinstance(ikoresho, Umutwe):
            urwego = min(max(ikoresho.urwego, 1), 6)
            html += f"<h{urwego} class=\"ibiro-umutwe\">{ikoresho.inyandiko}</h{urwego}>"
        elif isinstance(ikoresho, Paragarafu):
            html += f"<p class=\"ibiro-paragarafu\">{ikoresho.inyandiko}</p>"
        elif isinstance(ikoresho, Ihuza):
            html += f"<a class=\"ibiro-ihuza\" href=\"{ikoresho.inzira}\" data-indangamuntu=\"{indangamuntu}\">{ikoresho.inyandiko}</a>"
        elif isinstance(ikoresho, Inyandiko):
            ikimenyetso = getattr(ikoresho, "ikimenyetso", "")
            agaciro = getattr(ikoresho, "agaciro", "")
            label = f"<label class=\"ibiro-ikimenyetso-inyandiko\">{ikimenyetso}</label>" if ikimenyetso else ""
            html += f"""{label}<input type="text" class="ibiro-inyandiko" value="{agaciro}" data-indangamuntu="{indangamuntu}">"""
        elif isinstance(ikoresho, InyandikoIbanga):
            agaciro = getattr(ikoresho, "agaciro", "")
            html += f"""<input type="password" class="ibiro-inyandiko-ibanga" value="{agaciro}" data-indangamuntu="{indangamuntu}">"""
        elif isinstance(ikoresho, IkibanzaInyandiko):
            agaciro = getattr(ikoresho, "agaciro", "")
            html += f"""<textarea class="ibiro-ikibanza-inyandiko" data-indangamuntu="{indangamuntu}">{agaciro}</textarea>"""
        elif isinstance(ikoresho, Umubare):
            agaciro = getattr(ikoresho, "agaciro", 0)
            html += f"""<input type="number" class="ibiro-umubare" value="{agaciro}" data-indangamuntu="{indangamuntu}">"""
        elif isinstance(ikoresho, Ishusho):
            inzira = getattr(ikoresho, "inkomoko", "")
            ubugari = getattr(ikoresho, "ubugari", 0)
            uburebure = getattr(ikoresho, "uburebure", 0)
            style = ""
            if ubugari:
                style += f" width:{ubugari}px;"
            if uburebure:
                style += f" height:{uburebure}px;"
            inyandiko_mburabura = "Ishusho"
            html += f"""<img class="ibiro-ishusho" src="{inzira}" alt="{inyandiko_mburabura}"{(' style="' + style.strip() + '"') if style else ''}>"""
        elif isinstance(ikoresho, Kunyerera):
            agaciro = getattr(ikoresho, "agaciro", 50)
            nini = getattr(ikoresho, "nini", 100)
            html += f"""<input type="range" class="ibiro-kunyerera" min="0" max="{nini}" value="{agaciro}" data-indangamuntu="{indangamuntu}">"""
        elif isinstance(ikoresho, Iterambere):
            agaciro = getattr(ikoresho, "agaciro", 0)
            html += f"""<progress class="ibiro-iterambere" value="{agaciro}" max="100"></progress>"""
        elif isinstance(ikoresho, Uruziga):
            html += """<div class="ibiro-uruziga"><div class="ibiro-uruziga-umuzinga"></div></div>"""
        elif isinstance(ikoresho, Ihuza):
            html += f"""<a class="ibiro-ihuza" href="#" data-indangamuntu="{indangamuntu}">{getattr(ikoresho, "inyandiko", "Ihuza")}</a>"""
        elif isinstance(ikoresho, Ikarita):
            html += ""
        elif isinstance(ikoresho, Itangazo):
            ubwoko = getattr(ikoresho, "ubwoko", "amakuru")
            ubutumwa = getattr(ikoresho, "ubutumwa", "")
            urwego_klasi = ubwoko.lower() if ubwoko else "amakuru"
            html += f"""<div class="ibiro-itangazo {urwego_klasi}">{ubutumwa}</div>"""
        return html

    def _mitere_igikoresho(ibi: "Itara", ikoresho: Ikoresho) -> str:
        """Hindura imiterereshingiro ya CSS."""
        imit = ikoresho.imiterereshingiro
        styles: List[str] = []
        if imit.ibara_inyuma and imit.ibara_inyuma != "imyeyere" and imit.ibara_inyuma != "transparent":
            styles.append(f"background-color:{ibi._hindura_ibara(imit.ibara_inyuma)}")
        if imit.ibara_imbere and imit.ibara_imbere != "#000000":
            styles.append(f"color:{ibi._hindura_ibara(imit.ibara_imbere)}")
        if imit.ubugari_umupaka > 0:
            ibara_umupaka = ibi._hindura_ibara(imit.ibara_umupaka) if imit.ibara_umupaka != "imyeyere" else "#ccc"
            styles.append(f"border:{imit.ubugari_umupaka}px solid {ibara_umupaka}")
        if imit.uruziga > 0:
            styles.append(f"border-radius:{imit.uruziga}px")
        if imit.impande > 0:
            styles.append(f"padding:{imit.impande}px")

        if isinstance(ikoresho, Imiterere):
            if hasattr(ikoresho, "icyerekezo") and ikoresho.icyerekezo == Icyerekezo.HORIZONTAL:
                styles.append("display:flex;flex-direction:row")
            else:
                styles.append("display:flex;flex-direction:column")
            if isinstance(ikoresho, Gukuza):
                styles.append("overflow:auto")
            if isinstance(ikoresho, Gutandukanya):
                styles.append("flex:1")
            if isinstance(ikoresho, Gufunga):
                styles.append("position:relative")

        if isinstance(ikoresho, Ikirundo):
            styles.append("display:flex;flex-direction:column;position:relative")
        if isinstance(ikoresho, Urusenya):
            styles.append("display:grid")
        if isinstance(ikoresho, Ishusho):
            ubugari = getattr(ikoresho, "ubugari", 0)
            uburebure = getattr(ikoresho, "uburebure", 0)
            if ubugari:
                styles.append(f"width:{ubugari}px")
            if uburebure:
                styles.append(f"height:{uburebure}px")
        if isinstance(ikoresho, Uruziga):
            styles.append("display:flex;align-items:center;justify-content:center")

        return ";".join(styles)

    def _hindura_ibara(ibi: "Itara", ibara: str) -> str:
        """Hindura izina ry'ibara kuri CSS."""
        if ibara in ("imyeyere", "transparent"):
            return "transparent"
        if ibara.startswith("#") or ibara.startswith("rgb") or ibara.startswith("hsl"):
            return ibara
        amabara_nzita = {
            "umukara": "#000000", "umweru": "#ffffff", "umutuku": "#ff0000",
            "icyatsi": "#00ff00", "ubururu": "#0000ff", "umuhondo": "#ffff00",
            "ikigina": "#ff00ff", "umusemburo": "#00ffff", "ijeri": "#808080",
            "ijeri_ibijyejuru": "#a0a0a0", "ijeri_ijimye": "#606060",
            "ikijyejuru": "#87ceeb", "ikijyejuru_ijimye": "#4682b4",
            "icyatsi_kibisi": "#90ee90", "icyatsi_ijimye": "#228b22",
            "umutuku_wijimye": "#8b0000", "umuhondo_wijimye": "#bdb76b",
        }
        return amabara_nzita.get(ibara.lower(), ibara)

    def _mitere(ibi: "Itara", ingingo: Optional[Ingingo]) -> str:
        """Tanga CSS mitere ya porogaramu."""
        ibara_ibanze = "#0078d4"
        ibara_inyuma = "#ffffff"
        ibara_imbere = "#000000"
        if ingingo:
            ibara_ibanze = getattr(ingingo, "ibara_byibanze", ibara_ibanze)
            ibara_inyuma = getattr(ingingo, "ibara_inyuma", ibara_inyuma)
            ibara_imbere = getattr(ingingo, "ibara_imbere", ibara_imbere)
        return f"""<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
       background:{ibara_inyuma}; color:{ibara_imbere}; }}
#ibiro-igiti {{ width:100%; min-height:100vh; display:flex; flex-direction:column; }}
button, input, textarea, select {{ font-family:inherit; font-size:inherit; }}
button {{ cursor:pointer; padding:8px 16px; border:1px solid #ccc;
         border-radius:4px; background:{ibara_ibanze}; color:#fff; }}
button:hover {{ filter:brightness(1.1); }}
button:disabled {{ opacity:0.5; cursor:default; }}
input[type="text"], input[type="password"], input[type="number"], textarea {{
  padding:6px 10px; border:1px solid #ccc; border-radius:4px; width:100%; }}
textarea {{ min-height:80px; resize:vertical; }}
input[type="range"] {{ width:100%; }}
progress {{ width:100%; height:8px; border-radius:4px; }}
table {{ border-collapse:collapse; width:100%; }}
th, td {{ border:1px solid #ddd; padding:6px 10px; text-align:left; }}
th {{ background:#f5f5f5; }}
a {{ color:{ibara_ibanze}; text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.hishwe {{ display:none !important; }}
.ibiro-buto-input {{ margin:4px; }}
.ibiro-ikarita {{ border:1px solid #e0e0e0; border-radius:8px; padding:16px;
                 margin:8px; background:#fff; box-shadow:0 2px 4px rgba(0,0,0,0.1); }}
.ibiro-itangazo.amakuru {{ background:#d4edda; color:#155724; padding:12px; border-radius:4px; margin:8px; }}
.ibiro-itangazo.ikosa {{ background:#f8d7da; color:#721c24; padding:12px; border-radius:4px; margin:8px; }}
.ibiro-itangazo.icyitonderwa {{ background:#fff3cd; color:#856404; padding:12px; border-radius:4px; margin:8px; }}
.ibiro-uruziga {{ display:inline-block; width:24px; height:24px; }}
.ibiro-uruziga-umuzinga {{ width:100%; height:100%; border:3px solid #f3f3f3;
  border-top:3px solid {ibara_ibanze}; border-radius:50%; animation:spinziga 0.8s linear infinite; }}
@keyframes spinziga {{ to {{ transform:rotate(360deg); }} }}
</style>"""

    def _inkoranyigama(ibi: "Itara", ibara_ibanze: str) -> str:
        """Tanga JavaScript inkoranyigama."""
        return f"""<script>
(function(){{
const ibiro = {{
  ibikoresho: {{}},
  shaka: function(id) {{ return document.getElementById(id); }},
  ikintu: function(indangamuntu, ubwoko, amakuru) {{
    fetch('/_ikintu', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{indangamuntu:indangamuntu, ubwoko:ubwoko, amakuru:amakuru||{{}}}})
    }}).then(function(r){{return r.json()}}).then(function(d) {{
      if(d.kuvuguruza) location.reload();
    }});
  }}
}};
document.addEventListener('click', function(e) {{
  var t = e.target.closest('[data-indangamuntu]');
  if(!t) return;
  var id = t.getAttribute('data-indangamuntu');
  var tag = t.tagName.toLowerCase();
  if(tag==='button'||tag==='a') {{
    e.preventDefault();
    ibiro.ikintu(id, 'gukanda', {{}});
  }}
}});
document.addEventListener('change', function(e) {{
  var t = e.target.closest('[data-indangamuntu]');
  if(!t) return;
  var id = t.getAttribute('data-indangamuntu');
  if(t.type==='checkbox'||t.type==='radio') {{
    ibiro.ikintu(id, 'gucunga', {{agaciro:t.checked}});
  }}
}});
document.addEventListener('input', function(e) {{
  var t = e.target.closest('[data-indangamuntu]');
  if(!t) return;
  var id = t.getAttribute('data-indangamuntu');
  if(t.tagName==='INPUT'||t.tagName==='TEXTAREA') {{
    ibiro.ikintu(id, 'hinduka', {{agaciro:t.value}});
  }}
}});
}})();
</script>"""

    def shaka_ibikoresho(ibi: "Itara") -> Dict[str, Ikoresho]:
        """Shaka urutonde rw'ibikoresho byose."""
        return dict(ibi._ibikoresho_byose)

    def shaka_ikoresho(ibi: "Itara", indangamuntu: str) -> Optional[Ikoresho]:
        """Shaka igikoresho kimwe ku indangamuntu yaryo."""
        return ibi._ibikoresho_byose.get(indangamuntu)

    def kuvuguruza(ibi: "Itara", ikoresho: Ikoresho) -> bool:
        """Menyesha itara ko igikoresho cyahindutse."""
        return True
