#!/usr/bin/env python3
"""
Generador de Miniaturas desde YouTube
====================================

Extrae frames del video de YouTube para generar miniaturas reales
de los timestamps del análisis de biodiversidad.
"""

import os
import json
import subprocess
import re
from typing import Dict, List, Optional
from datetime import datetime

class YouTubeThumbnailGenerator:
    """
    Generador de miniaturas desde video de YouTube.
    """
    
    def __init__(self, youtube_url: str = "https://www.youtube.com/watch?v=Fa-iwwxiDr0"):
        """
        Inicializar el generador de miniaturas de YouTube.
        
        Args:
            youtube_url: URL del video de YouTube
        """
        self.youtube_url = youtube_url
        self.thumbnails_dir = "thumbnails"
        self.video_file = None
        self.ensure_thumbnails_directory()
    
    def ensure_thumbnails_directory(self):
        """Crear directorio de miniaturas si no existe."""
        if not os.path.exists(self.thumbnails_dir):
            os.makedirs(self.thumbnails_dir)
            print(f"📁 Directorio creado: {self.thumbnails_dir}")
    
    def download_video(self) -> bool:
        """
        Descargar video de YouTube usando yt-dlp.
        
        Returns:
            True si la descarga fue exitosa, False en caso contrario
        """
        try:
            print(f"📥 Descargando video de YouTube: {self.youtube_url}")
            
            # Comando para descargar video con yt-dlp
            cmd = [
                'yt-dlp',
                '--format', 'best[height<=720]',  # Calidad HD
                '--output', 'expedicion_marina.%(ext)s',
                '--write-thumbnail',
                self.youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Buscar el archivo descargado
                for file in os.listdir('.'):
                    if file.startswith('expedicion_marina.') and not file.endswith('.webp'):
                        self.video_file = file
                        print(f"✅ Video descargado: {self.video_file}")
                        return True
                print("❌ No se encontró el archivo de video descargado")
                return False
            else:
                print(f"❌ Error descargando video: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error en download_video: {e}")
            return False
    
    def timestamp_to_seconds(self, timestamp: str) -> float:
        """
        Convertir timestamp en formato HH:MM:SS.mmm a segundos.
        
        Args:
            timestamp: Timestamp en formato "HH:MM:SS.mmm"
            
        Returns:
            Segundos como float
        """
        try:
            # Parsear timestamp
            time_parts = timestamp.split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds_parts = time_parts[2].split('.')
            seconds = int(seconds_parts[0])
            milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            
            # Convertir a segundos totales
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return total_seconds
            
        except Exception as e:
            print(f"❌ Error parseando timestamp {timestamp}: {e}")
            return 0.0
    
    def extract_frame(self, timestamp: str, output_filename: str = None) -> Optional[str]:
        """
        Extraer frame de video en timestamp específico usando ffmpeg.
        
        Args:
            timestamp: Timestamp en formato "HH:MM:SS.mmm"
            output_filename: Nombre del archivo de salida (opcional)
            
        Returns:
            Ruta al archivo de imagen generado o None si falla
        """
        if not self.video_file or not os.path.exists(self.video_file):
            print(f"⚠️  No se encontró archivo de video: {self.video_file}")
            return None
        
        try:
            # Convertir timestamp a segundos
            seconds = self.timestamp_to_seconds(timestamp)
            
            # Generar nombre de archivo si no se proporciona
            if not output_filename:
                safe_timestamp = timestamp.replace(':', '_').replace('.', '_')
                output_filename = f"frame_{safe_timestamp}.jpg"
            
            output_path = os.path.join(self.thumbnails_dir, output_filename)
            
            # Comando ffmpeg optimizado para extracción rápida
            cmd = [
                'ffmpeg',
                '-ss', str(seconds),  # Buscar al timestamp específico
                '-i', self.video_file,
                '-vframes', '1',
                '-q:v', '3',  # Calidad media para velocidad
                '-y',  # Sobrescribir si existe
                '-loglevel', 'error',  # Solo errores para menos output
                output_path
            ]
            
            # Ejecutar comando con timeout de 10 segundos
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                return None
                
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            return None
    
    def create_visual_placeholder(self, timestamp: str, species_name: str) -> str:
        """
        Crear imagen placeholder visual usando Pillow.
        
        Args:
            timestamp: Timestamp de la detección
            species_name: Nombre de la especie
            
        Returns:
            Ruta al archivo de imagen placeholder
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen
            width, height = 400, 300
            image = Image.new('RGB', (width, height), color='#667eea')
            draw = ImageDraw.Draw(image)
            
            # Intentar usar una fuente del sistema
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Dibujar texto
            text_color = 'white'
            
            # Título
            draw.text((width//2, 50), "🐠 ESPECIE DETECTADA", 
                     fill=text_color, font=font_large, anchor="mm")
            
            # Nombre de la especie
            draw.text((width//2, 90), species_name, 
                     fill=text_color, font=font_large, anchor="mm")
            
            # Timestamp
            draw.text((width//2, 130), f"⏰ {timestamp}", 
                     fill=text_color, font=font_medium, anchor="mm")
            
            # Información adicional
            draw.text((width//2, 170), "📊 Análisis de Biodiversidad Marina", 
                     fill=text_color, font=font_medium, anchor="mm")
            
            draw.text((width//2, 200), "🌊 Expedición Cañón de Mar del Plata", 
                     fill=text_color, font=font_medium, anchor="mm")
            
            # Borde decorativo
            draw.rectangle([10, 10, width-10, height-10], 
                         outline='white', width=3)
            
            # Guardar imagen
            safe_timestamp = timestamp.replace(':', '_').replace('.', '_')
            safe_species = re.sub(r'[^a-zA-Z0-9]', '_', species_name)
            filename = f"placeholder_{safe_species}_{safe_timestamp}.jpg"
            output_path = os.path.join(self.thumbnails_dir, filename)
            
            image.save(output_path, 'JPEG', quality=95)
            print(f"🎨 Placeholder visual creado: {output_path}")
            return output_path
            
        except ImportError:
            print("⚠️  Pillow no está instalado. Creando placeholder de texto...")
            return self.create_text_placeholder(timestamp, species_name)
        except Exception as e:
            print(f"❌ Error creando placeholder visual: {e}")
            return self.create_text_placeholder(timestamp, species_name)
    
    def create_text_placeholder(self, timestamp: str, species_name: str) -> str:
        """
        Crear placeholder de texto como fallback.
        """
        try:
            safe_timestamp = timestamp.replace(':', '_').replace('.', '_')
            safe_species = re.sub(r'[^a-zA-Z0-9]', '_', species_name)
            filename = f"placeholder_{safe_species}_{safe_timestamp}.txt"
            output_path = os.path.join(self.thumbnails_dir, filename)
            
            placeholder_content = f"""
            🐠 ESPECIE: {species_name}
            ⏰ TIMESTAMP: {timestamp}
            📊 DETECCIÓN: Análisis de Biodiversidad Marina
            🌊 EXPEDICIÓN: Cañón de Mar del Plata
            
            [Imagen del momento de detección]
            [Video no disponible - Placeholder generado]
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            print(f"📝 Placeholder de texto creado: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generando placeholder de texto: {e}")
            return None
    
    def process_biodiversity_results(self, results_file: str = "biodiversity_results.json") -> Dict[str, str]:
        """
        Procesar resultados de biodiversidad y generar miniaturas.
        
        Args:
            results_file: Ruta al archivo de resultados JSON
            
        Returns:
            Diccionario con timestamps como claves y rutas de imágenes como valores
        """
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            thumbnails = {}
            species_data = data.get('species_data', [])
            
            print(f"🔄 Procesando {len(species_data)} especies...")
            
            # Primero descargar el video si no existe
            if not os.path.exists('expedicion_marina.mp4'):
                print("📥 Descargando video de YouTube...")
                if not self.download_video():
                    print("❌ No se pudo descargar el video")
                    return {}
            
            self.video_file = 'expedicion_marina.mp4'
            print(f"✅ Usando video: {self.video_file}")
            
            # Contar imágenes existentes
            existing_images = len([f for f in os.listdir(self.thumbnails_dir) if f.endswith('.jpg')])
            print(f"📸 Ya existen {existing_images} imágenes. Continuando desde la especie {existing_images}...")
            
            for i, species in enumerate(species_data):
                # Saltar especies que ya tienen imágenes
                if i < existing_images:
                    continue
                    
                timestamp = species.get('timestamp', '00:00:00.000')
                species_name = species.get('common_name', 'unknown')
                
                # Mostrar progreso cada 100 especies
                if i % 100 == 0:
                    print(f"📊 Progreso: {i}/{len(species_data)} especies procesadas")
                
                # Generar nombre único para la imagen
                safe_timestamp = timestamp.replace(':', '_').replace('.', '_')
                safe_species = re.sub(r'[^a-zA-Z0-9]', '_', species_name)
                image_filename = f"{safe_species}_{safe_timestamp}.jpg"
                
                # Verificar si ya existe la imagen
                image_path = os.path.join(self.thumbnails_dir, image_filename)
                if os.path.exists(image_path):
                    thumbnails[timestamp] = image_path
                    continue
                
                # Intentar extraer frame del video
                image_path = self.extract_frame(timestamp, image_filename)
                
                # Si falla la extracción, usar placeholder
                if not image_path:
                    image_path = self.create_visual_placeholder(timestamp, species_name)
                
                if image_path:
                    thumbnails[timestamp] = image_path
                
                # Mostrar progreso cada 500 especies
                if (i + 1) % 500 == 0:
                    print(f"📊 Progreso: {i + 1}/{len(species_data)} especies procesadas")
            
            print(f"✅ Procesamiento completado. {len(thumbnails)} miniaturas generadas.")
            return thumbnails
            
        except Exception as e:
            print(f"❌ Error procesando resultados: {e}")
            return {}
    
    def create_thumbnail_index(self, thumbnails: Dict[str, str]) -> str:
        """
        Crear archivo de índice de miniaturas.
        
        Args:
            thumbnails: Diccionario de timestamps y rutas de imágenes
            
        Returns:
            Ruta al archivo de índice
        """
        index_path = os.path.join(self.thumbnails_dir, "thumbnails_index.json")
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(thumbnails, f, ensure_ascii=False, indent=2)
            
            print(f"📋 Índice de miniaturas creado: {index_path}")
            return index_path
            
        except Exception as e:
            print(f"❌ Error creando índice: {e}")
            return None

def main():
    """Función principal para generar miniaturas desde YouTube."""
    print("🎬 Generador de Miniaturas desde YouTube")
    print("=" * 50)
    
    # Configurar generador con URL de YouTube
    youtube_url = "https://www.youtube.com/watch?v=Fa-iwwxiDr0"
    generator = YouTubeThumbnailGenerator(youtube_url)
    
    # Procesar resultados de biodiversidad
    print("\n🔄 Iniciando generación de miniaturas desde YouTube...")
    thumbnails = generator.process_biodiversity_results()
    
    # Crear índice
    if thumbnails:
        generator.create_thumbnail_index(thumbnails)
        print(f"\n✅ Generación completada. {len(thumbnails)} miniaturas creadas.")
        print(f"📁 Directorio de miniaturas: {generator.thumbnails_dir}")
    else:
        print("\n⚠️  No se generaron miniaturas.")

if __name__ == "__main__":
    main() 