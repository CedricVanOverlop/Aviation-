"""
Interface graphique principale de l'application de gestion aéroportuaire
Combine simulation temporelle et gestion en temps réel
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime, timedelta
import logging

from .utils.json_manager import JSONDataManager
from .controllers.data_controller import DataController
from .views.dashboard import DashboardView
from .views.flight_management import FlightManagementView
from .views.fleet_management import FleetManagementView
from .views.simulation_panel import SimulationPanel
from .views.event_log import EventLogView

logger = logging.getLogger(__name__)

class AirportManagementGUI:
    """Interface principale de gestion aéroportuaire"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Initialisation des contrôleurs
        self.data_manager = JSONDataManager()
        self.data_controller = DataController(self.data_manager)
        
        # Variables d'interface
        self.sim_running = tk.BooleanVar(value=False)
        self.sim_speed = tk.DoubleVar(value=1.0)
        self.current_time_var = tk.StringVar()
        
        # Vues
        self.views = {}
        
        self.setup_ui()
        self.setup_auto_save()
        self.start_simulation_thread()
        
        logger.info("Interface graphique initialisée")

    def setup_main_notebook(self):
        """Configure le notebook principal avec tous les onglets"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Onglet Tableau de Bord
        self.views['dashboard'] = DashboardView(self.notebook, self.data_controller)
        self.notebook.add(self.views['dashboard'], text="📊 Tableau de Bord")
        
        # Onglet Gestion des Vols
        self.views['flights'] = FlightManagementView(self.notebook, self.data_controller)
        self.notebook.add(self.views['flights'], text="🛫 Vols")
        
        # Onglet Gestion de la Flotte
        self.views['fleet'] = FleetManagementView(self.notebook, self.data_controller)
        self.notebook.add(self.views['fleet'], text="✈️ Flotte")
        
        # Onglet Journal des Événements
        self.views['events'] = EventLogView(self.notebook, self.data_controller)
        self.notebook.add(self.views['events'], text="📋 Journal")
        
        # Configurer les callbacks de mise à jour
        for view in self.views.values():
            if hasattr(view, 'update_data'):
                self.data_controller.simulator.add_callback(lambda t, v=view: v.update_data())

    def setup_statusbar(self):
        """Configure la barre de statut"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(fill='x', side='bottom')
        
        # Labels de statut
        self.status_text = tk.StringVar(value="Prêt")
        self.status_label = ttk.Label(self.statusbar, textvariable=self.status_text)
        self.status_label.pack(side='left', padx=5)
        
        # Séparateur
        ttk.Separator(self.statusbar, orient='vertical').pack(side='left', fill='y', padx=5)
        
        # Statistiques rapides
        self.quick_stats = tk.StringVar(value="Avions: 0 | Vols: 0 | Personnel: 0")
        self.stats_label = ttk.Label(self.statusbar, textvariable=self.quick_stats)
        self.stats_label.pack(side='left', padx=5)
        
        # Temps et vitesse de simulation
        self.sim_info = tk.StringVar(value="Simulation: Arrêtée")
        self.sim_label = ttk.Label(self.statusbar, textvariable=self.sim_info)
        self.sim_label.pack(side='right', padx=5)

    def setup_flight_event_handlers(self):
        """Configure les gestionnaires d'événements pour les vols"""
        
        def handle_vol_event(event):
            try:
                vol_id = event.target_id
                action = event.action
                
                vol_data = self.data_controller._vols_cache.get(vol_id)
                if not vol_data:
                    return
                
                vol = vol_data['vol']
                
                if action == 'decoller':
                    vol.demarrer_vol()
                    if hasattr(self, 'status_text'):
                        self.status_text.set(f"Vol {vol.numero_vol} a décollé")
                    
                elif action == 'atterrir':
                    vol.atterrir()
                    if hasattr(self, 'status_text'):
                        self.status_text.set(f"Vol {vol.numero_vol} a atterri")
                
                self.data_controller.save_vols()
                
            except Exception as e:
                logger.error(f"Erreur événement vol: {e}")
        
        # Enregistrer le gestionnaire
        self.data_controller.simulator.register_event_handler('vol', handle_vol_event)
    
    def setup_window(self):
        """Configure la fenêtre principale"""
        self.root.title("Gestion Aéroportuaire - Simulation Temps Réel")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Icône et style
        try:
            self.root.iconbitmap("assets/airport.ico")
        except:
            pass  # Pas d'icône disponible
        
        # Configuration de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Variables de style
        self.colors = {
            'primary': '#2E3440',
            'secondary': '#3B4252',
            'accent': '#5E81AC',
            'success': '#A3BE8C',
            'warning': '#EBCB8B',
            'error': '#BF616A',
            'background': '#ECEFF4'
        }
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        
        # Menu principal
        self.setup_menubar()
        
        # Barre d'outils
        self.setup_toolbar()
        
        # Panneau de simulation (toujours visible en haut)
        self.simulation_panel = SimulationPanel(self.root, self.data_controller.simulator, 
                                               self.sim_running, self.sim_speed,
                                               self.current_time_var)
        self.simulation_panel.pack(fill='x', padx=5, pady=2)
        
        # Notebook principal pour les onglets
        self.setup_main_notebook()
        
        # Barre de statut
        self.setup_statusbar()
    
    def setup_menubar(self):
        """Configure la barre de menus (version modifiée)"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier (inchangé)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.new_database, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir...", command=self.open_database, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Sauvegarder", command=self.save_all_data, accelerator="Ctrl+S")
        file_menu.add_command(label="Sauvegarder sous...", command=self.save_as_database)
        file_menu.add_separator()
        file_menu.add_command(label="Backup", command=self.create_backup)
        file_menu.add_command(label="Restaurer...", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exporter...", command=self.export_data)
        file_menu.add_command(label="Importer...", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menu Simulation (inchangé)
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Démarrer", command=self.start_simulation, accelerator="F5")
        sim_menu.add_command(label="Pause", command=self.pause_simulation, accelerator="F6")
        sim_menu.add_command(label="Arrêter", command=self.stop_simulation, accelerator="F7")
        sim_menu.add_separator()
        sim_menu.add_command(label="Réinitialiser", command=self.reset_simulation)
        sim_menu.add_command(label="Avance rapide...", command=self.fast_forward_dialog)
        
        # Menu Données (modifié)
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Données", menu=data_menu)
        data_menu.add_command(label="Nouvel Avion", command=self.new_aircraft_dialog)
        data_menu.add_command(label="Nouveau Vol", command=self.new_flight_dialog)
        data_menu.add_command(label="Nouveau Personnel", command=self.new_personnel_dialog)
        data_menu.add_command(label="Nouveau Passager", command=self.new_passenger_dialog)  # NOUVEAU
        data_menu.add_separator()
        data_menu.add_command(label="Optimiser Attribution", command=self.optimize_assignments)
        data_menu.add_command(label="Planifier Maintenance", command=self.schedule_maintenance_dialog)
        
        # Menu Rapports (inchangé)
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Rapports", menu=reports_menu)
        reports_menu.add_command(label="Statistiques", command=self.show_statistics)
        reports_menu.add_command(label="Planning Vols", command=self.show_flight_schedule)
        reports_menu.add_command(label="Planning Maintenance", command=self.show_maintenance_schedule)
        reports_menu.add_command(label="Journal Événements", command=self.show_event_log)
        
        # Menu Aide (inchangé)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Manuel Utilisateur", command=self.show_help)
        help_menu.add_command(label="Raccourcis Clavier", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Raccourcis clavier (inchangé)
        self.root.bind('<Control-n>', lambda e: self.new_database())
        self.root.bind('<Control-o>', lambda e: self.open_database())
        self.root.bind('<Control-s>', lambda e: self.save_all_data())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F5>', lambda e: self.start_simulation())
        self.root.bind('<F6>', lambda e: self.pause_simulation())
        self.root.bind('<F7>', lambda e: self.stop_simulation())

    
    def setup_toolbar(self):
        """Configure la barre d'outils (version modifiée)"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=2)
        
        # Boutons principaux
        ttk.Button(toolbar, text="📁 Nouveau", command=self.new_database).pack(side='left', padx=2)
        ttk.Button(toolbar, text="💾 Sauver", command=self.save_all_data).pack(side='left', padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)
        
        ttk.Button(toolbar, text="✈️ Nouvel Avion", command=self.new_aircraft_dialog).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🛫 Nouveau Vol", command=self.new_flight_dialog).pack(side='left', padx=2)
        ttk.Button(toolbar, text="👥 Personnel", command=self.new_personnel_dialog).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🎫 Passager", command=self.new_passenger_dialog).pack(side='left', padx=2)  # NOUVEAU
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)
        
        ttk.Button(toolbar, text="🔧 Maintenance", command=self.schedule_maintenance_dialog).pack(side='left', padx=2)
        ttk.Button(toolbar, text="📊 Stats", command=self.show_statistics).pack(side='left', padx=2)
        
        # Informations à droite (inchangé)
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side='right', padx=10)
        
        self.connection_label = ttk.Label(info_frame, text="🟢 Connecté", foreground='green')
        self.connection_label.pack(side='right', padx=5)
        
        def setup_statusbar(self):
            """Configure la barre de statut"""
            self.statusbar = ttk.Frame(self.root)
            self.statusbar.pack(fill='x', side='bottom')
            
            # Labels de statut
            self.status_text = tk.StringVar(value="Prêt")
            self.status_label = ttk.Label(self.statusbar, textvariable=self.status_text)
            self.status_label.pack(side='left', padx=5)
            
            # Séparateur
            ttk.Separator(self.statusbar, orient='vertical').pack(side='left', fill='y', padx=5)
            
            # Statistiques rapides
            self.quick_stats = tk.StringVar(value="Avions: 0 | Vols: 0 | Personnel: 0")
            self.stats_label = ttk.Label(self.statusbar, textvariable=self.quick_stats)
            self.stats_label.pack(side='left', padx=5)
            
            # Temps et vitesse de simulation
            self.sim_info = tk.StringVar(value="Simulation: Arrêtée")
            self.sim_label = ttk.Label(self.statusbar, textvariable=self.sim_info)
            self.sim_label.pack(side='right', padx=5)
        
    def setup_auto_save(self):
        """Configure la sauvegarde automatique"""
        def auto_save():
            try:
                self.data_controller.save_all_data()
                logger.debug("Sauvegarde automatique effectuée")
            except Exception as e:
                logger.error(f"Erreur sauvegarde automatique: {e}")
            
            # Programmer la prochaine sauvegarde
            self.root.after(300000, auto_save)  # 5 minutes
        
        # Démarrer après 5 minutes
        self.root.after(300000, auto_save)
    
    def start_simulation_thread(self):
        """Démarre le thread de simulation et de mise à jour UI"""
        def simulation_loop():
            while hasattr(self, 'root'):
                try:
                    # Mettre à jour la simulation
                    if hasattr(self.data_controller, 'simulator'):
                        self.data_controller.simulator.update()
                    
                    # Mettre à jour l'interface (dans le thread principal)
                    if self.root.winfo_exists():
                        self.root.after_idle(self.update_ui)
                    
                    time.sleep(0.1)  # 10 FPS
                    
                except Exception as e:
                    logger.error(f"Erreur dans boucle simulation: {e}")
                    time.sleep(1)  # Attendre avant de réessayer
        
        thread = threading.Thread(target=simulation_loop, daemon=True)
        thread.start()
        logger.info("Thread de simulation démarré")
    
    def update_ui(self):
        """Met à jour l'interface utilisateur (appelé dans le thread principal)"""
        try:
            # Temps de simulation
            current_time = self.data_controller.simulator.current_time
            self.current_time_var.set(current_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            # Statut simulation
            if self.data_controller.simulator.is_running:
                speed = self.data_controller.simulator.speed_multiplier
                self.sim_info.set(f"Simulation: {speed}x")
                self.sim_running.set(True)
            else:
                self.sim_info.set("Simulation: Pause")
                self.sim_running.set(False)
            
            # Statistiques rapides
            stats = self.data_controller.get_statistics()
            self.quick_stats.set(
                f"Avions: {stats['avions']['total']} | "
                f"Vols: {stats['vols']['total']} | "
                f"Personnel: {stats['personnel']['total']}"
            )
            
            # État de connexion (simulation)
            if hasattr(self, 'connection_label'):
                if self.data_controller.simulator.is_running:
                    self.connection_label.config(text="🟢 Simulation Active", foreground='green')
                else:
                    self.connection_label.config(text="🟡 Simulation Pause", foreground='orange')
            
        except Exception as e:
            logger.error(f"Erreur mise à jour UI: {e}")
    
    # =====================================================
    # GESTION DE LA SIMULATION
    # =====================================================
    
    def start_simulation(self):
        """Démarre la simulation"""
        self.data_controller.simulator.start()
        self.status_text.set("Simulation démarrée")
        logger.info("Simulation démarrée depuis l'interface")
    
    def pause_simulation(self):
        """Met en pause la simulation"""
        self.data_controller.simulator.stop()
        self.status_text.set("Simulation en pause")
        logger.info("Simulation mise en pause")
    
    def stop_simulation(self):
        """Arrête la simulation"""
        self.data_controller.simulator.stop()
        self.status_text.set("Simulation arrêtée")
        logger.info("Simulation arrêtée")
    
    def reset_simulation(self):
        """Remet la simulation à zéro"""
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment réinitialiser la simulation ?"):
            self.data_controller.simulator.reset_to_default()
            self.status_text.set("Simulation réinitialisée")
            logger.info("Simulation réinitialisée")
    
    def fast_forward_dialog(self):
        """Dialogue d'avance rapide"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Avance Rapide")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Contenu
        ttk.Label(dialog, text="Avancer jusqu'à:", font=('Arial', 12)).pack(pady=10)
        
        # Sélection de la date/heure
        frame = ttk.Frame(dialog)
        frame.pack(pady=10)
        
        # Date
        ttk.Label(frame, text="Date:").grid(row=0, column=0, sticky='w', padx=5)
        date_var = tk.StringVar(value=self.data_controller.simulator.current_time.strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(frame, textvariable=date_var, width=12)
        date_entry.grid(row=0, column=1, padx=5)
        
        # Heure
        ttk.Label(frame, text="Heure:").grid(row=0, column=2, sticky='w', padx=5)
        time_var = tk.StringVar(value="12:00:00")
        time_entry = ttk.Entry(frame, textvariable=time_var, width=10)
        time_entry.grid(row=0, column=3, padx=5)
        
        # Option traitement des événements
        process_events = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="Traiter les événements programmés", 
                       variable=process_events).pack(pady=10)
        
        # Boutons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def execute_fast_forward():
            try:
                target_datetime = datetime.strptime(f"{date_var.get()} {time_var.get()}", 
                                                  '%Y-%m-%d %H:%M:%S')
                events_processed = self.data_controller.simulator.fast_forward_to(
                    target_datetime, process_events.get()
                )
                messagebox.showinfo("Avance Rapide", 
                                  f"Avance effectuée.\n{events_processed} événements traités.")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Format de date/heure invalide")
        
        ttk.Button(btn_frame, text="Exécuter", command=execute_fast_forward).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side='left', padx=5)
    
    # =====================================================
    # GESTION DES DONNÉES
    # =====================================================
    
    def new_database(self):
        """Crée une nouvelle base de données"""
        if messagebox.askyesno("Confirmer", "Créer une nouvelle base de données ?\nLes données actuelles seront perdues."):
            # Sauvegarder d'abord
            self.create_backup()
            
            # Réinitialiser les caches
            self.data_controller._avions_cache.clear()
            self.data_controller._vols_cache.clear()
            self.data_controller._personnels_cache.clear()
            self.data_controller._passagers_cache.clear()
            
            # Sauvegarder les caches vides
            self.data_controller.save_all_data()
            
            # Mettre à jour l'interface
            self.refresh_all_views()
            self.status_text.set("Nouvelle base de données créée")
    
    def open_database(self):
        """Ouvre une base de données existante"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier de données")
        if folder:
            try:
                # Créer un nouveau gestionnaire de données
                self.data_manager = JSONDataManager(folder)
                self.data_controller = DataController(self.data_manager)
                
                # Réassigner le simulateur aux vues
                self.simulation_panel.simulator = self.data_controller.simulator
                
                self.refresh_all_views()
                self.status_text.set(f"Base de données chargée: {folder}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger la base de données:\n{e}")
    
    def save_all_data(self):
        """Sauvegarde toutes les données"""
        try:
            self.data_controller.save_all_data()
            self.status_text.set("Données sauvegardées")
            logger.info("Sauvegarde manuelle effectuée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            logger.error(f"Erreur sauvegarde: {e}")
    
    def save_as_database(self):
        """Sauvegarde sous un nouveau dossier"""
        folder = filedialog.askdirectory(title="Sauvegarder vers...")
        if folder:
            try:
                self.data_manager.export_data(folder)
                messagebox.showinfo("Succès", f"Données exportées vers:\n{folder}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")
    
    def create_backup(self):
        """Crée une sauvegarde complète"""
        try:
            backup_path = self.data_manager.backup_data()
            messagebox.showinfo("Backup", f"Sauvegarde créée:\n{backup_path}")
            self.status_text.set("Backup créé")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du backup:\n{e}")
    
    def restore_backup(self):
        """Restaure depuis une sauvegarde"""
        backup_folder = filedialog.askdirectory(title="Sélectionner la sauvegarde à restaurer")
        if backup_folder:
            if messagebox.askyesno("Confirmer", "Restaurer cette sauvegarde ?\nLes données actuelles seront remplacées."):
                try:
                    success = self.data_manager.restore_from_backup(backup_folder)
                    if success:
                        # Recharger les données
                        self.data_controller.load_all_data()
                        self.refresh_all_views()
                        messagebox.showinfo("Succès", "Sauvegarde restaurée avec succès")
                    else:
                        messagebox.showerror("Erreur", "Échec de la restauration")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la restauration:\n{e}")
    
    def export_data(self):
        """Exporte les données"""
        folder = filedialog.askdirectory(title="Exporter vers...")
        if folder:
            try:
                self.data_manager.export_data(folder)
                messagebox.showinfo("Export", f"Données exportées vers:\n{folder}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")
    
    def import_data(self):
        """Importe des données"""
        messagebox.showinfo("Import", "Fonctionnalité d'import en développement")
    
    # =====================================================
    # DIALOGUES DE CRÉATION
    # =====================================================
    
    def new_aircraft_dialog(self):
        """Dialogue de création d'un nouvel avion"""
        if hasattr(self.views['fleet'], 'show_add_aircraft_dialog'):
            self.views['fleet'].show_add_aircraft_dialog()
        else:
            messagebox.showinfo("Info", "Utilisez l'onglet Flotte pour ajouter un avion")
            self.notebook.select(self.views['fleet'])
    
    def new_flight_dialog(self):
        """Dialogue de création d'un nouveau vol"""
        from .views.creation_dialogs import FlightCreationDialog
        
        dialog = FlightCreationDialog(self.root, self.data_controller,
                                    callback=lambda flight_id: self.refresh_all_views())
    
    def new_personnel_dialog(self):
        """Dialogue de création d'un nouveau personnel"""
        messagebox.showinfo("Personnel", "Dialogue de création de personnel en développement")
    
    def schedule_maintenance_dialog(self):
        """Dialogue de programmation de maintenance"""
        if hasattr(self.views['fleet'], 'show_maintenance_dialog'):
            self.views['fleet'].show_maintenance_dialog()
        else:
            messagebox.showinfo("Info", "Utilisez l'onglet Flotte pour programmer une maintenance")
    
    # =====================================================
    # OPÉRATIONS ET RAPPORTS
    # =====================================================
    
    def optimize_assignments(self):
        """Optimise les attributions avion-vol"""
        try:
            optimizations = self.data_controller.optimize_aircraft_assignment()
            if optimizations:
                message = f"Optimisations effectuées:\n"
                for vol_id, avion_id in optimizations.items():
                    message += f"- Vol {vol_id}: avion {avion_id}\n"
                messagebox.showinfo("Optimisation", message)
                self.refresh_all_views()
            else:
                messagebox.showinfo("Optimisation", "Aucune optimisation nécessaire")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'optimisation:\n{e}")
    
    def show_statistics(self):
        """Affiche les statistiques détaillées"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistiques Détaillées")
        stats_window.geometry("600x500")
        
        # Récupérer les statistiques
        stats = self.data_controller.get_statistics()
        
        # Affichage des stats
        text_widget = tk.Text(stats_window, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(stats_window, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Formater les statistiques
        stats_text = "=== STATISTIQUES GÉNÉRALES ===\n\n"
        
        for category, data in stats.items():
            stats_text += f"{category.upper()}:\n"
            if isinstance(data, dict):
                for key, value in data.items():
                    stats_text += f"  {key}: {value}\n"
            else:
                stats_text += f"  {data}\n"
            stats_text += "\n"
        
        text_widget.insert('1.0', stats_text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def show_flight_schedule(self):
        """Affiche le planning des vols"""
        schedule_window = tk.Toplevel(self.root)
        schedule_window.title("Planning des Vols")
        schedule_window.geometry("800x600")
        
        # Treeview pour le planning
        columns = ('Numéro', 'Départ', 'Arrivée', 'Heure Départ', 'Heure Arrivée', 'Statut')
        tree = ttk.Treeview(schedule_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Charger les données
        schedule = self.data_controller.get_flight_schedule()
        for item in schedule:
            vol = item['vol']
            tree.insert('', 'end', values=(
                vol.numero_vol,
                getattr(vol.aeroport_depart, 'code_iata', 'N/A'),
                getattr(vol.aeroport_arrivee, 'code_iata', 'N/A'),
                vol.heure_depart.strftime('%H:%M'),
                vol.heure_arrivee_prevue.strftime('%H:%M'),
                vol.statut.obtenir_nom_affichage()
            ))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_maintenance_schedule(self):
        """Affiche le planning des maintenances"""
        maintenance_window = tk.Toplevel(self.root)
        maintenance_window.title("Planning des Maintenances")
        maintenance_window.geometry("700x400")
        
        # Treeview pour les maintenances
        columns = ('Avion', 'Type', 'Programmée', 'Action')
        tree = ttk.Treeview(maintenance_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Charger les données
        maintenance_schedule = self.data_controller.get_maintenance_schedule()
        for item in maintenance_schedule:
            event = item['event']
            avion = item['avion']
            tree.insert('', 'end', values=(
                avion.num_id,
                'Maintenance Programmée',
                event.event_time.strftime('%Y-%m-%d %H:%M'),
                event.action
            ))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_event_log(self):
        """Affiche le journal des événements détaillé"""
        self.notebook.select(self.views['events'])
    
    def show_help(self):
        """Affiche l'aide"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Manuel Utilisateur")
        help_window.geometry("600x400")
        
        help_text = """
MANUEL UTILISATEUR - GESTION AÉROPORTUAIRE

=== SIMULATION ===
- F5: Démarrer la simulation
- F6: Mettre en pause
- F7: Arrêter
- Utilisez les contrôles de vitesse pour accélérer le temps

=== GESTION DES DONNÉES ===
- Ctrl+N: Nouvelle base de données
- Ctrl+O: Ouvrir une base existante
- Ctrl+S: Sauvegarder

=== NAVIGATION ===
- Utilisez les onglets pour naviguer entre les vues
- Le tableau de bord montre l'état général
- Les vues spécialisées permettent la gestion détaillée

=== ÉVÉNEMENTS ===
- Les événements sont programmés automatiquement
- La simulation traite les décollages/atterrissages
- Les maintenances sont planifiées et exécutées

Pour plus d'informations, consultez la documentation complète.
        """
        
        text_widget = tk.Text(help_window, wrap='word')
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_shortcuts(self):
        """Affiche les raccourcis clavier"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Raccourcis Clavier")
        shortcuts_window.geometry("400x300")
        
        shortcuts_text = """
RACCOURCIS CLAVIER

Fichier:
  Ctrl+N    Nouvelle base de données
  Ctrl+O    Ouvrir
  Ctrl+S    Sauvegarder
  Ctrl+Q    Quitter

Simulation:
  F5        Démarrer
  F6        Pause
  F7        Arrêter

Navigation:
  Tab       Changer d'onglet
  Esc       Fermer dialogue
        """
        
        text_widget = tk.Text(shortcuts_window, wrap='word', font=('Courier', 10))
        text_widget.insert('1.0', shortcuts_text)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
    
    def show_about(self):
        """Affiche les informations sur l'application"""
        messagebox.showinfo("À propos", 
                           "Gestion Aéroportuaire v1.0\n\n"
                           "Système de gestion d'aéroport avec simulation temporelle\n"
                           "Développé avec Python et Tkinter\n\n"
                           "© 2024 - Tous droits réservés")
    
    # =====================================================
    # UTILITAIRES
    # =====================================================
    
    def refresh_all_views(self):
        """Actualise toutes les vues"""
        for view in self.views.values():
            if hasattr(view, 'refresh_data'):
                view.refresh_data()
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            try:
                # Arrêter la simulation
                self.data_controller.simulator.stop()
                
                # Sauvegarder les données
                self.data_controller.save_all_data()
                
                # Créer un backup final
                self.data_manager.backup_data()
                
                logger.info("Application fermée proprement")
                
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture: {e}")
            
            finally:
                self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        try:
            logger.info("Démarrage de l'interface graphique")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Erreur dans la boucle principale: {e}")
            messagebox.showerror("Erreur fatale", f"Erreur dans l'application:\n{e}")
        finally:
            logger.info("Interface graphique fermée")

    def new_personnel_dialog(self):
        """Dialogue de création d'un nouveau personnel"""
        from .views.creation_dialogs import PersonnelCreationDialog
        
        dialog = PersonnelCreationDialog(self.root, self.data_controller,
                                    callback=lambda personnel_id: self.refresh_all_views())

    def new_passenger_dialog(self):
        """Dialogue de création d'un nouveau passager"""  
        from .views.creation_dialogs import PassengerCreationDialog
        
        dialog = PassengerCreationDialog(self.root, self.data_controller,
                                    callback=lambda passager_id: self.refresh_all_views())
