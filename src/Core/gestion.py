from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .enums import TypePersonnel, StatutVol
import uuid

class GestionRetard:
    """Classe pour gérer les retards de vol"""
    
    def __init__(self, vol, cause_detaillee, temps_retard_minutes):
        """
        Initialise la gestion d'un retard.
        
        Args:
            vol: Vol concerné par le retard
            cause_detaillee (str): Description détaillée de la cause
            temps_retard_minutes (int): Durée du retard en minutes
        """
        self.vol = vol
        self.cause_detaillee = str(cause_detaillee)
        self.temps_retard = timedelta(minutes=int(temps_retard_minutes))
        self.date_creation = datetime.now()
        self.heure_depart_originale = getattr(vol, 'heure_depart', None)
    
    def notifier_passagers(self):
        """
        Notifie tous les passagers du vol du retard.
        
        Returns:
            bool: True si toutes les notifications ont été envoyées
        """
        if not hasattr(self.vol, 'passagers') or not self.vol.passagers:
            print(f"Aucun passager à notifier pour le vol {getattr(self.vol, 'numero_vol', 'N/A')}")
            return True
            
        for passager in self.vol.passagers:
            nom_passager = f"{getattr(passager, 'prenom', '')} {getattr(passager, 'nom', '')}"
            message = (f"Vol {getattr(self.vol, 'numero_vol', 'N/A')} retardé de {self.temps_retard.total_seconds()/60:.0f} minutes. "
                      f"Cause: {self.cause_detaillee}")
            print(f"Notification envoyée à {nom_passager}: {message}")
        return True
    
    def appliquer_procedure(self):
        """
        Applique la procédure de gestion du retard.
        
        Returns:
            bool: True si la procédure a été appliquée avec succès
        """
        # Mise à jour de l'heure de départ
        if hasattr(self.vol, 'heure_depart') and self.vol.heure_depart:
            self.vol.heure_depart += self.temps_retard
            
        # Mise à jour de l'heure d'arrivée si elle existe
        if hasattr(self.vol, 'heure_arrivee_prevue') and self.vol.heure_arrivee_prevue:
            self.vol.heure_arrivee_prevue += self.temps_retard
            
        # Mise à jour du statut
        if hasattr(self.vol, 'statut'):
            self.vol.statut = StatutVol.RETARDE
            
        # Notification des passagers
        self.notifier_passagers()
        
        # Ajout à l'historique des retards du vol
        if not hasattr(self.vol, 'retards'):
            self.vol.retards = []
        self.vol.retards.append(self)
        
        return True
    
    def est_retard_meteo(self):
        """Vérifie si le retard est lié à la météo"""
        mots_cles_meteo = ['météo', 'meteo', 'pluie', 'neige', 'vent', 'orage', 'brouillard', 'tempête']
        return any(mot in self.cause_detaillee.lower() for mot in mots_cles_meteo)
    
    def calculer_compensation(self):
        """
        Calcule la compensation basique selon la durée du retard.
        
        Returns:
            float: Montant de compensation en euros
        """
        heures_retard = self.temps_retard.total_seconds() / 3600
        
        if heures_retard >= 4:
            return 600.0
        elif heures_retard >= 3:
            return 400.0
        elif heures_retard >= 2:
            return 250.0
        elif heures_retard >= 1:
            return 50.0
        else:
            return 0.0
    
    def __str__(self):
        vol_num = getattr(self.vol, 'numero_vol', 'N/A')
        return f"Retard Vol {vol_num}: {self.cause_detaillee} - {self.temps_retard.total_seconds()/60:.0f}min"

