"""Saca frames del video de la inmersion y les lee el HUD (profundidad, temperatura, hora UTC).

python deteccion/frames.py perfil          un frame cada 5 minutos -> deteccion/perfil.json
python deteccion/frames.py avistajes       un frame por avistaje   -> fotos/<HHMMSS>.jpg + deteccion/hud.json

No baja el video: pide a YouTube solo el cuadro de cada segundo con ffmpeg sobre la URL directa.
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VIDEO = "https://www.youtube.com/watch?v=Fa-iwwxiDr0"
DURACION = 11 * 3600 + 55 * 60
CACHE = RAIZ / "deteccion" / "cache"


def url_directa():
    # 720p H264 solo video: un cuadro tarda ~4 s en llegar.
    return subprocess.run(["yt-dlp", "-g", "-f", "136", VIDEO], capture_output=True, text=True, check=True).stdout.strip()


def hms(seg):
    return f"{seg // 3600:02d}:{seg % 3600 // 60:02d}:{seg % 60:02d}"


def seg(t):
    h, m, s = (int(x) for x in t.split(":"))
    return h * 3600 + m * 60 + s


def sacar(url, t, destino):
    if destino.exists():
        return destino
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", t, "-i", url, "-frames:v", "1", "-q:v", "2", str(destino)],
                   check=True, timeout=120)
    return destino


def recortar_hud(img, destino):
    # El HUD de Schmidt: datos abajo a la izquierda, hora UTC abajo al centro. Se invierte para que el OCR lea mejor.
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(img), "-filter_complex",
                    "[0]crop=260:200:0:510,scale=780:-1,negate,pad=1400:600:0:0[a];"
                    "[0]crop=460:44:410:672,scale=1380:-1,negate[b];[a][b]overlay=0:610-132",
                    str(destino)], check=True)


def leer_huds(imgs):
    ps1 = RAIZ / "deteccion" / "ocr_hud.ps1"
    salida = {}
    for i in range(0, len(imgs), 40):
        tanda = imgs[i:i + 40]
        r = subprocess.run(["powershell", "-NoProfile", "-File", str(ps1), *map(str, tanda)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        for linea in r.stdout.splitlines():
            if linea.startswith("{"):
                d = json.loads(linea)
                salida[Path(d["img"]).stem] = interpretar(d["lineas"])
    return salida


def numero(texto):
    m = re.search(r"-?\d+(?:[.,]\d+)?", texto or "")
    return float(m.group().replace(",", ".")) if m else None


def interpretar(lineas):
    """Del texto suelto del OCR saca profundidad (m), temperatura (C) y hora UTC."""
    datos = {}
    for l in lineas:
        u = l.upper().replace("O", "0") if re.search(r"\d", l) else l.upper()
        if re.search(r"\d+\s*M$", u) and "depth" not in datos:
            datos["depth"] = numero(u)
        elif re.search(r"\d\s*[0O]?C$", l.upper().replace(" ", "")) and "temp" not in datos:
            datos["temp"] = numero(l)
        m = re.search(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})", l)
        if m:
            datos["utc"] = f"{m.group(1)}T{m.group(2)}Z"
    return datos


def correr(tiempos, carpeta, ancho):
    carpeta.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    url = url_directa()
    crudos = {}

    def uno(t):
        crudo = sacar(url, t, CACHE / f"{t.replace(':', '')}.jpg")
        crudos[t] = crudo
        final = carpeta / f"{t.replace(':', '')}.jpg"
        if ancho and not final.exists():
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(crudo), "-vf", f"scale={ancho}:-2",
                            "-q:v", "5", str(final)], check=True)
        hud = CACHE / f"hud_{t.replace(':', '')}.png"
        if not hud.exists():
            recortar_hud(crudo, hud)
        return hud

    with ThreadPoolExecutor(6) as pool:
        huds = list(pool.map(uno, tiempos))
    leidos = leer_huds(huds)
    return {t: leidos.get(f"hud_{t.replace(':', '')}", {}) for t in tiempos}


if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "perfil":
        tiempos = [hms(s) for s in range(30, DURACION, 300)]
        datos = correr(tiempos, CACHE, None)
        (RAIZ / "deteccion" / "perfil.json").write_text(json.dumps(datos, indent=1), encoding="utf-8")
    elif modo == "avistajes":
        avistajes = json.loads((RAIZ / "deteccion" / "avistajes.json").read_text(encoding="utf-8"))
        # Dos segundos despues de que lo nombran: la camara ya suele estar encima.
        tiempos = sorted({hms(seg(a["t"]) + 2) for a in avistajes})
        datos = correr(tiempos, RAIZ / "fotos", 640)
        (RAIZ / "deteccion" / "hud.json").write_text(json.dumps(datos, indent=1), encoding="utf-8")
    elif modo == "candidatas":
        # Para elegir portada: varios cuadros alrededor de los primeros avistajes de cada organismo,
        # porque los cientificos lo nombran unos segundos antes o despues de que la camara lo encuadre.
        fichas = json.loads((RAIZ / "oceanidex.json").read_text(encoding="utf-8"))["especies"]
        candidatas = {e["id"]: [hms(a["seg"] + d) for a in e["avistajes"][:3] for d in (-4, 2, 8, 16)] for e in fichas}
        url = url_directa()
        carpeta = CACHE / "candidatas"
        carpeta.mkdir(parents=True, exist_ok=True)

        def chica(t):
            final = carpeta / f"{t.replace(':', '')}.jpg"
            if not final.exists():
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", t, "-i", url, "-frames:v", "1",
                                "-vf", "scale=640:-2", "-q:v", "4", str(final)], check=True, timeout=120)
            return final

        with ThreadPoolExecutor(6) as pool:
            list(pool.map(chica, sorted({t for ts in candidatas.values() for t in ts})))
        (RAIZ / "deteccion" / "candidatas.json").write_text(json.dumps(candidatas, indent=1), encoding="utf-8")
        datos = {}
    print(modo, "listo:", sum(1 for d in datos.values() if d.get("depth")), "de", len(datos), "con profundidad")
