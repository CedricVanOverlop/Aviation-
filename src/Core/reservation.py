from datetime import datetime, timedelta
from .enums import StatutReservation
from typing import Optional, Dict, Any
import uuid
import re

class Reservation:
    """Classe représentant une réservation de vol avec gestion d'état optimisée"""
    
    # Pattern pour validation siège : "12A", "3B", etc.
    PATTERN_SIEGE = re.compile(r'^\d{1,3}[A-Z]$')
    
    def __init__(self, passager, vol, num_reservation=None, validite=None):
        """
        Initialise une réservation.
        
        Args:
            passager: Objet Passager
            vol: Objet Vol
            num_reservation (str, optional): Numéro unique
            validite (datetime, optional): Date limite validité
        """
        self.id_reservation = str(num_reservation) if num_reservation else str(uuid.uuid4())
        self.passager = passager
        self.vol = vol
        self.vol_original = vol  # Garde référence pour historique
        
        # Dates
        self.date_creation = datetime.now()
        if validite:
            self.validite = validite
        else:
            # Par défaut : valide 24h ou jusqu'à 2h avant départ
            if hasattr(vol, 'heure_depart') and vol.heure_depart:
                limite_vol = vol.heure_depart - timedelta(hours=2)
                limite_24h = self.date_creation + timedelta(days=1)
                self.validite = min(limite_vol, limite_24h)
            else:
                self.validite = self.date_creation + timedelta(days=1)
        
        # États
        self.statut = StatutReservation.ACTIVE
        self.siege_assigne = None
        self.checkin_effectue = False
        
        # Ajout automatique aux listes
        self._ajouter_aux_listes()
        
        print(f"[RÉSERVATION] Réservation {self.id_reservation[:8]}... créée pour {self._nom_passager()} sur vol {self._numero_vol()}")
    
    def _nom_passager(self):
        """Obtient le nom du passager de manière sécurisée"""
        if hasattr(self.passager, 'obtenir_nom_complet'):
            return self.passager.obtenir_nom_complet()
        elif hasattr(self.passager, 'nom') and hasattr(self.passager, 'prenom'):
            return f"{self.passager.prenom} {self.passager.nom}"
        else:
            return str(self.passager)
    
    def _numero_vol(self):
        """Obtient le numéro de vol de manière sécurisée"""
        if hasattr(self.vol, 'numero_vol'):
            return self.vol.numero_vol
        elif hasattr(self.vol, 'num_vol'):
            return self.vol.num_vol
        else:
            return str(self.vol)
    
    def _ajouter_aux_listes(self):
        """Ajoute la réservation aux listes du passager et vol"""
        # Ajout au passager
        if hasattr(self.passager, 'ajouter_reservation'):
            self.passager.ajouter_reservation(self)
        elif hasattr(self.passager, 'historique_reservations'):
            if self not in self.passager.historique_reservations:
                self.passager.historique_reservations.append(self)
        
        # Ajout au vol
        if hasattr(self.vol, 'ajouter_passager'):
            self.vol.ajouter_passager(self.passager)
        elif hasattr(self.vol, 'passagers'):
            if self.passager not in self.vol.passagers:
                self.vol.passagers.append(self.passager)
    
    def _retirer_des_listes(self):
        """Retire la réservation des listes du passager et vol"""
        # Retrait du vol
        if hasattr(self.vol, 'retirer_passager'):
            self.vol.retirer_passager(self.passager)
        elif hasattr(self.vol, 'passagers') and self.passager in self.vol.passagers:
            self.vol.passagers.remove(self.passager)
        
        # Note: Ne retire pas de l'historique du passager pour garder trace
    
    def est_valide(self):
        """
        Vérifie si la réservation est encore valide.
        
        Returns:
            bool: True si valide
        """
        if self.statut != StatutReservation.ACTIVE:
            return False
        
        if datetime.now() > self.validite:
            self.statut = StatutReservation.EXPIREE
            return False
            
        return True
    
    def est_active(self):
        """Vérifie si la réservation est active et valide"""
        return self.statut == StatutReservation.ACTIVE and self.est_valide()
    
    def annuler(self):
        """
        Annule la réservation tout en gardant l'historique.
        
        Returns:
            bool: True si annulation réussie
        """
        if self.statut == StatutReservation.ANNULEE:
            self.notification("Réservation déjà annulée.")
            return False
        
        if self.statut == StatutReservation.TERMINEE:
            self.notification("Impossible d'annuler une réservation terminée.")
            return False
        
        # Changement d'état sans perte d'information
        self.statut = StatutReservation.ANNULEE
        self.checkin_effectue = False
        self.siege_assigne = None
        
        # Retrait des listes actives
        self._retirer_des_listes()
        
        self.notification("Votre réservation a été annulée.")
        print(f"[RÉSERVATION] Réservation {self.id_reservation[:8]}... annulée")
        return True
    
    def modif_reservation(self, nouveau_vol):
        """
        Modifie le vol associé à la réservation.
        
        Args:
            nouveau_vol: Nouveau vol
            
        Returns:
            bool: True si modification réussie
        """
        if not self.est_active():
            self.notification("Impossible de modifier une réservation inactive.")
            return False
        
        if self.vol == nouveau_vol:
            self.notification("Le nouveau vol est identique au vol actuel.")
            return False
        
        # Vérification capacité du nouveau vol
        if hasattr(nouveau_vol, 'peut_ajouter_passager'):
            if not nouveau_vol.peut_ajouter_passager():
                self.notification("Le nouveau vol est complet.")
                return False
        
        # Retrait de l'ancien vol
        self._retirer_des_listes()
        
        # Mise à jour vers nouveau vol
        ancien_vol = self._numero_vol()
        self.vol = nouveau_vol
        
        # Reset des états liés au vol
        self.checkin_effectue = False
        self.siege_assigne = None
        
        # Ajout au nouveau vol
        self._ajouter_aux_listes()
        
        nouveau_numero = self._numero_vol()
        self.notification(f"Votre réservation a été modifiée du vol {ancien_vol} vers {nouveau_numero}.")
        print(f"[RÉSERVATION] Vol modifié de {ancien_vol} vers {nouveau_numero}")
        return True
    
    def effectuer_checkin(self):
        """
        Effectue le check-in si les conditions sont remplies.
        
        Returns:
            bool: True si check-in effectué
        """
        if not self.est_active():
            self.notification("Check-in impossible : réservation inactive.")
            return False
        
        if self.checkin_effectue:
            self.notification("Check-in déjà effectué.")
            return False
        
        # Vérification siège assigné (optionnel selon politique)
        if not self.siege_assigne:
            self.notification("Check-in impossible : aucun siège assigné.")
            return False
        
        # Vérification timing (exemple: pas trop tôt, pas trop tard)
        if hasattr(self.vol, 'heure_depart') and self.vol.heure_depart:
            temps_avant_depart = self.vol.heure_depart - datetime.now()
            if temps_avant_depart > timedelta(hours=24):
                self.notification("Check-in trop tôt : disponible 24h avant le départ.")
                return False
            if temps_avant_depart < timedelta(minutes=30):
                self.notification("Check-in trop tard : fermé 30min avant départ.")
                return False
        
        self.checkin_effectue = True
        
        # Mise à jour du passager si possible
        if hasattr(self.passager, 'effectuer_checkin'):
            self.passager.effectuer_checkin()
        elif hasattr(self.passager, 'checkin_effectue'):
            self.passager.checkin_effectue = True
        
        self.notification("Check-in effectué avec succès.")
        print(f"[RÉSERVATION] Check-in effectué pour {self._nom_passager()}")
        return True
    
    def annuler_checkin(self):
        """Annule le check-in"""
        if not self.checkin_effectue:
            self.notification("Aucun check-in à annuler.")
            return False
        
        self.checkin_effectue = False
        
        if hasattr(self.passager, 'checkin_effectue'):
            self.passager.checkin_effectue = False
        
        self.notification("Check-in annulé.")
        return True
    
    def assigner_siege(self, siege):
        """
        Assigne un siège avec validation du format.
        
        Args:
            siege (str): Numéro de siège (ex: "12A")
            
        Returns:
            bool: True si assignation réussie
        """
        if not self.est_active():
            self.notification("Impossible d'assigner un siège : réservation inactive.")
            return False
        
        if not isinstance(siege, str):
            self.notification("Le numéro de siège doit être une chaîne de caractères.")
            return False
        
        # Validation format
        siege_clean = siege.strip().upper()
        if not self.PATTERN_SIEGE.match(siege_clean):
            self.notification(f"Format de siège invalide : '{siege}'. Attendu : ex. '12A'")
            return False
        
        # Vérification disponibilité (si possible)
        if hasattr(self.vol, 'est_siege_disponible'):
            if not self.vol.est_siege_disponible(siege_clean):
                self.notification(f"Siège {siege_clean} non disponible.")
                return False
        
        ancien_siege = self.siege_assigne
        self.siege_assigne = siege_clean
        
        if ancien_siege:
            self.notification(f"Siège changé de {ancien_siege} à {siege_clean}.")
        else:
            self.notification(f"Siège {siege_clean} assigné.")
        
        print(f"[RÉSERVATION] Siège {siege_clean} assigné à {self._nom_passager()}")
        return True
    
    def changer_siege(self, nouveau_siege):
        """Change le siège assigné"""
        return self.assigner_siege(nouveau_siege)
    
    def liberer_siege(self):
        """Libère le siège assigné"""
        if not self.siege_assigne:
            self.notification("Aucun siège à libérer.")
            return False
        
        ancien_siege = self.siege_assigne
        self.siege_assigne = None
        self.notification(f"Siège {ancien_siege} libéré.")
        return True
    
    def marquer_terminee(self):
        """Marque la réservation comme terminée"""
        if self.statut == StatutReservation.TERMINEE:
            return False
        
        if self.statut == StatutReservation.ANNULEE:
            return False
        
        self.statut = StatutReservation.TERMINEE
        
        # Ajout à l'historique du passager si possible
        if hasattr(self.passager, 'ajouter_vol_historique'):
            self.passager.ajouter_vol_historique(self.vol)
        
        print(f"[RÉSERVATION] Réservation {self.id_reservation[:8]}... marquée terminée")
        return True
    
    def temps_restant_validite(self):
        """Retourne le temps restant avant expiration"""
        return self.validite - datetime.now()
    
    def notification(self, message):
        """
        Envoie une notification au passager.
        
        Args:
            message (str): Message à envoyer
        """
        nom = self._nom_passager()
        print(f"[NOTIFICATION] {nom}: {message}")
        
        # Envoi via email si disponible
        if hasattr(self.passager, 'email') and self.passager.email:
            print(f"[EMAIL] → {self.passager.email}: {message}")
    
    def obtenir_details(self):
        """
        Retourne un dictionnaire avec tous les détails de la réservation.
        
        Returns:
            dict: Détails complets
        """
        return {
            'id_reservation': self.id_reservation,
            'passager': self._nom_passager(),
            'vol': self._numero_vol(),
            'statut': self.statut.obtenir_nom_affichage(),
            'siege_assigne': self.siege_assigne,
            'checkin_effectue': self.checkin_effectue,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M'),
            'validite': self.validite.strftime('%Y-%m-%d %H:%M'),
            'temps_restant': str(self.temps_restant_validite()).split('.')[0],  # Sans microsecondes
            'est_valide': self.est_valide(),
            'est_active': self.est_active()
        }
    
    def to_dict(self):
        """Conversion pour sérialisation"""
        return {
            'id_reservation': self.id_reservation,
            'passager_id': getattr(self.passager, 'id_passager', str(self.passager)),
            'vol_numero': self._numero_vol(),
            'statut': self.statut.value,
            'siege_assigne': self.siege_assigne,
            'checkin_effectue': self.checkin_effectue,
            'date_creation': self.date_creation.isoformat(),
            'validite': self.validite.isoformat()
        }
    
    def __str__(self):
        """Représentation textuelle conviviale"""
        statut_str = self.statut.obtenir_nom_affichage()
        checkin_str = "✓ Check-in" if self.checkin_effectue else "✗ Non enregistré"
        siege_str = f"Siège: {self.siege_assigne}" if self.siege_assigne else "Pas de siège"
        
        return (f"Réservation {self.id_reservation[:8]}... | "
                f"Vol: {self._numero_vol()} | "
                f"Passager: {self._nom_passager()} | "
                f"Statut: {statut_str} | "
                f"{checkin_str} | {siege_str}")
    
    def __repr__(self):
        return (f"Reservation(id='{self.id_reservation}', "
                f"vol='{self._numero_vol()}', "
                f"statut={self.statut}, "
                f"checkin={self.checkin_effectue})")
    
    def __eq__(self, other):
        return isinstance(other, Reservation) and self.id_reservation == other.id_reservation
    
    def __hash__(self):
        return hash(self.id_reservation)