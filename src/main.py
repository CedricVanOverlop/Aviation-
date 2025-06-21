#!/usr/bin/env python3
"""
Script de démarrage de l'interface aéroportuaire - VERSION SANS SIMULATION
Fichier: main.py (à placer dans le dossier src/)

Cette version ne contient aucun élément de simulation temporelle.
L'interface fonctionne de manière statique avec rafraîchissement manuel.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def main():
    """Point d'entrée principal de l'application"""
    print("="*60)
    print("🏢 SYSTÈME DE GESTION AÉROPORTUAIRE")
    print("📊 Version Interface Statique (Sans Simulation)")
    print("="*60)
    print()
    
    try:
        # Vérifier la version Python
        if sys.version_info < (3, 7):
            print("❌ Python 3.7 ou plus récent requis")
            print(f"   Version actuelle: {sys.version}")
            return 1
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        # Obtenir le répertoire actuel (src/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"✅ Répertoire de travail: {current_dir}")
        
        # Ajouter les répertoires nécessaires au PYTHONPATH
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Ajouter le répertoire parent pour accéder aux modules Core
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Vérifier que les modules nécessaires sont disponibles
        try:
            import tkinter.ttk
            print("✅ Tkinter disponible")
        except ImportError:
            print("❌ Tkinter non disponible")
            return 1
        
        # Vérifier la structure des fichiers
        if not check_files_exist():
            print("❌ Fichiers manquants détectés")
            return 1
        
        # Importer et lancer l'interface principale
        print("🔄 Chargement de l'interface...")
        
        try:
            from interfaces.main_window import MainWindow
            print("✅ Module interface chargé")
        except ImportError as e:
            print(f"❌ Erreur import interface: {e}")
            print("   Vérifiez que le fichier interfaces/main_window.py existe")
            return 1
        
        # Initialiser et lancer l'application
        print("🚀 Démarrage de l'interface...")
        print()
        print("🔧 MODE: Interface statique sans simulation")
        print("📝 UTILISATION:")
        print("   • Utilisez le bouton 'Actualiser' pour mettre à jour les données")
        print("   • Naviguez entre les onglets pour gérer les entités")
        print("   • Toutes les modifications sont sauvegardées automatiquement")
        print("   • Aucun processus de simulation en arrière-plan")
        print()
        
        # Créer et lancer l'application
        app = MainWindow()
        
        print("✅ Interface initialisée avec succès")
        print("🖥️ Fenêtre principale ouverte")
        print()
        print("💡 Pour fermer l'application :")
        print("   • Cliquez sur le X de la fenêtre")
        print("   • Ou utilisez Ctrl+C dans ce terminal")
        print()
        
        # Lancer la boucle principale
        app.run()
        
        print("\n👋 Application fermée proprement")
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Interruption utilisateur (Ctrl+C)")
        print("👋 Fermeture de l'application...")
        return 0
        
    except Exception as e:
        print(f"\n❌ Erreur fatale lors du démarrage:")
        print(f"   {type(e).__name__}: {e}")
        print()
        print("🔍 Vérifications suggérées:")
        print("   1. Tous les fichiers source sont présents")
        print("   2. Les dépendances Python sont installées")
        print("   3. Les permissions de fichier sont correctes")
        print("   4. Le répertoire de données existe")
        print()
        
        # Afficher la traceback complète en mode debug
        import traceback
        print("📋 Traceback complète:")
        traceback.print_exc()
        
        return 1

def check_files_exist():
    """Vérifie que les fichiers nécessaires existent"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Fichiers requis dans la structure actuelle
    required_files = [
        'interfaces/main_window.py',
        'interfaces/tabs/dashboard_tab.py', 
        'interfaces/tabs/aircraft_tab.py',
        'interfaces/tabs/flights_tab.py',
        'interfaces/tabs/personnel_tab.py',
        'interfaces/tabs/passengers_tab.py',
        'interfaces/tabs/reservations_tab.py',
        'data/data_manager.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
            print(f"❌ Fichier manquant: {file_path}")
        else:
            print(f"✅ Fichier trouvé: {file_path}")
    
    # Vérifier et créer le répertoire de données si nécessaire
    data_dir = os.path.join(current_dir, '..', 'data')
    if not os.path.exists(data_dir):
        print(f"⚠️ Répertoire de données manquant: {data_dir}")
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"✅ Répertoire de données créé: {data_dir}")
        except OSError as e:
            print(f"❌ Impossible de créer le répertoire de données: {e}")
    
    return len(missing_files) == 0

