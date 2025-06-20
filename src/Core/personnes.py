from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from .enums import TypeSexe, TypePersonnel
from typing import List, Optional, Dict, Any
import uuid
import re

class Personne(ABC):
    """Classe abstraite représentant une personne"""
    
    def __init__(self, nom, prenom, sexe, adresse, date_naissance=None, 
                 numero_telephone=None, email=None):
        """
        Initialise une personne.
        
        Args:
            nom (str): Nom de famille
            prenom (str): Prénom
            sexe (TypeSexe ou str): Sexe
            adresse (str): Adresse
            date_naissance (datetime, optional): Date de naissance
            numero_telephone (str, optional): Numéro de téléphone
            email (str, optional): Adresse email
        """
        self.id_personne = str(uuid.uuid4())
        self.nom = str(nom).strip().upper() if nom else ""
        self.prenom = str(prenom).strip().capitalize() if prenom else ""
        
        # Gestion flexible du sexe
        if isinstance(sexe, str):
            try:
                self.sexe = TypeSexe(sexe.lower())
            except ValueError:
                self.sexe = TypeSexe.AUTRE
        elif isinstance(sexe, TypeSexe):
            self.sexe = sexe
        else:
            self.sexe = TypeSexe.AUTRE
            
        self.adresse = str(adresse).strip() if adresse else ""
        self.date_naissance = date_naissance or datetime.now()
        self.numero_telephone = self._valider_telephone(numero_telephone)
        self.email = self._valider_email(email)
    
    def _valider_telephone(self, telephone):
        """Valide le numéro de téléphone de manière souple"""
        if not telephone:
            return None
        # Accepte la plupart des formats de téléphone
        tel_clean = re.sub(r'[^\d+]', '', str(telephone))
        return tel_clean if len(tel_clean) >= 7 else None
    
    def _valider_email(self, email):
        """Valide l'email de manière souple"""
        if not email:
            return None
        email = str(email).strip()
        # Validation basique d'email
        if '@' in email and '.' in email.split('@')[-1]:
            return email
        return None
    
    def obtenir_nom(self):
        """Retourne le nom de famille"""
        return self.nom
    
    def obtenir_prenom(self):
        """Retourne le prénom"""
        return self.prenom
    
    def obtenir_nom_complet(self):
        """Retourne le nom complet"""
        return f"{self.prenom} {self.nom}".strip()
    
    def calculer_age(self):
        """Calcule l'âge en années"""
        if not self.date_naissance:
            return 0
        today = datetime.now()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
    
    def to_dict(self):
        """Convertit en dictionnaire pour sérialisation"""
        return {
            'id_personne': self.id_personne,
            'nom': self.nom,
            'prenom': self.prenom,
            'sexe': self.sexe.value,
            'adresse': self.adresse,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'numero_telephone': self.numero_telephone,
            'email': self.email
        }
    
    def __str__(self):
        return f"{self.obtenir_nom_complet()} ({self.calculer_age()} ans)"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(nom='{self.nom}', prenom='{self.prenom}')"