class Compagnie:
    """Classe représentant une compagnie aérienne"""
    
    def __init__(self, nom):
        """
        Initialise une compagnie aérienne.
        
        Args:
            nom (str): Nom de la compagnie
        """
        self.nom = str(nom) if nom else "Compagnie Aérienne"
        self.id_compagnie = str(uuid.uuid4())
        
        # Collections principales
        self.avions = {}  # {id_avion: objet_avion}
        self.vols = {}    # {numero_vol: objet_vol}
        self.employes = {}  # {id_employe: objet_employe}
        self.passagers = {}  # {id_passager: objet_passager}
        self.personnel = {}  # {id_personnel: objet_personnel}
        self.aeroports_desservis = {}  # {code_iata: objet_aeroport}
        self.retards = []  # Liste des objets GestionRetard
        
        # Statistiques basiques
        self.statistiques = {
            'vols_total': 0,
            'vols_programmes': 0,
            'vols_en_cours': 0,
            'vols_termines': 0,
            'vols_retardes': 0,
            'vols_annules': 0,
            'passagers_total': 0,
            'avions_total': 0,
            'avions_disponibles': 0,
            'employes_total': 0,
            'aeroports_total': 0
        }
    
    def ajouter_avion(self, avion):
        """
        Ajoute un avion à la flotte de la compagnie.
        
        Args:
            avion: Objet avion à ajouter
            
        Returns:
            bool: True si ajouté avec succès
        """
        if not hasattr(avion, 'num_id'):
            return False
            
        if avion.num_id in self.avions:
            print(f"Avion {avion.num_id} existe déjà dans la flotte")
            return False
            
        self.avions[avion.num_id] = avion
        self.statistiques['avions_total'] = len(self.avions)
        print(f"Avion {avion.num_id} ajouté à la flotte de {self.nom}")
        return True
    
    def enregistrer_avion(self, avion):
        """Alias pour ajouter_avion"""
        return self.ajouter_avion(avion)
    
    def ajouter_vol(self, vol):
        """
        Ajoute un vol au planning de la compagnie.
        
        Args:
            vol: Objet vol à ajouter
            
        Returns:
            bool: True si ajouté avec succès
        """
        if not hasattr(vol, 'numero_vol'):
            return False
            
        if vol.numero_vol in self.vols:
            print(f"Vol {vol.numero_vol} existe déjà dans le planning")
            return False
            
        self.vols[vol.numero_vol] = vol
        self.statistiques['vols_total'] = len(self.vols)
        print(f"Vol {vol.numero_vol} ajouté au planning de {self.nom}")
        return True
    
    def programmer_vol(self, vol):
        """Alias pour ajouter_vol"""
        return self.ajouter_vol(vol)
    
    def ajouter_employe(self, nom, prenom, sexe, adresse, metier, horaire, id_employe):
        """
        Ajoute un employé à la compagnie.
        
        Returns:
            dict: Objet employé créé (simulation)
        """
        if id_employe in self.employes:
            print(f"Employé {id_employe} existe déjà")
            return None
            
        # Création d'un objet employé simple
        employe = {
            'nom': nom,
            'prenom': prenom,
            'sexe': sexe,
            'adresse': adresse,
            'metier': metier,
            'horaire': horaire,
            'id_employe': id_employe,
            'disponible': True
        }
        
        self.employes[id_employe] = employe
        self.statistiques['employes_total'] = len(self.employes)
        print(f"Employé {prenom} {nom} ajouté à {self.nom}")
        return employe
    
    def enregistrer_personnel(self, personnel):
        """
        Enregistre un objet Personnel dans la compagnie.
        
        Args:
            personnel: Objet Personnel à enregistrer
            
        Returns:
            bool: True si enregistré avec succès
        """
        if not hasattr(personnel, 'id_employe'):
            return False
            
        self.personnel[personnel.id_employe] = personnel
        self.statistiques['employes_total'] = len(self.personnel)
        print(f"Personnel {personnel.obtenir_nom_complet()} enregistré")
        return True
    
    def ajouter_passager(self, id_passager, nom, prenom, sexe, adresse, numero_passeport):
        """
        Ajoute un passager à la base de données.
        
        Returns:
            dict: Objet passager créé (simulation)
        """
        if id_passager in self.passagers:
            print(f"Passager {id_passager} existe déjà")
            return None
            
        # Création d'un objet passager simple
        passager = {
            'id_passager': id_passager,
            'nom': nom,
            'prenom': prenom,
            'sexe': sexe,
            'adresse': adresse,
            'numero_passeport': numero_passeport
        }
        
        self.passagers[id_passager] = passager
        self.statistiques['passagers_total'] = len(self.passagers)
        print(f"Passager {prenom} {nom} ajouté à la base")
        return passager
    
    def enregistrer_passager(self, passager):
        """
        Enregistre un objet Passager dans la compagnie.
        
        Args:
            passager: Objet Passager à enregistrer
            
        Returns:
            bool: True si enregistré avec succès
        """
        if not hasattr(passager, 'id_passager'):
            return False
            
        self.passagers[passager.id_passager] = passager
        self.statistiques['passagers_total'] = len(self.passagers)
        print(f"Passager {passager.obtenir_nom_complet()} enregistré")
        return True
    
    def ajouter_aeroport_desservi(self, aeroport):
        """
        Ajoute un aéroport à la liste des aéroports desservis.
        
        Args:
            aeroport: Objet Aeroport
            
        Returns:
            bool: True si ajouté avec succès
        """
        if not hasattr(aeroport, 'code_iata'):
            return False
            
        self.aeroports_desservis[aeroport.code_iata] = aeroport
        self.statistiques['aeroports_total'] = len(self.aeroports_desservis)
        return True
    
    def obtenir_avions_disponibles(self):
        """Retourne la liste des avions disponibles pour voler"""
        disponibles = []
        for avion in self.avions.values():
            if hasattr(avion, 'etat') and hasattr(avion.etat, 'est_operationnel'):
                if avion.etat.est_operationnel():
                    disponibles.append(avion)
            else:
                # Fallback si pas d'attribut etat
                disponibles.append(avion)
        return disponibles
    
    def obtenir_vols_actifs(self):
        """Retourne les vols en cours ou programmés"""
        actifs = []
        for vol in self.vols.values():
            if hasattr(vol, 'statut'):
                if vol.statut in [StatutVol.PROGRAMME, StatutVol.EN_VOL, StatutVol.RETARDE]:
                    actifs.append(vol)
            else:
                # Fallback si pas d'attribut statut
                actifs.append(vol)
        return actifs
    
    def obtenir_tous_les_vols(self):
        """Retourne tous les vols"""
        return list(self.vols.values())
    
    def obtenir_tous_les_passagers(self):
        """Retourne tous les passagers"""
        return list(self.passagers.values())
    
    def rechercher_vol(self, critere, valeur):
        """
        Recherche un vol selon un critère.
        
        Args:
            critere (str): Critère de recherche ('numero', etc.)
            valeur: Valeur à rechercher
            
        Returns:
            Vol ou None: Vol trouvé ou None
        """
        if critere == "numero":
            return self.vols.get(valeur, None)
        return None
    
    def rechercher_avion(self, id_avion):
        """Recherche un avion par son ID"""
        return self.avions.get(id_avion, None)
    
    def rechercher_passager(self, id_passager):
        """Recherche un passager par son ID"""
        return self.passagers.get(id_passager, None)
    
    def enregistrer_retard(self, vol, cause, minutes_retard):
        """
        Enregistre un nouveau retard pour un vol.
        
        Args:
            vol: Vol concerné
            cause (str): Cause du retard
            minutes_retard (int): Durée en minutes
            
        Returns:
            GestionRetard: Objet retard créé
        """
        retard = GestionRetard(vol, cause, minutes_retard)
        retard.appliquer_procedure()
        self.retards.append(retard)
        self.statistiques['vols_retardes'] += 1
        print(f"Retard enregistré pour le vol {getattr(vol, 'numero_vol', 'N/A')}")
        return retard
    
    def obtenir_statistiques(self):
        """Retourne les statistiques actuelles"""
        # Mise à jour des stats calculées
        self.statistiques.update({
            'avions_total': len(self.avions),
            'employes_total': len(self.personnel),
            'vols_actifs': len(self.obtenir_vols_actifs()),
            'retards_total': len(self.retards),
            'aeroports_total': len(self.aeroports_desservis),
            'avions_disponibles': len(self.obtenir_avions_disponibles())
        })
        return self.statistiques.copy()
    
    def __str__(self):
        stats = self.obtenir_statistiques()
        return (f"{self.nom} - Avions: {stats['avions_total']}, "
                f"Vols: {stats['vols_total']}, Employés: {stats['employes_total']}")
    
    def __repr__(self):
        return f"Compagnie(nom='{self.nom}', id='{self.id_compagnie[:8]}...')"