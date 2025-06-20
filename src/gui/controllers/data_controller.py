"""
Contrôleur principal pour la gestion des données avec intégration Core
Fait le pont entre l'interface graphique et les classes métier
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import logging

# Imports Core
from Core.aviation import Avion, Aeroport, PisteAtterrissage, Coordonnees
from Core.vol import Vol
from Core.personnes import Personnel, Passager
from Core.reservation import Reservation
from Core.gestion import Compagnie, GestionRetard
from Core.meteo import Meteo
from Core.enums import *

from ..utils.json_manager import JSONDataManager
from ..utils.time_simulator import TimeSimulator

logger = logging.getLogger(__name__)

class DataController:
    """Contrôleur principal pour la gestion des données avec Core"""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        self.simulator = TimeSimulator(data_manager)
        
        # Caches en mémoire pour performance
        self._avions_cache: Dict[str, Avion] = {}
        self._vols_cache: Dict[str, Vol] = {}
        self._personnels_cache: Dict[str, Personnel] = {}
        self._passagers_cache: Dict[str, Passager] = {}
        self._aeroports_cache: Dict[str, Aeroport] = {}
        self._compagnies_cache: Dict[str, Compagnie] = {}
        self._reservations_cache: Dict[str, Reservation] = {}
        
        # Enregistrer les gestionnaires d'événements
        self.setup_event_handlers()
        
        # Charger toutes les données
        self.load_all_data()
        
        logger.info("DataController initialisé")
    
    def setup_event_handlers(self):
        """Configure les gestionnaires d'événements de simulation"""
        self.simulator.register_event_handler('vol', self.handle_vol_event)
        self.simulator.register_event_handler('avion', self.handle_avion_event)
        self.simulator.register_event_handler('maintenance', self.handle_maintenance_event)
        self.simulator.register_event_handler('personnel', self.handle_personnel_event)
    
    def load_all_data(self):
        """Charge toutes les données depuis JSON vers les objets Core"""
        logger.info("Chargement de toutes les données...")
        
        # Charger dans l'ordre de dépendance
        self.load_aeroports()
        self.load_avions() 
        self.load_personnels()
        self.load_passagers()
        self.load_compagnies()
        self.load_vols()
        self.load_reservations()
        
        logger.info("Toutes les données chargées avec succès")
    
    def save_all_data(self):
        """Sauvegarde toutes les données des objets Core vers JSON"""
        logger.info("Sauvegarde de toutes les données...")
        
        self.save_aeroports()
        self.save_avions()
        self.save_personnels()
        self.save_passagers()
        self.save_compagnies()
        self.save_vols()
        self.save_reservations()
        
        logger.info("Toutes les données sauvegardées")
    
    # =====================================================
    # GESTION DES AÉROPORTS
    # =====================================================
    
    def load_aeroports(self):
        """Charge les aéroports depuis JSON"""
        aeroports_data = self.data_manager.load_data('aeroports')
        
        for aeroport_id, aeroport_dict in aeroports_data.items():
            try:
                aeroport = self.dict_to_aeroport(aeroport_dict)
                self._aeroports_cache[aeroport_id] = aeroport
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'aéroport {aeroport_id}: {e}")
    
    def dict_to_aeroport(self, aeroport_dict: Dict) -> Aeroport:
        """Convertit un dict JSON en objet Aeroport"""
        coords = Coordonnees(
            aeroport_dict['coordonnees']['longitude'],
            aeroport_dict['coordonnees']['latitude']
        )
        
        aeroport = Aeroport(
            nom=aeroport_dict['nom'],
            code_iata=aeroport_dict['code_iata'],
            coordonnees=coords,
            villes_desservies=aeroport_dict.get('villes_desservies', [])
        )
        
        # Ajouter les pistes
        for piste_id, piste_data in aeroport_dict.get('pistes', {}).items():
            piste = PisteAtterrissage(
                numero=piste_data['numero'],
                longueur=piste_data['longueur'],
                largeur=piste_data['largeur'],
                surface=piste_data['surface']
            )
            piste.statut = StatutPiste(piste_data['statut'])
            aeroport.ajouter_piste(piste)
        
        return aeroport
    
    def aeroport_to_dict(self, aeroport: Aeroport) -> Dict:
        """Convertit un objet Aeroport en dict JSON"""
        pistes_dict = {}
        for i, piste in enumerate(aeroport.pistes):
            pistes_dict[f"piste_{i:02d}"] = {
                'numero': piste.numero,
                'longueur': piste.longueur,
                'largeur': piste.largeur,
                'surface': piste.surface,
                'statut': piste.statut.value
            }
        
        return {
            'nom': aeroport.nom,
            'code_iata': aeroport.code_iata,
            'coordonnees': {
                'longitude': aeroport.coordonnees.longitude,
                'latitude': aeroport.coordonnees.latitude
            },
            'pistes': pistes_dict,
            'villes_desservies': list(aeroport.villes_desservies)
        }
    
    def save_aeroports(self):
        """Sauvegarde les aéroports vers JSON"""
        aeroports_data = {}
        for aeroport_id, aeroport in self._aeroports_cache.items():
            aeroports_data[aeroport_id] = self.aeroport_to_dict(aeroport)
        self.data_manager.save_data('aeroports', aeroports_data)
    
    # =====================================================
    # GESTION DES AVIONS
    # =====================================================
    
    def load_avions(self):
        """Charge les avions depuis JSON"""
        avions_data = self.data_manager.load_data('avions')
        
        for avion_id, avion_dict in avions_data.items():
            try:
                avion = self.dict_to_avion(avion_dict)
                self._avions_cache[avion_id] = avion
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'avion {avion_id}: {e}")
    
    def dict_to_avion(self, avion_dict: Dict) -> Avion:
        """Convertit un dict JSON en objet Avion"""
        coords = Coordonnees(
            avion_dict['localisation']['longitude'],
            avion_dict['localisation']['latitude']
        )
        
        avion = Avion(
            num_id=avion_dict['num_id'],
            modele=avion_dict['modele'],
            capacite=avion_dict['capacite'],
            compagnie_aerienne=avion_dict['compagnie_aerienne'],
            vitesse_croisiere=avion_dict['vitesse_croisiere'],
            autonomie=avion_dict['autonomie'],
            localisation=coords,
            etat=EtatAvion(avion_dict['etat'])
        )
        
        if avion_dict.get('derniere_maintenance'):
            avion.derniere_maintenance = datetime.fromisoformat(avion_dict['derniere_maintenance'])
        
        return avion
    
    def avion_to_dict(self, avion: Avion) -> Dict:
        """Convertit un objet Avion en dict JSON"""
        return {
            'num_id': avion.num_id,
            'modele': avion.modele,
            'capacite': avion.capacite,
            'compagnie_aerienne': avion.compagnie_aerienne,
            'vitesse_croisiere': avion.vitesse_croisiere,
            'autonomie': avion.autonomie,
            'localisation': {
                'longitude': avion.localisation.longitude,
                'latitude': avion.localisation.latitude
            },
            'etat': avion.etat.value,
            'derniere_maintenance': avion.derniere_maintenance.isoformat() if avion.derniere_maintenance else None
        }
    
    def save_avions(self):
        """Sauvegarde les avions vers JSON"""
        avions_data = {}
        for avion_id, avion in self._avions_cache.items():
            avions_data[avion_id] = self.avion_to_dict(avion)
        self.data_manager.save_data('avions', avions_data)
    
    def create_avion(self, num_id: str, modele: str, capacite: int, 
                    compagnie_aerienne: str, vitesse_croisiere: float,
                    autonomie: float, longitude: float = 0, latitude: float = 0) -> str:
        """Crée un nouvel avion"""
        avion_id = str(uuid.uuid4())
        coords = Coordonnees(longitude, latitude)
        
        avion = Avion(
            num_id=num_id,
            modele=modele,
            capacite=capacite,
            compagnie_aerienne=compagnie_aerienne,
            vitesse_croisiere=vitesse_croisiere,
            autonomie=autonomie,
            localisation=coords
        )
        
        self._avions_cache[avion_id] = avion
        self.save_avions()
        
        logger.info(f"Nouvel avion créé: {num_id}")
        return avion_id
    
    # =====================================================
    # GESTION DU PERSONNEL
    # =====================================================
    
    def load_personnels(self):
        """Charge le personnel depuis JSON"""
        personnels_data = self.data_manager.load_data('personnels')
        
        for personnel_id, personnel_dict in personnels_data.items():
            try:
                personnel = self.dict_to_personnel(personnel_dict)
                self._personnels_cache[personnel_id] = personnel
            except Exception as e:
                logger.error(f"Erreur lors du chargement du personnel {personnel_id}: {e}")
    
    def dict_to_personnel(self, personnel_dict: Dict) -> Personnel:
        """Convertit un dict JSON en objet Personnel"""
        date_naissance = None
        if personnel_dict.get('date_naissance'):
            date_naissance = datetime.fromisoformat(personnel_dict['date_naissance'])
        
        personnel = Personnel(
            nom=personnel_dict['nom'],
            prenom=personnel_dict['prenom'],
            sexe=personnel_dict['sexe'],
            adresse=personnel_dict['adresse'],
            metier=personnel_dict['type_personnel'],
            id_employe=personnel_dict.get('id_employe'),
            date_naissance=date_naissance,
            numero_telephone=personnel_dict.get('numero_telephone'),
            email=personnel_dict.get('email'),
            horaire=personnel_dict.get('horaire', 'Temps plein'),
            specialisation=personnel_dict.get('specialisation')
        )
        
        # Restaurer attributs spécifiques
        personnel.disponible = personnel_dict.get('disponible', True)
        personnel.heures_vol = personnel_dict.get('heures_vol', 0.0)
        personnel.numero_licence = personnel_dict.get('numero_licence', '')
        personnel.langues_parlees = personnel_dict.get('langues_parlees', [])
        
        return personnel
    
    def personnel_to_dict(self, personnel: Personnel) -> Dict:
        """Convertit un objet Personnel en dict JSON"""
        return personnel.to_dict()
    
    def save_personnels(self):
        """Sauvegarde le personnel vers JSON"""
        personnels_data = {}
        for personnel_id, personnel in self._personnels_cache.items():
            personnels_data[personnel_id] = self.personnel_to_dict(personnel)
        self.data_manager.save_data('personnels', personnels_data)
    
    def create_personnel(self, nom: str, prenom: str, sexe: str, adresse: str,
                        metier: str, **kwargs) -> str:
        """Crée un nouveau membre du personnel"""
        personnel_id = str(uuid.uuid4())
        
        personnel = Personnel(
            nom=nom,
            prenom=prenom,
            sexe=sexe,
            adresse=adresse,
            metier=metier,
            **kwargs
        )
        
        self._personnels_cache[personnel_id] = personnel
        self.save_personnels()
        
        logger.info(f"Nouveau personnel créé: {prenom} {nom}")
        return personnel_id
    
    # =====================================================
    # GESTION DES PASSAGERS
    # =====================================================
    
    def load_passagers(self):
        """Charge les passagers depuis JSON"""
        passagers_data = self.data_manager.load_data('passagers')
        
        for passager_id, passager_dict in passagers_data.items():
            try:
                passager = self.dict_to_passager(passager_dict)
                self._passagers_cache[passager_id] = passager
            except Exception as e:
                logger.error(f"Erreur lors du chargement du passager {passager_id}: {e}")
    
    def dict_to_passager(self, passager_dict: Dict) -> Passager:
        """Convertit un dict JSON en objet Passager"""
        date_naissance = None
        if passager_dict.get('date_naissance'):
            date_naissance = datetime.fromisoformat(passager_dict['date_naissance'])
        
        passager = Passager(
            nom=passager_dict['nom'],
            prenom=passager_dict['prenom'],
            sexe=passager_dict['sexe'],
            adresse=passager_dict['adresse'],
            id_passager=passager_dict.get('id_passager'),
            numero_passeport=passager_dict.get('numero_passeport'),
            date_naissance=date_naissance,
            numero_telephone=passager_dict.get('numero_telephone'),
            email=passager_dict.get('email')
        )
        
        passager.checkin_effectue = passager_dict.get('checkin_effectue', False)
        return passager
    
    def passager_to_dict(self, passager: Passager) -> Dict:
        """Convertit un objet Passager en dict JSON"""
        return passager.to_dict()
    
    def save_passagers(self):
        """Sauvegarde les passagers vers JSON"""
        passagers_data = {}
        for passager_id, passager in self._passagers_cache.items():
            passagers_data[passager_id] = self.passager_to_dict(passager)
        self.data_manager.save_data('passagers', passagers_data)
    
    # =====================================================
    # GESTION DES VOLS
    # =====================================================
    
    def load_vols(self):
        """Charge les vols depuis JSON"""
        vols_data = self.data_manager.load_data('vols')
        
        for vol_id, vol_dict in vols_data.items():
            try:
                vol = self.dict_to_vol(vol_dict)
                self._vols_cache[vol_id] = vol
                
                # Programmer les événements automatiques
                self.schedule_flight_events(vol_id)
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement du vol {vol_id}: {e}")
    
    def dict_to_vol(self, vol_dict: Dict) -> Vol:
        """Convertit un dict JSON en objet Vol"""
        # Récupérer les objets liés
        avion = self._avions_cache.get(vol_dict.get('avion_id'))
        aeroport_depart = self._aeroports_cache.get(vol_dict.get('aeroport_depart_id'))
        aeroport_arrivee = self._aeroports_cache.get(vol_dict.get('aeroport_arrivee_id'))
        
        # Créer le vol
        vol = Vol(
            numero_vol=vol_dict['numero_vol'],
            aeroport_depart=aeroport_depart,
            aeroport_arrivee=aeroport_arrivee,
            avion_utilise=avion,
            heure_depart=datetime.fromisoformat(vol_dict['heure_depart']),
            heure_arrivee_prevue=datetime.fromisoformat(vol_dict['heure_arrivee_prevue'])
        )
        
        # Restaurer le statut
        if 'statut' in vol_dict:
            vol.statut = StatutVol(vol_dict['statut'])
        
        # Ajouter passagers et personnel
        for passager_id in vol_dict.get('passagers_ids', []):
            if passager_id in self._passagers_cache:
                vol.ajouter_passager(self._passagers_cache[passager_id])
        
        for personnel_id in vol_dict.get('personnel_ids', []):
            if personnel_id in self._personnels_cache:
                vol.ajouter_personnel(self._personnels_cache[personnel_id])
        
        return vol
    
    def vol_to_dict(self, vol: Vol, vol_id: str) -> Dict:
        """Convertit un objet Vol en dict JSON"""
        # Trouver les IDs des objets liés
        avion_id = None
        for aid, avion in self._avions_cache.items():
            if avion == vol.avion_utilise:
                avion_id = aid
                break
        
        aeroport_depart_id = None
        aeroport_arrivee_id = None
        for aid, aeroport in self._aeroports_cache.items():
            if aeroport == vol.aeroport_depart:
                aeroport_depart_id = aid
            if aeroport == vol.aeroport_arrivee:
                aeroport_arrivee_id = aid
        
        # IDs des passagers et personnel
        passagers_ids = []
        for pid, passager in self._passagers_cache.items():
            if passager in vol.passagers:
                passagers_ids.append(pid)
        
        personnel_ids = []
        for pid, personnel in self._personnels_cache.items():
            if personnel in vol.personnel:
                personnel_ids.append(pid)
        
        return {
            'numero_vol': vol.numero_vol,
            'avion_id': avion_id,
            'aeroport_depart_id': aeroport_depart_id,
            'aeroport_arrivee_id': aeroport_arrivee_id,
            'heure_depart': vol.heure_depart.isoformat(),
            'heure_arrivee_prevue': vol.heure_arrivee_prevue.isoformat(),
            'statut': vol.statut.value,
            'passagers_ids': passagers_ids,
            'personnel_ids': personnel_ids
        }
    
    def save_vols(self):
        """Sauvegarde les vols vers JSON"""
        vols_data = {}
        for vol_id, vol in self._vols_cache.items():
            vols_data[vol_id] = self.vol_to_dict(vol, vol_id)
        self.data_manager.save_data('vols', vols_data)
    
    def create_vol(self, numero_vol: str, aeroport_depart_id: str, 
                  aeroport_arrivee_id: str, avion_id: str,
                  heure_depart: datetime, heure_arrivee_prevue: datetime) -> str:
        """Crée un nouveau vol"""
        vol_id = str(uuid.uuid4())
        
        # Récupérer les objets
        aeroport_depart = self._aeroports_cache.get(aeroport_depart_id)
        aeroport_arrivee = self._aeroports_cache.get(aeroport_arrivee_id)
        avion = self._avions_cache.get(avion_id)
        
        if not all([aeroport_depart, aeroport_arrivee, avion]):
            raise ValueError("Objets liés introuvables")
        
        vol = Vol(
            numero_vol=numero_vol,
            aeroport_depart=aeroport_depart,
            aeroport_arrivee=aeroport_arrivee,
            avion_utilise=avion,
            heure_depart=heure_depart,
            heure_arrivee_prevue=heure_arrivee_prevue
        )
        
        self._vols_cache[vol_id] = vol
        self.save_vols()
        
        # Programmer les événements
        self.schedule_flight_events(vol_id)
        
        logger.info(f"Nouveau vol créé: {numero_vol}")
        return vol_id
    
    # =====================================================
    # AUTRES MÉTHODES (compagnies, réservations, etc.)
    # =====================================================
    
    def load_compagnies(self):
        """Charge les compagnies depuis JSON"""
        # Implementation similaire aux autres load_*
        pass
    
    def load_reservations(self):
        """Charge les réservations depuis JSON"""
        # Implementation similaire aux autres load_*
        pass
    
    def save_compagnies(self):
        """Sauvegarde les compagnies"""
        pass
    
    def save_reservations(self):
        """Sauvegarde les réservations"""
        pass
    
    # =====================================================
    # GESTION DES ÉVÉNEMENTS DE SIMULATION
    # =====================================================
    
    def schedule_flight_events(self, vol_id: str):
        """Programme les événements automatiques pour un vol"""
        vol = self._vols_cache.get(vol_id)
        if not vol:
            return
        
        # Programmer décollage
        self.simulator.schedule_event(
            vol.heure_depart,
            'vol',
            vol_id,
            'decoller',
            {'numero_vol': vol.numero_vol}
        )
        
        # Programmer atterrissage
        self.simulator.schedule_event(
            vol.heure_arrivee_prevue,
            'vol',
            vol_id,
            'atterrir',
            {'numero_vol': vol.numero_vol}
        )
    
    def schedule_maintenance(self, avion_id: str, maintenance_time: datetime, 
                           duree_heures: int = 4):
        """Programme une maintenance"""
        self.simulator.schedule_event(
            maintenance_time,
            'maintenance',
            avion_id,
            'debut_maintenance',
            {'duree_heures': duree_heures}
        )
        
        # Programmer la fin de maintenance
        fin_maintenance = maintenance_time + timedelta(hours=duree_heures)
        self.simulator.schedule_event(
            fin_maintenance,
            'maintenance',
            avion_id,
            'fin_maintenance',
            {}
        )
    
    def handle_vol_event(self, event):
        """Gestionnaire d'événements pour les vols"""
        vol = self._vols_cache.get(event.target_id)
        if not vol:
            logger.warning(f"Vol {event.target_id} introuvable pour événement {event.action}")
            return
        
        if event.action == 'decoller':
            success = vol.demarrer_vol()
            if success:
                logger.info(f"Vol {vol.numero_vol} a décollé")
            else:
                logger.warning(f"Impossible de faire décoller le vol {vol.numero_vol}")
        
        elif event.action == 'atterrir':
            success = vol.atterrir()
            if success:
                logger.info(f"Vol {vol.numero_vol} a atterri")
            else:
                logger.warning(f"Impossible de faire atterrir le vol {vol.numero_vol}")
        
        # Sauvegarder les changements
        self.save_vols()
    
    def handle_avion_event(self, event):
        """Gestionnaire d'événements pour les avions"""
        avion = self._avions_cache.get(event.target_id)
        if not avion:
            logger.warning(f"Avion {event.target_id} introuvable pour événement {event.action}")
            return
        
        if event.action == 'maintenance_start':
            success = avion.programmer_maintenance()
            if success:
                logger.info(f"Maintenance démarrée pour l'avion {avion.num_id}")
        
        elif event.action == 'maintenance_end':
            success = avion.terminer_maintenance()
            if success:
                logger.info(f"Maintenance terminée pour l'avion {avion.num_id}")
        
        # Sauvegarder les changements
        self.save_avions()
    
    def handle_maintenance_event(self, event):
        """Gestionnaire d'événements pour les maintenances"""
        avion = self._avions_cache.get(event.target_id)
        if not avion:
            return
        
        if event.action == 'debut_maintenance':
            avion.programmer_maintenance(self.simulator.current_time)
            logger.info(f"Début maintenance avion {avion.num_id}")
        
        elif event.action == 'fin_maintenance':
            avion.terminer_maintenance()
            logger.info(f"Fin maintenance avion {avion.num_id}")
        
        self.save_avions()
    
    def handle_personnel_event(self, event):
        """Gestionnaire d'événements pour le personnel"""
        personnel = self._personnels_cache.get(event.target_id)
        if not personnel:
            return
        
        # Logique pour événements personnel (horaires, formations, etc.)
        logger.info(f"Événement personnel: {event.action} pour {personnel.obtenir_nom_complet()}")
    
    # =====================================================
    # MÉTHODES D'ACCÈS ET RECHERCHE
    # =====================================================
    
    def get_all_avions(self) -> List[Dict]:
        """Retourne tous les avions avec leurs IDs"""
        return [
            {
                'id': avion_id,
                'avion': avion,
                'data': self.avion_to_dict(avion)
            }
            for avion_id, avion in self._avions_cache.items()
        ]
    
    def get_all_vols(self) -> List[Dict]:
        """Retourne tous les vols avec leurs IDs"""
        return [
            {
                'id': vol_id,
                'vol': vol,
                'data': self.vol_to_dict(vol, vol_id)
            }
            for vol_id, vol in self._vols_cache.items()
        ]
    
    def get_all_personnels(self) -> List[Dict]:
        """Retourne tout le personnel avec leurs IDs"""
        return [
            {
                'id': personnel_id,
                'personnel': personnel,
                'data': self.personnel_to_dict(personnel)
            }
            for personnel_id, personnel in self._personnels_cache.items()
        ]
    
    def get_all_aeroports(self) -> List[Dict]:
        """Retourne tous les aéroports avec leurs IDs"""
        return [
            {
                'id': aeroport_id,
                'aeroport': aeroport,
                'data': self.aeroport_to_dict(aeroport)
            }
            for aeroport_id, aeroport in self._aeroports_cache.items()
        ]
    
    def get_avions_disponibles(self) -> List[Dict]:
        """Retourne les avions disponibles pour voler"""
        return [
            {
                'id': avion_id,
                'avion': avion,
                'data': self.avion_to_dict(avion)
            }
            for avion_id, avion in self._avions_cache.items()
            if avion.etat.est_operationnel()
        ]
    
    def get_vols_actifs(self) -> List[Dict]:
        """Retourne les vols en cours ou programmés"""
        return [
            {
                'id': vol_id,
                'vol': vol,
                'data': self.vol_to_dict(vol, vol_id)
            }
            for vol_id, vol in self._vols_cache.items()
            if vol.statut in [StatutVol.PROGRAMME, StatutVol.EN_VOL, StatutVol.RETARDE]
        ]
    
    def get_personnel_disponible(self, type_personnel: str = None) -> List[Dict]:
        """Retourne le personnel disponible, optionnellement filtré par type"""
        personnel_list = []
        
        for personnel_id, personnel in self._personnels_cache.items():
            if personnel.disponible:
                if type_personnel is None or personnel.type_personnel.value == type_personnel:
                    personnel_list.append({
                        'id': personnel_id,
                        'personnel': personnel,
                        'data': self.personnel_to_dict(personnel)
                    })
        
        return personnel_list
    
    def search_vol_by_numero(self, numero_vol: str) -> Optional[Dict]:
        """Recherche un vol par son numéro"""
        for vol_id, vol in self._vols_cache.items():
            if vol.numero_vol == numero_vol:
                return {
                    'id': vol_id,
                    'vol': vol,
                    'data': self.vol_to_dict(vol, vol_id)
                }
        return None
    
    def search_avion_by_num_id(self, num_id: str) -> Optional[Dict]:
        """Recherche un avion par son num_id"""
        for avion_id, avion in self._avions_cache.items():
            if avion.num_id == num_id:
                return {
                    'id': avion_id,
                    'avion': avion,
                    'data': self.avion_to_dict(avion)
                }
        return None
    
    # =====================================================
    # STATISTIQUES ET RAPPORTS
    # =====================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques générales"""
        return {
            'avions': {
                'total': len(self._avions_cache),
                'disponibles': len([a for a in self._avions_cache.values() if a.etat.est_operationnel()]),
                'en_maintenance': len([a for a in self._avions_cache.values() if a.etat == EtatAvion.EN_MAINTENANCE]),
                'en_vol': len([a for a in self._avions_cache.values() if a.etat == EtatAvion.EN_VOL])
            },
            'vols': {
                'total': len(self._vols_cache),
                'programmes': len([v for v in self._vols_cache.values() if v.statut == StatutVol.PROGRAMME]),
                'en_cours': len([v for v in self._vols_cache.values() if v.statut == StatutVol.EN_VOL]),
                'retardes': len([v for v in self._vols_cache.values() if v.statut == StatutVol.RETARDE]),
                'annules': len([v for v in self._vols_cache.values() if v.statut == StatutVol.ANNULE])
            },
            'personnel': {
                'total': len(self._personnels_cache),
                'disponible': len([p for p in self._personnels_cache.values() if p.disponible]),
                'pilotes': len([p for p in self._personnels_cache.values() if p.type_personnel == TypePersonnel.PILOTE]),
                'personnel_navigant': len([p for p in self._personnels_cache.values() 
                                         if p.type_personnel in [TypePersonnel.HOTESSE, TypePersonnel.STEWARD]])
            },
            'passagers': {
                'total': len(self._passagers_cache),
                'enregistres': len([p for p in self._passagers_cache.values() if p.checkin_effectue])
            },
            'aeroports': {
                'total': len(self._aeroports_cache)
            },
            'simulation': self.simulator.get_simulation_statistics()
        }
    
    def get_flight_schedule(self, date: datetime = None) -> List[Dict]:
        """Retourne le planning des vols pour une date donnée"""
        if date is None:
            date = self.simulator.current_time.date()
        
        schedule = []
        for vol_id, vol in self._vols_cache.items():
            if vol.heure_depart.date() == date:
                schedule.append({
                    'id': vol_id,
                    'vol': vol,
                    'data': self.vol_to_dict(vol, vol_id),
                    'info': vol.obtenir_informations()
                })
        
        # Trier par heure de départ
        schedule.sort(key=lambda x: x['vol'].heure_depart)
        return schedule
    
    def get_maintenance_schedule(self) -> List[Dict]:
        """Retourne le planning des maintenances"""
        events = self.simulator.get_scheduled_events('maintenance')
        
        maintenance_schedule = []
        for event in events:
            avion = self._avions_cache.get(event.target_id)
            if avion:
                maintenance_schedule.append({
                    'event': event,
                    'avion': avion,
                    'avion_data': self.avion_to_dict(avion)
                })
        
        return maintenance_schedule
    
    # =====================================================
    # OPÉRATIONS COMPLEXES
    # =====================================================
    
    def assign_personnel_to_vol(self, vol_id: str, personnel_ids: List[str]) -> bool:
        """Assigne du personnel à un vol"""
        vol = self._vols_cache.get(vol_id)
        if not vol:
            return False
        
        for personnel_id in personnel_ids:
            personnel = self._personnels_cache.get(personnel_id)
            if personnel and personnel.disponible:
                vol.ajouter_personnel(personnel)
                personnel.definir_disponibilite(False)
        
        self.save_vols()
        self.save_personnels()
        return True
    
    def assign_passengers_to_vol(self, vol_id: str, passager_ids: List[str]) -> bool:
        """Assigne des passagers à un vol"""
        vol = self._vols_cache.get(vol_id)
        if not vol:
            return False
        
        for passager_id in passager_ids:
            passager = self._passagers_cache.get(passager_id)
            if passager:
                vol.ajouter_passager(passager)
        
        self.save_vols()
        return True
    
    def create_delay(self, vol_id: str, cause: str, minutes: int) -> bool:
        """Crée un retard pour un vol"""
        vol = self._vols_cache.get(vol_id)
        if not vol:
            return False
        
        # Ajouter le retard
        vol.ajouter_retard(cause, minutes, cause)
        vol.appliquer_retard()
        
        # Reprogrammer les événements
        self.simulator.cancel_event(f"vol_{vol_id}_depart")
        self.simulator.cancel_event(f"vol_{vol_id}_arrivee")
        self.schedule_flight_events(vol_id)
        
        self.save_vols()
        return True
    
    def optimize_aircraft_assignment(self) -> Dict[str, str]:
        """Optimise l'attribution des avions aux vols"""
        optimizations = {}
        
        # Récupérer vols non assignés ou mal assignés
        for vol_id, vol in self._vols_cache.items():
            if vol.statut == StatutVol.PROGRAMME:
                # Trouver le meilleur avion
                avions_disponibles = [a for a in self._avions_cache.values() 
                                    if a.etat.est_operationnel()]
                
                if avions_disponibles:
                    meilleur_avion = vol.choisir_avion(avions_disponibles)
                    if meilleur_avion and meilleur_avion != vol.avion_utilise:
                        vol.avion_utilise = meilleur_avion
                        optimizations[vol_id] = meilleur_avion.num_id
        
        if optimizations:
            self.save_vols()
            logger.info(f"Optimisations d'attribution: {len(optimizations)} vols modifiés")
        
        return optimizations
    
    """
Extensions pour le DataController pour supporter la création via l'interface
À ajouter au fichier data_controller.py existant
"""