class Personnel(Personne):
    """Classe représentant un employé de la compagnie"""
    
    def __init__(self, nom, prenom, sexe, adresse, metier, id_employe=None,
                 date_naissance=None, numero_telephone=None, email=None,
                 horaire="Temps plein", specialisation=None):
        """
        Initialise un employé.
        
        Args:
            nom (str): Nom de famille
            prenom (str): Prénom
            sexe: Sexe
            adresse (str): Adresse
            metier (TypePersonnel ou str): Poste occupé
            id_employe (str, optional): Identifiant unique
            horaire (str): Horaires de travail
            specialisation (str, optional): Spécialisation (pilote, mécanicien, etc.)
        """
        super().__init__(nom, prenom, sexe, adresse, date_naissance, numero_telephone, email)
        
        # Gestion flexible du métier
        if isinstance(metier, str):
            try:
                self.type_personnel = TypePersonnel(metier.lower())
            except ValueError:
                # Mapping pour compatibilité
                mapping = {
                    'pilote': TypePersonnel.PILOTE,
                    'hotesse': TypePersonnel.HOTESSE,
                    'mecanicien': TypePersonnel.MECANICIEN,
                    'controleur': TypePersonnel.CONTROLEUR
                }
                self.type_personnel = mapping.get(metier.lower(), TypePersonnel.GESTIONNAIRE)
        elif isinstance(metier, TypePersonnel):
            self.type_personnel = metier
        else:
            self.type_personnel = TypePersonnel.GESTIONNAIRE
            
        self.id_employe = str(id_employe) if id_employe else str(uuid.uuid4())
        self.horaire = str(horaire) if horaire else "Temps plein"
        self.disponible = True
        self.specialisation = str(specialisation) if specialisation else ""
        
        # Attributs spécifiques selon le type
        self.heures_vol = 0.0  # Pour pilotes/copilotes
        self.numero_licence = ""  # Pour pilotes
        self.langues_parlees = []  # Pour personnel navigant
        self.departement = ""  # Pour gestionnaires
        self.tour_controle = ""  # Pour contrôleurs
    
    def obtenir_metier(self):
        """Retourne le poste occupé"""
        return self.type_personnel.obtenir_nom_affichage()
    
    def obtenir_horaire(self):
        """Retourne les horaires de travail"""
        return self.horaire
    
    def definir_disponibilite(self, disponible):
        """
        Définit la disponibilité de l'employé.
        
        Args:
            disponible (bool): True si disponible, False sinon
        """
        self.disponible = bool(disponible)
        return self.disponible
    
    def ajouter_heures_vol(self, heures):
        """Ajoute des heures de vol (pour pilotes/copilotes)"""
        if self.type_personnel in [TypePersonnel.PILOTE, TypePersonnel.COPILOTE]:
            self.heures_vol += float(heures)
            return True
        return False
    
    def definir_licence(self, numero_licence):
        """Définit le numéro de licence (pour pilotes)"""
        if self.type_personnel == TypePersonnel.PILOTE:
            self.numero_licence = str(numero_licence)
            return True
        return False
    
    def ajouter_langue(self, langue):
        """Ajoute une langue parlée (pour personnel navigant)"""
        if self.type_personnel in [TypePersonnel.HOTESSE, TypePersonnel.STEWARD]:
            if langue not in self.langues_parlees:
                self.langues_parlees.append(str(langue).capitalize())
            return True
        return False
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        data = super().to_dict()
        data.update({
            'id_employe': self.id_employe,
            'type_personnel': self.type_personnel.value,
            'horaire': self.horaire,
            'disponible': self.disponible,
            'specialisation': self.specialisation,
            'heures_vol': self.heures_vol,
            'numero_licence': self.numero_licence,
            'langues_parlees': self.langues_parlees,
            'departement': self.departement,
            'tour_controle': self.tour_controle
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crée un personnel depuis un dictionnaire"""
        date_naiss = None
        if data.get('date_naissance'):
            date_naiss = datetime.fromisoformat(data['date_naissance'])
            
        personnel = cls(
            nom=data['nom'],
            prenom=data['prenom'],
            sexe=data['sexe'],
            adresse=data['adresse'],
            metier=data.get('type_personnel', 'gestionnaire'),
            id_employe=data.get('id_employe'),
            date_naissance=date_naiss,
            numero_telephone=data.get('numero_telephone'),
            email=data.get('email'),
            horaire=data.get('horaire', 'Temps plein'),
            specialisation=data.get('specialisation')
        )
        
        # Restaurer attributs spécifiques
        personnel.disponible = data.get('disponible', True)
        personnel.heures_vol = data.get('heures_vol', 0.0)
        personnel.numero_licence = data.get('numero_licence', '')
        personnel.langues_parlees = data.get('langues_parlees', [])
        personnel.departement = data.get('departement', '')
        personnel.tour_controle = data.get('tour_controle', '')
        
        return personnel
    
    def __str__(self):
        return f"{super().__str__()} - {self.obtenir_metier()} (ID: {self.id_employe[:8]}...)"

class Passager(Personne):
    """Classe représentant un passager"""
    
    def __init__(self, nom, prenom, sexe, adresse, id_passager=None, 
                 numero_passeport=None, date_naissance=None, 
                 numero_telephone=None, email=None):
        """
        Initialise un passager.
        
        Args:
            nom (str): Nom de famille
            prenom (str): Prénom
            sexe: Sexe
            adresse (str): Adresse
            id_passager (str, optional): Identifiant unique
            numero_passeport (str, optional): Numéro de passeport
        """
        super().__init__(nom, prenom, sexe, adresse, date_naissance, numero_telephone, email)
        self.id_passager = str(id_passager) if id_passager else str(uuid.uuid4())
        self.numero_passeport = self._valider_passeport(numero_passeport)
        self.reservation_actuelle = None
        self.historique_reservations = []
        self.checkin_effectue = False
    
    def _valider_passeport(self, passeport):
        """Valide le numéro de passeport de manière souple"""
        if not passeport:
            return None
        # Supprime espaces et garde seulement alphanumériques
        clean = re.sub(r'[^A-Z0-9]', '', str(passeport).upper())
        return clean if 6 <= len(clean) <= 15 else None
    
    def obtenir_historique(self):
        """Retourne l'historique des réservations"""
        return self.historique_reservations
    
    def effectuer_enregistrement(self):
        """
        Effectue l'enregistrement pour le vol actuel.
        
        Returns:
            bool: True si l'enregistrement a réussi
        """
        if self.reservation_actuelle and hasattr(self.reservation_actuelle, 'effectuer_enregistrement'):
            result = self.reservation_actuelle.effectuer_enregistrement()
            if result:
                self.checkin_effectue = True
            return result
        
        # Fallback si pas de réservation avec méthode
        if self.reservation_actuelle:
            self.checkin_effectue = True
            return True
        return False
    
    def est_enregistre(self):
        """
        Vérifie si l'enregistrement a été effectué.
        
        Returns:
            bool: True si enregistré
        """
        if self.reservation_actuelle and hasattr(self.reservation_actuelle, 'enregistrement_effectue'):
            return self.reservation_actuelle.enregistrement_effectue
        return self.checkin_effectue
    
    def creer_reservation(self, vol):
        """
        Crée une nouvelle réservation pour un vol.
        
        Args:
            vol: Vol à réserver
            
        Returns:
            dict: Réservation créée (format simplifié)
        """
        # Import local pour éviter circularité
        try:
            from .reservation import Reservation
            validite = datetime.now() + timedelta(days=1)
            num_reservation = f"RES-{self.id_passager}-{len(self.historique_reservations)+1}"
            reservation = Reservation(self, vol, num_reservation, validite)
            self.reservation_actuelle = reservation
            self.historique_reservations.append(reservation)
            return reservation
        except ImportError:
            # Fallback avec dict simple
            reservation = {
                'id_reservation': f"RES-{self.id_passager}-{len(self.historique_reservations)+1}",
                'passager': self,
                'vol': vol,
                'date_creation': datetime.now(),
                'validite': datetime.now() + timedelta(days=1),
                'enregistrement_effectue': False,
                'statut': 'active'
            }
            self.reservation_actuelle = reservation
            self.historique_reservations.append(reservation)
            print(f"Réservation créée avec succès: {reservation['id_reservation']}")
            return reservation
    
    def ajouter_reservation(self, reservation):
        """Ajoute une réservation à l'historique"""
        if reservation not in self.historique_reservations:
            self.historique_reservations.append(reservation)
    
    def effectuer_checkin(self):
        """Effectue le check-in"""
        if not self.checkin_effectue:
            self.checkin_effectue = True
            return True
        return False
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        data = super().to_dict()
        data.update({
            'id_passager': self.id_passager,
            'numero_passeport': self.numero_passeport,
            'checkin_effectue': self.checkin_effectue,
            'reservations_count': len(self.historique_reservations)
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Crée un passager depuis un dictionnaire"""
        date_naiss = None
        if data.get('date_naissance'):
            date_naiss = datetime.fromisoformat(data['date_naissance'])
            
        passager = cls(
            nom=data['nom'],
            prenom=data['prenom'],
            sexe=data['sexe'],
            adresse=data['adresse'],
            id_passager=data.get('id_passager'),
            numero_passeport=data.get('numero_passeport'),
            date_naissance=date_naiss,
            numero_telephone=data.get('numero_telephone'),
            email=data.get('email')
        )
        
        passager.checkin_effectue = data.get('checkin_effectue', False)
        return passager
    
    def __str__(self):
        passport_info = f" (Passeport: {self.numero_passeport})" if self.numero_passeport else ""
        return f"{super().__str__()} - Passager{passport_info}"
    
    def __eq__(self, other):
        return isinstance(other, Passager) and self.id_passager == other.id_passager
    
    def __hash__(self):
        return hash(self.id_passager)
