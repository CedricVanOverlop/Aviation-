# Module Core - Classes métier du système de gestion des vols
# Contient toutes les classes principales pour la logique métier

# Import des énumérations
from .enums import (
    TypeIntemperie, StatutVol, EtatAvion, StatutPiste, 
    TypeSexe, TypePersonnel, StatutReservation
)

# Import des classes d'aviation
from .aviation import Coordonnees, Avion, Aeroport, PisteAtterrissage

# Import des classes de gestion
from .gestion import Compagnie, GestionRetard

# Import des classes méteo
from .meteo import Meteo

# Import des classes de personnes
from .personnes import Personne, Personnel, Passager

# Import des classes de réservation
from .reservation import Reservation

# Import des classes de vol
from .vol import Vol

# Définition de ce qui est exporté quand on fait "from Core import *"
__all__ = [
    # Énumérations
    'TypeIntemperie', 'StatutVol', 'EtatAvion', 'StatutPiste', 
    'TypeSexe', 'TypePersonnel', 'StatutReservation',
    
    # Classes d'aviation
    'Coordonnees', 'Avion', 'Aeroport', 'PisteAtterrissage',
    
    # Classes de gestion
    'Compagnie', 'GestionRetard',
    
    # Classes méteo
    'Meteo',
    
    # Classes de personnes
    'Personne', 'Personnel', 'Passager',
    
    # Classes de réservation
    'Reservation',
    
    # Classes de vol
    'Vol'
]

# Métadonnées du module
__version__ = "1.0.0"
__author__ = "Votre Nom"
__description__ = "Module Core pour le système de gestion des vols"

# Fonction utilitaire pour obtenir toutes les classes disponibles
def get_available_classes():
    """
    Retourne un dictionnaire de toutes les classes disponibles dans le module Core.
    
    Returns:
        dict: Dictionnaire avec les noms des classes comme clés et les classes comme valeurs
    """
    import sys
    current_module = sys.modules[__name__]
    
    classes = {}
    for name in __all__:
        if hasattr(current_module, name):
            classes[name] = getattr(current_module, name)
    
    return classes

# Fonction pour vérifier la compatibilité des versions
def check_compatibility():
    """
    Vérifie la compatibilité des dépendances et des versions.
    
    Returns:
        bool: True si toutes les vérifications passent
    """
    import sys
    
    # Vérification de la version Python
    if sys.version_info < (3, 8):
        print("Attention: Python 3.8+ recommandé pour une compatibilité optimale")
        return False
    
    # Vérification des modules requis
    required_modules = ['datetime', 'uuid', 'math', 're', 'typing', 'abc']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Modules manquants: {', '.join(missing_modules)}")
        return False
    
    return True

# Initialisation du module
print(f"Module Core v{__version__} chargé avec succès")

# Vérification automatique de la compatibilité lors de l'import
if not check_compatibility():
    print("Attention: Problèmes de compatibilité détectés dans le module Core")