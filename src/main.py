#!/usr/bin/env python3
"""
Système de Gestion et Simulateur de Vols
Point d'entrée principal de l'application

Ce fichier lance l'interface graphique principale avec tous les systèmes intégrés.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback
from datetime import datetime

# Ajouter le répertoire racine au path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_dependencies():
    """Vérifie que toutes les dépendances sont disponibles"""
    try:
        # Vérifier Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 ou supérieur requis")
        
        # Vérifier tkinter
        import tkinter as tk
        
        # Vérifier les modules locaux
        from interfaces.main_window import MainWindow
        from data.data_manager import DataManager
        from simulation.simulation_engine import SimulationEngine
        
        return True
        
    except ImportError as e:
        messagebox.showerror("Dépendances manquantes", 
                           f"Module manquant: {e}\n\n"
                           "Vérifiez que tous les fichiers sont présents.")
        return False
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur de vérification: {e}")
        return False

def create_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas"""
    directories = [
        'data',
        'data/backups',
        'logs',
        'interfaces',
        'interfaces/dialogs',
        'simulation'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def setup_logging():
    """Configure le système de logging"""
    import logging
    from datetime import datetime
    
    # Créer le répertoire de logs
    os.makedirs('logs', exist_ok=True)
    
    # Configuration du logging
    log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Gestionnaire global d'exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Permettre Ctrl+C
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Logger l'exception
    logger = logging.getLogger(__name__)
    logger.error("Exception non gérée", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Afficher un message d'erreur à l'utilisateur
    error_msg = f"Une erreur inattendue s'est produite:\n\n{exc_type.__name__}: {exc_value}"
    
    try:
        messagebox.showerror("Erreur Critique", error_msg)
    except:
        print(f"ERREUR CRITIQUE: {error_msg}")

def main():
    """Fonction principale de l'application"""
    print("🚀 Démarrage du Système de Gestion Aéroportuaire")
    print("=" * 50)
    
    try:
        # Configuration initiale
        logger = setup_logging()
        logger.info("Application démarrée")
        
        # Configuration du gestionnaire d'exceptions global
        sys.excepthook = handle_exception
        
        # Créer les répertoires nécessaires
        create_directories()
        logger.info("Répertoires créés/vérifiés")
        
        # Vérifier les dépendances
        if not check_dependencies():
            logger.error("Vérification des dépendances échouée")
            return 1
        
        logger.info("Dépendances vérifiées avec succès")
        
        # Lancer l'interface principale
        logger.info("Lancement de l'interface principale")
        
        from interfaces.main_window import MainWindow
        
        app = MainWindow()
        logger.info("Interface initialisée")
        
        print("✅ Interface prête - Lancement de l'application")
        print("💡 Utilisez Ctrl+C pour arrêter proprement l'application")
        print("-" * 50)
        
        # Lancer la boucle principale
        app.run()
        
        logger.info("Application fermée normalement")
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur (Ctrl+C)")
        logger.info("Arrêt par interruption clavier")
        return 0
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Erreur critique: {e}")
        print(f"Trace complète:\n{error_trace}")
        
        if 'logger' in locals():
            logger.error(f"Erreur critique: {e}")
            logger.error(f"Trace: {error_trace}")
        
        try:
            messagebox.showerror("Erreur Critique", 
                               f"L'application n'a pas pu démarrer:\n\n{e}\n\n"
                               f"Consultez les logs pour plus de détails.")
        except:
            pass
        
        return 1

def check_data_integrity():
    """Vérifie l'intégrité des données au démarrage"""
    try:
        from data.data_manager import DataManager
        
        dm = DataManager()
        report = dm.validate_data_integrity()
        
        if not report['valid']:
            print("⚠️ Problèmes détectés dans les données:")
            for error in report['errors']:
                print(f"  • {error}")
        
        if report['warnings']:
            print("⚠️ Avertissements:")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        return report['valid']
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des données: {e}")
        return False

def show_startup_info():
    """Affiche les informations de démarrage"""
    print("📋 Informations système:")
    print(f"  • Python: {sys.version.split()[0]}")
    print(f"  • Plateforme: {sys.platform}")
    print(f"  • Répertoire: {os.getcwd()}")
    print(f"  • PID: {os.getpid()}")
    print()

def create_desktop_shortcut():
    """Crée un raccourci sur le bureau (Windows uniquement)"""
    if sys.platform.startswith('win'):
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Gestion Aéroportuaire.lnk")
            target = os.path.abspath(__file__)
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.save()
            
            print(f"✅ Raccourci créé: {path}")
            
        except ImportError:
            # Modules win32 non disponibles
            pass
        except Exception as e:
            print(f"⚠️ Impossible de créer le raccourci: {e}")

def check_first_run():
    """Vérifie si c'est le premier lancement de l'application"""
    marker_file = os.path.join('data', '.first_run_complete')
    
    if not os.path.exists(marker_file):
        print("🎉 Premier lancement détecté!")
        print("🔧 Configuration initiale en cours...")
        
        # Créer les fichiers de base s'ils n'existent pas
        try:
            from data.data_manager import DataManager
            dm = DataManager()
            
            # Vérifier que les fichiers airports.json et aircraft_models.json existent
            airports_file = dm.files['airports']
            models_file = dm.files['aircraft_models']
            
            if not airports_file.exists():
                print("⚠️ Fichier airports.json manquant!")
                print("📥 Vous devez copier le fichier airports.json dans le dossier data/")
                
            if not models_file.exists():
                print("⚠️ Fichier aircraft_models.json manquant!")
                print("📥 Vous devez copier le fichier aircraft_models.json dans le dossier data/")
            
            # Marquer comme configuré
            with open(marker_file, 'w') as f:
                f.write(f"First run completed on {sys.version}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
            
            print("✅ Configuration initiale terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de la configuration initiale: {e}")
            return False
    
    return True

if __name__ == "__main__":
    # Affichage des informations de démarrage
    show_startup_info()
    
    # Vérification du premier lancement
    if not check_first_run():
        print("❌ Configuration initiale échouée")
        sys.exit(1)
    
    # Vérification de l'intégrité des données
    print("🔍 Vérification de l'intégrité des données...")
    if not check_data_integrity():
        print("⚠️ Problèmes détectés dans les données, mais l'application peut continuer")
    
    # Création du raccourci (optionnel)
    create_desktop_shortcut()
    
    # Lancement de l'application principale
    exit_code = main()
    
    # Nettoyage et sortie
    print(f"\n👋 Application fermée (code: {exit_code})")
    sys.exit(exit_code)