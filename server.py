#!/usr/bin/env python3
"""
Servidor HTTP simple para el frontend del Analizador de Biodiversidad Marina
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

class BiodiversityServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_HEAD(self):
        self.handle_request()
    
    def handle_request(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Handle API endpoints first
        if path == '/api/stats':
            self.send_stats()
            return
        elif path == '/api/species':
            self.send_species()
            return
        elif path == '/api/phyla':
            self.send_phyla()
            return
        elif path.startswith('/api/thumbnail/'):
            self.send_thumbnail(path)
            return
        
        # Serve static files
        if path == '/':
            path = '/index.html'
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Serve the file
        try:
            if path.endswith('.html'):
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            elif path.endswith('.json'):
                self.send_header('Content-Type', 'application/json; charset=utf-8')
            elif path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                self.send_header('Content-Type', 'image/jpeg')
            elif path.endswith('.png'):
                self.send_header('Content-Type', 'image/png')
            else:
                self.send_header('Content-Type', 'text/plain')
            
            self.end_headers()
            
            # Read and send the file
            file_path = os.path.join(os.getcwd(), path.lstrip('/'))
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'File not found')
                
        except Exception as e:
            self.send_error(500, f'Server error: {str(e)}')
    
    def send_stats(self):
        """Send biodiversity statistics"""
        try:
            with open('biodiversity_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            stats = {
                'total_species': len(data['species_data']),
                'total_phyla': len(data['taxonomy_data']),
                'unknown_species': len(data.get('unknown_species', [])),
                'avg_confidence': sum(s.get('confidence', 0) for s in data['species_data']) / len(data['species_data'])
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f'Error loading stats: {str(e)}')
    
    def send_species(self):
        """Send species data with optional filtering"""
        try:
            with open('biodiversity_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load thumbnails index
            thumbnails_index = {}
            try:
                with open('thumbnails/thumbnails_index.json', 'r', encoding='utf-8') as f:
                    thumbnails_index = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading thumbnails index: {e}")
            
            # Parse query parameters for filtering
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            species = data['species_data']
            
            # Apply filters if provided
            if 'phylum' in query_params:
                phylum = query_params['phylum'][0]
                species = [s for s in species if s.get('phylum') == phylum]
            
            if 'confidence' in query_params:
                min_confidence = float(query_params['confidence'][0])
                species = [s for s in species if s.get('confidence', 0) >= min_confidence]
            
            if 'method' in query_params:
                method = query_params['method'][0]
                species = [s for s in species if s.get('detection_method') == method]
            
            if 'search' in query_params:
                search_term = query_params['search'][0].lower()
                species = [s for s in species if 
                          search_term in s.get('common_name', '').lower() or
                          search_term in s.get('scientific_name', '').lower()]
            
            # Add thumbnail paths to each species
            for s in species:
                timestamp = s.get('timestamp', '00:00:00.000')
                
                # Look up thumbnail in index
                if timestamp in thumbnails_index:
                    thumbnail_path = thumbnails_index[timestamp]
                    # Extract just the filename from the path
                    thumbnail_filename = os.path.basename(thumbnail_path)
                    s['thumbnail_url'] = f"/api/thumbnail/{thumbnail_filename}"
                else:
                    # Fallback: no thumbnail available
                    s['thumbnail_url'] = None
            
            # Limit results for performance
            if len(species) > 1000:
                species = species[:1000]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(species, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f'Error loading species: {str(e)}')
    
    def send_phyla(self):
        """Send phyla data"""
        try:
            with open('biodiversity_results.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            phyla = data.get('taxonomy_data', {})
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(phyla, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f'Error loading phyla: {str(e)}')
    
    def send_thumbnail(self, path):
        """Send thumbnail image"""
        try:
            # Extract filename from path
            filename = path.replace('/api/thumbnail/', '')
            thumbnail_path = os.path.join('thumbnails', filename)
            
            print(f"🔍 Buscando thumbnail: {filename}")
            print(f"📁 Ruta completa: {thumbnail_path}")
            print(f"✅ Existe: {os.path.exists(thumbnail_path)}")
            
            if os.path.exists(thumbnail_path):
                # Read the image file
                with open(thumbnail_path, 'rb') as f:
                    image_data = f.read()
                
                # Send the response
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.send_header('Content-Length', str(len(image_data)))
                self.end_headers()
                
                # Write the image data
                self.wfile.write(image_data)
                print(f"✅ Thumbnail enviado: {filename} ({len(image_data)} bytes)")
            else:
                print(f"❌ Thumbnail no encontrado: {filename}")
                self.send_error(404, f'Thumbnail not found: {filename}')
                
        except Exception as e:
            print(f"❌ Error sirviendo thumbnail: {e}")
            self.send_error(500, f'Error serving thumbnail: {str(e)}')

def main():
    """Start the server"""
    PORT = 8080
    
    try:
        with socketserver.TCPServer(("", PORT), BiodiversityServer) as httpd:
            print(f"🌊 Servidor iniciado en http://localhost:{PORT}")
            print(f"📊 Frontend disponible en http://localhost:{PORT}")
            print(f"📁 Archivos servidos desde: {os.getcwd()}")
            print("\n🎯 Características:")
            print("   • Visualización interactiva de especies")
            print("   • Filtros por filo, confianza y método")
            print("   • Búsqueda en tiempo real")
            print("   • Estadísticas en tiempo real")
            print("   • Diseño responsive")
            print("   • Miniaturas de timestamps")
            print("\n🔄 Presiona Ctrl+C para detener el servidor")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Servidor detenido")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Puerto {PORT} ya está en uso")
            print("💡 Intenta: pkill -f 'python.*server.py'")
        else:
            print(f"❌ Error iniciando servidor: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main() 