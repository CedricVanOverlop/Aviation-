"""
Dashboard Tab - Tableau de bord avancé temps réel
Fichier: src/interfaces/tabs/dashboard_tab.py

Ce module crée un tableau de bord moderne et complet pour l'application
de gestion aéroportuaire avec des visualisations temps réel et intégration
complète avec le moteur de simulation.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime, timedelta
import math
import random
import threading

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.meteo import Meteo
from Core.enums import TypeIntemperie, StatutVol, EtatAvion

class ModernDashboard:
    """Tableau de bord principal avec visualisations en temps réel"""
    
    def __init__(self, parent_frame, data_manager, simulation_engine=None):
        """
        Initialise le tableau de bord.
        
        Args:
            parent_frame: Frame parent Tkinter
            data_manager: Gestionnaire de données
            simulation_engine: Moteur de simulation (optionnel)
        """
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.simulation_engine = simulation_engine
        
        # Variables pour les statistiques
        self.stat_vars = {}
        self.widgets = {}
        self.charts_canvas = {}
        
        # Configuration des couleurs du thème moderne
        self.colors = {
            'primary': '#1E3A8A',      # Bleu professionnel
            'secondary': '#7C3AED',    # Violet moderne
            'success': '#059669',      # Vert succès
            'warning': '#D97706',      # Orange attention
            'danger': '#DC2626',       # Rouge danger
            'info': '#0284C7',         # Bleu information
            'light': '#F1F5F9',        # Gris clair
            'dark': '#1E293B',         # Gris foncé
            'background': '#FFFFFF',   # Blanc
            'border': '#E2E8F0',       # Bordure grise
            'accent': '#10B981',       # Vert accent
            'surface': '#F8FAFC'       # Surface claire
        }
        
        # Données météo actuelles (simulées)
        self.current_weather = Meteo(
            temperature=18.5,
            vitesse_vent=15.0,
            intemperie=TypeIntemperie.AUCUNE,
            visibilite=10.0,
            pression=1013.25
        )
        
        # Configuration du layout
        self.setup_dashboard()
        self.load_initial_data()
        
        # Démarrage des mises à jour automatiques
        self.start_auto_refresh()
        
        print("✅ Dashboard avancé initialisé avec succès")
    
    def setup_dashboard(self):
        """Configure l'interface complète du dashboard"""
        # Configuration du scrolling pour le dashboard
        self.setup_scrollable_container()
        
        # Création des différentes sections
        self.create_header_section()           # En-tête avec horloge et météo
        self.create_kpi_section()             # Indicateurs clés de performance
        self.create_operations_section()      # Opérations en cours
        self.create_departures_section()      # Prochains départs
        self.create_checkin_section()         # Check-ins ouverts
        self.create_fleet_section()           # État de la flotte
        self.create_weather_section()         # Informations météo détaillées
        self.create_activity_section()        # Activité temps réel
        self.update_header_info()
    
    def setup_scrollable_container(self):
        """Configure le conteneur avec défilement"""
        # Canvas principal pour le défilement
        self.canvas = tk.Canvas(self.parent_frame, bg=self.colors['background'])
        self.scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configuration du défilement
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Placement dans la grille
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configuration responsive
        self.parent_frame.grid_rowconfigure(0, weight=1)
        self.parent_frame.grid_columnconfigure(0, weight=1)
        
        # Configuration de la molette de souris
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Gestionnaire de la molette de souris"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_header_section(self):
        """Crée la section d'en-tête avec titre, horloge et météo"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Configuration responsive
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Section gauche - Titre et informations système
        left_frame = ttk.Frame(header_frame)
        left_frame.grid(row=0, column=0, sticky="w")
        
        # Titre principal avec icône
        title_label = ttk.Label(left_frame, 
                               text="🏢 Tableau de Bord Aéroportuaire",
                               font=('Arial', 24, 'bold'),
                               foreground=self.colors['primary'])
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ttk.Label(left_frame,
                                  text="Vue d'ensemble temps réel des opérations",
                                  font=('Arial', 12),
                                  foreground=self.colors['dark'])
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Section droite - Horloge et météo
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=0, column=1, sticky="e")
        
        # Horloge système et simulation
        clock_frame = ttk.LabelFrame(right_frame, text="🕐 Temps", padding=10)
        clock_frame.grid(row=0, column=0, padx=(0, 10), sticky="e")
        
        # Horloge système
        self.system_clock_var = tk.StringVar()
        system_clock_label = ttk.Label(clock_frame, text="Système:")
        system_clock_label.grid(row=0, column=0, sticky="w")
        clock_label = ttk.Label(clock_frame, textvariable=self.system_clock_var,
                               font=('Arial', 12, 'bold'),
                               foreground=self.colors['primary'])
        clock_label.grid(row=0, column=1, sticky="e", padx=(5, 0))
        
        # Horloge simulation
        self.sim_clock_var = tk.StringVar()
        sim_clock_label = ttk.Label(clock_frame, text="Simulation:")
        sim_clock_label.grid(row=1, column=0, sticky="w")
        sim_time_label = ttk.Label(clock_frame, textvariable=self.sim_clock_var,
                                  font=('Arial', 12, 'bold'),
                                  foreground=self.colors['info'])
        sim_time_label.grid(row=1, column=1, sticky="e", padx=(5, 0))
        
        # Statut simulation
        self.sim_status_var = tk.StringVar()
        status_label = ttk.Label(clock_frame, textvariable=self.sim_status_var,
                                font=('Arial', 9),
                                foreground=self.colors['secondary'])
        status_label.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Météo rapide
        weather_frame = ttk.LabelFrame(right_frame, text="🌤️ Météo", padding=10)
        weather_frame.grid(row=0, column=1, sticky="e")
        
        self.weather_temp_var = tk.StringVar()
        self.weather_wind_var = tk.StringVar()
        self.weather_condition_var = tk.StringVar()
        
        ttk.Label(weather_frame, textvariable=self.weather_temp_var,
                 font=('Arial', 14, 'bold'),
                 foreground=self.colors['info']).grid(row=0, column=0)
        ttk.Label(weather_frame, textvariable=self.weather_wind_var,
                 font=('Arial', 10)).grid(row=1, column=0)
        ttk.Label(weather_frame, textvariable=self.weather_condition_var,
                 font=('Arial', 10)).grid(row=2, column=0)

    
    def create_kpi_section(self):
        """Crée la section des indicateurs de performance clés"""
        kpi_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Indicateurs Clés", padding=20)
        kpi_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration responsive - 4 colonnes
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        # Définition des KPI principaux
        kpis = [
            # Première ligne - Opérations de vol
            ("Vols Aujourd'hui", "0", "🛫", "primary", "Nombre total de vols programmés", 0, 0),
            ("Vols en Cours", "0", "✈️", "success", "Vols actuellement en l'air", 0, 1),
            ("Vols Retardés", "0", "⏰", "warning", "Vols avec retard signalé", 0, 2),
            ("Taux Ponctualité", "100%", "🎯", "info", "Pourcentage de vols à l'heure", 0, 3),
            
            # Deuxième ligne - Ressources
            ("Avions Actifs", "0", "🛩️", "secondary", "Avions opérationnels", 1, 0),
            ("Personnel Dispo.", "0", "👨‍✈️", "primary", "Personnel disponible", 1, 1),
            ("Check-ins Ouverts", "0", "✅", "accent", "Check-ins actuellement ouverts", 1, 2),
            ("Passagers Total", "0", "👥", "info", "Passagers enregistrés", 1, 3),
        ]
        
        # Création des cartes KPI
        for title, value, icon, color, tooltip, row, col in kpis:
            self.create_kpi_card(kpi_frame, title, value, icon, color, tooltip, row, col)
    
    def create_kpi_card(self, parent, title, value, icon, color, tooltip, row, col):
        """Crée une carte KPI moderne avec animations"""
        # Frame principale de la carte avec effet d'ombre
        card_frame = ttk.Frame(parent, relief="raised", borderwidth=2, padding=15)
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
        
        # Configuration
        card_frame.grid_columnconfigure(0, weight=1)
        
        # En-tête avec icône et titre
        header_frame = ttk.Frame(card_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Icône grande
        icon_label = ttk.Label(header_frame, text=icon, font=('Arial', 20))
        icon_label.grid(row=0, column=0, sticky="w")
        
        # Titre et description
        title_label = ttk.Label(header_frame, text=title, 
                               font=('Arial', 11, 'bold'),
                               foreground=self.colors['dark'])
        title_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Valeur principale (très grande et colorée)
        value_var = tk.StringVar(value=value)
        value_label = ttk.Label(card_frame, textvariable=value_var,
                               font=('Arial', 18, 'bold'),
                               foreground=self.colors.get(color, self.colors['primary']))
        value_label.grid(row=1, column=0, pady=(0, 5))
        
        # Indicateur de tendance (animé)
        trend_var = tk.StringVar(value="📈 +0%")
        trend_label = ttk.Label(card_frame, textvariable=trend_var,
                               font=('Arial', 9),
                               foreground=self.colors['success'])
        trend_label.grid(row=2, column=0)
        
        # Barre de progression (optionnelle)
        progress_var = tk.DoubleVar(value=75.0)
        progress_bar = ttk.Progressbar(card_frame, variable=progress_var,
                                     maximum=100, length=120, mode='determinate')
        progress_bar.grid(row=3, column=0, pady=(5, 0), sticky="ew")
        
        # Stockage des variables pour mises à jour
        self.stat_vars[title] = {
            'value': value_var,
            'trend': trend_var,
            'progress': progress_var
        }
        
        # Effet hover (simulation)
        self.create_hover_effect(card_frame, tooltip)
        
        return card_frame
    
    def create_hover_effect(self, widget, tooltip_text):
        """Crée un effet hover pour les widgets"""
        def on_enter(event):
            widget.configure(relief="solid")
            # Créer tooltip (simplifié)
            self.show_tooltip(widget, tooltip_text)
        
        def on_leave(event):
            widget.configure(relief="raised")
            self.hide_tooltip()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def show_tooltip(self, widget, text):
        """Affiche un tooltip (version simplifiée)"""
        # Version simplifiée - juste changer le curseur
        widget.configure(cursor="hand2")
    
    def hide_tooltip(self):
        """Cache le tooltip"""
        pass  # Version simplifiée
    
    def create_operations_section(self):
        """Crée la section des opérations en cours"""
        ops_frame = ttk.LabelFrame(self.scrollable_frame, text="⚡ Opérations en Cours", padding=20)
        ops_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration en 2 colonnes
        ops_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Vols en cours
        flights_frame = ttk.LabelFrame(ops_frame, text="✈️ Vols en Cours", padding=10)
        flights_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Tableau vols en cours
        columns = ('Vol', 'Route', 'Progression', 'ETA')
        self.current_flights_tree = ttk.Treeview(flights_frame, columns=columns, 
                                               show='headings', height=6)
        
        for col in columns:
            self.current_flights_tree.heading(col, text=col)
            self.current_flights_tree.column(col, width=80, anchor="center")
        
        self.current_flights_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour vols en cours
        flights_scroll = ttk.Scrollbar(flights_frame, orient="vertical", 
                                     command=self.current_flights_tree.yview)
        flights_scroll.grid(row=0, column=1, sticky="ns")
        self.current_flights_tree.configure(yscrollcommand=flights_scroll.set)
        
        # Maintenance en cours
        maint_frame = ttk.LabelFrame(ops_frame, text="🔧 Maintenances", padding=10)
        maint_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Liste des maintenances
        self.maintenance_text = tk.Text(maint_frame, height=6, width=40,
                                      font=('Arial', 10), bg=self.colors['light'],
                                      relief="sunken", bd=1)
        self.maintenance_text.grid(row=0, column=0, sticky="ew")
        
        maint_scroll = ttk.Scrollbar(maint_frame, orient="vertical",
                                   command=self.maintenance_text.yview)
        maint_scroll.grid(row=0, column=1, sticky="ns")
        self.maintenance_text.configure(yscrollcommand=maint_scroll.set)
        
        # Configuration responsive
        flights_frame.grid_columnconfigure(0, weight=1)
        maint_frame.grid_columnconfigure(0, weight=1)
    
    def create_departures_section(self):
        """Crée la section des prochains départs"""
        dep_frame = ttk.LabelFrame(self.scrollable_frame, text="🛫 Prochains Départs", padding=20)
        dep_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Tableau des prochains départs
        columns = ('Vol', 'Destination', 'Heure', 'Porte', 'Statut', 'Check-in')
        self.departures_tree = ttk.Treeview(dep_frame, columns=columns, 
                                          show='headings', height=8)
        
        # Configuration des colonnes
        column_widths = {'Vol': 80, 'Destination': 100, 'Heure': 80, 
                        'Porte': 60, 'Statut': 100, 'Check-in': 80}
        for col in columns:
            self.departures_tree.heading(col, text=col)
            self.departures_tree.column(col, width=column_widths[col], anchor="center")
        
        self.departures_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar
        dep_scrollbar = ttk.Scrollbar(dep_frame, orient="vertical", 
                                    command=self.departures_tree.yview)
        dep_scrollbar.grid(row=0, column=1, sticky="ns")
        self.departures_tree.configure(yscrollcommand=dep_scrollbar.set)
        
        # Configuration responsive
        dep_frame.grid_columnconfigure(0, weight=1)
    
    def create_checkin_section(self):
        """Crée la section des check-ins ouverts"""
        checkin_frame = ttk.LabelFrame(self.scrollable_frame, text="✅ Check-ins Ouverts", padding=20)
        checkin_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration en 2 colonnes
        checkin_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Check-ins disponibles
        available_frame = ttk.LabelFrame(checkin_frame, text="🟢 Disponibles", padding=10)
        available_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        columns = ('Vol', 'Destination', 'Départ', 'Fermeture')
        self.checkin_tree = ttk.Treeview(available_frame, columns=columns, 
                                       show='headings', height=5)
        
        for col in columns:
            self.checkin_tree.heading(col, text=col)
            self.checkin_tree.column(col, width=80, anchor="center")
        
        self.checkin_tree.grid(row=0, column=0, sticky="ew")
        
        # Check-ins fermés récemment
        closed_frame = ttk.LabelFrame(checkin_frame, text="🔴 Récemment Fermés", padding=10)
        closed_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.closed_checkin_text = tk.Text(closed_frame, height=5, width=30,
                                         font=('Arial', 9), bg=self.colors['light'])
        self.closed_checkin_text.grid(row=0, column=0, sticky="ew")
        
        # Configuration responsive
        available_frame.grid_columnconfigure(0, weight=1)
        closed_frame.grid_columnconfigure(0, weight=1)
    
    def create_fleet_section(self):
        """Crée la section de l'état de la flotte"""
        fleet_frame = ttk.LabelFrame(self.scrollable_frame, text="🛩️ État de la Flotte", padding=20)
        fleet_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration en 3 colonnes
        fleet_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Avions disponibles
        available_frame = ttk.LabelFrame(fleet_frame, text="🟢 Disponibles", padding=10)
        available_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.available_aircraft_text = tk.Text(available_frame, height=6, width=25,
                                             font=('Arial', 9), bg=self.colors['light'])
        self.available_aircraft_text.grid(row=0, column=0, sticky="ew")
        
        # Avions en vol
        flying_frame = ttk.LabelFrame(fleet_frame, text="🔵 En Vol", padding=10)
        flying_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.flying_aircraft_text = tk.Text(flying_frame, height=6, width=25,
                                          font=('Arial', 9), bg=self.colors['light'])
        self.flying_aircraft_text.grid(row=0, column=0, sticky="ew")
        
        # Avions en maintenance
        maintenance_frame = ttk.LabelFrame(fleet_frame, text="🟡 Maintenance", padding=10)
        maintenance_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.maintenance_aircraft_text = tk.Text(maintenance_frame, height=6, width=25,
                                               font=('Arial', 9), bg=self.colors['light'])
        self.maintenance_aircraft_text.grid(row=0, column=0, sticky="ew")
        
        # Configuration responsive
        available_frame.grid_columnconfigure(0, weight=1)
        flying_frame.grid_columnconfigure(0, weight=1)
        maintenance_frame.grid_columnconfigure(0, weight=1)
    
    def create_weather_section(self):
        """Crée la section météo détaillée"""
        weather_frame = ttk.LabelFrame(self.scrollable_frame, text="🌤️ Conditions Météorologiques", padding=20)
        weather_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration en 2 colonnes
        weather_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Conditions actuelles
        current_frame = ttk.LabelFrame(weather_frame, text="📊 Conditions Actuelles", padding=15)
        current_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Variables météo
        self.detailed_temp_var = tk.StringVar()
        self.detailed_wind_var = tk.StringVar()
        self.detailed_pressure_var = tk.StringVar()
        self.detailed_visibility_var = tk.StringVar()
        self.detailed_condition_var = tk.StringVar()
        
        # Affichage détaillé
        ttk.Label(current_frame, text="🌡️ Température:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(current_frame, textvariable=self.detailed_temp_var, font=('Arial', 10)).grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(current_frame, text="💨 Vent:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(current_frame, textvariable=self.detailed_wind_var, font=('Arial', 10)).grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(current_frame, text="📊 Pression:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(current_frame, textvariable=self.detailed_pressure_var, font=('Arial', 10)).grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(current_frame, text="👁️ Visibilité:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(current_frame, textvariable=self.detailed_visibility_var, font=('Arial', 10)).grid(row=3, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(current_frame, text="🌤️ Conditions:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky="w", pady=2)
        ttk.Label(current_frame, textvariable=self.detailed_condition_var, font=('Arial', 10)).grid(row=4, column=1, sticky="w", padx=(10, 0))
        
        # Impact sur les vols
        impact_frame = ttk.LabelFrame(weather_frame, text="✈️ Impact sur les Vols", padding=15)
        impact_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.weather_impact_text = tk.Text(impact_frame, height=8, width=35,
                                         font=('Arial', 10), bg=self.colors['light'],
                                         relief="sunken", bd=1)
        self.weather_impact_text.grid(row=0, column=0, sticky="ew")
        
        # Configuration responsive
        current_frame.grid_columnconfigure(1, weight=1)
        impact_frame.grid_columnconfigure(0, weight=1)
    
    def create_activity_section(self):
        """Crée la section d'activité temps réel"""
        activity_frame = ttk.LabelFrame(self.scrollable_frame, text="📡 Activité Temps Réel", padding=20)
        activity_frame.grid(row=7, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        # Zone de log d'activité avec couleurs
        self.activity_text = tk.Text(activity_frame, height=12, width=100,
                                   font=('Consolas', 9), bg=self.colors['dark'],
                                   fg='white', relief="sunken", bd=2)
        self.activity_text.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour le log
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical",
                                         command=self.activity_text.yview)
        activity_scrollbar.grid(row=0, column=1, sticky="ns")
        self.activity_text.configure(yscrollcommand=activity_scrollbar.set)
        
        # Configuration des tags de couleur
        self.setup_activity_tags()
        
        # Ajout d'événements d'exemple
        self.add_sample_activity_events()
        
        # Configuration responsive
        activity_frame.grid_columnconfigure(0, weight=1)
    
    def setup_activity_tags(self):
        """Configure les tags de couleur pour le log d'activité"""
        self.activity_text.tag_config("INFO", foreground="#60A5FA")      # Bleu
        self.activity_text.tag_config("SUCCESS", foreground="#34D399")   # Vert
        self.activity_text.tag_config("WARNING", foreground="#FBBF24")   # Orange
        self.activity_text.tag_config("ERROR", foreground="#F87171")     # Rouge
        self.activity_text.tag_config("SYSTEM", foreground="#A78BFA")    # Violet
        self.activity_text.tag_config("FLIGHT", foreground="#FB7185")    # Rose
        self.activity_text.tag_config("timestamp", foreground="#9CA3AF")  # Gris
    
    def add_sample_activity_events(self):
        """Ajoute des événements d'exemple au log d'activité"""
        sample_events = [
            ("SYSTEM", "🖥️ Dashboard initialisé avec succès"),
            ("INFO", "📡 Connexion au moteur de simulation établie"),
            ("SUCCESS", "✅ Données météo mises à jour"),
            ("INFO", "🔄 Synchronisation des données en cours..."),
            ("FLIGHT", "✈️ Vol AF123 - Préparation du décollage"),
            ("SUCCESS", "🛫 Vol BA456 - Décollage effectué"),
            ("WARNING", "⚠️ Vent fort détecté - Surveillance renforcée"),
            ("INFO", "👥 Nouveau passager enregistré"),
            ("SYSTEM", "💾 Sauvegarde automatique effectuée"),
        ]
        
        for level, message in sample_events:
            self.log_activity(level, message)
    
    def log_activity(self, level, message):
        """Ajoute un message au log d'activité avec formatage"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insérer le timestamp
        self.activity_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insérer le niveau avec tag de couleur
        self.activity_text.insert(tk.END, f"{level:<8} ", level)
        
        # Insérer le message
        self.activity_text.insert(tk.END, f"{message}\n")
        
        # Faire défiler vers le bas
        self.activity_text.see(tk.END)
        
        # Limiter le nombre de lignes (garder les 200 dernières)
        lines = self.activity_text.get("1.0", tk.END).split('\n')
        if len(lines) > 200:
            self.activity_text.delete("1.0", f"{len(lines)-200}.0")
    
    def update_header_info(self):
        """Met à jour les informations d'en-tête"""
        # Horloge système
        current_time = datetime.now().strftime("%H:%M:%S")
        self.system_clock_var.set(current_time)
        
        # Horloge et statut de simulation
        if self.simulation_engine:
            try:
                sim_info = self.simulation_engine.get_simulation_info()
                sim_time = datetime.fromisoformat(sim_info['simulation_time'])
                sim_time_str = sim_time.strftime("%H:%M:%S")
                speed = sim_info['speed_value']
                
                self.sim_clock_var.set(sim_time_str)
                
                if sim_info['is_running'] and not sim_info['is_paused']:
                    status = f"🟢 Actif (x{speed})"
                elif sim_info['is_paused']:
                    status = f"🟡 Pause (x{speed})"
                else:
                    status = "🔴 Arrêtée"
                
                self.sim_status_var.set(status)
            except Exception as e:
                self.sim_clock_var.set("--:--:--")
                self.sim_status_var.set("⚠️ Erreur simulation")
        else:
            self.sim_clock_var.set("--:--:--")
            self.sim_status_var.set("📴 Non disponible")
        
        # Météo
        self.update_weather_display()
    
    def update_weather_display(self):
        """Met à jour l'affichage météo"""
        # Simuler des variations météo légères
        if random.random() < 0.1:  # 10% de chance de changement
            self.current_weather.temperature += random.uniform(-0.5, 0.5)
            self.current_weather.vitesse_vent += random.uniform(-2.0, 2.0)
            self.current_weather.vitesse_vent = max(0, self.current_weather.vitesse_vent)
        
        # Météo en-tête (rapide)
        self.weather_temp_var.set(f"{self.current_weather.temperature:.1f}°C")
        wind_status = self.current_weather.statut_vent()
        wind_color = {
            "ok": "🟢", "modere": "🟡", "attention": "🟠", "danger": "🔴"
        }.get(wind_status, "🟢")
        self.weather_wind_var.set(f"{wind_color} {self.current_weather.vitesse_vent:.0f} km/h")
        self.weather_condition_var.set(self.current_weather.intemperie.obtenir_nom_affichage())
        
        # Météo détaillée
        self.detailed_temp_var.set(f"{self.current_weather.temperature:.1f}°C")
        self.detailed_wind_var.set(f"{self.current_weather.vitesse_vent:.0f} km/h ({wind_status.title()})")
        self.detailed_pressure_var.set(f"{self.current_weather.pression:.1f} hPa")
        self.detailed_visibility_var.set(f"{self.current_weather.visibilite:.1f} km")
        self.detailed_condition_var.set(self.current_weather.intemperie.obtenir_nom_affichage())
        
        # Impact sur les vols
        self.update_weather_impact()
    
    def update_weather_impact(self):
        """Met à jour l'impact météo sur les vols"""
        self.weather_impact_text.delete("1.0", tk.END)
        
        # Analyser les conditions
        rapport = self.current_weather.obtenir_rapport_complet()
        
        # Titre
        self.weather_impact_text.insert(tk.END, "📊 RAPPORT MÉTÉO\n", "header")
        self.weather_impact_text.insert(tk.END, "=" * 30 + "\n\n")
        
        # Niveau de risque
        niveau_risque = rapport['niveau_risque']
        risk_colors = {
            'faible': '🟢 FAIBLE',
            'modere': '🟡 MODÉRÉ', 
            'eleve': '🔴 ÉLEVÉ'
        }
        self.weather_impact_text.insert(tk.END, f"⚠️ Niveau de risque: {risk_colors.get(niveau_risque, niveau_risque.upper())}\n\n")
        
        # Recommandations
        self.weather_impact_text.insert(tk.END, "📋 Recommandations:\n")
        self.weather_impact_text.insert(tk.END, f"• {rapport['recommandation_vent']}\n")
        self.weather_impact_text.insert(tk.END, f"• {rapport['recommandation_visibilite']}\n")
        self.weather_impact_text.insert(tk.END, f"• {rapport['recommandation_generale']}\n\n")
        
        # Types de vols possibles
        self.weather_impact_text.insert(tk.END, "✈️ Vols autorisés:\n")
        if rapport['vol_vfr_possible']:
            self.weather_impact_text.insert(tk.END, "• 🟢 Vols VFR: AUTORISÉS\n")
        else:
            self.weather_impact_text.insert(tk.END, "• 🔴 Vols VFR: INTERDITS\n")
            
        if rapport['vol_ifr_possible']:
            self.weather_impact_text.insert(tk.END, "• 🟢 Vols IFR: AUTORISÉS\n")
        else:
            self.weather_impact_text.insert(tk.END, "• 🔴 Vols IFR: INTERDITS\n")
        
        # Configuration des tags pour les couleurs
        self.weather_impact_text.tag_config("header", font=('Arial', 10, 'bold'))
    
    def load_initial_data(self):
        """Charge toutes les données initiales du dashboard"""
        try:
            #self.refresh_kpi_data()
            self.refresh_flights_data()
            self.refresh_fleet_data()
            self.refresh_checkin_data()
            print("✅ Données initiales du dashboard chargées")
        except Exception as e:
            print(f"❌ Erreur chargement données dashboard: {e}")
            self.log_activity("ERROR", f"Erreur chargement données: {e}")
    
    def refresh_kpi_data(self):
        """Met à jour tous les indicateurs KPI"""
        try:
            stats = self.data_manager.get_statistics()
            
            # Calculs des KPI
            total_flights = stats.get('total_flights', 0)
            flights_in_progress = stats.get('flight_statuses', {}).get('en_vol', 0)
            delayed_flights = stats.get('flight_statuses', {}).get('retarde', 0)
            total_passengers = stats.get('total_passengers', 0)
            operational_aircraft = stats.get('aircraft_states', {}).get('operationnel', 0)
            total_personnel = stats.get('total_personnel', 0)
            
            # Calcul du taux de ponctualité
            if total_flights > 0:
                punctuality_rate = ((total_flights - delayed_flights) / total_flights) * 100
            else:
                punctuality_rate = 100
            
            # Check-ins ouverts (vols dans les 24h)
            checkins_open = self.count_open_checkins()
            
            # Mise à jour des KPI avec animations
            kpi_updates = {
                "Vols Aujourd'hui": str(total_flights),
                "Vols en Cours": str(flights_in_progress),
                "Vols Retardés": str(delayed_flights),
                "Taux Ponctualité": f"{punctuality_rate:.1f}%",
                "Avions Actifs": str(operational_aircraft),
                "Personnel Dispo.": str(total_personnel),
                "Check-ins Ouverts": str(checkins_open),
                "Passagers Total": str(total_passengers)
            }
            
            # Application des mises à jour avec tendances simulées
            for kpi_name, value in kpi_updates.items():
                if kpi_name in self.stat_vars:
                    # Mise à jour de la valeur
                    self.stat_vars[kpi_name]['value'].set(value)
                    
                    # Calcul de tendance simulée
                    trend_direction = random.choice(["+", "-"])
                    trend_value = random.randint(0, 15)
                    trend_icon = "📈" if trend_direction == "+" else "📉"
                    self.stat_vars[kpi_name]['trend'].set(f"{trend_icon} {trend_direction}{trend_value}%")
                    
                    # Mise à jour de la barre de progression
                    progress_value = min(100, float(value.replace('%', '').replace('str', '0')) if value != 'str' else random.randint(40, 95))
                    self.stat_vars[kpi_name]['progress'].set(progress_value)
                    
        except Exception as e:
            print(f"❌ Erreur mise à jour KPI: {e}")
            self.log_activity("ERROR", f"Erreur KPI: {e}")
    
    def count_open_checkins(self):
        """Compte les check-ins actuellement ouverts"""
        try:
            flights = self.data_manager.get_flights()
            now = datetime.now()
            open_count = 0
            
            for flight in flights:
                if flight.get('statut') not in ['programme', 'en_attente', 'retarde']:
                    continue
                    
                try:
                    if isinstance(flight.get('heure_depart'), str):
                        depart_time = datetime.fromisoformat(flight['heure_depart'])
                    else:
                        depart_time = flight.get('heure_depart')
                    
                    if not depart_time:
                        continue
                    
                    time_to_departure = depart_time - now
                    
                    # Check-in ouvert si entre 24h et 30min avant départ
                    if timedelta(minutes=30) <= time_to_departure <= timedelta(hours=24):
                        open_count += 1
                        
                except:
                    continue
            
            return open_count
            
        except Exception as e:
            print(f"❌ Erreur comptage check-ins: {e}")
            return 0
    
    def refresh_flights_data(self):
        """Met à jour les données des vols en cours et prochains départs"""
        try:
            # Vider les tableaux
            for item in self.current_flights_tree.get_children():
                self.current_flights_tree.delete(item)
            for item in self.departures_tree.get_children():
                self.departures_tree.delete(item)
            
            flights = self.data_manager.get_flights()
            airports = {a['code_iata']: a['ville'] for a in self.data_manager.get_airports()}
            now = datetime.now()
            
            current_flights = []
            upcoming_departures = []
            
            for flight in flights:
                try:
                    # Parser les heures
                    if isinstance(flight.get('heure_depart'), str):
                        departure_time = datetime.fromisoformat(flight['heure_depart'])
                    else:
                        departure_time = flight.get('heure_depart')
                    
                    if isinstance(flight.get('heure_arrivee_prevue'), str):
                        arrival_time = datetime.fromisoformat(flight['heure_arrivee_prevue'])
                    else:
                        arrival_time = flight.get('heure_arrivee_prevue')
                    
                    status = flight.get('statut', 'programme')
                    
                    # Vols en cours
                    if status == 'en_vol':
                        # Calculer la progression
                        total_duration = (arrival_time - departure_time).total_seconds()
                        elapsed = (now - departure_time).total_seconds()
                        progression = min(100, max(0, (elapsed / total_duration) * 100))
                        
                        eta = arrival_time.strftime('%H:%M')
                        route = f"{flight.get('aeroport_depart', '')} → {flight.get('aeroport_arrivee', '')}"
                        
                        current_flights.append((
                            flight.get('numero_vol', ''),
                            route,
                            f"{progression:.0f}%",
                            eta
                        ))
                    
                    # Prochains départs (6 heures)
                    elif status in ['programme', 'en_attente', 'retarde'] and departure_time:
                        time_to_departure = departure_time - now
                        if timedelta(0) <= time_to_departure <= timedelta(hours=6):
                            
                            # Déterminer si check-in est ouvert
                            checkin_status = "🔴 Fermé"
                            if timedelta(minutes=30) <= time_to_departure <= timedelta(hours=24):
                                checkin_status = "🟢 Ouvert"
                            elif time_to_departure > timedelta(hours=24):
                                checkin_status = "🟡 Pas encore"
                            
                            # Icônes de statut
                            status_icons = {
                                'programme': '🟢 À l\'heure',
                                'en_attente': '🟡 Embarquement', 
                                'retarde': '🔴 Retardé'
                            }
                            
                            destination = airports.get(flight.get('aeroport_arrivee', ''), flight.get('aeroport_arrivee', ''))
                            porte = f"A{random.randint(1, 50)}"  # Simulé
                            
                            upcoming_departures.append((
                                departure_time,
                                flight.get('numero_vol', ''),
                                destination,
                                departure_time.strftime('%H:%M'),
                                porte,
                                status_icons.get(status, status),
                                checkin_status
                            ))
                            
                except Exception as e:
                    continue
            
            # Trier et afficher les vols en cours
            for vol, route, prog, eta in current_flights[:10]:
                self.current_flights_tree.insert('', 'end', values=(vol, route, prog, eta))
            
            # Trier et afficher les prochains départs
            upcoming_departures.sort(key=lambda x: x[0])
            for _, vol, dest, heure, porte, statut, checkin in upcoming_departures[:15]:
                self.departures_tree.insert('', 'end', values=(vol, dest, heure, porte, statut, checkin))
                
        except Exception as e:
            print(f"❌ Erreur mise à jour vols: {e}")
            self.log_activity("ERROR", f"Erreur vols: {e}")
    
    def refresh_fleet_data(self):
        """Met à jour les données de la flotte"""
        try:
            # Vider les zones de texte
            self.available_aircraft_text.delete("1.0", tk.END)
            self.flying_aircraft_text.delete("1.0", tk.END)
            self.maintenance_aircraft_text.delete("1.0", tk.END)
            self.maintenance_text.delete("1.0", tk.END)
            
            aircraft_list = self.data_manager.get_aircraft()
            flights = self.data_manager.get_flights()
            
            # Créer un mapping des vols en cours
            aircraft_in_flight = {}
            for flight in flights:
                if flight.get('statut') == 'en_vol':
                    aircraft_id = flight.get('avion_utilise')
                    if aircraft_id:
                        aircraft_in_flight[aircraft_id] = flight
            
            # Catégoriser les avions
            available_count = 0
            flying_count = 0
            maintenance_count = 0
            
            for aircraft in aircraft_list:
                aircraft_id = aircraft.get('num_id', '')
                model = aircraft.get('modele', '')
                state = aircraft.get('etat', 'au_sol')
                
                display_line = f"{aircraft_id} - {model}\n"
                
                if state == 'operationnel' or state == 'au_sol':
                    if aircraft_id not in aircraft_in_flight:
                        self.available_aircraft_text.insert(tk.END, f"🟢 {display_line}")
                        available_count += 1
                    else:
                        # En vol
                        flight = aircraft_in_flight[aircraft_id]
                        route = f"{flight.get('aeroport_depart', '')} → {flight.get('aeroport_arrivee', '')}"
                        self.flying_aircraft_text.insert(tk.END, f"✈️ {aircraft_id} - {model}\n   📍 {route}\n\n")
                        flying_count += 1
                        
                elif state == 'en_maintenance':
                    self.maintenance_aircraft_text.insert(tk.END, f"🔧 {display_line}")
                    maintenance_count += 1
                    
                    # Ajouter au texte de maintenance générale
                    maintenance_type = random.choice(["Révision moteur", "Contrôle hydraulique", "Inspection cabine", "Maintenance préventive"])
                    self.maintenance_text.insert(tk.END, f"🔧 {aircraft_id}: {maintenance_type}\n")
            
            # Ajouter des résumés
            if available_count == 0:
                self.available_aircraft_text.insert(tk.END, "Aucun avion disponible")
            
            if flying_count == 0:
                self.flying_aircraft_text.insert(tk.END, "Aucun vol en cours")
                
            if maintenance_count == 0:
                self.maintenance_aircraft_text.insert(tk.END, "Aucune maintenance")
                self.maintenance_text.insert(tk.END, "🟢 Aucune maintenance programmée")
                
        except Exception as e:
            print(f"❌ Erreur mise à jour flotte: {e}")
            self.log_activity("ERROR", f"Erreur flotte: {e}")
    
    def refresh_checkin_data(self):
        """Met à jour les données des check-ins"""
        try:
            # Vider les widgets
            for item in self.checkin_tree.get_children():
                self.checkin_tree.delete(item)
            self.closed_checkin_text.delete("1.0", tk.END)
            
            flights = self.data_manager.get_flights()
            now = datetime.now()
            
            open_checkins = []
            recently_closed = []
            
            for flight in flights:
                if flight.get('statut') not in ['programme', 'en_attente', 'retarde']:
                    continue
                    
                try:
                    if isinstance(flight.get('heure_depart'), str):
                        depart_time = datetime.fromisoformat(flight['heure_depart'])
                    else:
                        depart_time = flight.get('heure_depart')
                    
                    if not depart_time:
                        continue
                    
                    time_to_departure = depart_time - now
                    
                    # Check-ins ouverts
                    if timedelta(minutes=30) <= time_to_departure <= timedelta(hours=24):
                        closing_time = depart_time - timedelta(minutes=30)
                        open_checkins.append((
                            flight.get('numero_vol', ''),
                            flight.get('aeroport_arrivee', ''),
                            depart_time.strftime('%H:%M'),
                            closing_time.strftime('%H:%M')
                        ))
                    
                    # Check-ins récemment fermés (dernières 2 heures)
                    elif timedelta(minutes=-120) <= time_to_departure < timedelta(minutes=30):
                        closed_time = depart_time - timedelta(minutes=30)
                        recently_closed.append((
                            closed_time,
                            flight.get('numero_vol', ''),
                            closed_time.strftime('%H:%M')
                        ))
                        
                except:
                    continue
            
            # Afficher check-ins ouverts
            for vol, dest, depart, fermeture in open_checkins[:10]:
                self.checkin_tree.insert('', 'end', values=(vol, dest, depart, fermeture))
            
            # Afficher check-ins récemment fermés
            recently_closed.sort(key=lambda x: x[0], reverse=True)
            for _, vol, closed_time in recently_closed[:8]:
                self.closed_checkin_text.insert(tk.END, f"🔴 {vol} - Fermé à {closed_time}\n")
            
            if not recently_closed:
                self.closed_checkin_text.insert(tk.END, "Aucun check-in récemment fermé")
                
        except Exception as e:
            print(f"❌ Erreur mise à jour check-ins: {e}")
            self.log_activity("ERROR", f"Erreur check-ins: {e}")
    
    def start_auto_refresh(self):
        """Démarre les mises à jour automatiques"""
        self.auto_refresh()
    
    def auto_refresh(self):
        """Actualisation automatique du dashboard"""
        try:
            # Mise à jour des différentes sections
            self.update_header_info()
            #self.refresh_kpi_data()
            self.refresh_flights_data()
            self.refresh_fleet_data()
            self.refresh_checkin_data()
            
            # Ajouter des événements d'activité aléatoires
            if random.random() < 0.2:  # 20% de chance
                self.add_random_activity_event()
                
        except Exception as e:
            print(f"❌ Erreur lors de l'actualisation: {e}")
            self.log_activity("ERROR", f"Erreur actualisation: {e}")
        
        # Programmer la prochaine mise à jour (toutes les 5 secondes)
        self.parent_frame.after(5000, self.auto_refresh)
    
    def add_random_activity_event(self):
        """Ajoute un événement d'activité aléatoire"""
        activities = [
            ("INFO", "🔄 Synchronisation des données en cours..."),
            ("SUCCESS", "✅ Rapport de sécurité généré"),
            ("INFO", "📊 Mise à jour des statistiques"),
            ("SYSTEM", "💾 Sauvegarde automatique effectuée"),
            ("INFO", "🌡️ Données météo actualisées"),
            ("SUCCESS", "🎯 Optimisation des créneaux terminée"),
            ("INFO", "📱 Notification envoyée aux passagers"),
            ("SYSTEM", "🔍 Vérification des systèmes OK"),
            ("SUCCESS", "📈 Rapport de performance généré"),
            ("INFO", "🔧 Maintenance préventive planifiée"),
        ]
        
        level, message = random.choice(activities)
        self.log_activity(level, message)


    def create_dashboard_tab_content(parent_frame, data_manager, simulation_engine=None):
        """
        Point d'entrée principal pour créer le contenu de l'onglet dashboard.
        
        Args:
            parent_frame: Frame parent Tkinter
            data_manager: Instance du gestionnaire de données
            simulation_engine: Instance du moteur de simulation (optionnel)
        
        Returns:
            ModernDashboard: Instance du dashboard créé
        """
        try:
            dashboard = ModernDashboard(parent_frame, data_manager, simulation_engine)
            print("✅ Dashboard moderne créé avec succès")
            return dashboard
        except Exception as e:
            print(f"❌ Erreur création Dashboard: {e}")
            # Fallback en cas d'erreur
            error_label = ttk.Label(parent_frame, 
                                text=f"❌ Erreur de chargement du dashboard:\n{str(e)}", 
                                font=('Arial', 12), 
                                foreground='red',
                                justify='center')
            error_label.pack(expand=True)
            return None


    # Fonction d'intégration dans l'interface principale
    def integrate_dashboard_in_main_window(main_window):
        """
        Intègre le dashboard moderne dans la fenêtre principale.
        
        Args:
            main_window: Instance de MainWindow
        """
        try:
            # Remplacer le contenu de l'onglet dashboard existant
            if hasattr(main_window, 'dashboard_frame'):
                # Nettoyer l'ancien contenu
                for widget in main_window.dashboard_frame.winfo_children():
                    widget.destroy()
                
                # Créer le nouveau dashboard
                dashboard = create_dashboard_tab_content(
                    main_window.dashboard_frame, 
                    main_window.data_manager,
                    main_window.simulation_engine if hasattr(main_window, 'simulation_engine') else None
                )
                
                # Stocker la référence pour les mises à jour
                main_window.dashboard_instance = dashboard
                
                print("✅ Dashboard moderne intégré dans MainWindow")
                return dashboard
            else:
                print("❌ Aucun dashboard_frame trouvé dans MainWindow")
                return None
                
        except Exception as e:
            print(f"❌ Erreur intégration dashboard: {e}")
            return None
  