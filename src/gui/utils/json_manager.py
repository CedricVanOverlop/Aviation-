"""
Gestionnaire de persistance JSON pour toutes les données de l'application
Gère la lecture, écriture, sauvegarde et validation des données
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JSONDataManager:
    """Gestionnaire de persistance JSON pour toutes les données"""
    
    def __init__(self, data_folder="data"):
        self.data_folder = data_folder
        self.ensure_data_folder()
        
        # Fichiers de données
        self.files = {
            'avions': 'avions.json',
            'personnels': 'personnels.json', 
            'passagers': 'passagers.json',
            'vols': 'vols.json',
            'aeroports': 'aeroports.json',
            'reservations': 'reservations.json',
            'compagnies': 'compagnies.json',
            'simulation': 'simulation_state.json',
            'events': 'events_log.json',
            'config': 'app_config.json'
        }
        
        self.init_files()
        logger.info(f"JSONDataManager initialisé avec dossier: {self.data_folder}")
    
    def ensure_data_folder(self):
        """Crée le dossier data s'il n'existe pas"""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            logger.info(f"Dossier de données créé: {self.data_folder}")
    
    def get_file_path(self, file_type: str) -> str:
        """Retourne le chemin complet d'un fichier"""
        if file_type not in self.files:
            raise ValueError(f"Type de fichier inconnu: {file_type}")
        return os.path.join(self.data_folder, self.files[file_type])
    
    def init_files(self):
        """Initialise les fichiers JSON s'ils n'existent pas"""
        for file_type in self.files:
            file_path = self.get_file_path(file_type)
            if not os.path.exists(file_path):
                default_data = self.get_default_data(file_type)
                self.save_data(file_type, default_data)
                logger.info(f"Fichier initialisé: {file_path}")
    
    def get_default_data(self, file_type: str) -> Any:
        """Retourne les données par défaut selon le type de fichier"""
        defaults = {
            'simulation': {
                'current_time': datetime.now().isoformat(),
                'speed_multiplier': 1.0,
                'is_running': False,
                'last_update': datetime.now().isoformat(),
                'events_scheduled': []
            },
            'events': [],
            'config': {
                'app_name': 'Gestion Aéroportuaire',
                'version': '1.0.0',
                'last_backup': None,
                'auto_save': True,
                'auto_save_interval': 300,  # secondes
                'simulation_speed_options': [0.5, 1, 2, 5, 10, 30, 60],
                'default_simulation_speed': 1.0,
                'max_events_log': 1000,
                'ui_settings': {
                    'window_width': 1400,
                    'window_height': 900,
                    'theme': 'default'
                }
            },
            'aeroports': {
                'default_airport': {
                    'nom': 'Aéroport International',
                    'code_iata': 'ARI',
                    'coordonnees': {
                        'longitude': 2.3522,
                        'latitude': 48.8566
                    },
                    'pistes': {
                        'piste_01': {
                            'numero': '07L',
                            'longueur': 3000,
                            'largeur': 45,
                            'surface': 'Asphalte',
                            'statut': 'disponible'
                        },
                        'piste_02': {
                            'numero': '25R',
                            'longueur': 3500,
                            'largeur': 50,
                            'surface': 'Asphalte',
                            'statut': 'disponible'
                        }
                    },
                    'villes_desservies': ['Paris', 'Lyon', 'Marseille']
                }
            }
        }
        
        return defaults.get(file_type, {})
    
    def load_data(self, file_type: str) -> Any:
        """Charge les données depuis un fichier JSON"""
        try:
            file_path = self.get_file_path(file_type)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Données chargées depuis: {file_path}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors du chargement de {file_type}: {e}")
            default_data = self.get_default_data(file_type)
            self.save_data(file_type, default_data)
            return default_data
    
    def save_data(self, file_type: str, data: Any):
        """Sauvegarde les données dans un fichier JSON"""
        try:
            file_path = self.get_file_path(file_type)
            
            # Créer une copie de sauvegarde si le fichier existe
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            
            logger.debug(f"Données sauvegardées dans: {file_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de {file_type}: {e}")
            raise
    
    def _json_serializer(self, obj):
        """Sérialiseur personnalisé pour JSON"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'value'):  # Pour les Enums
            return obj.value
        return str(obj)
    
    def backup_data(self) -> str:
        """Crée une sauvegarde complète de toutes les données"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_folder = os.path.join(self.data_folder, f"backup_{timestamp}")
        
        try:
            os.makedirs(backup_folder, exist_ok=True)
            
            files_backed_up = 0
            for file_type in self.files:
                src = self.get_file_path(file_type)
                if os.path.exists(src):
                    dst = os.path.join(backup_folder, self.files[file_type])
                    shutil.copy2(src, dst)
                    files_backed_up += 1
            
            # Mettre à jour la config avec la date de dernière sauvegarde
            config = self.load_data('config')
            config['last_backup'] = datetime.now().isoformat()
            self.save_data('config', config)
            
            logger.info(f"Sauvegarde créée: {backup_folder} ({files_backed_up} fichiers)")
            return backup_folder
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise
    
    def restore_from_backup(self, backup_folder: str) -> bool:
        """Restaure les données depuis une sauvegarde"""
        try:
            if not os.path.exists(backup_folder):
                raise FileNotFoundError(f"Dossier de sauvegarde non trouvé: {backup_folder}")
            
            files_restored = 0
            for file_type in self.files:
                backup_file = os.path.join(backup_folder, self.files[file_type])
                if os.path.exists(backup_file):
                    dst = self.get_file_path(file_type)
                    shutil.copy2(backup_file, dst)
                    files_restored += 1
            
            logger.info(f"Restauration effectuée: {files_restored} fichiers restaurés")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            return False
    
    def cleanup_old_backups(self, keep_last: int = 10):
        """Nettoie les anciennes sauvegardes"""
        try:
            backup_folders = []
            for item in os.listdir(self.data_folder):
                if item.startswith('backup_') and os.path.isdir(os.path.join(self.data_folder, item)):
                    backup_folders.append(item)
            
            # Trier par date (nom du dossier)
            backup_folders.sort(reverse=True)
            
            # Supprimer les anciens
            for folder in backup_folders[keep_last:]:
                folder_path = os.path.join(self.data_folder, folder)
                shutil.rmtree(folder_path)
                logger.info(f"Ancienne sauvegarde supprimée: {folder}")
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des sauvegardes: {e}")
    
    def validate_data_integrity(self) -> Dict[str, bool]:
        """Valide l'intégrité de tous les fichiers de données"""
        results = {}
        
        for file_type in self.files:
            try:
                data = self.load_data(file_type)
                # Validation basique
                if isinstance(data, (dict, list)):
                    results[file_type] = True
                else:
                    results[file_type] = False
                    logger.warning(f"Format de données invalide pour: {file_type}")
                    
            except Exception as e:
                results[file_type] = False
                logger.error(f"Erreur de validation pour {file_type}: {e}")
        
        return results
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les données"""
        stats = {}
        
        try:
            # Statistiques par type de fichier
            for file_type in self.files:
                file_path = self.get_file_path(file_type)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    data = self.load_data(file_type)
                    if isinstance(data, dict):
                        item_count = len(data)
                    elif isinstance(data, list):
                        item_count = len(data)
                    else:
                        item_count = 1
                    
                    stats[file_type] = {
                        'size_bytes': file_size,
                        'last_modified': modification_time.isoformat(),
                        'item_count': item_count
                    }
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
        
        return stats
    
    def export_data(self, export_path: str, file_types: Optional[List[str]] = None):
        """Exporte les données vers un dossier spécifique"""
        if file_types is None:
            file_types = list(self.files.keys())
        
        try:
            os.makedirs(export_path, exist_ok=True)
            
            for file_type in file_types:
                if file_type in self.files:
                    src = self.get_file_path(file_type)
                    if os.path.exists(src):
                        dst = os.path.join(export_path, self.files[file_type])
                        shutil.copy2(src, dst)
            
            logger.info(f"Données exportées vers: {export_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}")
            raise