def create_vol(self, numero_vol, aeroport_depart, aeroport_arrivee, 
               heure_depart, heure_arrivee, auto_assign_aircraft=True, aircraft_id=None):
    """
    Crée un nouveau vol
    
    Args:
        numero_vol (str): Numéro du vol
        aeroport_depart (str): Code de l'aéroport de départ  
        aeroport_arrivee (str): Code de l'aéroport d'arrivée
        heure_depart (datetime): Heure de départ
        heure_arrivee (datetime): Heure d'arrivée
        auto_assign_aircraft (bool): Assignation automatique d'avion
        aircraft_id (str): ID de l'avion spécifique (si pas auto)
        
    Returns:
        str: ID du vol créé
    """
    from Core import Vol, Aeroport, Coordonnees
    
    # Trouver ou créer les aéroports
    aeroport_dep = self._get_or_create_airport(aeroport_depart)
    aeroport_arr = self._get_or_create_airport(aeroport_arrivee)
    
    # Assigner un avion
    if auto_assign_aircraft:
        avion = self._find_best_aircraft_for_flight(heure_depart, heure_arrivee)
        if not avion:
            raise ValueError("Aucun avion disponible pour ce vol")
    else:
        if not aircraft_id:
            raise ValueError("ID d'avion requis pour assignation manuelle")
        avion_data = self._avions_cache.get(aircraft_id)
        if not avion_data:
            raise ValueError(f"Avion {aircraft_id} non trouvé")
        avion = avion_data['avion']
        
        # Vérifier disponibilité
        if not avion.etat.est_operationnel():
            raise ValueError(f"Avion {aircraft_id} non opérationnel")
    
    # Créer le vol
    vol = Vol(
        numero_vol=numero_vol,
        aeroport_depart=aeroport_dep,
        aeroport_arrivee=aeroport_arr,
        avion_utilise=avion,
        heure_depart=heure_depart,
        heure_arrivee_prevue=heure_arrivee
    )
    
    # Générer un ID unique
    vol_id = f"vol_{self._generate_id()}"
    
    # Ajouter au cache
    self._vols_cache[vol_id] = {
        'id': vol_id,
        'vol': vol,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Programmer les événements de simulation
    self._schedule_flight_events(vol_id, vol)
    
    # Sauvegarder
    self.save_vols()
    
    logger.info(f"Vol {numero_vol} créé avec ID {vol_id}")
    return vol_id

def create_personnel(self, nom, prenom, sexe, adresse, metier, 
                    horaire="Temps plein", specialisation="", **kwargs):
    """
    Crée un nouveau membre du personnel
    
    Args:
        nom (str): Nom de famille
        prenom (str): Prénom
        sexe (str): Sexe
        adresse (str): Adresse
        metier (str): Type de poste
        horaire (str): Horaire de travail
        specialisation (str): Spécialisation
        **kwargs: Autres attributs optionnels
        
    Returns:
        str: ID du personnel créé
    """
    from Core import Personnel
    
    # Créer l'objet Personnel
    personnel = Personnel(
        nom=nom,
        prenom=prenom,
        sexe=sexe,
        adresse=adresse,
        metier=metier,
        horaire=horaire,
        specialisation=specialisation,
        **kwargs
    )
    
    # Générer un ID unique
    personnel_id = f"pers_{self._generate_id()}"
    
    # Ajouter au cache
    self._personnels_cache[personnel_id] = {
        'id': personnel_id,
        'personnel': personnel,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Sauvegarder
    self.save_personnels()
    
    logger.info(f"Personnel {prenom} {nom} créé avec ID {personnel_id}")
    return personnel_id

def create_passager(self, nom, prenom, sexe, adresse, numero_passeport="", **kwargs):
    """
    Crée un nouveau passager
    
    Args:
        nom (str): Nom de famille
        prenom (str): Prénom
        sexe (str): Sexe
        adresse (str): Adresse
        numero_passeport (str): Numéro de passeport
        **kwargs: Autres attributs optionnels
        
    Returns:
        str: ID du passager créé
    """
    from Core import Passager
    
    # Créer l'objet Passager
    passager = Passager(
        nom=nom,
        prenom=prenom,
        sexe=sexe,
        adresse=adresse,
        numero_passeport=numero_passeport,
        **kwargs
    )
    
    # Générer un ID unique
    passager_id = f"pass_{self._generate_id()}"
    
    # Ajouter au cache
    self._passagers_cache[passager_id] = {
        'id': passager_id,
        'passager': passager,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Sauvegarder
    self.save_passagers()
    
    logger.info(f"Passager {prenom} {nom} créé avec ID {passager_id}")
    return passager_id

def create_reservation(self, passager_id, vol_numero):
    """
    Crée une réservation pour un passager sur un vol
    
    Args:
        passager_id (str): ID du passager
        vol_numero (str): Numéro du vol
        
    Returns:
        str: ID de la réservation créée
    """
    from Core import Reservation
    
    # Trouver le passager
    passager_data = self._passagers_cache.get(passager_id)
    if not passager_data:
        raise ValueError(f"Passager {passager_id} non trouvé")
    
    # Trouver le vol
    vol_data = None
    for v_data in self._vols_cache.values():
        if v_data['vol'].numero_vol == vol_numero:
            vol_data = v_data
            break
    
    if not vol_data:
        raise ValueError(f"Vol {vol_numero} non trouvé")
    
    # Vérifier la capacité
    vol = vol_data['vol']
    avion = vol.avion_utilise
    if len(vol.passagers) >= avion.capacite:
        raise ValueError(f"Vol {vol_numero} complet")
    
    # Créer la réservation
    passager = passager_data['passager']
    reservation = Reservation(passager, vol)
    
    # Générer un ID unique
    reservation_id = f"res_{self._generate_id()}"
    
    # Ajouter au cache des réservations
    if not hasattr(self, '_reservations_cache'):
        self._reservations_cache = {}
    
    self._reservations_cache[reservation_id] = {
        'id': reservation_id,
        'reservation': reservation,
        'passager_id': passager_id,
        'vol_id': vol_data['id'],
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Sauvegarder
    self.save_reservations()
    
    logger.info(f"Réservation {reservation_id} créée pour {passager.obtenir_nom_complet()} sur vol {vol_numero}")
    return reservation_id

def get_all_aeroports(self):
    """
    Retourne tous les aéroports
    
    Returns:
        list: Liste des données d'aéroports
    """
    # Si pas de cache d'aéroports, créer des aéroports par défaut
    if not hasattr(self, '_aeroports_cache'):
        self._aeroports_cache = {}
        self._create_default_airports()
    
    return list(self._aeroports_cache.values())

def _get_or_create_airport(self, airport_code):
    """
    Récupère ou crée un aéroport depuis son code
    
    Args:
        airport_code (str): Code de l'aéroport (format "CDG - Charles de Gaulle")
        
    Returns:
        Aeroport: Objet aéroport
    """
    from Core import Aeroport, Coordonnees
    
    # Extraire le code IATA
    if ' - ' in airport_code:
        code_iata = airport_code.split(' - ')[0]
        nom = airport_code.split(' - ')[1]
    else:
        code_iata = airport_code
        nom = airport_code
    
    # Chercher dans le cache
    if not hasattr(self, '_aeroports_cache'):
        self._aeroports_cache = {}
        self._create_default_airports()
    
    for aeroport_data in self._aeroports_cache.values():
        if aeroport_data['aeroport'].code_iata == code_iata:
            return aeroport_data['aeroport']
    
    # Créer un nouvel aéroport avec coordonnées par défaut
    coords = self._get_default_coordinates(code_iata)
    aeroport = Aeroport(
        nom=nom,
        code_iata=code_iata,
        coordonnees=coords
    )
    
    # Ajouter au cache
    aeroport_id = f"aero_{self._generate_id()}"
    self._aeroports_cache[aeroport_id] = {
        'id': aeroport_id,
        'aeroport': aeroport,
        'created_at': datetime.now()
    }
    
    return aeroport

def _create_default_airports(self):
    """Crée des aéroports par défaut"""
    from Core import Aeroport, Coordonnees
    
    default_airports = [
        ("CDG", "Charles de Gaulle", 49.0097, 2.5479),
        ("ORY", "Orly", 48.7233, 2.3794),
        ("LHR", "Londres Heathrow", 51.4700, -0.4543),
        ("FRA", "Francfort", 50.0379, 8.5622),
        ("BCN", "Barcelone", 41.2974, 2.0833),
        ("MAD", "Madrid Barajas", 40.4719, -3.5626),
        ("FCO", "Rome Fiumicino", 41.8003, 12.2389),
        ("AMS", "Amsterdam Schiphol", 52.3086, 4.7639),
        ("ZUR", "Zurich", 47.4647, 8.5492),
        ("MUC", "Munich", 48.3537, 11.7750)
    ]
    
    for code, nom, lat, lon in default_airports:
        coords = Coordonnees(lon, lat)
        aeroport = Aeroport(nom=nom, code_iata=code, coordonnees=coords)
        
        aeroport_id = f"aero_{code.lower()}"
        self._aeroports_cache[aeroport_id] = {
            'id': aeroport_id,
            'aeroport': aeroport,
            'created_at': datetime.now()
        }

def _get_default_coordinates(self, code_iata):
    """Retourne des coordonnées par défaut pour un code d'aéroport"""
    from Core import Coordonnees
    
    # Coordonnées approximatives pour quelques aéroports
    coords_map = {
        'CDG': (49.0097, 2.5479),
        'ORY': (48.7233, 2.3794),
        'LHR': (51.4700, -0.4543),
        'FRA': (50.0379, 8.5622),
        'BCN': (41.2974, 2.0833),
        'MAD': (40.4719, -3.5626),
        'FCO': (41.8003, 12.2389),
        'AMS': (52.3086, 4.7639),
        'ZUR': (47.4647, 8.5492),
        'MUC': (48.3537, 11.7750)
    }
    
    if code_iata in coords_map:
        lat, lon = coords_map[code_iata]
        return Coordonnees(lon, lat)
    else:
        # Coordonnées par défaut (Paris)
        return Coordonnees(2.3522, 48.8566)

def _find_best_aircraft_for_flight(self, heure_depart, heure_arrivee):
    """
    Trouve le meilleur avion disponible pour un vol
    
    Args:
        heure_depart (datetime): Heure de départ
        heure_arrivee (datetime): Heure d'arrivée
        
    Returns:
        Avion: Meilleur avion disponible ou None
    """
    available_aircraft = []
    
    for aircraft_data in self._avions_cache.values():
        avion = aircraft_data['avion']
        
        # Vérifier si l'avion est opérationnel
        if not avion.etat.est_operationnel():
            continue
        
        # Vérifier les conflits d'horaire
        if self._aircraft_has_conflict(aircraft_data['id'], heure_depart, heure_arrivee):
            continue
        
        available_aircraft.append(avion)
    
    if not available_aircraft:
        return None
    
    # Sélectionner le premier disponible (à améliorer avec des critères d'optimisation)
    return available_aircraft[0]

def _aircraft_has_conflict(self, aircraft_id, heure_debut, heure_fin):
    """
    Vérifie si un avion a un conflit d'horaire
    
    Args:
        aircraft_id (str): ID de l'avion
        heure_debut (datetime): Début de la période
        heure_fin (datetime): Fin de la période
        
    Returns:
        bool: True si conflit détecté
    """
    for vol_data in self._vols_cache.values():
        vol = vol_data['vol']
        
        # Vérifier si c'est le même avion
        if hasattr(vol.avion_utilise, 'num_id'):
            avion_vol_id = None
            for aid, adata in self._avions_cache.items():
                if adata['avion'].num_id == vol.avion_utilise.num_id:
                    avion_vol_id = aid
                    break
            
            if avion_vol_id == aircraft_id:
                # Vérifier le chevauchement temporel
                if not (heure_fin <= vol.heure_depart or heure_debut >= vol.heure_arrivee_prevue):
                    return True
    
    return False

def _schedule_flight_events(self, vol_id, vol):
    """
    Programme les événements de simulation pour un vol
    
    Args:
        vol_id (str): ID du vol
        vol: Objet Vol
    """
    try:
        # Programmer le décollage
        self.simulator.schedule_event(
            vol.heure_depart,
            'vol',
            vol_id,
            'decoller',
            {'numero_vol': vol.numero_vol, 'action': 'Décollage'}
        )
        
        # Programmer l'atterrissage
        self.simulator.schedule_event(
            vol.heure_arrivee_prevue,
            'vol',
            vol_id,
            'atterrir',
            {'numero_vol': vol.numero_vol, 'action': 'Atterrissage'}
        )
        
        logger.debug(f"Événements programmés pour le vol {vol.numero_vol}")
        
    except Exception as e:
        logger.error(f"Erreur programmation événements vol {vol.numero_vol}: {e}")

def _generate_id(self):
    """Génère un ID unique"""
    import time
    return str(int(time.time() * 1000))

def save_reservations(self):
    """Sauvegarde les réservations"""
    try:
        if hasattr(self, '_reservations_cache'):
            reservations_data = {}
            for res_id, res_data in self._reservations_cache.items():
                reservation = res_data['reservation']
                reservations_data[res_id] = {
                    'id': res_id,
                    'passager_id': res_data['passager_id'],
                    'vol_id': res_data['vol_id'],
                    'numero_reservation': reservation.id_reservation,
                    'statut': reservation.statut.value,
                    'siege_assigne': reservation.siege_assigne,
                    'checkin_effectue': reservation.checkin_effectue,
                    'date_creation': res_data['created_at'].isoformat(),
                    'validite': reservation.validite.isoformat()
                }
            
            self.data_manager.save_data('reservations', reservations_data)
            logger.debug("Réservations sauvegardées")
    except Exception as e:
        logger.error(f"Erreur sauvegarde réservations: {e}")

def load_reservations(self):
    """Charge les réservations"""
    try:
        reservations_data = self.data_manager.load_data('reservations')
        self._reservations_cache = {}
        
        for res_id, res_data in reservations_data.items():
            # Reconstruire la réservation serait complexe, on garde juste les métadonnées
            self._reservations_cache[res_id] = {
                'id': res_id,
                'passager_id': res_data.get('passager_id'),
                'vol_id': res_data.get('vol_id'),
                'created_at': datetime.fromisoformat(res_data.get('date_creation', datetime.now().isoformat())),
                'updated_at': datetime.now()
            }
        
        logger.debug(f"{len(self._reservations_cache)} réservations chargées")
    except Exception as e:
        logger.error(f"Erreur chargement réservations: {e}")
        self._reservations_cache = {}