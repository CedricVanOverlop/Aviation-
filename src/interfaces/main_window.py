import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from data.data_manager import DataManager
from simulation.simulation_engine import SimulationEngine, SimulationSpeed

class MainWindow:
    """Fenêtre principale de l'application avec onglets et contrôles de simulation"""
    
    def __init__(self):
        """Initialise la fenêtre principale"""
        self.root = tk.Tk()
        self.root.title("Gestion Aéroportuaire - Simulation Temps Réel")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Gestionnaires
        self.data_manager = DataManager()
        self.simulation_engine = SimulationEngine(self.data_manager)
        
        # Variables d'interface
        self.simulation_time_var = tk.StringVar()
        self.speed_var = tk.StringVar(value="PAUSE")
        self.status_var = tk.StringVar(value="Simulation en pause")
        
        # Variables pour les statistiques (initialiser AVANT setup_ui)
        self.stat_vars = {}
        
        # Callbacks de simulation
        self.simulation_engine.add_callback('time_update', self.update_simulation_display)
        self.simulation_engine.add_callback('flight_update', self.refresh_flight_data)
        self.simulation_engine.add_callback('statistics_update', self.refresh_statistics)
        
        self.setup_ui()
        self.setup_styles()
        self.load_initial_data()
        
        print("🖥️ Interface principale initialisée")
    
    def setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        
        # Style pour les boutons principaux
        style.configure('Action.TButton', padding=(10, 5))
        style.configure('Danger.TButton', foreground='red')
        style.configure('Success.TButton', foreground='green')
        
        # Style pour les labels de statistiques
        style.configure('Stat.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Value.TLabel', font=('Arial', 14, 'bold'), foreground='blue')
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Barre supérieure avec contrôles de simulation
        self.create_simulation_controls(main_frame)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Création des onglets
        self.create_tabs()
        
        # Barre de statut
        self.create_status_bar(main_frame)
    
    def create_simulation_controls(self, parent):
        """Crée la barre de contrôles de simulation"""
        control_frame = ttk.LabelFrame(parent, text="Contrôles de Simulation", padding=10)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Temps simulé
        time_frame = ttk.Frame(control_frame)
        time_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        ttk.Label(time_frame, text="Temps simulé:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w")
        time_label = ttk.Label(time_frame, textvariable=self.simulation_time_var, 
                              style='Value.TLabel')
        time_label.grid(row=1, column=0, sticky="w")
        
        # Contrôles de vitesse
        speed_frame = ttk.Frame(control_frame)
        speed_frame.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(speed_frame, text="Vitesse:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w")
        
        # Combobox pour la vitesse
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, width=12, state="readonly")
        speed_combo['values'] = ['PAUSE', 'x1', 'x10', 'x60', 'x100', 'x360']
        speed_combo.grid(row=1, column=0, sticky="w")
        speed_combo.bind('<<ComboboxSelected>>', self.on_speed_change)
        
        # Boutons de contrôle
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=2, sticky="w", padx=(0, 20))
        
        ttk.Label(button_frame, text="Contrôles:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=4, sticky="w")
        
        self.btn_start = ttk.Button(button_frame, text="▶️ Démarrer", command=self.start_simulation, style='Success.TButton')
        self.btn_start.grid(row=1, column=0, padx=(0, 5))
        
        self.btn_pause = ttk.Button(button_frame, text="⏸️ Pause", command=self.pause_simulation)
        self.btn_pause.grid(row=1, column=1, padx=(0, 5))
        
        self.btn_stop = ttk.Button(button_frame, text="⏹️ Arrêter", command=self.stop_simulation, style='Danger.TButton')
        self.btn_stop.grid(row=1, column=2, padx=(0, 5))
        
        self.btn_reset = ttk.Button(button_frame, text="🔄 Reset", command=self.reset_simulation)
        self.btn_reset.grid(row=1, column=3, padx=(0, 5))
        
        # Avance rapide
        fast_frame = ttk.Frame(control_frame)
        fast_frame.grid(row=0, column=3, sticky="w")
        
        ttk.Label(fast_frame, text="Avance Rapide:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=3, sticky="w")
        
        ttk.Button(fast_frame, text="+1h", command=lambda: self.fast_forward(1)).grid(row=1, column=0, padx=(0, 2))
        ttk.Button(fast_frame, text="+6h", command=lambda: self.fast_forward(6)).grid(row=1, column=1, padx=(0, 2))
        ttk.Button(fast_frame, text="+24h", command=lambda: self.fast_forward(24)).grid(row=1, column=2)
        
        # Mise à jour initial
        self.update_simulation_display(datetime.now())
    
    def create_tabs(self):
        """Crée tous les onglets de l'application"""
        # Onglet Dashboard (Tableau de bord)
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Tableau de Bord")
        self.create_dashboard_tab()
        
        # Onglet Avions
        self.aircraft_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.aircraft_frame, text="✈️ Avions")
        self.create_aircraft_tab()
        
        # Onglet Personnel
        self.personnel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.personnel_frame, text="👥 Personnel")
        self.create_personnel_tab()
        
        # Onglet Vols
        self.flights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flights_frame, text="🛫 Vols")
        self.create_flights_tab()
        
        # Onglet Passagers
        self.passengers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.passengers_frame, text="🧳 Passagers")
        self.create_passengers_tab()
        
        # Onglet Réservations
        self.reservations_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reservations_frame, text="🎫 Réservations")
        self.create_reservations_tab()
    
    def create_dashboard_tab(self):
        """Crée l'onglet tableau de bord"""
        # Frame principal avec défilement
        canvas = tk.Canvas(self.dashboard_frame)
        scrollbar = ttk.Scrollbar(self.dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.dashboard_frame.grid_rowconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        
        # Section Statistiques Générales
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📈 Statistiques Générales", padding=15)
        stats_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Grid de statistiques (2x3)
        self.create_stat_card(stats_frame, "Vols Aujourd'hui", "0", "🛫", 0, 0)
        self.create_stat_card(stats_frame, "Vols en Cours", "0", "✈️", 0, 1)
        self.create_stat_card(stats_frame, "Avions Disponibles", "0", "🛩️", 0, 2)
        self.create_stat_card(stats_frame, "Personnel Actif", "0", "👥", 1, 0)
        self.create_stat_card(stats_frame, "Retards", "0", "⏰", 1, 1)
        self.create_stat_card(stats_frame, "Maintenances", "0", "🔧", 1, 2)
        
        # Section État des Vols
        flights_frame = ttk.LabelFrame(scrollable_frame, text="📊 État des Vols", padding=15)
        flights_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Grid état des vols (1x4)
        self.create_stat_card(flights_frame, "Programmés", "0", "📅", 0, 0)
        self.create_stat_card(flights_frame, "En Vol", "0", "🛫", 0, 1)
        self.create_stat_card(flights_frame, "Retardés", "0", "⏰", 0, 2)
        self.create_stat_card(flights_frame, "Annulés", "0", "❌", 0, 3)
        
        # Section Prochains Départs
        departures_frame = ttk.LabelFrame(scrollable_frame, text="🕐 Prochains Départs", padding=10)
        departures_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Tableau des prochains vols
        columns = ('Vol', 'Destination', 'Heure', 'Statut')
        self.departures_tree = ttk.Treeview(departures_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.departures_tree.heading(col, text=col)
            self.departures_tree.column(col, width=120)
        
        self.departures_tree.grid(row=0, column=0, sticky="ew")
        
        # Section État de la Flotte
        fleet_frame = ttk.LabelFrame(scrollable_frame, text="🛩️ État de la Flotte", padding=10)
        fleet_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        # Tableau de la flotte
        fleet_columns = ('Avion', 'Type', 'Compagnie', 'Capacité', 'État', 'Localisation', 'Autonomie', 'Dernière Maintenance')
        self.fleet_tree = ttk.Treeview(fleet_frame, columns=fleet_columns, show='headings', height=6)
        
        for col in fleet_columns:
            self.fleet_tree.heading(col, text=col)
            self.fleet_tree.column(col, width=100)
        
        self.fleet_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour les tableaux
        fleet_scrollbar = ttk.Scrollbar(fleet_frame, orient="vertical", command=self.fleet_tree.yview)
        fleet_scrollbar.grid(row=0, column=1, sticky="ns")
        self.fleet_tree.configure(yscrollcommand=fleet_scrollbar.set)
        
        # Configuration responsive
        scrollable_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        flights_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        departures_frame.grid_columnconfigure(0, weight=1)
        fleet_frame.grid_columnconfigure(0, weight=1)
        
        # Variables pour les statistiques
        self.stat_vars = {}
    
    def create_stat_card(self, parent, title, value, icon, row, col):
        """Crée une carte de statistique"""
        card_frame = ttk.Frame(parent, relief="solid", borderwidth=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Configuration de la grille
        card_frame.grid_columnconfigure(0, weight=1)
        
        # Icône et titre
        header_frame = ttk.Frame(card_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text=icon, font=('Arial', 16)).grid(row=0, column=0, sticky="w")
        ttk.Label(header_frame, text=title, font=('Arial', 10), foreground="gray").grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Valeur
        value_var = tk.StringVar(value=value)
        value_label = ttk.Label(card_frame, textvariable=value_var, style='Value.TLabel')
        value_label.grid(row=1, column=0, pady=(0, 10))
        
        # Stocker la variable pour mise à jour
        self.stat_vars[title] = value_var
        
        return card_frame
    
    def create_aircraft_tab(self):
        """Crée l'onglet de gestion des avions"""
        # Barre d'outils
        toolbar = ttk.Frame(self.aircraft_frame)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Button(toolbar, text="➕ Nouvel Avion", command=self.new_aircraft_dialog, style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
        ttk.Button(toolbar, text="✏️ Modifier", command=self.edit_aircraft).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(toolbar, text="🔧 Maintenance", command=self.aircraft_maintenance).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(toolbar, text="🗑️ Retirer", command=self.delete_aircraft, style='Danger.TButton').grid(row=0, column=3, padx=(0, 20))
        
        # Recherche
        ttk.Label(toolbar, text="🔍 Recherche:").grid(row=0, column=4, padx=(0, 5))
        self.aircraft_search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.aircraft_search_var, width=20)
        search_entry.grid(row=0, column=5, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.filter_aircraft)
        
        # Filtre par état
        ttk.Label(toolbar, text="État:").grid(row=0, column=6, padx=(10, 5))
        self.aircraft_filter_var = tk.StringVar(value="Tous")
        filter_combo = ttk.Combobox(toolbar, textvariable=self.aircraft_filter_var, width=15, state="readonly")
        filter_combo['values'] = ['Tous', 'Opérationnel', 'En vol', 'Maintenance', 'Hors service']
        filter_combo.grid(row=0, column=7, padx=(0, 5))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_aircraft)
        
        # Tableau des avions
        columns = ('ID', 'Modèle', 'Compagnie', 'Capacité', 'État', 'Localisation', 'Autonomie', 'Dernière Maintenance')
        self.aircraft_tree = ttk.Treeview(self.aircraft_frame, columns=columns, show='headings')
        self.aircraft_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Configuration colonnes
        column_widths = {'ID': 100, 'Modèle': 150, 'Compagnie': 120, 'Capacité': 80, 'État': 100, 'Localisation': 120, 'Autonomie': 100, 'Dernière Maintenance': 150}
        for col in columns:
            self.aircraft_tree.heading(col, text=col)
            self.aircraft_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        aircraft_v_scrollbar = ttk.Scrollbar(self.aircraft_frame, orient="vertical", command=self.aircraft_tree.yview)
        aircraft_v_scrollbar.grid(row=1, column=1, sticky="ns")
        self.aircraft_tree.configure(yscrollcommand=aircraft_v_scrollbar.set)
        
        aircraft_h_scrollbar = ttk.Scrollbar(self.aircraft_frame, orient="horizontal", command=self.aircraft_tree.xview)
        aircraft_h_scrollbar.grid(row=2, column=0, sticky="ew")
        self.aircraft_tree.configure(xscrollcommand=aircraft_h_scrollbar.set)
        
        # Configuration responsive
        self.aircraft_frame.grid_rowconfigure(1, weight=1)
        self.aircraft_frame.grid_columnconfigure(0, weight=1)
    
    def create_personnel_tab(self):
        """Crée l'onglet de gestion du personnel"""
        # Placeholder pour maintenant
        ttk.Label(self.personnel_frame, text="Gestion du Personnel - À implémenter", 
                 font=('Arial', 14), foreground='gray').pack(expand=True)
    
    def create_flights_tab(self):
        """Crée l'onglet de gestion des vols"""
        # Placeholder pour maintenant
        ttk.Label(self.flights_frame, text="Gestion des Vols - À implémenter", 
                 font=('Arial', 14), foreground='gray').pack(expand=True)
    
    def create_passengers_tab(self):
        """Crée l'onglet de gestion des passagers"""
        # Placeholder pour maintenant
        ttk.Label(self.passengers_frame, text="Gestion des Passagers - À implémenter", 
                 font=('Arial', 14), foreground='gray').pack(expand=True)
    
    def create_reservations_tab(self):
        """Crée l'onglet de gestion des réservations"""
        # Placeholder pour maintenant
        ttk.Label(self.reservations_frame, text="Gestion des Réservations - À implémenter", 
                 font=('Arial', 14), foreground='gray').pack(expand=True)
    
    def create_status_bar(self, parent):
        """Crée la barre de statut"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Label(status_frame, text=f"Données: {self.data_manager.data_dir}").grid(row=0, column=1, sticky="e")
        
        status_frame.grid_columnconfigure(0, weight=1)
    
    # Méthodes de contrôle de simulation
    def on_speed_change(self, event=None):
        """Gestionnaire de changement de vitesse"""
        speed_text = self.speed_var.get()
        speed_mapping = {
            'PAUSE': SimulationSpeed.PAUSE,
            'x1': SimulationSpeed.REAL_TIME,
            'x10': SimulationSpeed.SPEED_10X,
            'x60': SimulationSpeed.SPEED_60X,
            'x100': SimulationSpeed.SPEED_100X,
            'x360': SimulationSpeed.SPEED_360X
        }
        
        speed = speed_mapping.get(speed_text, SimulationSpeed.PAUSE)
        self.simulation_engine.set_speed(speed)
        self.update_status()
    
    def start_simulation(self):
        """Démarre la simulation"""
        if self.speed_var.get() == 'PAUSE':
            self.speed_var.set('x1')
            self.on_speed_change()
        
        self.simulation_engine.start()
        self.update_status()
    
    def pause_simulation(self):
        """Met en pause la simulation"""
        self.simulation_engine.pause()
        self.update_status()
    
    def stop_simulation(self):
        """Arrête la simulation"""
        self.simulation_engine.stop()
        self.speed_var.set('PAUSE')
        self.update_status()
    
    def reset_simulation(self):
        """Remet à zéro la simulation"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment remettre à zéro la simulation ?"):
            self.simulation_engine.reset()
            self.speed_var.set('PAUSE')
            self.update_status()
            self.refresh_all_data()
    
    def fast_forward(self, hours):
        """Avance rapide de X heures"""
        self.simulation_engine.fast_forward(hours)
        self.refresh_all_data()
    
    def update_simulation_display(self, sim_time):
        """Met à jour l'affichage du temps de simulation"""
        self.simulation_time_var.set(sim_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    def update_status(self):
        """Met à jour la barre de statut"""
        info = self.simulation_engine.get_simulation_info()
        if info['is_running'] and not info['is_paused']:
            self.status_var.set(f"Simulation en cours - Vitesse: {info['speed']}")
        elif info['is_paused']:
            self.status_var.set("Simulation en pause")
        else:
            self.status_var.set("Simulation arrêtée")
    
    # Méthodes de gestion des avions
    def new_aircraft_dialog(self):
        """Ouvre le dialogue de création d'avion"""
        from interfaces.tabs.aircraft_tab import AircraftDialog
        dialog = AircraftDialog(self.root, self.data_manager)
        if dialog.result:
            self.refresh_aircraft_data()
            self.refresh_statistics()
    
    def edit_aircraft(self):
        """Modifie l'avion sélectionné"""
        selection = self.aircraft_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un avion à modifier.")
            return
        
        # TODO: Implémenter la modification
        messagebox.showinfo("Info", "Modification d'avion - À implémenter")
    
    def aircraft_maintenance(self):
        """Met l'avion en maintenance"""
        selection = self.aircraft_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un avion pour la maintenance.")
            return
        
        # TODO: Implémenter la maintenance
        messagebox.showinfo("Info", "Maintenance d'avion - À implémenter")
    
    def delete_aircraft(self):
        """Supprime l'avion sélectionné"""
        selection = self.aircraft_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un avion à supprimer.")
            return
        
        item = self.aircraft_tree.item(selection[0])
        aircraft_id = item['values'][0]
        aircraft_model = item['values'][1]
        
        if messagebox.askyesno("Confirmation", 
                              f"Voulez-vous vraiment supprimer l'avion {aircraft_id} ({aircraft_model}) ?"):
            if self.data_manager.delete_aircraft(aircraft_id):
                self.refresh_aircraft_data()
                self.refresh_statistics()
                messagebox.showinfo("Succès", "Avion supprimé avec succès.")
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer l'avion.")
    
    def filter_aircraft(self, event=None):
        """Filtre la liste des avions"""
        # TODO: Implémenter le filtrage
        pass
    
    # Méthodes de rafraîchissement des données
    def refresh_aircraft_data(self):
        """Rafraîchit les données des avions"""
        if not hasattr(self, 'aircraft_tree'):
            return
            
        # Vider le tableau
        for item in self.aircraft_tree.get_children():
            self.aircraft_tree.delete(item)
        
        # Recharger les données
        aircraft_list = self.data_manager.get_aircraft()
        airports = {a['code_iata']: a['ville'] for a in self.data_manager.get_airports()}
        
        for aircraft in aircraft_list:
            # Obtenir le nom de la ville depuis les coordonnées
            location = "Inconnu"
            if 'localisation' in aircraft:
                loc_coords = aircraft['localisation']
                # Trouver l'aéroport le plus proche (simplifié)
                for airport in self.data_manager.get_airports():
                    if (abs(airport['coordonnees']['latitude'] - loc_coords.get('latitude', 0)) < 0.1 and
                        abs(airport['coordonnees']['longitude'] - loc_coords.get('longitude', 0)) < 0.1):
                        location = f"{airport['ville']} ({airport['code_iata']})"
                        break
            
            values = (
                aircraft.get('num_id', ''),
                aircraft.get('modele', ''),
                aircraft.get('compagnie_aerienne', ''),
                aircraft.get('capacite', ''),
                aircraft.get('etat', 'au_sol'),
                location,
                f"{aircraft.get('autonomie', 0)} km",
                aircraft.get('derniere_maintenance', 'Jamais')
            )
            
            self.aircraft_tree.insert('', 'end', values=values)
    
    def refresh_flight_data(self, flight_data=None):
        """Rafraîchit les données des vols"""
        # TODO: Implémenter
        pass
    
    def refresh_statistics(self):
        """Rafraîchit les statistiques du dashboard"""
        stats = self.data_manager.get_statistics()
        
        # Mise à jour des cartes de statistiques (vérifier l'existence d'abord)
        if hasattr(self, 'stat_vars') and self.stat_vars:
            if "Vols Aujourd'hui" in self.stat_vars:
                self.stat_vars["Vols Aujourd'hui"].set(str(stats.get('total_flights', 0)))
            if "Avions Disponibles" in self.stat_vars:
                available = stats.get('aircraft_states', {}).get('operationnel', 0)
                self.stat_vars["Avions Disponibles"].set(str(available))
            if "Personnel Actif" in self.stat_vars:
                self.stat_vars["Personnel Actif"].set(str(stats.get('total_personnel', 0)))
        
        # Rafraîchir le tableau de la flotte
        if hasattr(self, 'fleet_tree'):
            self.refresh_fleet_display()
    
    def refresh_fleet_display(self):
        """Rafraîchit l'affichage de la flotte dans le dashboard"""
        if not hasattr(self, 'fleet_tree'):
            return
            
        # Vider le tableau
        for item in self.fleet_tree.get_children():
            self.fleet_tree.delete(item)
        
        # Recharger les données des avions
        aircraft_list = self.data_manager.get_aircraft()
        
        for aircraft in aircraft_list[:10]:  # Limiter à 10 pour le dashboard
            values = (
                aircraft.get('num_id', ''),
                aircraft.get('modele', ''),
                aircraft.get('compagnie_aerienne', ''),
                aircraft.get('capacite', ''),
                aircraft.get('etat', 'au_sol').replace('_', ' ').title(),
                "Base principale",  # Simplifié pour maintenant
                f"{aircraft.get('autonomie', 0)} km",
                aircraft.get('derniere_maintenance', 'Jamais')
            )
            
            self.fleet_tree.insert('', 'end', values=values)
    
    def refresh_all_data(self):
        """Rafraîchit toutes les données"""
        self.refresh_aircraft_data()
        self.refresh_statistics()
        self.refresh_flight_data()
    
    def load_initial_data(self):
        """Charge les données initiales"""
        try:
            # Vérifier l'intégrité des données
            integrity_report = self.data_manager.validate_data_integrity()
            if not integrity_report['valid']:
                messagebox.showwarning("Données", 
                    f"Problèmes détectés dans les données:\n" + 
                    "\n".join(integrity_report['errors'][:3]))
            
            # Charger les données dans l'interface
            self.refresh_all_data()
            
            print(f"✓ Données chargées: {integrity_report['files_checked']} fichiers")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données:\n{e}")
            print(f"❌ Erreur chargement: {e}")
    
    def run(self):
        """Lance l'application"""
        try:
            # Gérer la fermeture propre
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Lancer la boucle principale
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n🛑 Interruption clavier détectée")
            self.on_closing()
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        try:
            # Arrêter la simulation
            if self.simulation_engine.is_running:
                self.simulation_engine.stop()
            
            # Sauvegarder les données si nécessaire
            print("💾 Sauvegarde finale...")
            
            # Fermer l'application
            self.root.destroy()
            print("👋 Application fermée proprement")
            
        except Exception as e:
            print(f"❌ Erreur lors de la fermeture: {e}")
            self.root.destroy()

if __name__ == "__main__":
    app = MainWindow()
    app.run()