#!/usr/bin/env python3
"""
Analizador de Biodiversidad Marina - Versión Corregida
====================================================

Versión corregida que extrae correctamente los timestamps del formato de subtítulos.
"""

import re
import unicodedata
import json
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from collections import Counter

class BiodiversityAnalyzerFixed:
    """
    Analizador de biodiversidad marina con extracción correcta de timestamps.
    """
    
    def __init__(self):
        """Inicializar el analizador corregido."""
        self.species_data = {}
        self.taxonomy_data = {}
        self.unknown_species = []
        
        # Normalización se hará con reglas simples (sin diccionario de sinónimos):
        # - minúsculas
        # - quitar acentos
        # - quitar diminutivos (ito/ita/itos/itas)
        # - singularizar (s/es/ces -> z)
        
        # Patrones base conocidos
        self.base_patterns = {
            'Arthropoda': [
                r'\b(?:balanus|Balanus)\b',
                r'\b(?:langosta|langostas)\b',
                r'\b(?:camarón|camarones|camaroncitos)\b',
                r'\b(?:cangrejo|cangrejos)\b',
                r'\b(?:crustáceo|crustáceos)\b',
                r'\b(?:decápodo|decápodos)\b',
                r'\b(?:isópodo|isópodos)\b',
                r'\b(?:anfípodo|anfípodos)\b'
            ],
            'Cnidaria': [
                r'\b(?:coral|corales)\b',
                r'\b(?:anémona|anémonas|anemona)\b',
                r'\b(?:hidro|hidros)\b',
                r'\b(?:octocoral|octocorales)\b',
                r'\b(?:némoda|némodas|nemoda)\b',
                r'\b(?:pólipo|pólipos|polipo)\b',
                r'\b(?:pluma de mar)\b',
                r'\b(?:nidario|nidarios)\b',
                r'\b(?:nidroso|nidrosos)\b'
            ],
            'Mollusca': [
                r'\b(?:pulpo|pulpos)\b',
                r'\b(?:caracol|caracoles)\b',
                r'\b(?:quitón|quitones)\b',
                r'\b(?:vivalvo|vivalvos)\b',
                r'\b(?:calamar|calamares)\b',
                r'\b(?:ostra|ostras)\b',
                r'\b(?:mejillón|mejillones)\b'
            ],
            'Porifera': [
                r'\b(?:esponja|esponjas)\b',
                r'\b(?:porífero|poríferos|porifero)\b'
            ],
            'Echinodermata': [
                r'\b(?:estrella de mar)\b',
                r'\b(?:equinodermo|equinodermos)\b',
                r'\b(?:centa|centas)\b',
                r'\b(?:entolla|entollas)\b',
                r'\b(?:erizo|erizos)\b',
                r'\b(?:pepino de mar)\b'
            ],
            'Annelida': [
                r'\b(?:poliqueto|poliquetos)\b',
                r'\b(?:anélido|anélidos)\b'
            ],
            'Chordata': [
                r'\b(?:pez|peces)\b',
                r'\b(?:raya|rayas)\b',
                r'\b(?:caballito de mar)\b',
                r'\b(?:ventónico|ventonicos)\b',
                r'\b(?:tiburón|tiburones)\b',
                r'\b(?:atún|atunes)\b'
            ]
        }
        
        # Palabras clave que indican especies marinas
        self.marine_keywords = [
            'especie marina', 'organismo marino', 'animal marino',
            'invertebrado marino', 'vertebrado marino', 'fauna marina',
            'bentónico', 'pelágico', 'planctónico', 'larva marina',
            'juvenil marino', 'adulto marino'
        ]
        
        # Patrones de nombres científicos reales
        self.scientific_patterns = [
            r'\b([A-Z][a-z]+)\s+([a-z]+)\b',  # Género especie
            r'\b([A-Z][a-z]+)\s+sp\.\b',      # Género sp.
            r'\b([A-Z][a-z]+)\s+cf\.\s+([a-z]+)\b',  # Género cf. especie
        ]
        
        # Palabras comunes que NO son especies
        self.common_words = {
            'este', 'esta', 'esto', 'estos', 'estas', 'como', 'para', 'por',
            'con', 'sin', 'sobre', 'entre', 'hacia', 'desde', 'hasta', 'durante',
            'antes', 'después', 'mientras', 'cuando', 'donde', 'quien', 'que',
            'cual', 'cuyo', 'cuya', 'cuyos', 'cuyas', 'cuyo', 'cuyas',
            'todos', 'todas', 'todo', 'nada', 'nadie', 'alguien', 'algo',
            'mucho', 'poco', 'más', 'menos', 'muy', 'tan', 'tanto', 'tanta',
            'aquí', 'allí', 'ahí', 'acá', 'allá', 'ahora', 'antes', 'después',
            'siempre', 'nunca', 'jamás', 'tampoco', 'también', 'además',
            'pero', 'sin embargo', 'no obstante', 'aunque', 'si', 'cuando',
            'donde', 'como', 'porque', 'pues', 'ya que', 'dado que',
            'nosotros', 'nosotras', 'ustedes', 'ellos', 'ellas', 'yo', 'tú',
            'vos', 'él', 'ella', 'ello', 'sí', 'no', 'tal', 'cual',
            'cada', 'cualquier', 'cualquiera', 'ningún', 'ninguna',
            'alguno', 'alguna', 'otro', 'otra', 'demás', 'mismo', 'misma'
        }
        
    def load_subtitles(self, file_path: str) -> str:
        """Cargar subtítulos desde archivo."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
    
    def extract_species_mentions(self, subtitles: str) -> List[Dict[str, Any]]:
        """
        Extraer menciones de especies usando métodos inteligentes.
        """
        all_species = []
        
        # Método 1: Patrones conocidos (más confiable)
        known_species = self._extract_known_species(subtitles)
        all_species.extend(known_species)
        
        # Método 2: Nombres científicos reales
        scientific_species = self._extract_scientific_names(subtitles)
        all_species.extend(scientific_species)
        
        # Método 3: Análisis contextual inteligente
        contextual_species = self._extract_contextual_species_smart(subtitles)
        all_species.extend(contextual_species)
        
        # Método 4: Detección de especies mencionadas en contexto científico
        scientific_context_species = self._extract_scientific_context_species(subtitles)
        all_species.extend(scientific_context_species)
        
        # Eliminar duplicados y limpiar
        unique_species = self._remove_duplicates(all_species)
        
        # Filtrar por confianza
        filtered_species = self._filter_by_confidence(unique_species)
        
        # Analizar especies desconocidas
        self._analyze_unknown_species(filtered_species, subtitles)
        
        return filtered_species
    
    def _extract_known_species(self, subtitles: str) -> List[Dict[str, Any]]:
        """Extraer especies usando patrones conocidos."""
        species_list = []
        
        for phylum, patterns in self.base_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, subtitles, re.IGNORECASE)
                
                for match in matches:
                    species_data = self._create_species_entry(
                        match.group(), phylum, subtitles, match.start()
                    )
                    species_data['detection_method'] = 'known_pattern'
                    species_data['confidence'] = 0.9  # Alta confianza para patrones conocidos
                    species_list.append(species_data)
        
        return species_list
    
    def _extract_scientific_names(self, subtitles: str) -> List[Dict[str, Any]]:
        """Extraer nombres científicos reales."""
        species_list = []
        
        for pattern in self.scientific_patterns:
            matches = re.finditer(pattern, subtitles)
            
            for match in matches:
                if pattern == r'\b([A-Z][a-z]+)\s+([a-z]+)\b':
                    genus = match.group(1)
                    species = match.group(2)
                    scientific_name = f"{genus} {species}"
                    
                    # Verificar que no sea una palabra común
                    if not self._is_common_word(genus) and not self._is_common_word(species):
                        species_data = self._create_species_entry(
                            scientific_name, "Desconocido", subtitles, match.start()
                        )
                        species_data['scientific_name'] = scientific_name
                        species_data['detection_method'] = 'scientific_name'
                        species_data['genus'] = genus
                        species_data['species'] = species
                        species_data['confidence'] = 0.95  # Muy alta confianza
                        species_list.append(species_data)
                
                elif pattern == r'\b([A-Z][a-z]+)\s+sp\.\b':
                    genus = match.group(1)
                    scientific_name = f"{genus} sp."
                    
                    if not self._is_common_word(genus):
                        species_data = self._create_species_entry(
                            scientific_name, "Desconocido", subtitles, match.start()
                        )
                        species_data['scientific_name'] = scientific_name
                        species_data['detection_method'] = 'scientific_name'
                        species_data['genus'] = genus
                        species_data['confidence'] = 0.9
                        species_list.append(species_data)
        
        return species_list
    
    def _extract_contextual_species_smart(self, subtitles: str) -> List[Dict[str, Any]]:
        """Extraer especies basándose en contexto científico."""
        species_list = []
        
        # Buscar frases que contengan palabras clave marinas específicas
        marine_context_patterns = [
            r'\b(\w+)\s+(?:especie marina|organismo marino|animal marino)\b',
            r'\b(?:especie marina|organismo marino|animal marino)\s+(\w+)\b',
            r'\b(\w+)\s+(?:bentónico|pelágico|planctónico)\b',
            r'\b(?:bentónico|pelágico|planctónico)\s+(\w+)\b'
        ]
        
        for pattern in marine_context_patterns:
            matches = re.finditer(pattern, subtitles, re.IGNORECASE)
            
            for match in matches:
                potential_species = match.group(1)
                if self._is_valid_species_name(potential_species):
                    species_data = self._create_species_entry(
                        potential_species, "Desconocido", subtitles, match.start()
                    )
                    species_data['detection_method'] = 'scientific_context'
                    species_data['confidence'] = 0.8
                    species_list.append(species_data)
        
        return species_list
    
    def _extract_scientific_context_species(self, subtitles: str) -> List[Dict[str, Any]]:
        """Extraer especies mencionadas en contexto científico."""
        species_list = []
        
        # Buscar patrones como "el/la [especie]"
        patterns = [
            r'\b(?:el|la|los|las)\s+(\w+)\b',
            r'\b(?:un|una|unos|unas)\s+(\w+)\b'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, subtitles, re.IGNORECASE)
            
            for match in matches:
                potential_species = match.group(1)
                
                # Verificar contexto científico
                context = self._get_context(subtitles, match.start(), 200)
                if self._has_scientific_context(context):
                    if self._is_valid_species_name(potential_species):
                        species_data = self._create_species_entry(
                            potential_species, "Desconocido", subtitles, match.start()
                        )
                        species_data['detection_method'] = 'scientific_context'
                        species_data['confidence'] = 0.7
                        species_list.append(species_data)
        
        return species_list
    
    def _is_valid_species_name(self, name: str) -> bool:
        """Verificar si un nombre podría ser una especie válida."""
        if len(name) < 3:
            return False
        
        if self._is_common_word(name):
            return False
        
        # Verificar que no contenga caracteres extraños
        if re.search(r'[0-9@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', name):
            return False
        
        return True
    
    def _has_scientific_context(self, context: str) -> bool:
        """Verificar si el contexto es científico."""
        scientific_indicators = [
            'especie', 'organismo', 'animal', 'marino', 'bentónico', 'pelágico',
            'taxonomía', 'filo', 'clase', 'orden', 'familia', 'género',
            'identificación', 'muestra', 'colección', 'estudio', 'investigación',
            'expedición', 'biodiversidad', 'ecosistema', 'hábitat'
        ]
        
        context_lower = context.lower()
        return any(indicator in context_lower for indicator in scientific_indicators)
    
    def _create_species_entry(self, name: str, phylum: str, text: str, position: int) -> Dict[str, Any]:
        """Crear entrada de especie con metadatos."""
        timestamp = self._find_nearest_timestamp_corrected(text, position)
        context = self._get_context(text, position, 150)
        canonical_name = self._normalize_common_name(name)
        
        return {
            "common_name": canonical_name,
            "original_common_name": name,
            "scientific_name": self._get_scientific_name(canonical_name),
            "phylum": phylum,
            "class": self._get_class_for_species(canonical_name, phylum),
            "timestamp": timestamp,
            "context": context,
            "additional_info": self._get_additional_info(canonical_name, context),
            "detection_method": "unknown",
            "confidence": 0.5
        }

    def _strip_accents(self, s: str) -> str:
        """Eliminar acentos/diacríticos para normalizar claves de sinónimos."""
        normalized = unicodedata.normalize('NFKD', s)
        return ''.join(c for c in normalized if not unicodedata.combining(c))

    def _normalize_common_name(self, raw_name: str) -> str:
        """Normalizar nombre común de forma simple y genérica:
        - minúsculas y espacios colapsados
        - quitar acentos
        - quitar diminutivos (ito/ita/itos/itas)
        - singularizar heurísticamente el último término (ces→z, es luego s)
        """
        name = raw_name.strip().lower()
        name = re.sub(r"\s+", " ", name)
        name_no_accents = self._strip_accents(name)

        # Excepciones de frases conocidas
        phrase = name_no_accents
        if "caballito de mar" in phrase or "caballitos de mar" in phrase:
            return "caballito de mar"

        tokens = []
        for t in name_no_accents.split(" "):
            # Manejar diminutivos comunes: -cito/-cita/-citos/-citas (ej. camaroncito→camaron)
            t = re.sub(r"(cito|cita|citos|citas)$", "", t)
            # Manejar -ito/-ita/-itos/-itas de forma conservadora (evitar romper caballito)
            if re.search(r"(ito|ita|itos|itas)$", t) and len(t) > 4:
                # Reemplazar sufijo por vocal final aproximada si existe
                t = re.sub(r"itos$", "os", t)
                t = re.sub(r"itas$", "as", t)
                t = re.sub(r"ito$", "o", t)
                t = re.sub(r"ita$", "a", t)
            tokens.append(t)

        # Singularizar el último término
        def singularize(word: str) -> str:
            if re.search(r"ces$", word):
                return re.sub(r"ces$", "z", word)
            if word.endswith("es"):
                return word[:-2]
            if re.search(r"[aeiou]s$", word):
                return word[:-1]
            return word

        if tokens:
            tokens[-1] = singularize(tokens[-1])

        normalized = " ".join(tokens).strip()

        # Restaurar acentos en formas canónicas comunes
        accent_map = {
            "camaron": "camarón",
            "crustaceo": "crustáceo",
            "decapodo": "decápodo",
            "isopodo": "isópodo",
            "anfipodo": "anfípodo",
            "quiton": "quitón",
            "atun": "atún",
            "tiburon": "tiburón",
            "ventonico": "ventónico",
        }
        return accent_map.get(normalized, normalized)
    
    def _find_nearest_timestamp_corrected(self, text: str, position: int) -> str:
        """
        Encontrar el timestamp más cercano CORREGIDO.
        Busca el timestamp real más cercano a la posición.
        """
        # Buscar timestamp antes de la posición
        before_text = text[:position]
        
        # Buscar el último timestamp antes de la posición
        timestamp_matches = list(re.finditer(r'\[(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\]', before_text))
        
        if timestamp_matches:
            # Tomar el último timestamp encontrado (más cercano)
            last_match = timestamp_matches[-1]
            return last_match.group(1)  # Retornar el timestamp de inicio
        
        # Si no encuentra timestamp antes, buscar después
        after_text = text[position:]
        timestamp_match = re.search(r'\[(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\]', after_text)
        
        if timestamp_match:
            return timestamp_match.group(1)
        
        return "00:00:00.000"
    
    def _is_common_word(self, word: str) -> bool:
        """Verificar si una palabra es muy común."""
        return word.lower() in self.common_words
    
    def _filter_by_confidence(self, species_list: List[Dict[str, Any]], 
                            min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """Filtrar especies por nivel de confianza."""
        return [species for species in species_list if species.get('confidence', 0.0) >= min_confidence]
    
    def _analyze_unknown_species(self, species_list: List[Dict[str, Any]], subtitles: str):
        """Analizar especies desconocidas."""
        unknown_species = [s for s in species_list if s.get('phylum') == 'Desconocido']
        
        if unknown_species:
            print(f"\n🔍 Especies potencialmente nuevas detectadas:")
            for species in unknown_species[:5]:  # Mostrar solo las primeras 5
                confidence = species.get('confidence', 0.0)
                if confidence > 0.7:  # Solo mostrar las más probables
                    print(f"   • {species['common_name']} (confianza: {confidence:.2f})")
                    print(f"     Método: {species.get('detection_method', 'unknown')}")
                    print(f"     Timestamp: {species.get('timestamp', 'N/A')}")
                    print(f"     Contexto: {species['context'][:80]}...")
                    print()
            
            self.unknown_species = unknown_species
    
    def _get_context(self, text: str, position: int, context_size: int) -> str:
        """Obtener contexto alrededor de una posición."""
        start = max(0, position - context_size)
        end = min(len(text), position + context_size)
        context = text[start:end].strip()
        
        # Limpiar contexto - eliminar timestamps del formato de subtítulos
        context = re.sub(r'\[\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\]', '', context)
        # Eliminar también timestamps sueltos que puedan quedar
        context = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', context)
        # Eliminar fragmentos de timestamps que puedan quedar
        context = re.sub(r':\d{2}:\d{2}\.\d{3}', '', context)
        context = re.sub(r'\d{2}:\d{2}\.\d{3}', '', context)
        context = re.sub(r'\d{2}:\d{2}', '', context)
        # Eliminar corchetes y fragmentos restantes
        context = re.sub(r'\[.*?\]', '', context)
        context = re.sub(r'-->', '', context)
        # Eliminar cualquier fragmento que contenga números y puntos
        context = re.sub(r'\d+\.\d+', '', context)
        # Eliminar corchetes sueltos y fragmentos restantes
        context = re.sub(r'\[', '', context)
        context = re.sub(r'\]', '', context)
        context = re.sub(r'\n+', ' ', context)
        context = re.sub(r'\s+', ' ', context)
        context = context.strip()
        
        return context
    
    def _get_class_for_species(self, species_name: str, phylum: str) -> str:
        """Obtener clase taxonómica."""
        class_map = {
            'Arthropoda': {
                'balanus': 'Cirripedia', 'langosta': 'Malacostraca',
                'camarón': 'Malacostraca', 'cangrejo': 'Malacostraca',
                'crustáceo': 'Malacostraca', 'decápodo': 'Malacostraca',
                'isópodo': 'Malacostraca', 'anfípodo': 'Malacostraca'
            },
            'Cnidaria': {
                'coral': 'Anthozoa', 'anémona': 'Anthozoa', 'hidro': 'Hydrozoa',
                'octocoral': 'Anthozoa', 'némoda': 'Anthozoa', 'pólipo': 'Anthozoa',
                'pluma de mar': 'Anthozoa', 'nidario': 'Anthozoa'
            },
            'Mollusca': {
                'pulpo': 'Cephalopoda', 'caracol': 'Gastropoda',
                'quitón': 'Polyplacophora', 'vivalvo': 'Bivalvia',
                'calamar': 'Cephalopoda', 'ostra': 'Bivalvia'
            },
            'Porifera': {
                'esponja': 'Demospongiae', 'porífero': 'Demospongiae'
            },
            'Echinodermata': {
                'estrella de mar': 'Asteroidea', 'equinodermo': 'Asteroidea',
                'centa': 'Echinoidea', 'entolla': 'Holothuroidea', 'erizo': 'Echinoidea',
                'pepino de mar': 'Holothuroidea'
            },
            'Annelida': {
                'poliqueto': 'Polychaeta', 'anélido': 'Polychaeta'
            },
            'Chordata': {
                'pez': 'Actinopterygii', 'raya': 'Chondrichthyes',
                'caballito de mar': 'Actinopterygii', 'ventónico': 'Actinopterygii',
                'tiburón': 'Chondrichthyes', 'atún': 'Actinopterygii'
            }
        }
        
        def _norm(s: str) -> str:
            return self._strip_accents(s.lower())

        if phylum in class_map:
            species_norm = _norm(species_name)
            for key, class_name in class_map[phylum].items():
                if _norm(key) in species_norm:
                    return class_name
        
        return "Desconocida"
    
    def _get_scientific_name(self, common_name: str) -> str:
        """Obtener nombre científico aproximado."""
        scientific_names = {
            'balanus': 'Balanus sp.', 'langosta': 'Palinuridae',
            'camarón': 'Caridea', 'cangrejo': 'Brachyura',
            'coral': 'Anthozoa', 'anémona': 'Actiniaria',
            'pulpo': 'Octopoda', 'caracol': 'Gastropoda',
            'esponja': 'Porifera', 'estrella de mar': 'Asteroidea',
            'poliqueto': 'Polychaeta', 'pez': 'Actinopterygii',
            'raya': 'Rajiformes', 'caballito de mar': 'Hippocampus sp.',
            'quitón': 'Polyplacophora', 'vivalvo': 'Bivalvia',
            'hidro': 'Hydrozoa', 'octocoral': 'Octocorallia',
            'némoda': 'Actiniaria', 'pólipo': 'Anthozoa',
            'pluma de mar': 'Pennatulacea', 'centa': 'Echinoidea',
            'entolla': 'Holothuroidea', 'ventónico': 'Actinopterygii',
            'isópodo': 'Isopoda', 'anfípodo': 'Amphipoda',
            'nidario': 'Anthozoa', 'nidroso': 'Anthozoa',
            'calamar': 'Teuthida', 'ostra': 'Ostreidae',
            'mejillón': 'Mytilidae', 'erizo': 'Echinoidea',
            'anélido': 'Annelida', 'tiburón': 'Selachimorpha',
            'atún': 'Thunnus', 'pepino de mar': 'Holothuroidea'
        }
        
        def _norm(s: str) -> str:
            return self._strip_accents(s.lower())

        name_norm = _norm(common_name)
        for key, scientific_name in scientific_names.items():
            if _norm(key) in name_norm:
                return scientific_name
        
        return ""
    
    def _get_additional_info(self, species_name: str, context: str) -> str:
        """Extraer información adicional del contexto."""
        info = []
        
        # Buscar información sobre profundidad
        depth_match = re.search(r'(\d+)\s*metros?', context)
        if depth_match:
            info.append(f"Profundidad: {depth_match.group(1)}m")
        
        # Buscar información sobre tamaño
        size_match = re.search(r'(\d+)\s*cm', context)
        if size_match:
            info.append(f"Tamaño: {size_match.group(1)}cm")
        
        # Buscar información sobre comportamiento
        behavior_keywords = ['comportamiento', 'movimiento', 'alimentación', 'reproducción']
        for keyword in behavior_keywords:
            if keyword in context.lower():
                info.append(f"Menciona {keyword}")
        
        return "; ".join(info) if info else ""
    
    def _remove_duplicates(self, species_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Eliminar duplicados basados en nombre y proximidad temporal."""
        from datetime import datetime, timedelta
        
        def parse_timestamp(timestamp_str: str) -> datetime:
            """Convertir timestamp string a datetime object."""
            try:
                # Formato esperado: HH:MM:SS.mmm
                time_parts = timestamp_str.split(':')
                if len(time_parts) == 3:
                    seconds_parts = time_parts[2].split('.')
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1])
                    seconds = int(seconds_parts[0])
                    milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
                    
                    return datetime(2024, 1, 1, hours, minutes, seconds, milliseconds * 1000)
                return datetime.min
            except:
                return datetime.min
        
        def time_difference(timestamp1: str, timestamp2: str) -> float:
            """Calcular diferencia en segundos entre dos timestamps."""
            dt1 = parse_timestamp(timestamp1)
            dt2 = parse_timestamp(timestamp2)
            return abs((dt2 - dt1).total_seconds())
        
        # Agrupar especies por nombre (case insensitive)
        species_groups = {}
        for species in species_list:
            name_lower = species['common_name'].lower()
            if name_lower not in species_groups:
                species_groups[name_lower] = []
            species_groups[name_lower].append(species)
        
        # Para cada grupo, mantener solo la primera detección en un rango temporal
        unique_species = []
        time_threshold = 300.0  # 5 minutos de diferencia máxima
        
        for name_lower, group in species_groups.items():
            # Ordenar por timestamp
            group.sort(key=lambda x: parse_timestamp(x.get('timestamp', '00:00:00.000')))
            
            kept_species = []
            for species in group:
                timestamp = species.get('timestamp', '00:00:00.000')
                
                # Verificar si hay una especie similar ya guardada en el rango temporal
                is_duplicate = False
                for kept in kept_species:
                    kept_timestamp = kept.get('timestamp', '00:00:00.000')
                    if time_difference(timestamp, kept_timestamp) <= time_threshold:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    kept_species.append(species)
            
            unique_species.extend(kept_species)
        
        print(f"🔍 Deduplicación: {len(species_list)} -> {len(unique_species)} especies únicas")
        return unique_species
    
    def organize_by_taxonomy(self, species_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Organizar especies por taxonomía."""
        taxonomy = {}
        
        for species in species_list:
            phylum = species.get('phylum', 'Desconocido')
            if phylum not in taxonomy:
                taxonomy[phylum] = []
            
            taxonomy[phylum].append(species)
        
        return taxonomy
    
    def generate_fixed_report(self, taxonomy_data: Dict[str, Any]) -> str:
        """Generar reporte corregido."""
        report = []
        report.append("=" * 60)
        report.append("🌊 REPORTE CORREGIDO DE BIODIVERSIDAD MARINA")
        report.append("Expedición Cañón de Mar del Plata")
        report.append("=" * 60)
        report.append("")
        
        total_species = sum(len(species) for species in taxonomy_data.values())
        report.append(f"📊 Total de especies identificadas: {total_species}")
        
        # Estadísticas de detección
        detection_methods = Counter()
        confidence_levels = []
        
        for phylum_species in taxonomy_data.values():
            for species in phylum_species:
                method = species.get('detection_method', 'unknown')
                detection_methods[method] += 1
                confidence_levels.append(species.get('confidence', 0.0))
        
        report.append(f"🔍 Métodos de detección utilizados:")
        for method, count in detection_methods.most_common():
            report.append(f"   • {method}: {count} especies")
        
        if confidence_levels:
            avg_confidence = sum(confidence_levels) / len(confidence_levels)
            report.append(f"📈 Confianza promedio: {avg_confidence:.2f}")
        
        report.append("")
        
        # Ordenar por número de especies
        sorted_phyla = sorted(taxonomy_data.items(), key=lambda x: len(x[1]), reverse=True)
        
        for phylum, species_list in sorted_phyla:
            report.append(f"🦠 FILO: {phylum.upper()}")
            report.append(f"   Especies encontradas: {len(species_list)}")
            report.append("")
            
            for species in species_list:
                report.append(f"   • {species.get('common_name', 'N/A')}")
                if species.get('scientific_name'):
                    report.append(f"     Nombre científico: {species['scientific_name']}")
                if species.get('class') and species['class'] != "Desconocida":
                    report.append(f"     Clase: {species['class']}")
                if species.get('timestamp'):
                    report.append(f"     Timestamp: {species['timestamp']}")
                if species.get('confidence'):
                    report.append(f"     Confianza: {species['confidence']:.2f}")
                if species.get('detection_method'):
                    report.append(f"     Método: {species['detection_method']}")
                if species.get('additional_info'):
                    report.append(f"     Info adicional: {species['additional_info']}")
                report.append("")
        
        return "\n".join(report)
    
    def save_fixed_results(self, species_data: List[Dict[str, Any]], 
                          taxonomy_data: Dict[str, Any], 
                          output_file: str = "biodiversity_results.json"):
        """Guardar resultados corregidos en archivo JSON."""
        results = {
            "metadata": {
                "expedition": "Cañón de Mar del Plata",
                "analysis_date": datetime.now().isoformat(),
                "total_species": len(species_data),
                "phyla_count": len(taxonomy_data),
                "method": "fixed_text_processing",
                "unknown_species_count": len(self.unknown_species)
            },
            "species_data": species_data,
            "taxonomy_data": taxonomy_data,
            "unknown_species": self.unknown_species
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Resultados guardados en: {output_file}")
    
    def analyze_biodiversity(self, subtitles_file: str = "subtitulos_espanol.txt"):
        """Analizar biodiversidad con timestamps corregidos."""
        print("🔍 Iniciando análisis de biodiversidad marina...")
        
        # Cargar subtítulos
        print("📖 Cargando subtítulos...")
        subtitles = self.load_subtitles(subtitles_file)
        
        # Extraer especies con timestamps corregidos
        print("🐠 Extrayendo especies con timestamps corregidos...")
        species_data = self.extract_species_mentions(subtitles)
        
        # Organizar por taxonomía
        print("📋 Organizando por taxonomía...")
        taxonomy_data = self.organize_by_taxonomy(species_data)
        
        # Generar reporte corregido
        print("📊 Generando reporte corregido...")
        report = self.generate_fixed_report(taxonomy_data)
        
        # Guardar resultados
        self.save_fixed_results(species_data, taxonomy_data)
        
        # Mostrar reporte
        print("\n" + "=" * 60)
        print("📋 REPORTE CORREGIDO")
        print("=" * 60)
        print(report)
        
        return species_data, taxonomy_data

def main():
    """Función principal para ejecutar el analizador corregido."""
    analyzer = BiodiversityAnalyzerFixed()
    
    try:
        species_data, taxonomy_data = analyzer.analyze_biodiversity()
        print("\n✅ Análisis completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")

if __name__ == "__main__":
    main() 