# 🌊 OceaniDex - Pokédex de Biodiversidad Marina

Una herramienta tipo Pokédex para analizar y visualizar especies marinas detectadas en expediciones científicas. OceaniDex agrupa especies similares y permite explorar múltiples detecciones con sus respectivas fotos y timestamps.

## 🚀 Características

### 📊 Vista Tipo Pokédex
- **Agrupación inteligente**: Las especies se agrupan por nombre común, evitando duplicados
- **Navegación de fotos**: Cada especie puede tener múltiples fotos que se pueden recorrer
- **Timestamps detallados**: Registro completo de todas las detecciones de cada especie
- **Información taxonómica**: Filo, clase, método de detección y nivel de confianza

### 🔍 Funcionalidades de Búsqueda y Filtrado
- **Búsqueda en tiempo real**: Busca por nombre común o científico
- **Filtros por filo**: Arthropoda, Cnidaria, Mollusca, Porifera, Echinodermata, Annelida, Chordata
- **Filtros por método**: Patrones conocidos, nombres científicos, contexto científico
- **Pestañas de navegación**: Acceso rápido a especies por filo

### 📱 Diseño Responsive
- **Optimizado para móvil**: Interfaz adaptativa para celulares y tablets
- **Navegación táctil**: Controles optimizados para pantallas táctiles
- **Modal interactivo**: Vista detallada con galería de fotos y navegación

### 🖼️ Galería de Fotos
- **Navegación con flechas**: Botones para recorrer las fotos
- **Navegación con teclado**: Flechas izquierda/derecha para cambiar foto
- **Contador de fotos**: Muestra la posición actual en la galería
- **Información contextual**: Cada foto incluye timestamp y contexto

## 🛠️ Instalación y Uso

### Requisitos
- Python 3.7+
- Navegador web moderno

### Instalación
```bash
# Clonar el repositorio
git clone <repository-url>
cd OceaniDex

# Instalar dependencias (si las hay)
pip install -r requirements.txt

# Ejecutar el servidor
python3 server.py
```

### Acceso
1. Abrir el navegador en `http://localhost:8080`
2. La interfaz se cargará automáticamente con los datos de biodiversidad
3. Usar los filtros y búsqueda para explorar especies
4. Hacer clic en cualquier especie para ver detalles completos

## 📋 Estructura de Datos

### Especies Agrupadas (Formato Pokédex)
```json
{
  "id": 1,
  "common_name": "balanus",
  "scientific_name": "Balanus sp.",
  "phylum": "Arthropoda",
  "class": "Cirripedia",
  "detection_method": "known_pattern",
  "confidence": 0.9,
  "total_mentions": 2,
  "first_timestamp": "00:01:01.760",
  "last_timestamp": "10:23:47.350",
  "main_thumbnail": "/api/thumbnail/balanus_00_01_01_760.jpg",
  "all_occurrences": [
    {
      "timestamp": "00:01:01.760",
      "context": "Estoy estoy casi seguro que vi antes...",
      "thumbnail_url": "/api/thumbnail/balanus_00_01_01_760.jpg",
      "confidence": 0.9,
      "detection_method": "known_pattern"
    }
  ]
}
```

## 🎯 Casos de Uso

### Para Científicos
- **Análisis de biodiversidad**: Explorar especies detectadas en expediciones
- **Validación de datos**: Revisar múltiples detecciones de la misma especie
- **Documentación visual**: Acceso a fotos de cada detección con contexto temporal

### Para Investigadores
- **Estudios taxonómicos**: Filtrar por filo y clase para análisis específicos
- **Análisis temporal**: Ver patrones de detección a lo largo del tiempo
- **Control de calidad**: Evaluar confianza y métodos de detección

### Para Educadores
- **Material didáctico**: Interfaz visual para enseñar biodiversidad marina
- **Exploración interactiva**: Navegación intuitiva tipo Pokédex
- **Contexto científico**: Información completa de cada especie

## 🔧 API Endpoints

### `/api/species-grouped`
Retorna especies agrupadas tipo Pokédex con todas sus ocurrencias.

**Parámetros de consulta:**
- `phylum`: Filtrar por filo específico
- `method`: Filtrar por método de detección
- `search`: Buscar por nombre
- `confidence`: Filtrar por nivel de confianza mínimo

### `/api/thumbnail/{filename}`
Sirve las imágenes de thumbnails para cada timestamp.

### `/api/stats`
Estadísticas generales de biodiversidad.

## 🎨 Características de la Interfaz

### Diseño Visual
- **Gradiente marino**: Fondo con colores del océano
- **Tarjetas modernas**: Diseño tipo Pokédex con información clara
- **Iconografía**: Emojis y símbolos para mejor UX
- **Animaciones suaves**: Transiciones y hover effects

### Navegación
- **Modal detallado**: Vista completa de cada especie
- **Galería de fotos**: Navegación con controles visuales
- **Lista de ocurrencias**: Todas las detecciones con contexto
- **Información taxonómica**: Datos científicos organizados

### Responsive Design
- **Mobile-first**: Optimizado para pantallas pequeñas
- **Touch-friendly**: Controles adaptados para táctil
- **Grid adaptativo**: Layout que se ajusta al tamaño de pantalla


## 📌 Backlog

- Obtener todas las campañas
- Utilizar IA para mejorar la detección de especies: hay casos donde se menciona una especie de otro momento de la expedición y se toma como nueva
- Poder ver el momento exacto del video
- Descargar datos desde un CSV

### Difícil
- Análisis de imágenes

## 🤝 Contribución

Este proyecto está diseñado para la comunidad científica marina. Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🌊 Expedición

**Expedición Cañón de Mar del Plata**
- Análisis de biodiversidad marina
- Detección automática de especies
- Documentación visual completa
- Herramienta tipo Pokédex para científicos

---

*OceaniDex: Explorando la biodiversidad marina, una especie a la vez* 🌊🐠 