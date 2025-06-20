"""
Point d'entrée principal de l'application de gestion aéroportuaire
Démarre l'interface graphique avec simulation temporelle
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Ajouter le dossier Core au path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'Core'))

def setup_logging():
    """Configure le système de logs"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('airport_management.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Vérifie que tous les modules requis sont disponibles"""
    try:
        # Vérifier Core
        import Core
        
        # Vérifier tkinter
        import tkinter as tk
        
        # Vérifier autres dépendances
        import json
        import datetime
        import threading
        import uuid
        
        return True
    except ImportError as e:
        messagebox.showerror("Erreur de dépendance", 
                           f"Module manquant: {e}\nVeuillez vérifier l'installation.")
        return False

def main():
    """Fonction principale"""
    # Configuration des logs
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Démarrage de l'application de gestion aéroportuaire")
    
    # Vérification des dépendances
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Import de l'interface principale
        from gui.main_window import AirportManagementGUI
        
        # Création et lancement de l'application
        app = AirportManagementGUI()
        logger.info("Interface graphique initialisée")
        
        # Démarrage de l'application
        app.run()
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}", exc_info=True)
        messagebox.showerror("Erreur fatale", 
                           f"Impossible de démarrer l'application:\n{e}")
        sys.exit(1)
    
    finally:
        logger.info("Arrêt de l'application")

if __name__ == "__main__":
    main()