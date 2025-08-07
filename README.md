# 🌊 Analizador de Biodiversidad Marina

Herramienta para analizar la biodiversidad marina a partir de subtítulos de expediciones científicas.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/tu-usuario/MarinaDex)

## 📖 Descripción

Este proyecto analiza automáticamente subtítulos de expediciones científicas marinas para identificar y catalogar especies marinas. Utiliza técnicas de procesamiento de lenguaje natural y patrones de reconocimiento para extraer información taxonómica, timestamps y contexto de cada detección.

## 📋 Características

- **Detección inteligente** de especies marinas
- **Extracción precisa** de timestamps
- **Análisis contextual** para especies nuevas
- **Organización taxonómica** por filo y clase
- **Sistema de confianza** para validar detecciones
- **Información adicional** (tamaños, profundidades, comportamientos)
- **Frontend interactivo** para visualizar resultados

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior
- Navegador web moderno

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/MarinaDex.git
cd MarinaDex

# Instalar dependencias (opcional)
pip install -r requirements.txt
```

### Análisis de Datos
```bash
python3 biodiversity_analyzer.py
```

### Visualización Web
```bash
python3 server.py
```
Luego abre http://localhost:8000 en tu navegador.

## 📊 Resultados

El analizador genera:
- **Reporte detallado** en consola
- **Archivo JSON** con todos los datos (`biodiversity_results.json`)
- **Estadísticas** por filo taxonómico
- **Especies nuevas** detectadas automáticamente
- **Frontend interactivo** con filtros y búsqueda

## 🎯 Frontend Interactivo

### Características del Frontend:
- **📊 Dashboard** con estadísticas en tiempo real
- **🔍 Búsqueda** de especies por nombre
- **🦠 Filtros** por filo, confianza y método de detección
- **📱 Diseño responsive** para móviles y desktop
- **🎨 Interfaz moderna** con gradientes y animaciones
- **⚡ Carga rápida** con paginación inteligente

### Funcionalidades:
- **Visualización de especies** en tarjetas interactivas
- **Filtros múltiples** combinables
- **Barras de confianza** con colores
- **Contexto de detección** para cada especie
- **Información taxonómica** completa
- **Timestamps precisos** de cada detección

## 🔍 Filos Detectados

- **Arthropoda**: Langostas, camarones, cangrejos
- **Cnidaria**: Corales, anémonas, hidros
- **Mollusca**: Pulpos, caracoles, calamares
- **Chordata**: Peces, rayas, tiburones
- **Echinodermata**: Estrellas de mar, erizos
- **Porifera**: Esponjas
- **Annelida**: Poliquetos

## 📁 Archivos

- `biodiversity_analyzer.py` - Analizador principal
- `server.py` - Servidor web para el frontend
- `index.html` - Frontend interactivo
- `subtitulos_espanol.txt` - Datos de entrada
- `biodiversity_results.json` - Resultados del análisis
- `services/` - Servicios de IA (opcional)

## 🎯 Ejemplo de Salida

```
🌊 REPORTE DE BIODIVERSIDAD MARINA
====================================
📊 Total de especies identificadas: 1,000+
🔍 Métodos de detección utilizados:
   • known_pattern: 1,000+ especies
📈 Confianza promedio: 0.90

🦠 FILO: CHORDATA
   Especies encontradas: 63
   • pez (Timestamp: 05:01:19.920)
   • raya (Timestamp: 01:51:47.149)
   • caballito de mar (Timestamp: 06:40:51.868)
```

## 🌐 Acceso Web

Una vez iniciado el servidor:
- **URL**: http://localhost:8000
- **Puerto**: 8000 (configurable en server.py)
- **Compatibilidad**: Chrome, Firefox, Safari, Edge

## 🔧 Tecnologías

- **Backend**: Python 3.x
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Servidor**: HTTP Server nativo de Python
- **Datos**: JSON con encoding UTF-8

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Contacto

- **Autor**: Tu Nombre
- **Email**: tu-email@ejemplo.com
- **Proyecto**: [https://github.com/tu-usuario/MarinaDex](https://github.com/tu-usuario/MarinaDex) 