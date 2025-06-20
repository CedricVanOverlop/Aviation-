from enum import Enum

class TypeIntemperie(Enum):
    """Types d'intempéries possibles"""
    AUCUNE = "aucune"
    PLUIE = "pluie"
    NEIGE = "neige"
    ORAGE = "orage"
    BROUILLARD = "brouillard"
    TEMPETE = "tempete"
    GRELE = "grele"
    
    def est_risquee(self):
        """Vérifie si l'intempérie présente un risque pour l'aviation"""
        return self in [
            TypeIntemperie.ORAGE, 
            TypeIntemperie.TEMPETE, 
            TypeIntemperie.GRELE
        ]
    
    def obtenir_nom_affichage(self):
        """Retourne le nom d'affichage de l'intempérie"""
        noms = {
            TypeIntemperie.AUCUNE: "Aucune",
            TypeIntemperie.PLUIE: "Pluie",
            TypeIntemperie.NEIGE: "Neige",
            TypeIntemperie.ORAGE: "Orage",
            TypeIntemperie.BROUILLARD: "Brouillard",
            TypeIntemperie.TEMPETE: "Tempête",
            TypeIntemperie.GRELE: "Grêle"
        }
        return noms.get(self, self.value.capitalize())

class StatutVol(Enum):
    """États possibles d'un vol"""
    PROGRAMME = "programme"
    EN_ATTENTE = "en_attente"
    EN_VOL = "en_vol"
    ATTERRI = "atterri"
    RETARDE = "retarde"
    ANNULE = "annule"
    TERMINE = "termine"
    
    def obtenir_nom_affichage(self):
        noms = {
            StatutVol.PROGRAMME: "Programmé",
            StatutVol.EN_ATTENTE: "En attente",
            StatutVol.EN_VOL: "En vol",
            StatutVol.ATTERRI: "Atterri",
            StatutVol.RETARDE: "Retardé",
            StatutVol.ANNULE: "Annulé",
            StatutVol.TERMINE: "Terminé"
        }
        return noms.get(self, self.value.capitalize())

class EtatAvion(Enum):
    """États possibles d'un avion"""
    AU_SOL = "au_sol"
    EN_VOL = "en_vol"
    EN_MAINTENANCE = "en_maintenance"
    OPERATIONNEL = "operationnel"
    
    def est_operationnel(self):
        return self in [EtatAvion.AU_SOL, EtatAvion.OPERATIONNEL]

class StatutPiste(Enum):
    """États possibles d'une piste d'atterrissage"""
    DISPONIBLE = "disponible"
    OCCUPEE = "occupee"
    MAINTENANCE = "maintenance"
    HORS_SERVICE = "hors_service"

class TypeSexe(Enum):
    """Types de sexe"""
    MASCULIN = "masculin"
    FEMININ = "feminin"
    AUTRE = "autre"
    
    def obtenir_nom_affichage(self):
        noms = {
            TypeSexe.MASCULIN: "Masculin",
            TypeSexe.FEMININ: "Féminin", 
            TypeSexe.AUTRE: "Autre"
        }
        return noms.get(self, self.value.capitalize())

class TypePersonnel(Enum):
    """Types de personnel"""
    PILOTE = "pilote"
    COPILOTE = "copilote"
    HOTESSE = "hotesse"
    STEWARD = "steward"
    MECANICIEN = "mecanicien"
    CONTROLEUR = "controleur"
    GESTIONNAIRE = "gestionnaire"
    
    def obtenir_nom_affichage(self):
        noms = {
            TypePersonnel.PILOTE: "Pilote",
            TypePersonnel.COPILOTE: "Copilote",
            TypePersonnel.HOTESSE: "Hôtesse de l'air",
            TypePersonnel.STEWARD: "Steward",
            TypePersonnel.MECANICIEN: "Mécanicien",
            TypePersonnel.CONTROLEUR: "Contrôleur aérien",
            TypePersonnel.GESTIONNAIRE: "Gestionnaire"
        }
        return noms.get(self, self.value.capitalize())

class StatutReservation(Enum):
    """États possibles d'une réservation"""
    ACTIVE = "active"
    ANNULEE = "annulee"
    TERMINEE = "terminee"
    EXPIREE = "expiree"
    
    def obtenir_nom_affichage(self):
        noms = {
            StatutReservation.ACTIVE: "Active",
            StatutReservation.ANNULEE: "Annulée",
            StatutReservation.TERMINEE: "Terminée",
            StatutReservation.EXPIREE: "Expirée"
        }
        return noms.get(self, self.value.capitalize())