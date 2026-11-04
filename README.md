# OceaniDex

Todo lo que vio el ROV SuBastian en el cañón submarino de Mar del Plata, como una Pokédex: cada organismo con su foto, la profundidad y la temperatura a la que apareció, lo que dijeron los científicos y el segundo exacto del video.

**Web:** https://kvothesson.com/OceaniDex/

## Qué tiene

- **La inmersión entera en un gráfico:** la curva de profundidad de las 12 horas de transmisión, con cada avistaje marcado. Tocás un punto y se abre la ficha.
- **Fichas con foto real** sacada del video en el momento en que lo nombran, profundidad y temperatura leídas del HUD del ROV, y la frase de los científicos.
- **Ver en el video:** reproduce la transmisión justo en ese momento, sin salir de la página.
- **Ya la vi:** marcás las que viste y lleva la cuenta, en tu navegador.
- **Buscar, filtrar por grupo y ordenar** por aparición, cantidad de avistajes o profundidad.
- **Link directo a cada ficha** para compartir, y búsqueda del taxón en WoRMS.
- **Datos abiertos:** `oceanidex.csv` con cada avistaje, su minuto y su link.

Es una página estática: `index.html` lee `oceanidex.json`. Para verla local, cualquier servidor sirve:

```bash
python -m http.server 8080
```

## Cómo se arma

Ver [deteccion/LEEME.md](deteccion/LEEME.md). En corto: la transcripción se lee en tramos con un modelo que separa lo que se ve en cámara de lo que se comenta, y los cuadros y datos del HUD se sacan directo del video de YouTube.

## Próximo

- Sumar el resto de las transmisiones de Talud Continental IV (esta es una de 12 horas).
- Campaña de filtraciones de metano (diciembre 2025 a enero 2026).
- Talud Continental V, cañones Ameghino y Almirante Brown (prevista para 2027): seguirla en vivo.

## Créditos

Imágenes y transmisión: [Schmidt Ocean Institute](https://schmidtocean.org) con el CONICET, expedición *Underwater Oases of Mar del Plata Canyon: Talud Continental IV*, 2025. Esta herramienta no está afiliada a ninguna de las dos.

Licencia MIT para el código.
