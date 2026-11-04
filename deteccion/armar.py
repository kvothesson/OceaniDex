"""Junta los avistajes leidos de la transcripcion en las fichas que muestra la web.

python deteccion/armar.py juntar   avistajes_*.json -> avistajes.json (para sacar las fotos)
python deteccion/armar.py fichas   avistajes.json + hud.json + perfil.json -> oceanidex.json

Los avistajes_N.json los escribe un modelo leyendo cada tramo de la transcripcion
(ver deteccion/LEEME.md). Aca no se decide que es un organismo: solo se ordena y se agrupa.
"""
import csv
import json
import shutil
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DET = RAIZ / "deteccion"
CONFIANZA_MINIMA = 0.5
RANGOS = ["filo", "clase", "orden", "familia", "genero", "especie"]
# Distintos tramos nombran igual al mismo bicho de formas distintas.
SINONIMOS = {
    "coral primnoideo": "coral primnoide", "primnoideo": "coral primnoide",
    "picnogonido": "araña de mar", "isopodo valvifero": "isópodo",
    "gusano poliqueto": "poliqueto", "remolacha de mar": "remolacha",
}


def seg(t):
    h, m, s = (int(x) for x in t.split(":"))
    return h * 3600 + m * 60 + s


def clave(nombre):
    sin = unicodedata.normalize("NFD", nombre.lower().strip())
    return "".join(c for c in sin if unicodedata.category(c) != "Mn")


def juntar():
    todos = []
    for f in sorted(DET.glob("avistajes_[0-9]*.json")):
        todos += json.loads(f.read_text(encoding="utf-8"))
    buenos = sorted((a for a in todos if a.get("confianza", 0) >= CONFIANZA_MINIMA), key=lambda a: seg(a["t"]))
    for a in buenos:
        a["nombre"] = SINONIMOS.get(clave(a["nombre"]), a["nombre"])
    (DET / "avistajes.json").write_text(json.dumps(buenos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(todos), "leidos,", len(buenos), "con confianza >=", CONFIANZA_MINIMA)


PORTADAS = {}
for _f in sorted(DET.glob("portadas_[0-9]*.json")):
    PORTADAS.update(json.loads(_f.read_text(encoding="utf-8")))


def limpiar_perfil(perfil):
    """El OCR a veces suma o come un digito (24804, 443): se descarta lo que se aleja de sus vecinos."""
    puntos = sorted([seg(t), d["depth"]] for t, d in perfil.items() if d.get("depth"))
    buenos = []
    for i, (s, d) in enumerate(puntos):
        vecinos = sorted(p[1] for p in puntos[max(i - 3, 0):i + 4] if p is not puntos[i])
        if vecinos and abs(d - vecinos[len(vecinos) // 2]) < 60:
            buenos.append([s, d])
    return buenos


def interpolar(curva, s):
    for (s0, d0), (s1, d1) in zip(curva, curva[1:]):
        if s0 <= s <= s1:
            return d0 + (d1 - d0) * (s - s0) / (s1 - s0)
    return curva[0][1] if s < curva[0][0] else curva[-1][1]


def fichas():
    avistajes = json.loads((DET / "avistajes.json").read_text(encoding="utf-8"))
    hud = json.loads((DET / "hud.json").read_text(encoding="utf-8"))
    curva = limpiar_perfil(json.loads((DET / "perfil.json").read_text(encoding="utf-8")))

    grupos = {}
    for a in avistajes:
        grupos.setdefault(clave(a["nombre"]), []).append(a)

    especies = []
    for lista in sorted(grupos.values(), key=lambda l: seg(l[0]["t"])):
        # El taxon mas preciso que haya dado cualquiera de sus avistajes.
        mejor = max(lista, key=lambda a: (RANGOS.index(a.get("rango", "filo")) if a.get("rango") in RANGOS else 0))
        vistos = []
        for a in lista:
            s = seg(a["t"]) + 2
            t = f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"
            h = hud.get(t, {})
            foto = RAIZ / "fotos" / f"{t.replace(':', '')}.jpg"
            # Si el OCR de ese cuadro fallo o se fue lejos de la curva, vale la curva.
            esperada = interpolar(curva, s)
            depth = h.get("depth") if h.get("depth") and abs(h["depth"] - esperada) < 40 else round(esperada)
            temp = h.get("temp") if h.get("temp") is not None and 0 < h["temp"] < 15 else None
            vistos.append({
                "seg": seg(a["t"]),
                "foto": f"fotos/{foto.name}" if foto.exists() else None,
                "depth": depth,
                "temp": temp,
                "cita": a.get("cita", ""),
            })
        # Portada elegida mirando los cuadros (portadas_N.json): reemplaza la foto del avistaje mas cercano.
        portada, verificada = 0, False
        elegida = PORTADAS.get(str(len(especies) + 1), {})
        if elegida.get("foto"):
            origen = Path(elegida["foto"])
            s_foto = seg(f"{origen.stem[:2]}:{origen.stem[2:4]}:{origen.stem[4:]}")
            portada = min(range(len(vistos)), key=lambda i: abs(vistos[i]["seg"] - s_foto))
            destino = RAIZ / "fotos" / f"portada_{len(especies) + 1:03d}.jpg"
            shutil.copy(origen, destino)
            vistos[portada]["foto"] = f"fotos/{destino.name}"
            verificada = bool(elegida.get("seguro"))
        profundidades = [v["depth"] for v in vistos if v["depth"]]
        especies.append({
            "id": len(especies) + 1,
            "nombre": lista[0]["nombre"],
            "taxon": mejor.get("taxon", ""),
            "rango": mejor.get("rango", ""),
            "filo": mejor.get("filo", ""),
            "grupo": mejor.get("grupo", "Otros"),
            "dato": next((a["dato"] for a in lista if a.get("dato")), ""),
            "prof_min": min(profundidades) if profundidades else None,
            "prof_max": max(profundidades) if profundidades else None,
            "portada": portada,
            "verificada": verificada,
            "avistajes": vistos,
        })

    salida = {
        "expedicion": {
            "nombre": "Talud Continental IV",
            "lugar": "Cañón submarino de Mar del Plata",
            "fecha": "2025-07-31",
            "video": "Fa-iwwxiDr0",
            "creditos": "Schmidt Ocean Institute y CONICET",
        },
        "perfil": curva,
        "especies": especies,
    }
    (RAIZ / "oceanidex.json").write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    with open(RAIZ / "oceanidex.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["n", "nombre", "taxon", "rango", "filo", "tiempo_video", "profundidad_m", "temperatura_c", "link", "cita"])
        for e in especies:
            for v in e["avistajes"]:
                s = v["seg"]
                w.writerow([e["id"], e["nombre"], e["taxon"], e["rango"], e["filo"],
                            f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}", v["depth"] or "", v["temp"] or "",
                            f"https://www.youtube.com/watch?v=Fa-iwwxiDr0&t={s}s", v["cita"]])
    print(len(especies), "especies,", len(avistajes), "avistajes,", len(curva), "puntos de perfil")


if __name__ == "__main__":
    {"juntar": juntar, "fichas": fichas}[sys.argv[1]]()