def check_environment():
    """Vérifie l'environnement d'exécution complet"""
    print("🔍 Vérification complète de l'environnement...")
    print()
    
    issues = []
    
    # Vérifier Python
    print("1. Version Python...")
    if sys.version_info < (3, 7):
        issues.append(f"Python 3.7+ requis (actuel: {sys.version_info.major}.{sys.version_info.minor})")
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (requis: 3.7+)")
    else:
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Vérifier Tkinter
    print("2. Tkinter...")
    try:
        import tkinter
        import tkinter.ttk
        print("   ✅ Tkinter disponible")
    except ImportError:
        issues.append("Tkinter non disponible")
        print("   ❌ Tkinter non disponible")
    
    # Vérifier la structure des fichiers
    print("3. Structure des fichiers...")
    if check_files_exist():
        print("   ✅ Tous les fichiers requis sont présents")
    else:
        issues.append("Fichiers manquants")
        print("   ❌ Fichiers manquants détectés")
    
    # Vérifier les modules Core
    print("4. Modules Core...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(current_dir, '..', 'Core')
    
    if os.path.exists(core_dir):
        print(f"   ✅ Répertoire Core trouvé: {core_dir}")
        
        # Vérifier quelques modules Core essentiels
        core_files = ['aviation.py', 'vol.py', 'enums.py', 'personnes.py']
        for core_file in core_files:
            core_path = os.path.join(core_dir, core_file)
            if os.path.exists(core_path):
                print(f"   ✅ {core_file}")
            else:
                print(f"   ⚠️ {core_file} manquant")
    else:
        print(f"   ⚠️ Répertoire Core non trouvé: {core_dir}")
    
    print()
    
    if issues:
        print("❌ Problèmes détectés:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ Environnement prêt pour l'interface")
        return True

def show_help():
    """Affiche l'aide"""
    help_text = """
🏢 SYSTÈME DE GESTION AÉROPORTUAIRE - AIDE

UTILISATION:
    python main.py [OPTIONS]

OPTIONS:
    --help, -h      Affiche cette aide
    --check         Vérifie l'environnement sans lancer l'interface
    --version       Affiche la version

STRUCTURE ATTENDUE:
    src/
    ├── main.py                    (ce fichier)
    ├── interfaces/
    │   ├── main_window.py
    │   └── tabs/
    │       ├── dashboard_tab.py
    │       ├── aircraft_tab.py
    │       ├── flights_tab.py
    │       ├── personnel_tab.py
    │       ├── passengers_tab.py
    │       └── reservations_tab.py
    ├── data/
    │   └── data_manager.py
    └── simulation/
        └── simulation_engine.py

FONCTIONNALITÉS:
    ✈️ Gestion de la flotte d'avions
    👥 Administration du personnel
    🛫 Planification des vols
    🧳 Gestion des passagers
    🎫 Suivi des réservations
    📊 Tableau de bord avec statistiques

MODE DE FONCTIONNEMENT:
    Cette version fonctionne sans simulation temps réel.
    Toutes les données sont gérées de manière statique.
    
    • Pas de threads secondaires
    • Pas de mises à jour automatiques
    • Rafraîchissement manuel uniquement
    • Interface stable et performante

NAVIGATION:
    • Utilisez les onglets pour naviguer entre les modules
    • Bouton "Actualiser" pour mettre à jour les données
    • Bouton "Statistiques" pour voir un résumé global
    • Bouton "Sauvegarder" pour forcer la sauvegarde

DÉPANNAGE:
    1. Vérifiez que vous êtes dans le répertoire src/
    2. Exécutez 'python main.py --check' pour diagnostiquer
    3. Vérifiez que tous les fichiers sont présents
    4. Assurez-vous que Python 3.7+ est installé
    
EXEMPLES:
    python main.py                 # Lancer l'interface
    python main.py --check         # Vérifier l'environnement
    python main.py --help          # Afficher cette aide
    
Pour plus d'informations, consultez la documentation.
"""
    print(help_text)

def show_file_structure():
    """Affiche la structure de fichiers attendue"""
    print("📁 STRUCTURE DE FICHIERS ATTENDUE:")
    print()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    structure = [
        ("src/", "📁"),
        ("├── main.py", "🐍"),
        ("├── interfaces/", "📁"),
        ("│   ├── main_window.py", "🖥️"),
        ("│   └── tabs/", "📁"),
        ("│       ├── dashboard_tab.py", "📊"),
        ("│       ├── aircraft_tab.py", "✈️"),
        ("│       ├── flights_tab.py", "🛫"),
        ("│       ├── personnel_tab.py", "👥"),
        ("│       ├── passengers_tab.py", "🧳"),
        ("│       └── reservations_tab.py", "🎫"),
        ("├── data/", "📁"),
        ("│   └── data_manager.py", "💾"),
        ("└── simulation/", "📁"),
        ("    └── simulation_engine.py", "⚙️")
    ]
    
    for path, icon in structure:
        full_path = os.path.join(current_dir, path.replace("├── ", "").replace("│   ", "").replace("│       ", "").replace("└── ", "").replace("    ", ""))
        
        if "main.py" in path:
            status = "✅" if os.path.exists(full_path) else "❌"
        elif path.endswith("/"):
            status = "✅" if os.path.exists(full_path) else "❌"
        elif path.endswith(".py"):
            status = "✅" if os.path.exists(full_path) else "❌"
        else:
            status = ""
        
        print(f"{status} {icon} {path}")
    
    print()
    print("💡 CONSEIL: Placez main.py dans le dossier src/ et exécutez-le depuis là.")

if __name__ == "__main__":
    # Gestion des arguments de ligne de commande
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            show_help()
            sys.exit(0)
        elif arg == '--check':
            if check_environment():
                sys.exit(0)
            else:
                print("\n📁 Structure attendue:")
                show_file_structure()
                sys.exit(1)
        elif arg == '--structure':
            show_file_structure()
            sys.exit(0)
        elif arg == '--version':
            print("Système de Gestion Aéroportuaire - Version Interface Statique")
            print("Version: 1.0.0-static")
            print("Mode: Sans simulation temporelle")
            sys.exit(0)
        else:
            print(f"❌ Argument inconnu: {arg}")
            print("Utilisez --help pour voir les options disponibles")
            sys.exit(1)
    
    # Vérification rapide avant lancement
    if not check_environment():
        print("\n❌ L'environnement n'est pas prêt")
        print("📁 Voici la structure attendue:")
        show_file_structure()
        print("\n💡 Utilisez 'python main.py --check' pour plus de détails")
        sys.exit(1)
    
    # Lancer l'application
    exit_code = main()
    sys.exit(exit_code)