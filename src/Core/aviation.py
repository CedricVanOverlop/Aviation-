from datetime import datetime
from math import radians, sin, cos, asin, sqrt
from .enums import StatutVol,EtatAvion,StatutPiste,TypePersonnel

class Coordonnees:
    """Classe pour gérer les coordonnées géographiques (longitude, latitude)"""
    
    def __init__(self, longitude, latitude):
        """
        Initialise une paire de coordonnées géographiques.
        
        Args:
            longitude (float): Longitude en degrés décimaux
            latitude (float): Latitude en degrés décimaux
        """
        self.longitude = longitude
        self.latitude = latitude
    
    def obtenir_coordonnees(self):
        """
        Retourne les coordonnées sous forme de tuple.
        
        Returns:
            tuple: (longitude, latitude)
        """
        return self.longitude, self.latitude
    
    def calculer_distance(self, autre):
        """

        Calcule la distance en km entre deux points avec la formule de Haversine
        
        Args:
            autre (Coordonnees): L'autre point
            
        Returns:
            float: Distance en kilomètres
        """

        R = 6371  # Rayon de la Terre en km
        
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(autre.latitude), radians(autre.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        distance = R * 2 * asin(sqrt(a))
        
        return distance

class Avion:
    """Classe représentant un avion avec ses caractéristiques essentielles"""
    
    def __init__(self, num_id, modele, capacite, compagnie_aerienne, 
                 vitesse_croisiere, autonomie, localisation, 
                 etat=EtatAvion.AU_SOL):
        """
        Initialise un avion.
        
        Args:
            num_id (str): Identifiant unique
            modele (str): Modèle de l'avion
            capacite (int): Capacité maximale de passagers
            compagnie_aerienne (str): Compagnie propriétaire
            vitesse_croisiere (float): Vitesse de croisière en km/h
            autonomie (float): Autonomie en km
            localisation (Coordonnees): Position actuelle
            etat (EtatAvion): État actuel
        """
        self.num_id = num_id
        self.modele = modele
        self.capacite = int(capacite)
        self.compagnie_aerienne = compagnie_aerienne
        self.vitesse_croisiere = float(vitesse_croisiere)
        self.autonomie = float(autonomie)
        self.localisation = localisation
        self.etat = etat
        self.vol_actuel = None
        self.derniere_maintenance = None
    
    def peut_effectuer_vol(self, distance, meteo=None):
        """
        Vérifie si l'avion peut effectuer un vol.
        
        Args:
            distance (float): Distance du vol en km
            meteo: Conditions météorologiques (optionnel)
            
        Returns:
            bool: True si possible, False sinon
        """
        if not self.etat.est_operationnel():
            return False
        
        if distance > self.autonomie:
            return False
            
        if meteo and hasattr(meteo, 'est_vol_possible'):
            return meteo.est_vol_possible()
            
        return True
    
    def demarrer_vol(self, vol):
        """
        Démarre un vol.
        
        Args:
            vol: Objet Vol
            
        Returns:
            bool: True si démarré avec succès
        """
        if not self.peut_effectuer_vol(vol.distance if hasattr(vol, 'distance') else 0):
            return False
            
        self.vol_actuel = vol
        self.etat = EtatAvion.EN_VOL
        return True
    
    def atterrir(self, aeroport_destination):
        """
        Fait atterrir l'avion.
        
        Args:
            aeroport_destination: Aéroport de destination
            
        Returns:
            bool: True si atterrissage réussi
        """
        if self.etat != EtatAvion.EN_VOL:
            return False
            
        # Vérifier si l'avion est à proximité de l'aéroport
        if hasattr(aeroport_destination, 'localisation'):
            distance = self.localisation.calculer_distance(aeroport_destination.localisation)
            if distance > 50:  # Trop loin pour atterrir
                return False
        
        self.localisation = aeroport_destination.localisation
        self.etat = EtatAvion.AU_SOL
        self.vol_actuel = None
        return True
    
    def programmer_maintenance(self, date_maintenance=None):
        """
        Programme une maintenance.
        
        Args:
            date_maintenance (datetime): Date de maintenance (défaut: maintenant)
            
        Returns:
            bool: True si programmée avec succès
        """
        if self.etat == EtatAvion.EN_VOL:
            return False
            
        self.etat = EtatAvion.EN_MAINTENANCE
        self.derniere_maintenance = date_maintenance or datetime.now()
        return True
    
    def terminer_maintenance(self):
        """Termine la maintenance et remet l'avion en service"""
        if self.etat == EtatAvion.EN_MAINTENANCE:
            self.etat = EtatAvion.OPERATIONNEL
            return True
        return False
    
    def ou_est_avion(self):
        """Retourne la position actuelle de l'avion"""
        return self.localisation
    
    def mettre_au_sol(self):
        """Met l'avion au sol"""
        if self.etat == EtatAvion.EN_VOL:
            self.etat = EtatAvion.AU_SOL
            return True
        return False
    
    def mettre_en_vol(self):
        """Met l'avion en vol"""
        if self.etat.est_operationnel():
            self.etat = EtatAvion.EN_VOL
            return True
        return False
    
    def changer_etat(self, nouvel_etat):
        """Change l'état de l'avion de manière contrôlée"""
        if isinstance(nouvel_etat, EtatAvion):
            self.etat = nouvel_etat
            return True
        return False
    
    def __repr__(self):
        return f"Avion(num_id='{self.num_id}', modele='{self.modele}', etat={self.etat})"

class Aeroport:
    """Classe représentant un aéroport avec ses infrastructures"""
    
    def __init__(self, nom, code_iata, coordonnees, 
                 pistes=None, villes_desservies=None):
        """
        Initialise un aéroport.
        
        Args:
            nom (str): Nom de l'aéroport
            code_iata (str): Code IATA (3 lettres)
            coordonnees (Coordonnees): Position géographique
            pistes (list): Liste des pistes
            villes_desservies (list): Villes desservies
        """
        self.nom = nom
        self.code_iata = code_iata.upper() if code_iata else ""
        self.coordonnees = coordonnees
        self.pistes = set(pistes) if pistes else set()
        self.villes_desservies = set(villes_desservies) if villes_desservies else set()
        self.avions_au_sol = set()
        self.quais = set()  # Gates/portes d'embarquement
        self.vols_programmes = []
        self.meteo_actuelle = None
    
    def ajouter_piste(self, piste):
        """
        Ajoute une piste à l'aéroport.
        
        Returns:
            bool: True si ajoutée avec succès
        """
        if isinstance(piste, PisteAtterrissage):
            self.pistes.add(piste)
            return True
        return False
    
    def retirer_piste(self, numero_piste):
        """Retire une piste par son numéro"""
        piste_a_retirer = next((p for p in self.pistes if p.numero == numero_piste), None)
        if piste_a_retirer:
            self.pistes.remove(piste_a_retirer)
            return True
        return False
    
    def obtenir_pistes_disponibles(self):
        """Retourne la liste des pistes disponibles"""
        return [p for p in self.pistes if p.est_disponible()]
    
    def avions_prets(self):
        """Retourne les avions prêts à voler"""
        return [avion for avion in self.avions_au_sol 
                if hasattr(avion, 'etat') and avion.etat.est_operationnel()] # self.etat: EtatAvion = etat  # ✅ Annotation explicite
    
    def enregistrer_arrivee_avion(self, avion):
        if hasattr(avion, 'etat') and hasattr(avion, 'localisation'):
            self.avions_au_sol.add(avion)
            # Utilise setattr pour éviter l'erreur
            setattr(avion, 'etat', EtatAvion.AU_SOL)
            avion.localisation = self.coordonnees
            return True
        return False

    def enregistrer_depart_avion(self, avion):
        if avion in self.avions_au_sol:
            self.avions_au_sol.remove(avion)
            if hasattr(avion, 'etat'):
                setattr(avion, 'etat', EtatAvion.EN_VOL)
            return True
        return False
    
    def peut_accueillir_vol(self, avion, distance=0):
        """
        Vérifie si l'aéroport peut accueillir un vol.
        
        Args:
            avion: Avion à accueillir
            distance: Distance minimale requise pour la piste
            
        Returns:
            bool: True si possible
        """
        # Vérifier météo si disponible
        if (self.meteo_actuelle and 
            hasattr(self.meteo_actuelle, 'est_vol_possible') and
            not self.meteo_actuelle.est_vol_possible()):
            return False
        
        # Vérifier pistes disponibles
        pistes_disponibles = self.obtenir_pistes_disponibles()
        if not pistes_disponibles:
            return False
            
        # Vérifier compatibilité basique
        pistes_compatibles = [p for p in pistes_disponibles 
                             if p.longueur >= max(1500, distance)]
        
        return len(pistes_compatibles) > 0
    
    def gerer_trafic(self):
        """
        Gère le trafic aérien basique.
        
        Returns:
            dict: Résumé des attributions
        """
        pistes_disponibles = self.obtenir_pistes_disponibles()
        attributions = {}
        
        for i, piste in enumerate(pistes_disponibles):
            if i < len(self.vols_programmes):
                vol = self.vols_programmes[i]
                attributions[vol] = piste.numero
        
        return attributions
    
    def ajouter_ville_desservie(self, ville):
        """Ajoute une ville desservie"""
        if isinstance(ville, str) and ville:
            self.villes_desservies.add(ville)
            return True
        return False
    
    def mettre_a_jour_meteo(self, nouvelle_meteo):   #ça veut changer encore
        """Met à jour les conditions météorologiques"""
        self.meteo_actuelle = nouvelle_meteo
        return True
    
    def __str__(self):
        pistes_count = len(self.pistes)
        avions_count = len(self.avions_au_sol)
        return f"Aéroport {self.nom} ({self.code_iata}) - Pistes: {pistes_count}, Avions: {avions_count}"
    
    def __repr__(self):
        return f"Aeroport(nom='{self.nom}', code_iata='{self.code_iata}')"

class PisteAtterrissage:
    """Classe représentant une piste d'atterrissage avec ses caractéristiques physiques et son état"""
    
    def __init__(self, numero, longueur=3000, largeur=45, surface="Asphalte"):
        """
        Initialise une piste d'atterrissage.
        
        Args:
            numero (str): Numéro d'identification de la piste (ex: "07", "25R")
            longueur (float): Longueur en mètres (défaut: 3000m)
            largeur (float): Largeur en mètres (défaut: 45m)
            surface (str): Type de surface (défaut: "Asphalte")
        """
        self.numero = str(numero)
        self.longueur = float(longueur)
        self.largeur = float(largeur)
        self.surface = surface
        self.statut = StatutPiste.DISPONIBLE
        self.avion_utilisant = None
    
    def est_disponible(self):
        """
        Vérifie si la piste est disponible pour utilisation.
        
        Returns:
            bool: True si la piste est libre et en service
        """
        return self.statut == StatutPiste.DISPONIBLE
    
    @property
    def en_service(self):
        """Vérifie si la piste est en service (pas hors service)"""
        return self.statut != StatutPiste.HORS_SERVICE
    
    def occuper_piste(self, avion):
        """
        Occupe la piste avec un avion donné.
        
        Args:
            avion: Avion utilisant la piste
            
        Returns:
            bool: True si l'occupation a réussi, False sinon
        """
        if self.est_disponible():
            self.statut = StatutPiste.OCCUPEE
            self.avion_utilisant = avion
            return True
        return False
    
    def liberer_piste(self):
        """
        Libère la piste après utilisation.
        
        Returns:
            bool: True si la libération a réussi, False sinon
        """
        if self.statut == StatutPiste.OCCUPEE:
            self.statut = StatutPiste.DISPONIBLE
            self.avion_utilisant = None
            return True
        return False
    
    def programmer_maintenance(self):
        """
        Met la piste en maintenance.
        
        Returns:
            bool: True si la maintenance a pu être programmée, False sinon
        """
        if self.statut != StatutPiste.OCCUPEE:
            self.statut = StatutPiste.MAINTENANCE
            self.avion_utilisant = None
            return True
        return False
    
    def terminer_maintenance(self):
        """
        Termine la maintenance et remet la piste en service.
        
        Returns:
            bool: True si la maintenance a été terminée avec succès
        """
        if self.statut == StatutPiste.MAINTENANCE:
            self.statut = StatutPiste.DISPONIBLE
            return True
        return False
    
    def mettre_hors_service(self):
        """
        Met la piste hors service.
        
        Returns:
            bool: True si mise hors service réussie
        """
        if self.statut != StatutPiste.OCCUPEE:
            self.statut = StatutPiste.HORS_SERVICE
            self.avion_utilisant = None
            return True
        return False
    
    def mettre_en_service(self):
        """
        Remet la piste en service.
        
        Returns:
            bool: True si remise en service réussie
        """
        if self.statut == StatutPiste.HORS_SERVICE:
            self.statut = StatutPiste.DISPONIBLE
            return True
        return False
    
    def peut_accueillir_avion(self, longueur_necessaire=1500):
        """
        Vérifie si la piste peut accueillir un avion nécessitant une certaine longueur.
        
        Args:
            longueur_necessaire (float): Longueur minimum requise en mètres
            
        Returns:
            bool: True si la piste est assez longue et disponible
        """
        return (self.est_disponible() and 
                self.longueur >= longueur_necessaire)
    
    def obtenir_informations(self):
        """
        Retourne un dictionnaire avec toutes les informations de la piste.
        
        Returns:
            dict: Informations complètes de la piste
        """
        return {
            'numero': self.numero,
            'longueur': self.longueur,
            'largeur': self.largeur,
            'surface': self.surface,
            'statut': self.statut.value,
            'en_service': self.en_service,
            'disponible': self.est_disponible(),
            'avion_utilisant': str(self.avion_utilisant) if self.avion_utilisant else None
        }
    
    def __str__(self):
        """Représentation textuelle conviviale de la piste"""
        avion_info = f" (utilisée par {self.avion_utilisant})" if self.avion_utilisant else ""
        return f"Piste {self.numero} ({self.longueur}m x {self.largeur}m, {self.surface}) - {self.statut.value}{avion_info}"
    
    def __repr__(self):
        """Représentation officielle pour le débogage"""
        return (f"PisteAtterrissage(numero='{self.numero}', longueur={self.longueur}, "
                f"largeur={self.largeur}, surface='{self.surface}', statut={self.statut})")
    
    def __eq__(self, other):
        """Compare deux pistes basé sur leur numéro"""
        if not isinstance(other, PisteAtterrissage):
            return NotImplemented
        return self.numero == other.numero
    
    def __hash__(self):
        """Hash basé sur le numéro de piste pour utilisation dans sets/dicts"""
        return hash(self.numero)
