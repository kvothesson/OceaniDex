# Cómo se arma OceaniDex

De la transmisión a la web, en cuatro pasos. Sirve igual para una campaña nueva: cambiar `VIDEO` en `frames.py` y los textos de `expedicion` en `armar.py`.

1. **Transcripción en tramos.** Los subtítulos (`subtitulos_espanol.txt`) se compactan a una línea por frase, `[HH:MM:SS] texto`, y se parten en tramos de unas 3 horas (`trozo_N.txt`).
2. **Lectura de avistajes.** Un modelo lee cada tramo entero con la consigna de abajo y escribe `avistajes_N.json`. Esto reemplazó al analizador por patrones (`biodiversity_analyzer.py`), que marcaba como especie cualquier frase cercana a una palabra científica: de 2421 detecciones, 2139 eran frases como "vamos a" o "instagram". La lectura con contexto separa lo que se ve ahora de lo que se recuerda o se explica.
3. **Fotos y HUD.** `python deteccion/armar.py juntar` filtra por confianza y unifica sinónimos. `python deteccion/frames.py avistajes` pide a YouTube el cuadro de cada avistaje (2 s después de que lo nombran) sin bajar el video, y lee del HUD del ROV la profundidad y la temperatura con el OCR de Windows (`ocr_hud.ps1`). `python deteccion/frames.py perfil` hace lo mismo cada 5 minutos para dibujar la curva de la inmersión.
4. **Fichas.** `python deteccion/armar.py fichas` agrupa por organismo y deja `oceanidex.json` (lo que lee la web) y `oceanidex.csv`.

## Consigna para leer un tramo

> Sos biólogo marino. Leé COMPLETO el tramo: es la transcripción automática (con errores) de una transmisión en vivo del ROV SuBastian. Cada línea es `[HH:MM:SS] texto`.
> Extraé los AVISTAJES: momentos en que se está viendo o recolectando un organismo en cámara AHORA. Descartá menciones a algo visto en otro momento, respuestas generales al chat, explicaciones teóricas, comida y animales terrestres. Corregí errores de transcripción con criterio. Si el mismo organismo se comenta varios minutos seguidos es un solo avistaje; si reaparece en otra escena, es otro.
> Cada avistaje: `{"t", "nombre" (común, singular, minúscula), "taxon" (lo más preciso que se pueda afirmar), "rango", "filo", "grupo" (Corales y anémonas | Esponjas | Estrellas y erizos | Cangrejos y crustáceos | Pulpos, calamares y caracoles | Peces | Gusanos | Medusas y afines | Otros), "cita" (textual, máx 160), "dato" (solo si lo dicen en la transmisión), "confianza" (0 a 1)}`. No inventar nada que no esté en el texto.
