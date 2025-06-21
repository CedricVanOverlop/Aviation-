"""
Dashboard Tab - Tableau de bord avancé
Fichier: src/interfaces/tabs/dashboard_tab.py

Ce module crée un tableau de bord moderne et interactif pour l'application
de gestion aéroportuaire avec des visualisations temps réel.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime, timedelta
import math
import random

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class DashboardTab:
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
        self.charts = {}
        
        # Configuration des couleurs du thème
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'info': '#17A2B8',
            'light': '#F8F9FA',
            'dark': '#343A40',
            'background': '#FFFFFF',
            'border': '#DEE2E6'
        }
        
        # Configuration du layout
        self.setup_dashboard()
        self.load_initial_data()
        
        # Démarrage des mises à jour automatiques
        self.auto_refresh()
        
        print("✓ Dashboard Tab initialisé avec succès")
    
    def setup_dashboard(self):
        """Configure l'interface complète du dashboard"""
        # Configuration du scrolling pour le dashboard
        self.setup_scrollable_container()
        
        # Création des différentes sections
        self.create_header_section()           # En-tête avec horloge
        self.create_kpi_section()             # Indicateurs clés 
        self.create_charts_section()          # Graphiques et visualisations
        self.create_flights_overview()        # Vue d'ensemble des vols
        self.create_fleet_status()            # État de la flotte
        self.create_alerts_section()          # Alertes et notifications
        self.create_realtime_activity()       # Activité temps réel
    
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
        """Crée la section d'en-tête avec titre et informations système"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Titre principal avec icône
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky="w")
        
        title_label = ttk.Label(title_frame, 
                               text="🏢 Tableau de Bord Aéroportuaire",
                               font=('Arial', 24, 'bold'),
                               foreground=self.colors['primary'])
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame,
                                  text="Vue d'ensemble temps réel des opérations",
                                  font=('Arial', 12),
                                  foreground=self.colors['dark'])
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Section informations système (droite)
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=1, sticky="e")
        
        # Horloge système
        self.system_clock_var = tk.StringVar()
        clock_label = ttk.Label(info_frame, textvariable=self.system_clock_var,
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        clock_label.grid(row=0, column=0, sticky="e")
        
        # Statut simulation
        self.sim_status_var = tk.StringVar()
        sim_label = ttk.Label(info_frame, textvariable=self.sim_status_var,
                             font=('Arial', 10),
                             foreground=self.colors['info'])
        sim_label.grid(row=1, column=0, sticky="e")
        
        # Indicateur de connexion
        self.connection_var = tk.StringVar(value="🟢 Système opérationnel")
        conn_label = ttk.Label(info_frame, textvariable=self.connection_var,
                              font=('Arial', 9),
                              foreground=self.colors['success'])
        conn_label.grid(row=2, column=0, sticky="e")
        
        # Configuration responsive
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Mise à jour initiale
        self.update_header_info()
    
    def create_kpi_section(self):
        """Crée la section des indicateurs de performance clés"""
        kpi_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Indicateurs de Performance", padding=20)
        kpi_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Définition des KPI principaux
        kpis = [
            # Première ligne - Opérations de vol
            ("Vols Aujourd'hui", "0", "🛫", "primary", "Nombre total de vols programmés", 0, 0),
            ("Vols en Cours", "0", "✈️", "success", "Vols actuellement en l'air", 0, 1),
            ("Vols Retardés", "0", "⏰", "warning", "Vols avec retard signalé", 0, 2),
            ("Taux Ponctualité", "0%", "🎯", "info", "Pourcentage de vols à l'heure", 0, 3),
            
            # Deuxième ligne - Ressources
            ("Avions Actifs", "0", "🛩️", "secondary", "Avions en service", 1, 0),
            ("Personnel Dispo.", "0", "👨‍✈️", "primary", "Personnel disponible", 1, 1),
            ("Passagers Total", "0", "👥", "info", "Passagers enregistrés aujourd'hui", 1, 2),
            ("Taux Occupation", "0%", "📈", "success", "Taux d'occupation moyen", 1, 3),
        ]
        
        # Création des cartes KPI
        for title, value, icon, color, tooltip, row, col in kpis:
            self.create_kpi_card(kpi_frame, title, value, icon, color, tooltip, row, col)
        
        # Configuration responsive
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
    
    def create_kpi_card(self, parent, title, value, icon, color, tooltip, row, col):
        """Crée une carte KPI individuelle avec design moderne"""
        # Frame principale de la carte
        card_frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=15)
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
        
        # En-tête avec icône et titre
        header_frame = ttk.Frame(card_frame)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Icône grande
        icon_label = ttk.Label(header_frame, text=icon, font=('Arial', 24))
        icon_label.grid(row=0, column=0, rowspan=2, sticky="w")
        
        # Titre
        title_label = ttk.Label(header_frame, text=title, 
                               font=('Arial', 11, 'bold'),
                               foreground=self.colors['dark'])
        title_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Sous-titre/description
        desc_label = ttk.Label(header_frame, text=tooltip,
                              font=('Arial', 8),
                              foreground="gray")
        desc_label.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Valeur principale (grande)
        value_var = tk.StringVar(value=value)
        value_label = ttk.Label(card_frame, textvariable=value_var,
                               font=('Arial', 20, 'bold'),
                               foreground=self.colors.get(color, self.colors['primary']))
        value_label.grid(row=1, column=0, pady=(10, 5))
        
        # Indicateur de tendance (simulé)
        trend_var = tk.StringVar(value="📈 +0%")
        trend_label = ttk.Label(card_frame, textvariable=trend_var,
                               font=('Arial', 9),
                               foreground=self.colors['success'])
        trend_label.grid(row=2, column=0)
        
        # Configuration
        card_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Stockage des variables pour mises à jour
        self.stat_vars[title] = {
            'value': value_var,
            'trend': trend_var
        }
        
        # Tooltip (effet survol simulé)
        self.create_tooltip(card_frame, tooltip)
        
        return card_frame
    
    def create_tooltip(self, widget, text):
        """Crée un effet tooltip pour les widgets"""
        def on_enter(event):
            widget.configure(relief="raised")
        
        def on_leave(event):
            widget.configure(relief="solid")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_charts_section(self):
        """Crée la section des graphiques et visualisations"""
        charts_frame = ttk.LabelFrame(self.scrollable_frame, text="📈 Analyses Visuelles", padding=20)
        charts_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Container principal pour 2 graphiques côte à côte
        charts_container = ttk.Frame(charts_frame)
        charts_container.grid(row=0, column=0, sticky="ew")
        
        # Graphique 1: Répartition des vols par statut
        self.create_flight_status_chart(charts_container, 0, 0)
        
        # Graphique 2: Activité horaire des vols
        self.create_hourly_activity_chart(charts_container, 0, 1)
        
        # Configuration responsive
        charts_container.grid_columnconfigure((0, 1), weight=1)
        charts_frame.grid_columnconfigure(0, weight=1)
    
    def create_flight_status_chart(self, parent, row, col):
        """Crée un graphique camembert pour les statuts de vols"""
        chart_frame = ttk.LabelFrame(parent, text="📊 Répartition des Vols", padding=15)
        chart_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        
        # Canvas pour le graphique
        canvas = tk.Canvas(chart_frame, width=280, height=220, bg='white', relief="sunken", bd=1)
        canvas.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Données initiales (seront mises à jour)
        self.flight_status_data = {
            'Programmé': 12,
            'En vol': 5,
            'Atterri': 18,
            'Retardé': 2,
            'Annulé': 1
        }
        
        # Dessiner le graphique
        self.draw_pie_chart(canvas, self.flight_status_data)
        
        # Légende colorée
        self.create_chart_legend(chart_frame, self.flight_status_data)
        
        # Stockage pour mises à jour
        self.charts['flight_status'] = canvas
    
    def create_hourly_activity_chart(self, parent, row, col):
        """Crée un graphique en barres de l'activité horaire"""
        chart_frame = ttk.LabelFrame(parent, text="⏰ Activité par Heure", padding=15)
        chart_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        
        # Canvas pour le graphique
        canvas = tk.Canvas(chart_frame, width=280, height=220, bg='white', relief="sunken", bd=1)
        canvas.grid(row=0, column=0, pady=10)
        
        # Données exemple (24 heures)
        self.hourly_data = [
            1, 0, 0, 0, 1, 2, 6, 8, 12, 15, 18, 22, 
            25, 28, 24, 20, 18, 15, 12, 8, 5, 3, 2, 1
        ]
        
        # Dessiner le graphique
        self.draw_bar_chart(canvas, self.hourly_data)
        
        # Informations supplémentaires
        info_frame = ttk.Frame(chart_frame)
        info_frame.grid(row=1, column=0, pady=5)
        
        ttk.Label(info_frame, text="🕐 Heure de pointe: 13h-14h", 
                 font=('Arial', 9), foreground=self.colors['info']).pack()
        ttk.Label(info_frame, text="📊 Moyenne: 11.2 vols/heure", 
                 font=('Arial', 9), foreground=self.colors['dark']).pack()
        
        # Stockage pour mises à jour
        self.charts['hourly_activity'] = canvas
    
    def draw_pie_chart(self, canvas, data):
        """Dessine un graphique camembert amélioré"""
        canvas.delete("all")
        
        total = sum(data.values())
        if total == 0:
            canvas.create_text(140, 110, text="Aucune donnée\ndisponible", 
                             font=('Arial', 12), justify=tk.CENTER, fill='gray')
            return
        
        # Configuration du cercle
        center_x, center_y = 140, 110
        radius = 80
        x1, y1 = center_x - radius, center_y - radius
        x2, y2 = center_x + radius, center_y + radius
        
        # Couleurs pour chaque section
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40', '#C9CBCF', '#4BC0C0']
        
        start_angle = 0
        for i, (label, value) in enumerate(data.items()):
            if value == 0:
                continue
                
            extent = (value / total) * 360
            color = colors[i % len(colors)]
            
            # Dessiner la section
            canvas.create_arc(x1, y1, x2, y2, start=start_angle, extent=extent,
                            fill=color, outline='white', width=3, style='pieslice')
            
            # Ajouter le pourcentage au centre de la section
            if extent > 20:  # Seulement si la section est assez grande
                mid_angle = start_angle + extent / 2
                angle_rad = math.radians(mid_angle)
                label_x = center_x + (radius * 0.7) * math.cos(angle_rad)
                label_y = center_y + (radius * 0.7) * math.sin(angle_rad)
                
                percentage = (value / total) * 100
                canvas.create_text(label_x, label_y, text=f"{percentage:.1f}%",
                                 font=('Arial', 9, 'bold'), fill='white')
            
            start_angle += extent
    
    def draw_bar_chart(self, canvas, data):
        """Dessine un graphique en barres amélioré"""
        canvas.delete("all")
        
        if not data or max(data) == 0:
            canvas.create_text(140, 110, text="Aucune donnée\ndisponible",
                             font=('Arial', 12), justify=tk.CENTER, fill='gray')
            return
        
        # Dimensions et marges
        width, height = 280, 220
        margin_left, margin_right = 40, 20
        margin_top, margin_bottom = 20, 40
        
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        
        # Axes
        canvas.create_line(margin_left, height - margin_bottom, 
                          width - margin_right, height - margin_bottom, 
                          width=2, fill=self.colors['dark'])  # Axe X
        canvas.create_line(margin_left, margin_top, 
                          margin_left, height - margin_bottom, 
                          width=2, fill=self.colors['dark'])  # Axe Y
        
        # Barres
        bar_width = chart_width / len(data)
        max_value = max(data)
        
        for i, value in enumerate(data):
            if value == 0:
                continue
                
            x1 = margin_left + i * bar_width + 2
            x2 = margin_left + (i + 1) * bar_width - 2
            y1 = height - margin_bottom
            y2 = height - margin_bottom - (value / max_value) * chart_height
            
            # Couleur selon l'heure (pointe, normal, nuit)
            if 7 <= i <= 9 or 17 <= i <= 19:  # Heures de pointe
                color = self.colors['danger']
            elif 22 <= i or i <= 5:  # Nuit
                color = self.colors['info']
            else:
                color = self.colors['primary']
            
            # Dessiner la barre avec dégradé simulé
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='white', width=1)
            
            # Valeur au-dessus de la barre si assez haute
            if value > max_value * 0.1:
                canvas.create_text((x1 + x2) / 2, y2 - 5, text=str(value),
                                 font=('Arial', 8), fill=self.colors['dark'])
            
            # Étiquettes des heures (toutes les 4h)
            if i % 4 == 0:
                canvas.create_text(margin_left + i * bar_width + bar_width/2,
                                 height - margin_bottom + 15, text=f"{i}h",
                                 font=('Arial', 8), fill=self.colors['dark'])
        
        # Étiquettes des axes
        canvas.create_text(width/2, height - 10, text="Heures", 
                         font=('Arial', 10, 'bold'), fill=self.colors['dark'])
        canvas.create_text(15, height/2, text="Vols", angle=90,
                         font=('Arial', 10, 'bold'), fill=self.colors['dark'])
    
    def create_chart_legend(self, parent, data):
        """Crée une légende pour le graphique camembert"""
        legend_frame = ttk.Frame(parent)
        legend_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40', '#C9CBCF']
        
        col = 0
        for i, (status, count) in enumerate(data.items()):
            # Carré de couleur
            color_label = tk.Label(legend_frame, text="■", font=('Arial', 14),
                                 fg=colors[i % len(colors)], bg='white')
            color_label.grid(row=i//2, column=col, sticky="w", padx=5)
            
            # Texte descriptif
            text_label = ttk.Label(legend_frame, text=f"{status}: {count}",
                                  font=('Arial', 9))
            text_label.grid(row=i//2, column=col+1, sticky="w", padx=(2, 15))
            
            col += 2
            if col >= 4:  # 2 colonnes maximum
                col = 0
    
    def create_flights_overview(self):
        """Crée la vue d'ensemble des vols"""
        flights_frame = ttk.LabelFrame(self.scrollable_frame, text="✈️ Aperçu des Vols", padding=20)
        flights_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Container pour les deux tableaux
        tables_container = ttk.Frame(flights_frame)
        tables_container.grid(row=0, column=0, sticky="ew")
        
        # Tableau des prochains départs
        self.create_departures_table(tables_container, 0, 0)
        
        # Tableau des arrivées récentes
        self.create_arrivals_table(tables_container, 0, 1)
        
        # Configuration
        tables_container.grid_columnconfigure((0, 1), weight=1)
        flights_frame.grid_columnconfigure(0, weight=1)
    
    def create_departures_table(self, parent, row, col):
        """Crée le tableau des prochains départs"""
        dep_frame = ttk.LabelFrame(parent, text="🛫 Prochains Départs", padding=10)
        dep_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        
        # Configuration du tableau
        columns = ('Vol', 'Destination', 'Heure', 'Statut')
        self.departures_tree = ttk.Treeview(dep_frame, columns=columns, 
                                          show='headings', height=8)
        
        # Configuration des colonnes
        column_widths = {'Vol': 60, 'Destination': 80, 'Heure': 60, 'Statut': 90}
        for col_name in columns:
            self.departures_tree.heading(col_name, text=col_name)
            self.departures_tree.column(col_name, width=column_widths[col_name], anchor="center")
        
        self.departures_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar
        dep_scrollbar = ttk.Scrollbar(dep_frame, orient="vertical", 
                                     command=self.departures_tree.yview)
        dep_scrollbar.grid(row=0, column=1, sticky="ns")
        self.departures_tree.configure(yscrollcommand=dep_scrollbar.set)
        
        dep_frame.grid_columnconfigure(0, weight=1)
    
    def create_arrivals_table(self, parent, row, col):
        """Crée le tableau des arrivées récentes"""
        arr_frame = ttk.LabelFrame(parent, text="🛬 Arrivées Récentes", padding=10)
        arr_frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        
        # Configuration du tableau
        columns = ('Vol', 'Origine', 'Heure', 'Statut')
        self.arrivals_tree = ttk.Treeview(arr_frame, columns=columns, 
                                        show='headings', height=8)
        
        # Configuration des colonnes
        column_widths = {'Vol': 60, 'Origine': 80, 'Heure': 60, 'Statut': 90}
        for col_name in columns:
            self.arrivals_tree.heading(col_name, text=col_name)
            self.arrivals_tree.column(col_name, width=column_widths[col_name], anchor="center")
        
        self.arrivals_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar
        arr_scrollbar = ttk.Scrollbar(arr_frame, orient="vertical", 
                                     command=self.arrivals_tree.yview)
        arr_scrollbar.grid(row=0, column=1, sticky="ns")
        self.arrivals_tree.configure(yscrollcommand=arr_scrollbar.set)
        
        arr_frame.grid_columnconfigure(0, weight=1)
    
    def create_fleet_status(self):
        """Crée la section d'état de la flotte"""
        fleet_frame = ttk.LabelFrame(self.scrollable_frame, text="🛩️ État de la Flotte", padding=20)
        fleet_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        
        # Tableau de la flotte
        columns = ('Avion', 'Type', 'Statut', 'Localisation', 'Prochaine Mission')
        self.fleet_tree = ttk.Treeview(fleet_frame, columns=columns, show='headings', height=6)
        
        # Configuration des colonnes
        column_widths = {
            'Avion': 100, 'Type': 120, 'Statut': 100, 
            'Localisation': 120, 'Prochaine Mission': 150
        }
        for col in columns:
            self.fleet_tree.heading(col, text=col)
            self.fleet_tree.column(col, width=column_widths[col])
        
        self.fleet_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar
        fleet_scrollbar = ttk.Scrollbar(fleet_frame, orient="vertical", command=self.fleet_tree.yview)
        fleet_scrollbar.grid(row=0, column=1, sticky="ns")
        self.fleet_tree.configure(yscrollcommand=fleet_scrollbar.set)
        
        fleet_frame.grid_columnconfigure(0, weight=1)
    
    def create_alerts_section(self):
        """Crée la section des alertes et notifications"""
        alerts_frame = ttk.LabelFrame(self.scrollable_frame, text="🚨 Alertes et Notifications", padding=20)
        alerts_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        
        # Container pour les alertes avec scroll
        alerts_container = ttk.Frame(alerts_frame)
        alerts_container.grid(row=0, column=0, sticky="ew")
        
        # Types d'alertes avec exemples
        alert_items = [
            ("🔴", "CRITIQUE", "Vol AF001 - Retard technique de 45 minutes", "danger"),
            ("🟡", "ATTENTION", "Conditions météo dégradées prévues à 15h30", "warning"),  
            ("🔵", "INFO", "Maintenance programmée Piste 2 - 22h à 02h", "info"),
            ("🟢", "SUCCÈS", "Nouvel avion ajouté à la flotte - A320 Neo", "success"),
        ]
        
        for i, (icon, level, message, alert_type) in enumerate(alert_items):
            self.create_alert_item(alerts_container, icon, level, message, alert_type, i)
        
        alerts_frame.grid_columnconfigure(0, weight=1)
    
    def create_alert_item(self, parent, icon, level, message, alert_type, row):
        """Crée un élément d'alerte individuel"""
        alert_frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=10)
        alert_frame.grid(row=row, column=0, sticky="ew", pady=3)
        
        # Icône de statut
        icon_label = ttk.Label(alert_frame, text=icon, font=('Arial', 16))
        icon_label.grid(row=0, column=0, padx=(0, 10))
        
        # Niveau d'alerte
        level_label = ttk.Label(alert_frame, text=level, font=('Arial', 10, 'bold'),
                               foreground=self.colors.get(alert_type, self.colors['dark']))
        level_label.grid(row=0, column=1, sticky="w")
        
        # Message principal
        msg_label = ttk.Label(alert_frame, text=message, font=('Arial', 10))
        msg_label.grid(row=0, column=2, sticky="w", padx=(10, 0))
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        time_label = ttk.Label(alert_frame, text=timestamp, font=('Arial', 9), 
                              foreground="gray")
        time_label.grid(row=0, column=3, sticky="e")
        
        # Configuration responsive
        alert_frame.grid_columnconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)
    
    def create_realtime_activity(self):
        """Crée la section d'activité temps réel"""
        activity_frame = ttk.LabelFrame(self.scrollable_frame, text="⚡ Activité Temps Réel", padding=20)
        activity_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        # Zone de texte pour le log d'activité
        self.activity_text = tk.Text(activity_frame, height=10, width=100,
                                   font=('Consolas', 9), bg=self.colors['light'],
                                   relief="sunken", bd=2)
        self.activity_text.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour le log
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical",
                                         command=self.activity_text.yview)
        activity_scrollbar.grid(row=0, column=1, sticky="ns")
        self.activity_text.configure(yscrollcommand=activity_scrollbar.set)
        
        # Configuration des tags de couleur pour les différents niveaux
        self.setup_activity_tags()
        
        # Ajout d'événements d'exemple
        self.add_sample_activity_events()
        
        activity_frame.grid_columnconfigure(0, weight=1)
    
    def setup_activity_tags(self):
        """Configure les tags de couleur pour le log d'activité"""
        self.activity_text.tag_config("INFO", foreground=self.colors['info'])
        self.activity_text.tag_config("SUCCESS", foreground=self.colors['success'])
        self.activity_text.tag_config("WARNING", foreground=self.colors['warning'])
        self.activity_text.tag_config("ERROR", foreground=self.colors['danger'])
        self.activity_text.tag_config("SYSTEM", foreground=self.colors['secondary'])
        self.activity_text.tag_config("timestamp", foreground="gray")
    
    def add_sample_activity_events(self):
        """Ajoute des événements d'exemple au log d'activité"""
        sample_events = [
            ("INFO", "Vol AF123 en approche finale - ETA 5 minutes"),
            ("SUCCESS", "Check-in ouvert pour vol BA456 - Terminal 2A"),
            ("WARNING", "Retard signalé vol LH789 - Problème technique mineur"),
            ("INFO", "Nouveau passager enregistré - Réservation confirmée"),
            ("SYSTEM", "Sauvegarde automatique des données effectuée"),
            ("SUCCESS", "Maintenance préventive terminée - Avion F-ABCD opérationnel"),
            ("INFO", "Mise à jour météo reçue - Conditions normales"),
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
        
        # Limiter le nombre de lignes (garder les 500 dernières)
        lines = self.activity_text.get("1.0", tk.END).split('\n')
        if len(lines) > 500:
            self.activity_text.delete("1.0", f"{len(lines)-500}.0")
    
    def update_header_info(self):
        """Met à jour les informations d'en-tête"""
        # Horloge système
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.system_clock_var.set(current_time)
        
        # Statut de simulation
        if self.simulation_engine:
            try:
                sim_info = self.simulation_engine.get_simulation_info()
                sim_time_str = datetime.fromisoformat(sim_info['simulation_time']).strftime("%H:%M:%S")
                speed = sim_info['speed_value']
                status = "🟢 Actif" if sim_info['is_running'] and not sim_info['is_paused'] else "🟡 Pause"
                self.sim_status_var.set(f"Simulation: {sim_time_str} (x{speed}) {status}")
            except Exception as e:
                self.sim_status_var.set("⚠️ Simulation: Erreur de connexion")
        else:
            self.sim_status_var.set("📴 Simulation: Non disponible")
    
    def load_initial_data(self):
        """Charge toutes les données initiales du dashboard"""
        try:
            self.refresh_kpi_data()
            self.refresh_flights_data()
            self.refresh_fleet_data()
            self.refresh_charts_data()
            print("✓ Données initiales du dashboard chargées")
        except Exception as e:
            print(f"❌ Erreur chargement données dashboard: {e}")
    
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
            
            # Calcul du taux d'occupation (simulé)
            if operational_aircraft > 0:
                occupation_rate = min((flights_in_progress / operational_aircraft) * 100, 100)
            else:
                occupation_rate = 0
            
            # Mise à jour des KPI
            kpi_updates = {
                "Vols Aujourd'hui": str(total_flights),
                "Vols en Cours": str(flights_in_progress),
                "Vols Retardés": str(delayed_flights),
                "Taux Ponctualité": f"{punctuality_rate:.1f}%",
                "Avions Actifs": str(operational_aircraft),
                "Personnel Dispo.": str(total_personnel),
                "Passagers Total": str(total_passengers),
                "Taux Occupation": f"{occupation_rate:.1f}%"
            }
            
            # Application des mises à jour
            for kpi_name, value in kpi_updates.items():
                if kpi_name in self.stat_vars:
                    self.stat_vars[kpi_name]['value'].set(value)
                    
                    # Calcul de tendance simulée
                    trend = random.choice(["+", "-"]) + str(random.randint(0, 15)) + "%"
                    trend_icon = "📈" if trend.startswith("+") else "📉"
                    self.stat_vars[kpi_name]['trend'].set(f"{trend_icon} {trend}")
                    
        except Exception as e:
            print(f"❌ Erreur mise à jour KPI: {e}")
    
    def refresh_flights_data(self):
        """Met à jour les données des tableaux de vols"""
        try:
            # Nettoyer les tableaux
            for item in self.departures_tree.get_children():
                self.departures_tree.delete(item)
            for item in self.arrivals_tree.get_children():
                self.arrivals_tree.delete(item)
            
            flights = self.data_manager.get_flights()
            now = datetime.now()
            
            # Traitement des départs
            departures = []
            arrivals = []
            
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
                    
                    # Statut formaté
                    status_icons = {
                        'programme': '🟢 Programmé',
                        'en_attente': '🟡 En attente',
                        'en_vol': '✈️ En vol',
                        'atterri': '🛬 Atterri',
                        'retarde': '🔴 Retardé',
                        'annule': '❌ Annulé',
                        'termine': '✅ Terminé'
                    }
                    status_display = status_icons.get(flight.get('statut', ''), flight.get('statut', ''))
                    
                    # Trier les départs futurs
                    if departure_time and departure_time > now and flight.get('statut') in ['programme', 'en_attente', 'retarde']:
                        departures.append((
                            departure_time,
                            flight.get('numero_vol', ''),
                            flight.get('aeroport_arrivee', ''),
                            departure_time.strftime('%H:%M'),
                            status_display
                        ))
                    
                    # Trier les arrivées récentes
                    if arrival_time and arrival_time <= now + timedelta(hours=2) and flight.get('statut') in ['atterri', 'termine']:
                        arrivals.append((
                            arrival_time,
                            flight.get('numero_vol', ''),
                            flight.get('aeroport_depart', ''),
                            arrival_time.strftime('%H:%M'),
                            status_display
                        ))
                        
                except Exception as e:
                    continue
            
            # Trier et afficher les départs (10 prochains)
            departures.sort(key=lambda x: x[0])
            for _, vol, dest, heure, status in departures[:10]:
                self.departures_tree.insert('', 'end', values=(vol, dest, heure, status))
            
            # Trier et afficher les arrivées (10 dernières)
            arrivals.sort(key=lambda x: x[0], reverse=True)
            for _, vol, orig, heure, status in arrivals[:10]:
                self.arrivals_tree.insert('', 'end', values=(vol, orig, heure, status))
                
        except Exception as e:
            print(f"❌ Erreur mise à jour vols: {e}")
    
    def refresh_fleet_data(self):
        """Met à jour les données de la flotte"""
        try:
            # Nettoyer le tableau
            for item in self.fleet_tree.get_children():
                self.fleet_tree.delete(item)
            
            aircraft_list = self.data_manager.get_aircraft()
            flights = self.data_manager.get_flights()
            
            # Créer un mapping des vols en cours
            current_flights = {}
            for flight in flights:
                if flight.get('statut') in ['programme', 'en_attente', 'en_vol']:
                    aircraft_id = flight.get('avion_utilise')
                    if aircraft_id:
                        current_flights[aircraft_id] = flight
            
            # Afficher la flotte
            for aircraft in aircraft_list[:15]:  # Limiter à 15 avions
                aircraft_id = aircraft.get('num_id', '')
                model = aircraft.get('modele', '')
                
                # Statut formaté
                status_icons = {
                    'operationnel': '🟢 Opérationnel',
                    'au_sol': '🟡 Au sol',
                    'en_vol': '✈️ En vol',
                    'en_maintenance': '🔧 Maintenance'
                }
                status = status_icons.get(aircraft.get('etat', ''), aircraft.get('etat', ''))
                
                # Localisation (simplifiée)
                location = "Base principale"  # Pourrait être amélioré
                
                # Prochaine mission
                next_mission = "Disponible"
                if aircraft_id in current_flights:
                    flight = current_flights[aircraft_id]
                    dest = flight.get('aeroport_arrivee', '')
                    try:
                        if isinstance(flight.get('heure_depart'), str):
                            dep_time = datetime.fromisoformat(flight['heure_depart'])
                            next_mission = f"{dest} à {dep_time.strftime('%H:%M')}"
                        else:
                            next_mission = f"{dest}"
                    except:
                        next_mission = f"Vol {flight.get('numero_vol', '')}"
                
                values = (aircraft_id, model, status, location, next_mission)
                self.fleet_tree.insert('', 'end', values=values)
                
        except Exception as e:
            print(f"❌ Erreur mise à jour flotte: {e}")
    
    def refresh_charts_data(self):
        """Met à jour les données des graphiques"""
        try:
            flights = self.data_manager.get_flights()
            
            # Compter les vols par statut pour le camembert
            status_counts = {}
            hourly_counts = [0] * 24  # 24 heures
            
            for flight in flights:
                # Statuts pour le camembert
                status = flight.get('statut', 'inconnu')
                status_mapping = {
                    'programme': 'Programmé',
                    'en_attente': 'En attente',
                    'en_vol': 'En vol',
                    'atterri': 'Atterri',
                    'retarde': 'Retardé',
                    'annule': 'Annulé',
                    'termine': 'Terminé'
                }
                display_status = status_mapping.get(status, status.capitalize())
                status_counts[display_status] = status_counts.get(display_status, 0) + 1
                
                # Activité horaire
                try:
                    if isinstance(flight.get('heure_depart'), str):
                        departure_time = datetime.fromisoformat(flight['heure_depart'])
                        hour = departure_time.hour
                        hourly_counts[hour] += 1
                except:
                    continue
            
            # Mettre à jour les graphiques
            if status_counts:
                self.flight_status_data = status_counts
                if 'flight_status' in self.charts:
                    self.draw_pie_chart(self.charts['flight_status'], self.flight_status_data)
            
            if any(hourly_counts):
                self.hourly_data = hourly_counts
                if 'hourly_activity' in self.charts:
                    self.draw_bar_chart(self.charts['hourly_activity'], self.hourly_data)
                    
        except Exception as e:
            print(f"❌ Erreur mise à jour graphiques: {e}")
    
    def auto_refresh(self):
        """Actualisation automatique du dashboard"""
        try:
            # Mise à jour des différentes sections
            self.update_header_info()
            self.refresh_kpi_data()
            self.refresh_flights_data()
            self.refresh_fleet_data()
            self.refresh_charts_data()
            
            # Ajouter des événements d'activité aléatoires
            if random.random() < 0.3:  # 30% de chance
                self.add_random_activity_event()
                
        except Exception as e:
            print(f"❌ Erreur lors de l'actualisation: {e}")
        
        # Programmer la prochaine mise à jour (toutes les 30 secondes)
        self.parent_frame.after(30000, self.auto_refresh)
    
    def add_random_activity_event(self):
        """Ajoute un événement d'activité aléatoire"""
        activities = [
            ("INFO", "Contrôle automatique des systèmes effectué"),
            ("SUCCESS", "Synchronisation des données terminée"),
            ("INFO", "Mise à jour météorologique reçue"),
            ("SYSTEM", "Sauvegarde automatique des données"),
            ("INFO", "Vérification des équipements de sécurité"),
            ("SUCCESS", "Communication établie avec nouvelle tour de contrôle"),
            ("INFO", "Rapport de maintenance automatique généré"),
            ("SYSTEM", "Optimisation des créneaux de vol en cours"),
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
        DashboardTab: Instance du dashboard créé
    """
    try:
        dashboard = DashboardTab(parent_frame, data_manager, simulation_engine)
        print("✓ Dashboard Tab créé avec succès")
        return dashboard
    except Exception as e:
        print(f"❌ Erreur création Dashboard Tab: {e}")
        # Fallback en cas d'erreur
        error_label = ttk.Label(parent_frame, 
                               text=f"❌ Erreur de chargement du dashboard:\n{str(e)}", 
                               font=('Arial', 12), 
                               foreground='red',
                               justify='center')
        error_label.pack(expand=True)
        return None


# Fonction d'intégration dans l'interface principale existante
def integrate_dashboard_in_main_window(main_window):
    """
    Intègre le dashboard avancé dans la fenêtre principale existante.
    
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
            
            print("✓ Dashboard intégré dans MainWindow")
            return dashboard
        else:
            print("❌ Aucun dashboard_frame trouvé dans MainWindow")
            return None
            
    except Exception as e:
        print(f"❌ Erreur intégration dashboard: {e}")
        return None