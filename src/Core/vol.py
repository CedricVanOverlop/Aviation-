from datetime import datetime, timedelta
from .enums import StatutVol
from typing import List, Optional, Dict, Any, Set
import uuid

class Vol:
    """Classe représentant un vol commercial avec gestion d'état complète"""
    
    def __init__(self, numero_vol, aeroport_depart, aeroport_arrivee, 
                 avion_utilise, heure_depart, heure_arrivee_prevue,
                 passagers=None, personnel=None):
        """
        Initialise un vol.
        
        Args:
            numero_vol (str): Numéro unique du vol
            aeroport_depart: Aéroport de départ  
            aeroport_arrivee: Aéroport d'arrivée
            avion_utilise: Avion assigné au vol
            heure_depart (datetime): Heure de départ prévue
            heure_arrivee_prevue (datetime): Heure d'arrivée prévue
            passagers (list, optional): Liste des passagers
            personnel (list, optional): Équipage du vol
        """
        # Validation basique
        if not numero_vol:
            raise ValueError("Le numéro de vol ne peut pas être vide")
        if not isinstance(heure_depart, datetime) or not isinstance(heure_arrivee_prevue, datetime):
            raise TypeError("Les heures doivent être des objets datetime")
        if heure_arrivee_prevue <= heure_depart:
            raise ValueError("L'heure d'arrivée doit être postérieure au départ")
        
        # Propriétés principales
        self.numero_vol = str(numero_vol)
        self.aeroport_depart = aeroport_depart
        self.aeroport_arrivee = aeroport_arrivee
        self.avion_utilise = avion_utilise
        self.heure_depart = heure_depart
        self.heure_arrivee_prevue = heure_arrivee_prevue
        
        # État et gestion
        self.statut = StatutVol.PROGRAMME
        self.passagers = list(passagers) if passagers else []
        self.personnel = list(personnel) if personnel else []
        self.retards = []
        self.meteo_actuelle = None
        
        # Propriétés calculées/cachées
        self._distance = None
        self._piste_depart = None
        self._piste_arrivee = None
        
        print(f"[VOL] Vol {self.numero_vol} créé: {self._code_depart()} → {self._code_arrivee()}")
    
    def _code_depart(self):
        """Obtient le code de l'aéroport de départ de manière sécurisée"""
        if hasattr(self.aeroport_depart, 'code_iata'):
            return self.aeroport_depart.code_iata
        elif hasattr(self.aeroport_depart, 'nom'):
            return self.aeroport_depart.nom[:3].upper()
        else:
            return str(self.aeroport_depart)[:3].upper()
    
    def _code_arrivee(self):
        """Obtient le code de l'aéroport d'arrivée de manière sécurisée"""
        if hasattr(self.aeroport_arrivee, 'code_iata'):
            return self.aeroport_arrivee.code_iata
        elif hasattr(self.aeroport_arrivee, 'nom'):
            return self.aeroport_arrivee.nom[:3].upper()
        else:
            return str(self.aeroport_arrivee)[:3].upper()
    
    def calculer_distance(self):
        """
        Calcule la distance entre les aéroports de départ et d'arrivée.
        
        Returns:
            float: Distance en kilomètres
        """
        if self._distance is not None:
            return self._distance
        
        # Utilise la méthode de Coordonnees si disponible
        if (hasattr(self.aeroport_depart, 'coordonnees') and 
            hasattr(self.aeroport_arrivee, 'coordonnees') and
            hasattr(self.aeroport_depart.coordonnees, 'calculer_distance')):
            self._distance = self.aeroport_depart.coordonnees.calculer_distance(
                self.aeroport_arrivee.coordonnees
            )
        else:
            # Fallback avec distance approximative par défaut
            self._distance = 1000.0  # 1000km par défaut
            print(f"[VOL] Distance approximative utilisée pour {self.numero_vol}")
        
        return self._distance
    
    def autonomie_suffisante(self):
        """
        Vérifie si l'avion a une autonomie suffisante pour le vol.
        
        Returns:
            bool: True si l'autonomie est suffisante
        """
        if not hasattr(self.avion_utilise, 'autonomie'):
            return True  # Assume suffisante si pas d'info
        
        distance = self.calculer_distance()
        # Marge de sécurité de 20%
        distance_securite = distance * 1.2
        
        return distance_securite <= self.avion_utilise.autonomie
    
    def peut_decoller(self, meteo=None):
        """
        Vérifie si le vol peut décoller dans les conditions actuelles.
        
        Args:
            meteo: Conditions météorologiques (optionnel)
            
        Returns:
            bool: True si le décollage est possible
        """
        # Vérification statut
        if self.statut not in [StatutVol.PROGRAMME, StatutVol.EN_ATTENTE]:
            return False
        
        # Vérification avion
        if hasattr(self.avion_utilise, 'etat'):
            if hasattr(self.avion_utilise.etat, 'est_operationnel'):
                if not self.avion_utilise.etat.est_operationnel():
                    return False
        
        # Vérification autonomie
        if not self.autonomie_suffisante():
            print(f"[VOL] {self.numero_vol}: Autonomie insuffisante")
            return False
        
        # Vérification météo
        if meteo:
            if hasattr(meteo, 'est_vol_possible'):
                if not meteo.est_vol_possible():
                    print(f"[VOL] {self.numero_vol}: Conditions météo défavorables")
                    return False
            elif hasattr(meteo, 'statut_vent'):
                if meteo.statut_vent() == "danger":
                    print(f"[VOL] {self.numero_vol}: Vent dangereux")
                    return False
        
        # Vérification équipage minimum
        if not self.a_equipage_minimum():
            print(f"[VOL] {self.numero_vol}: Équipage insuffisant")
            return False
        
        return True
    
    def a_equipage_minimum(self):
        """Vérifie si l'équipage minimum est présent"""
        if not self.personnel:
            return False
        
        # Recherche pilote et personnel navigant
        a_pilote = False
        a_personnel_navigant = False
        
        for membre in self.personnel:
            if hasattr(membre, 'type_personnel'):
                type_personnel = getattr(membre.type_personnel, 'value', str(membre.type_personnel))
                if 'pilote' in type_personnel.lower():
                    a_pilote = True
                elif 'hotesse' in type_personnel.lower() or 'steward' in type_personnel.lower():
                    a_personnel_navigant = True
            elif hasattr(membre, 'metier'):
                metier = str(membre.metier).lower()
                if 'pilote' in metier:
                    a_pilote = True
                elif 'hotesse' in metier or 'steward' in metier:
                    a_personnel_navigant = True
        
        # Pilote obligatoire, personnel navigant si passagers
        return a_pilote and (len(self.passagers) == 0 or a_personnel_navigant)
    
    def qui_est_enregistre(self):
        """
        Retourne la liste des passagers ayant effectué leur enregistrement.
        
        Returns:
            list: Liste des passagers enregistrés
        """
        enregistres = []
        
        for passager in self.passagers:
            # Vérification multiple selon la structure de l'objet passager
            if hasattr(passager, 'est_enregistre') and callable(passager.est_enregistre):
                if passager.est_enregistre():
                    enregistres.append(passager)
            elif hasattr(passager, 'checkin_effectue'):
                if passager.checkin_effectue:
                    enregistres.append(passager)
            elif hasattr(passager, 'reservation_actuelle'):
                if (passager.reservation_actuelle and 
                    hasattr(passager.reservation_actuelle, 'checkin_effectue') and
                    passager.reservation_actuelle.checkin_effectue):
                    enregistres.append(passager)
        
        return enregistres
    
    def obtenir_personnel(self):
        """
        Retourne la liste du personnel assigné au vol par catégorie.
        
        Returns:
            dict: Personnel organisé par catégorie
        """
        personnel_organise = {
            'pilotes': [],
            'personnel_navigant': [],
            'autres': []
        }
        
        for membre in self.personnel:
            # Classification selon attributs disponibles
            if hasattr(membre, 'type_personnel'):
                type_personnel = getattr(membre.type_personnel, 'value', str(membre.type_personnel))
                if 'pilote' in type_personnel.lower():
                    personnel_organise['pilotes'].append(membre)
                elif any(x in type_personnel.lower() for x in ['hotesse', 'steward', 'navigant']):
                    personnel_organise['personnel_navigant'].append(membre)
                else:
                    personnel_organise['autres'].append(membre)
            elif hasattr(membre, 'metier'):
                metier = str(membre.metier).lower()
                if 'pilote' in metier:
                    personnel_organise['pilotes'].append(membre)
                elif any(x in metier for x in ['hotesse', 'steward', 'navigant']):
                    personnel_organise['personnel_navigant'].append(membre)
                else:
                    personnel_organise['autres'].append(membre)
            else:
                personnel_organise['autres'].append(membre)
        
        return personnel_organise
    
    def ajouter_passager(self, passager):
        """
        Ajoute un passager au vol.
        
        Args:
            passager: Passager à ajouter
            
        Returns:
            bool: True si ajouté avec succès
        """
        if passager in self.passagers:
            return False
        
        # Vérification capacité
        if hasattr(self.avion_utilise, 'capacite'):
            if len(self.passagers) >= self.avion_utilise.capacite:
                print(f"[VOL] {self.numero_vol}: Capacité maximale atteinte")
                return False
        
        self.passagers.append(passager)
        print(f"[VOL] Passager ajouté au vol {self.numero_vol}")
        return True
    
    def retirer_passager(self, passager):
        """Retire un passager du vol"""
        if passager in self.passagers:
            self.passagers.remove(passager)
            return True
        return False
    
    def ajouter_personnel(self, membre):
        """
        Ajoute un membre du personnel au vol.
        
        Args:
            membre: Membre du personnel à ajouter
            
        Returns:
            bool: True si ajouté avec succès
        """
        if membre in self.personnel:
            return False
        
        self.personnel.append(membre)
        print(f"[VOL] Personnel ajouté au vol {self.numero_vol}")
        return True
    
    def ajouter_retard(self, type_retard, duree_minutes, cause=""):
        """
        Ajoute un retard au vol.
        
        Args:
            type_retard (str): Type/cause du retard
            duree_minutes (int): Durée du retard en minutes
            cause (str): Cause détaillée
            
        Returns:
            bool: True si le retard a été ajouté avec succès
        """
        if duree_minutes <= 0:
            return False
        
        # Création d'un objet retard simple
        retard = {
            'type': str(type_retard),
            'duree_minutes': int(duree_minutes),
            'cause': str(cause) if cause else str(type_retard),
            'heure_creation': datetime.now(),
            'applique': False
        }
        
        self.retards.append(retard)
        print(f"[VOL] Retard ajouté au vol {self.numero_vol}: {duree_minutes}min - {type_retard}")
        return True
    
    def appliquer_retard(self, index_retard=None):
        """
        Applique un retard (modifie les heures de départ/arrivée).
        
        Args:
            index_retard (int, optional): Index du retard à appliquer (dernier par défaut)
            
        Returns:
            bool: True si retard appliqué
        """
        if not self.retards:
            return False
        
        # Prend le dernier retard par défaut
        if index_retard is None:
            index_retard = len(self.retards) - 1
        
        if index_retard < 0 or index_retard >= len(self.retards):
            return False
        
        retard = self.retards[index_retard]
        
        if retard['applique']:
            return False
        
        # Application du retard
        duree = timedelta(minutes=retard['duree_minutes'])
        self.heure_depart += duree
        self.heure_arrivee_prevue += duree
        retard['applique'] = True
        
        # Mise à jour statut
        if self.statut == StatutVol.PROGRAMME:
            self.statut = StatutVol.RETARDE
        
        print(f"[VOL] Retard appliqué au vol {self.numero_vol}: +{retard['duree_minutes']}min")
        return True
    
    def choisir_avion(self, liste_avions_disponibles):
        """
        Choisit le meilleur avion pour ce vol parmi ceux disponibles.
        
        Args:
            liste_avions_disponibles (list): Avions disponibles
            
        Returns:
            Avion: Meilleur avion pour ce vol, None si aucun convient
        """
        if not liste_avions_disponibles:
            return None
        
        distance = self.calculer_distance()
        nb_passagers = len(self.passagers)
        
        avions_compatibles = []
        
        for avion in liste_avions_disponibles:
            # Vérifications de base
            if hasattr(avion, 'etat'):
                if hasattr(avion.etat, 'est_operationnel') and not avion.etat.est_operationnel():
                    continue
            
            # Vérification autonomie (avec marge)
            if hasattr(avion, 'autonomie'):
                if distance * 1.2 > avion.autonomie:
                    continue
            
            # Vérification capacité
            if hasattr(avion, 'capacite'):
                if nb_passagers > avion.capacite:
                    continue
            
            # Calcul score (favorise capacité proche du besoin)
            score = 0
            if hasattr(avion, 'capacite'):
                # Pénalise les avions trop grands ou trop petits
                ratio_capacite = nb_passagers / avion.capacite if avion.capacite > 0 else 0
                if 0.6 <= ratio_capacite <= 1.0:
                    score += 100
                elif 0.3 <= ratio_capacite < 0.6:
                    score += 50
                else:
                    score += 10
            
            if hasattr(avion, 'autonomie'):
                # Favorise autonomie suffisante mais pas excessive
                ratio_autonomie = distance / avion.autonomie if avion.autonomie > 0 else 1
                if 0.3 <= ratio_autonomie <= 0.7:
                    score += 50
                elif ratio_autonomie < 0.3:
                    score += 20  # Trop d'autonomie = moins économique
                else:
                    score += 10
            
            avions_compatibles.append((avion, score))
        
        if not avions_compatibles:
            return None
        
        # Retourne l'avion avec le meilleur score
        meilleur_avion = max(avions_compatibles, key=lambda x: x[1])[0]
        print(f"[VOL] Avion {getattr(meilleur_avion, 'num_id', 'N/A')} sélectionné pour {self.numero_vol}")
        return meilleur_avion
    
    def preparer_depart(self):
        """
        Prépare le vol pour le départ.
        
        Returns:
            bool: True si préparation réussie
        """
        if self.statut != StatutVol.PROGRAMME:
            return False
        
        # Vérifications de base
        if not self.peut_decoller(self.meteo_actuelle):
            return False
        
        self.statut = StatutVol.EN_ATTENTE
        print(f"[VOL] Vol {self.numero_vol} préparé pour le départ")
        return True
    
    def demarrer_vol(self):
        """
        Démarre le vol (passage en vol).
        
        Returns:
            bool: True si démarrage réussi
        """
        if self.statut != StatutVol.EN_ATTENTE:
            return False
        
        if not self.peut_decoller(self.meteo_actuelle):
            return False
        
        self.statut = StatutVol.EN_VOL
        
        # Mise à jour état avion
        if hasattr(self.avion_utilise, 'etat'):
            if hasattr(self.avion_utilise.etat, '__class__'):
                self.avion_utilise.etat = self.avion_utilise.etat.__class__.EN_VOL
        
        print(f"[VOL] Vol {self.numero_vol} en cours")
        return True
    
    def atterrir(self):
        """
        Fait atterrir le vol.
        
        Returns:
            bool: True si atterrissage réussi
        """
        if self.statut != StatutVol.EN_VOL:
            return False
        
        self.statut = StatutVol.ATTERRI
        
        # Mise à jour état avion
        if hasattr(self.avion_utilise, 'etat'):
            if hasattr(self.avion_utilise.etat, '__class__'):
                self.avion_utilise.etat = self.avion_utilise.etat.__class__.AU_SOL
        
        print(f"[VOL] Vol {self.numero_vol} atterri")
        return True
    
    def annuler_vol(self, cause=""):
        """
        Annule le vol.
        
        Args:
            cause (str): Raison de l'annulation
            
        Returns:
            bool: True si annulation réussie
        """
        if self.statut in [StatutVol.ANNULE, StatutVol.TERMINE]:
            return False
        
        self.statut = StatutVol.ANNULE
        
        # Ajouter retard d'annulation pour statistiques
        if cause:
            self.ajouter_retard("Annulation", 0, cause)
        
        print(f"[VOL] Vol {self.numero_vol} annulé: {cause}")
        return True
    
    def terminer_vol(self):
        """Marque le vol comme terminé"""
        if self.statut != StatutVol.ATTERRI:
            return False
        
        self.statut = StatutVol.TERMINE
        print(f"[VOL] Vol {self.numero_vol} terminé")
        return True
    
    def obtenir_duree_estimee(self):
        """Calcule la durée estimée du vol"""
        return self.heure_arrivee_prevue - self.heure_depart
    
    def obtenir_informations(self):
        """
        Retourne un dictionnaire avec toutes les informations du vol.
        
        Returns:
            dict: Informations complètes du vol
        """
        return {
            'numero_vol': self.numero_vol,
            'aeroport_depart': self._code_depart(),
            'aeroport_arrivee': self._code_arrivee(),
            'heure_depart': self.heure_depart.strftime('%Y-%m-%d %H:%M'),
            'heure_arrivee_prevue': self.heure_arrivee_prevue.strftime('%Y-%m-%d %H:%M'),
            'statut': self.statut.obtenir_nom_affichage(),
            'duree_estimee': str(self.obtenir_duree_estimee()),
            'distance_km': round(self.calculer_distance(), 2),
            'nb_passagers': len(self.passagers),
            'nb_personnel': len(self.personnel),
            'nb_retards': len(self.retards),
            'autonomie_suffisante': self.autonomie_suffisante(),
            'peut_decoller': self.peut_decoller(self.meteo_actuelle),
            'equipage_complet': self.a_equipage_minimum(),
            'passagers_enregistres': len(self.qui_est_enregistre())
        }
    
    def to_dict(self):
        """Conversion pour sérialisation"""
        return {
            'numero_vol': self.numero_vol,
            'aeroport_depart': str(self.aeroport_depart),
            'aeroport_arrivee': str(self.aeroport_arrivee),
            'avion_utilise': str(self.avion_utilise),
            'heure_depart': self.heure_depart.isoformat(),
            'heure_arrivee_prevue': self.heure_arrivee_prevue.isoformat(),
            'statut': self.statut.value,
            'nb_passagers': len(self.passagers),
            'nb_personnel': len(self.personnel),
            'retards': self.retards
        }
    
    def __str__(self):
        """Représentation textuelle conviviale"""
        depart_str = self.heure_depart.strftime("%H:%M")
        arrivee_str = self.heure_arrivee_prevue.strftime("%H:%M")
        
        return (f"Vol {self.numero_vol} ({self._code_depart()} → {self._code_arrivee()}) | "
                f"Statut: {self.statut.obtenir_nom_affichage()} | "
                f"Horaire: {depart_str} → {arrivee_str} | "
                f"Passagers: {len(self.passagers)}")
    
    def __repr__(self):
        return (f"Vol(numero='{self.numero_vol}', "
                f"statut={self.statut}, "
                f"passagers={len(self.passagers)})")
    
    def __eq__(self, other):
        return isinstance(other, Vol) and self.numero_vol == other.numero_vol
    
    def __hash__(self):
        return hash(self.numero_vol)