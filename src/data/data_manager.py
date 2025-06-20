import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class DataManager:
    """Gestionnaire centralisé pour toutes les données JSON de l'application"""
    
    def __init__(self, data_dir="data"):
        """
        Initialise le gestionnaire de données.
        
        Args:
            data_dir (str): Répertoire des fichiers de données
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Fichiers de données
        self.files = {
            'airports': self.data_dir / 'airports.json',
            'aircraft_models': self.data_dir / 'aircraft_models.json',
            'aircraft': self.data_dir / 'aircraft.json',
            'personnel': self.data_dir / 'personnel.json',
            'flights': self.data_dir / 'flights.json',
            'passengers': self.data_dir / 'passengers.json',
            'reservations': self.data_dir / 'reservations.json',
            'company': self.data_dir / 'company.json'
        }
        
        # Cache des données
        self._cache = {}
        
        # Initialiser les fichiers vides si nécessaire
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialise les fichiers de données vides s'ils n'existent pas"""
        default_structures = {
            'aircraft': {'aircraft': []},
            'personnel': {'personnel': []},
            'flights': {'flights': []},
            'passengers': {'passengers': []},
            'reservations': {'reservations': []},
            'company': {
                'nom': 'Ma Compagnie Aérienne',
                'created_at': datetime.now().isoformat(),
                'statistics': {
                    'total_flights': 0,
                    'total_passengers': 0,
                    'total_aircraft': 0,
                    'total_personnel': 0
                }
            }
        }
        
        for file_key, default_data in default_structures.items():
            file_path = self.files[file_key]
            if not file_path.exists():
                self.save_data(file_key, default_data)
                print(f"✓ Fichier {file_path.name} créé")
    
    def load_data(self, file_key: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Charge les données depuis un fichier JSON.
        
        Args:
            file_key (str): Clé du fichier à charger
            use_cache (bool): Utiliser le cache si disponible
            
        Returns:
            Dict: Données chargées
        """
        if use_cache and file_key in self._cache:
            return self._cache[file_key]
        
        file_path = self.files.get(file_key)
        if not file_path:
            print(f"⚠️ Fichier {file_key} non configuré")
            return {}
            
        if not file_path.exists():
            print(f"⚠️ Fichier {file_path.name} non trouvé, création d'un fichier vide")
            # Créer un fichier vide avec la structure appropriée
            empty_data = self._get_empty_structure(file_key)
            self.save_data(file_key, empty_data)
            return empty_data
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier que c'est bien un dictionnaire
            if not isinstance(data, dict):
                print(f"⚠️ Format invalide dans {file_key}, conversion en dictionnaire")
                if isinstance(data, list):
                    # Convertir liste en dictionnaire avec clé appropriée
                    key_name = self._get_list_key_name(file_key)
                    data = {key_name: data}
                else:
                    data = {}
            
            self._cache[file_key] = data
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON dans {file_key}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file_key}: {e}")
            return {}
    
    def _get_empty_structure(self, file_key: str) -> Dict[str, Any]:
        """Retourne la structure vide appropriée pour un type de fichier"""
        structures = {
            'airports': {'airports': []},
            'aircraft_models': {'aircraft_models': []},
            'aircraft': {'aircraft': []},
            'personnel': {'personnel': []},
            'flights': {'flights': []},
            'passengers': {'passengers': []},
            'reservations': {'reservations': []},
            'company': {
                'nom': 'Ma Compagnie Aérienne',
                'created_at': datetime.now().isoformat(),
                'statistics': {}
            }
        }
        return structures.get(file_key, {})
    
    def _get_list_key_name(self, file_key: str) -> str:
        """Retourne le nom de clé approprié pour une liste"""
        return file_key if file_key.endswith('s') else f"{file_key}s"
    
    def save_data(self, file_key: str, data: Dict[str, Any]) -> bool:
        """
        Sauvegarde les données dans un fichier JSON.
        
        Args:
            file_key (str): Clé du fichier à sauvegarder
            data (Dict): Données à sauvegarder
            
        Returns:
            bool: True si réussi
        """
        file_path = self.files.get(file_key)
        if not file_path:
            print(f"❌ Fichier {file_key} non configuré")
            return False
        
        try:
            # Backup du fichier existant
            if file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                file_path.replace(backup_path)
            
            # Ajout timestamp de modification
            if isinstance(data, dict):
                data['last_modified'] = datetime.now().isoformat()
            
            # Sauvegarde
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Mise à jour cache
            self._cache[file_key] = data
            
            print(f"✓ Données sauvegardées: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde {file_key}: {e}")
            return False
    
    def get_airports(self) -> List[Dict[str, Any]]:
        """Retourne la liste des aéroports"""
        try:
            data = self.load_data('airports')
            if isinstance(data, dict) and 'airports' in data:
                return data.get('airports', [])
            elif isinstance(data, list):
                return data
            else:
                print("⚠️ Format de données airports invalide")
                return []
        except Exception as e:
            print(f"❌ Erreur chargement airports: {e}")
            return []
    
    def get_aircraft_models(self) -> List[Dict[str, Any]]:
        """Retourne la liste des modèles d'avions"""
        try:
            data = self.load_data('aircraft_models')
            if isinstance(data, dict) and 'aircraft_models' in data:
                return data.get('aircraft_models', [])
            elif isinstance(data, list):
                return data
            else:
                print("⚠️ Format de données aircraft_models invalide")
                return []
        except Exception as e:
            print(f"❌ Erreur chargement aircraft_models: {e}")
            return []
    
    def get_aircraft(self) -> List[Dict[str, Any]]:
        """Retourne la liste des avions de la flotte"""
        data = self.load_data('aircraft')
        return data.get('aircraft', [])
    
    def add_aircraft(self, aircraft_data: Dict[str, Any]) -> bool:
        """Ajoute un avion à la flotte"""
        data = self.load_data('aircraft')
        aircraft_list = data.get('aircraft', [])
        
        # Vérification unicité ID
        aircraft_id = aircraft_data.get('num_id')
        if any(a.get('num_id') == aircraft_id for a in aircraft_list):
            print(f"❌ Avion {aircraft_id} existe déjà")
            return False
        
        aircraft_data['created_at'] = datetime.now().isoformat()
        aircraft_list.append(aircraft_data)
        data['aircraft'] = aircraft_list
        
        return self.save_data('aircraft', data)
    
    def update_aircraft(self, aircraft_id: str, aircraft_data: Dict[str, Any]) -> bool:
        """Met à jour un avion existant"""
        data = self.load_data('aircraft')
        aircraft_list = data.get('aircraft', [])
        
        for i, aircraft in enumerate(aircraft_list):
            if aircraft.get('num_id') == aircraft_id:
                aircraft_data['updated_at'] = datetime.now().isoformat()
                aircraft_list[i] = {**aircraft, **aircraft_data}
                data['aircraft'] = aircraft_list
                return self.save_data('aircraft', data)
        
        print(f"❌ Avion {aircraft_id} non trouvé")
        return False
    
    def delete_aircraft(self, aircraft_id: str) -> bool:
        """Supprime un avion de la flotte"""
        data = self.load_data('aircraft')
        aircraft_list = data.get('aircraft', [])
        
        original_length = len(aircraft_list)
        aircraft_list = [a for a in aircraft_list if a.get('num_id') != aircraft_id]
        
        if len(aircraft_list) < original_length:
            data['aircraft'] = aircraft_list
            return self.save_data('aircraft', data)
        
        print(f"❌ Avion {aircraft_id} non trouvé pour suppression")
        return False
    
    def get_personnel(self) -> List[Dict[str, Any]]:
        """Retourne la liste du personnel"""
        data = self.load_data('personnel')
        return data.get('personnel', [])
    
    def update_personnel(self, personnel_id: str, personnel_data: Dict[str, Any]) -> bool:
        """Met à jour un membre du personnel existant"""
        data = self.load_data('personnel')
        personnel_list = data.get('personnel', [])
        
        for i, person in enumerate(personnel_list):
            if person.get('id_employe') == personnel_id:
                personnel_data['updated_at'] = datetime.now().isoformat()
                personnel_list[i] = {**person, **personnel_data}
                data['personnel'] = personnel_list
                return self.save_data('personnel', data)
        
        print(f"❌ Personnel {personnel_id} non trouvé")
        return False
    
    def delete_personnel(self, personnel_id: str) -> bool:
        """Supprime un membre du personnel"""
        data = self.load_data('personnel')
        personnel_list = data.get('personnel', [])
        
        original_length = len(personnel_list)
        personnel_list = [p for p in personnel_list if p.get('id_employe') != personnel_id]
        
        if len(personnel_list) < original_length:
            data['personnel'] = personnel_list
            return self.save_data('personnel', data)
        
        print(f"❌ Personnel {personnel_id} non trouvé pour suppression")
        return False
        """Ajoute un membre du personnel"""
        data = self.load_data('personnel')
        personnel_list = data.get('personnel', [])
        
        # Vérification unicité ID
        personnel_id = personnel_data.get('id_employe')
        if any(p.get('id_employe') == personnel_id for p in personnel_list):
            print(f"❌ Personnel {personnel_id} existe déjà")
            return False
        
        personnel_data['created_at'] = datetime.now().isoformat()
        personnel_list.append(personnel_data)
        data['personnel'] = personnel_list
        
        return self.save_data('personnel', data)
    
    def get_flights(self) -> List[Dict[str, Any]]:
        """Retourne la liste des vols"""
        data = self.load_data('flights')
        return data.get('flights', [])
    
    def add_flight(self, flight_data: Dict[str, Any]) -> bool:
        """Ajoute un vol"""
        data = self.load_data('flights')
        flights_list = data.get('flights', [])
        
        # Vérification unicité numéro vol
        flight_number = flight_data.get('numero_vol')
        if any(f.get('numero_vol') == flight_number for f in flights_list):
            print(f"❌ Vol {flight_number} existe déjà")
            return False
        
        flight_data['created_at'] = datetime.now().isoformat()
        flights_list.append(flight_data)
        data['flights'] = flights_list
        
        return self.save_data('flights', data)
    
    def get_passengers(self) -> List[Dict[str, Any]]:
        """Retourne la liste des passagers"""
        data = self.load_data('passengers')
        return data.get('passengers', [])
    
    def add_passenger(self, passenger_data: Dict[str, Any]) -> bool:
        """Ajoute un passager"""
        data = self.load_data('passengers')
        passengers_list = data.get('passengers', [])
        
        # Vérification unicité ID
        passenger_id = passenger_data.get('id_passager')
        if any(p.get('id_passager') == passenger_id for p in passengers_list):
            print(f"❌ Passager {passenger_id} existe déjà")
            return False
        
        passenger_data['created_at'] = datetime.now().isoformat()
    def update_passenger(self, passenger_id: str, passenger_data: Dict[str, Any]) -> bool:
        """Met à jour un passager existant"""
        data = self.load_data('passengers')
        passengers_list = data.get('passengers', [])
        
        for i, passenger in enumerate(passengers_list):
            if passenger.get('id_passager') == passenger_id:
                passenger_data['updated_at'] = datetime.now().isoformat()
                passengers_list[i] = {**passenger, **passenger_data}
                data['passengers'] = passengers_list
                return self.save_data('passengers', data)
        
        print(f"❌ Passager {passenger_id} non trouvé")
        return False
    
    def delete_passenger(self, passenger_id: str) -> bool:
        """Supprime un passager"""
        data = self.load_data('passengers')
        passengers_list = data.get('passengers', [])
        
        original_length = len(passengers_list)
        passengers_list = [p for p in passengers_list if p.get('id_passager') != passenger_id]
        
        if len(passengers_list) < original_length:
            data['passengers'] = passengers_list
            return self.save_data('passengers', data)
        
        print(f"❌ Passager {passenger_id} non trouvé pour suppression")
        return False
    
    def update_flight(self, flight_number: str, flight_data: Dict[str, Any]) -> bool:
        """Met à jour un vol existant"""
        data = self.load_data('flights')
        flights_list = data.get('flights', [])
        
        for i, flight in enumerate(flights_list):
            if flight.get('numero_vol') == flight_number:
                flight_data['updated_at'] = datetime.now().isoformat()
                flights_list[i] = {**flight, **flight_data}
                data['flights'] = flights_list
                return self.save_data('flights', data)
        
        print(f"❌ Vol {flight_number} non trouvé")
        return False
    
    def delete_flight(self, flight_number: str) -> bool:
        """Supprime un vol"""
        data = self.load_data('flights')
        flights_list = data.get('flights', [])
        
        original_length = len(flights_list)
        flights_list = [f for f in flights_list if f.get('numero_vol') != flight_number]
        
        if len(flights_list) < original_length:
            data['flights'] = flights_list
            return self.save_data('flights', data)
        
        print(f"❌ Vol {flight_number} non trouvé pour suppression")
        return False
    
    def get_reservations(self) -> List[Dict[str, Any]]:
        """Retourne la liste des réservations"""
        data = self.load_data('reservations')
        return data.get('reservations', [])
    
    def add_reservation(self, reservation_data: Dict[str, Any]) -> bool:
        """Ajoute une réservation"""
        data = self.load_data('reservations')
        reservations_list = data.get('reservations', [])
        
        # Vérification unicité ID
        reservation_id = reservation_data.get('id_reservation')
        if any(r.get('id_reservation') == reservation_id for r in reservations_list):
            print(f"❌ Réservation {reservation_id} existe déjà")
            return False
        
        reservation_data['created_at'] = datetime.now().isoformat()
        reservations_list.append(reservation_data)
        data['reservations'] = reservations_list
        
        return self.save_data('reservations', data)
    
    def update_reservation(self, reservation_id: str, reservation_data: Dict[str, Any]) -> bool:
        """Met à jour une réservation existante"""
        data = self.load_data('reservations')
        reservations_list = data.get('reservations', [])
        
        for i, reservation in enumerate(reservations_list):
            if reservation.get('id_reservation') == reservation_id:
                reservation_data['updated_at'] = datetime.now().isoformat()
                reservations_list[i] = {**reservation, **reservation_data}
                data['reservations'] = reservations_list
                return self.save_data('reservations', data)
        
        print(f"❌ Réservation {reservation_id} non trouvée")
        return False
    
    def get_company_info(self) -> Dict[str, Any]:
        """Retourne les informations de la compagnie"""
        return self.load_data('company')
    
    def update_company_stats(self, stats: Dict[str, Any]) -> bool:
        """Met à jour les statistiques de la compagnie"""
        data = self.load_data('company')
        if 'statistics' not in data:
            data['statistics'] = {}
        
        data['statistics'].update(stats)
        return self.save_data('company', data)
    
    def search_data(self, file_key: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """
        Recherche des éléments dans une liste de données.
        
        Args:
            file_key (str): Fichier à rechercher
            field (str): Champ à chercher
            value: Valeur à chercher
            
        Returns:
            List: Éléments trouvés
        """
        data = self.load_data(file_key)
        
        # Détermine la clé de liste selon le fichier
        list_keys = {
            'aircraft': 'aircraft',
            'personnel': 'personnel',
            'flights': 'flights',
            'passengers': 'passengers',
            'reservations': 'reservations',
            'airports': 'airports',
            'aircraft_models': 'aircraft_models'
        }
        
        list_key = list_keys.get(file_key)
        if not list_key:
            return []
        
        items = data.get(list_key, [])
        
        # Recherche simple
        if isinstance(value, str):
            value = value.lower()
            return [
                item for item in items 
                if field in item and value in str(item[field]).lower()
            ]
        else:
            return [
                item for item in items 
                if field in item and item[field] == value
            ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calcule et retourne les statistiques générales"""
        stats = {
            'total_aircraft': len(self.get_aircraft()),
            'total_personnel': len(self.get_personnel()),
            'total_flights': len(self.get_flights()),
            'total_passengers': len(self.get_passengers()),
            'total_reservations': len(self.get_reservations()),
            'total_airports': len(self.get_airports())
        }
        
        # Statistiques des vols par statut
        flights = self.get_flights()
        flight_statuses = {}
        for flight in flights:
            status = flight.get('statut', 'unknown')
            flight_statuses[status] = flight_statuses.get(status, 0) + 1
        
        stats['flight_statuses'] = flight_statuses
        
        # Statistiques des avions par état
        aircraft = self.get_aircraft()
        aircraft_states = {}
        for plane in aircraft:
            state = plane.get('etat', 'unknown')
            aircraft_states[state] = aircraft_states.get(state, 0) + 1
        
        stats['aircraft_states'] = aircraft_states
        
        # Mise à jour des stats de la compagnie
        self.update_company_stats(stats)
        
        return stats
    
    def clear_cache(self):
        """Vide le cache des données"""
        self._cache.clear()
        print("✓ Cache vidé")
    
    def backup_all_data(self) -> bool:
        """Crée une sauvegarde de toutes les données"""
        backup_dir = self.data_dir / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_subdir = backup_dir / f'backup_{timestamp}'
        backup_subdir.mkdir(exist_ok=True)
        
        try:
            for file_key, file_path in self.files.items():
                if file_path.exists():
                    backup_file = backup_subdir / file_path.name
                    with open(file_path, 'r', encoding='utf-8') as src:
                        with open(backup_file, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
            
            print(f"✓ Sauvegarde créée: {backup_subdir}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Valide l'intégrité des données et retourne un rapport"""
        report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'files_checked': 0
        }
        
        for file_key in self.files.keys():
            try:
                data = self.load_data(file_key, use_cache=False)
                if data:
                    report['files_checked'] += 1
                else:
                    report['warnings'].append(f"Fichier {file_key} vide ou illisible")
                    
            except Exception as e:
                report['valid'] = False
                report['errors'].append(f"Erreur dans {file_key}: {e}")
        
        # Vérifications spécifiques
        # Vérifier que les vols référencent des avions existants
        flights = self.get_flights()
        aircraft_ids = {a.get('num_id') for a in self.get_aircraft()}
        
        for flight in flights:
            aircraft_id = flight.get('avion_utilise')
            if aircraft_id and aircraft_id not in aircraft_ids:
                report['warnings'].append(
                    f"Vol {flight.get('numero_vol')} référence un avion inexistant: {aircraft_id}"
                )
        
        return report