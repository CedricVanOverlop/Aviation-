"""
Dashboard Tab - Tableau de bord statique
Fichier: src/interfaces/tabs/dashboard_tab.py

Version nettoyée sans simulation temps réel ni threading.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class SimpleDashboard:
    """Tableau de bord principal statique (sans simulation temps réel)"""
    
    def __init__(self, parent_frame, data_manager):
        """
        Initialise le tableau de bord.
        
        Args:
            parent_frame: Frame parent Tkinter
            data_manager: Gestionnaire de données
        """
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        
        # Variables pour les statistiques
        self.stat_vars = {}
        self.widgets = {}
        
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
        
        # Configuration du layout
        self.setup_dashboard()
        self.load_initial_data()
        
        print("✅ Dashboard statique initialisé avec succès")
    
    def setup_dashboard(self):
        """Configure l'interface complète du dashboard"""
        # Configuration du scrolling pour le dashboard
        self.setup_scrollable_container()
        
        # Création des différentes sections
        self.create_header_section()           # En-tête avec informations système
        self.create_kpi_section()             # Indicateurs clés de performance
        self.create_data_overview_section()   # Vue d'ensemble des données
        self.create_fleet_section()           # État de la flotte
        self.create_recent_activity_section() # Activité récente
    
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
                                  text="Vue d'ensemble des opérations",
                                  font=('Arial', 12),
                                  foreground=self.colors['dark'])
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Section droite - Informations système
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=0, column=1, sticky="e")
        
        # Horloge système
        clock_frame = ttk.LabelFrame(right_frame, text="🕐 Informations", padding=10)
        clock_frame.grid(row=0, column=0, padx=(0, 10), sticky="e")
        
        # Horloge système
        self.system_clock_var = tk.StringVar()
        ttk.Label(clock_frame, text="Heure système:").grid(row=0, column=0, sticky="w")
        clock_label = ttk.Label(clock_frame, textvariable=self.system_clock_var,
                               font=('Arial', 12, 'bold'),
                               foreground=self.colors['primary'])
        clock_label.grid(row=0, column=1, sticky="e", padx=(5, 0))
        
        # Type d'interface
        ttk.Label(clock_frame, text="Mode:").grid(row=1, column=0, sticky="w")
        mode_label = ttk.Label(clock_frame, text="Statique",
                              font=('Arial', 12, 'bold'),
                              foreground=self.colors['success'])
        mode_label.grid(row=1, column=1, sticky="e", padx=(5, 0))
        
        # Dernière mise à jour
        self.last_update_var = tk.StringVar()
        ttk.Label(clock_frame, text="Dernière MàJ:").grid(row=2, column=0, sticky="w")
        update_label = ttk.Label(clock_frame, textvariable=self.last_update_var,
                                font=('Arial', 10),
                                foreground=self.colors['info'])
        update_label.grid(row=2, column=1, sticky="e", padx=(5, 0))
        
        # Mettre à jour les informations
        self.update_header_info()

    def create_kpi_section(self):
        """Crée la section des indicateurs de performance clés"""
        kpi_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Indicateurs Clés", padding=20)
        kpi_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration responsive - 4 colonnes
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        # Définition des KPI principaux (statiques)
        kpis = [
            # Première ligne - Données principales
            ("Total Avions", "0", "🛩️", "primary", "Nombre total d'avions enregistrés", 0, 0),
            ("Total Personnel", "0", "👨‍✈️", "secondary", "Personnel enregistré", 0, 1),
            ("Total Vols", "0", "🛫", "info", "Vols programmés", 0, 2),
            ("Total Passagers", "0", "👥", "accent", "Passagers enregistrés", 0, 3),
            
            # Deuxième ligne - Données complémentaires
            ("Réservations", "0", "🎫", "warning", "Réservations actives", 1, 0),
            ("Avions Opérationnels", "0", "✅", "success", "Avions en service", 1, 1),
            ("Personnel Disponible", "0", "🟢", "primary", "Personnel disponible", 1, 2),
            ("État Système", "OK", "💾", "success", "État de la base de données", 1, 3),
        ]
        
        # Création des cartes KPI
        for title, value, icon, color, tooltip, row, col in kpis:
            self.create_kpi_card(kpi_frame, title, value, icon, color, tooltip, row, col)
    
    def create_kpi_card(self, parent, title, value, icon, color, tooltip, row, col):
        """Crée une carte KPI moderne"""
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
        
        # Information supplémentaire
        info_var = tk.StringVar(value="")
        info_label = ttk.Label(card_frame, textvariable=info_var,
                              font=('Arial', 9),
                              foreground=self.colors['secondary'])
        info_label.grid(row=2, column=0)
        
        # Stocker les variables pour mises à jour
        self.stat_vars[title] = {
            'value': value_var,
            'info': info_var
        }
        
        return card_frame
    
    def create_data_overview_section(self):
        """Crée la section de vue d'ensemble des données"""
        overview_frame = ttk.LabelFrame(self.scrollable_frame, text="📋 Vue d'Ensemble", padding=20)
        overview_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Configuration en 2 colonnes
        overview_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Répartition des données
        data_frame = ttk.LabelFrame(overview_frame, text="📊 Répartition", padding=10)
        data_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.data_text = tk.Text(data_frame, height=8, width=40,
                                font=('Arial', 10), bg=self.colors['light'],
                                relief="sunken", bd=1, wrap=tk.WORD)
        self.data_text.pack(fill="both", expand=True)
        
        # État des ressources
        resources_frame = ttk.LabelFrame(overview_frame, text="🔧 Ressources", padding=10)
        resources_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.resources_text = tk.Text(resources_frame, height=8, width=40,
                                     font=('Arial', 10), bg=self.colors['light'],
                                     relief="sunken", bd=1, wrap=tk.WORD)
        self.resources_text.pack(fill="both", expand=True)
        
        # Configuration responsive
        data_frame.grid_columnconfigure(0, weight=1)
        resources_frame.grid_columnconfigure(0, weight=1)
    
    def create_fleet_section(self):
        """Crée la section de l'état de la flotte"""
        fleet_frame = ttk.LabelFrame(self.scrollable_frame, text="🛩️ État de la Flotte", padding=20)
        fleet_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        # Tableau simplifié de la flotte
        columns = ('ID', 'Modèle', 'Compagnie', 'Capacité', 'État', 'Localisation')
        self.fleet_tree = ttk.Treeview(fleet_frame, columns=columns, 
                                      show='headings', height=6)
        
        for col in columns:
            self.fleet_tree.heading(col, text=col)
            self.fleet_tree.column(col, width=120, anchor="center")
        
        self.fleet_tree.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour la flotte
        fleet_scroll = ttk.Scrollbar(fleet_frame, orient="vertical", 
                                    command=self.fleet_tree.yview)
        fleet_scroll.grid(row=0, column=1, sticky="ns")
        self.fleet_tree.configure(yscrollcommand=fleet_scroll.set)
        
        # Configuration responsive
        fleet_frame.grid_columnconfigure(0, weight=1)
    
    def create_recent_activity_section(self):
        """Crée la section d'activité récente"""
        activity_frame = ttk.LabelFrame(self.scrollable_frame, text="📝 Informations Système", padding=20)
        activity_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        # Zone de texte pour les informations
        self.activity_text = tk.Text(activity_frame, height=10, width=100,
                                   font=('Consolas', 9), bg=self.colors['light'],
                                   fg='black', relief="sunken", bd=2, wrap=tk.WORD)
        self.activity_text.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar pour les informations
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient="vertical",
                                         command=self.activity_text.yview)
        activity_scrollbar.grid(row=0, column=1, sticky="ns")
        self.activity_text.configure(yscrollcommand=activity_scrollbar.set)
        
        # Ajout d'informations système
        self.add_system_info()
        
        # Configuration responsive
        activity_frame.grid_columnconfigure(0, weight=1)
    
    def add_system_info(self):
        """Ajoute des informations système"""
        info_text = f"""=== INFORMATIONS SYSTÈME ===

📅 Date de démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Mode de fonctionnement : Interface statique
💾 Base de données : Opérationnelle
🔄 Auto-refresh : Désactivé (mode manuel)

=== ACTIONS DISPONIBLES ===

• Utiliser le bouton "Actualiser" pour mettre à jour les données
• Naviguer entre les onglets pour gérer les différentes entités
• Toutes les modifications sont sauvegardées automatiquement
• Aucun processus de simulation en arrière-plan

=== STATISTIQUES DE SESSION ===

• Interface initialisée avec succès
• Tous les modules chargés correctement
• Pas de threads secondaires actifs
• Mémoire optimisée pour performance stable

=== NOTES IMPORTANTES ===

Cette version de l'interface ne contient pas de simulation temps réel.
Toutes les données affichées correspondent à l'état actuel de la base de données.
Pour voir les mises à jour, utilisez les boutons de rafraîchissement disponibles."""

        self.activity_text.insert(tk.END, info_text)
    
    def update_header_info(self):
        """Met à jour les informations d'en-tête"""
        # Horloge système
        current_time = datetime.now().strftime("%H:%M:%S")
        self.system_clock_var.set(current_time)
        
        # Dernière mise à jour
        last_update = datetime.now().strftime("%H:%M:%S")
        self.last_update_var.set(last_update)
        
        # Programmer la prochaine mise à jour de l'horloge dans 1 seconde
        self.parent_frame.after(1000, self.update_header_info)
    
    def load_initial_data(self):
        """Charge toutes les données initiales du dashboard"""
        try:
            self.refresh_kpi_data()
            self.refresh_data_overview()
            self.refresh_fleet_data()
            print("✅ Données initiales du dashboard chargées")
        except Exception as e:
            print(f"❌ Erreur chargement données dashboard: {e}")
    
    def refresh_kpi_data(self):
        """Met à jour tous les indicateurs KPI"""
        try:
            # Charger les données
            aircraft_list = self.data_manager.get_aircraft()
            personnel_list = self.data_manager.get_personnel()
            flights_list = self.data_manager.get_flights()
            passengers_list = self.data_manager.get_passengers()
            reservations_list = self.data_manager.get_reservations()
            
            # Calculs des KPI
            total_aircraft = len(aircraft_list)
            total_personnel = len(personnel_list)
            total_flights = len(flights_list)
            total_passengers = len(passengers_list)
            total_reservations = len(reservations_list)
            
            # Calculs plus détaillés
            operational_aircraft = sum(1 for a in aircraft_list if a.get('etat') in ['operationnel', 'au_sol'])
            available_personnel = sum(1 for p in personnel_list if p.get('disponible', True))
            active_reservations = sum(1 for r in reservations_list if r.get('statut') == 'active')
            
            # Mise à jour des KPI
            kpi_updates = {
                "Total Avions": (str(total_aircraft), f"En service: {operational_aircraft}"),
                "Total Personnel": (str(total_personnel), f"Disponible: {available_personnel}"),
                "Total Vols": (str(total_flights), "Tous statuts"),
                "Total Passagers": (str(total_passengers), "Enregistrés"),
                "Réservations": (str(active_reservations), f"Total: {total_reservations}"),
                "Avions Opérationnels": (str(operational_aircraft), f"Total: {total_aircraft}"),
                "Personnel Disponible": (str(available_personnel), f"Total: {total_personnel}"),
                "État Système": ("OK", "Base de données active")
            }
            
            # Application des mises à jour
            for kpi_name, (value, info) in kpi_updates.items():
                if kpi_name in self.stat_vars:
                    self.stat_vars[kpi_name]['value'].set(value)
                    self.stat_vars[kpi_name]['info'].set(info)
                    
        except Exception as e:
            print(f"❌ Erreur mise à jour KPI: {e}")
    
    def refresh_data_overview(self):
        """Met à jour la vue d'ensemble des données"""
        try:
            # Vider les zones de texte
            self.data_text.delete("1.0", tk.END)
            self.resources_text.delete("1.0", tk.END)
            
            # Charger les données
            aircraft_list = self.data_manager.get_aircraft()
            personnel_list = self.data_manager.get_personnel()
            flights_list = self.data_manager.get_flights()
            
            # Répartition des données
            data_overview = "=== RÉPARTITION DES DONNÉES ===\n\n"
            
            # Répartition des avions par état
            aircraft_states = {}
            for aircraft in aircraft_list:
                state = aircraft.get('etat', 'inconnu')
                aircraft_states[state] = aircraft_states.get(state, 0) + 1
            
            data_overview += "🛩️ AVIONS PAR ÉTAT :\n"
            for state, count in aircraft_states.items():
                state_display = state.replace('_', ' ').title()
                data_overview += f"• {state_display}: {count}\n"
            
            # Répartition du personnel par type
            personnel_types = {}
            for person in personnel_list:
                ptype = person.get('type_personnel', 'inconnu')
                personnel_types[ptype] = personnel_types.get(ptype, 0) + 1
            
            data_overview += "\n👥 PERSONNEL PAR TYPE :\n"
            for ptype, count in personnel_types.items():
                ptype_display = ptype.replace('_', ' ').title()
                data_overview += f"• {ptype_display}: {count}\n"
            
            # Répartition des vols par statut
            flight_statuses = {}
            for flight in flights_list:
                status = flight.get('statut', 'inconnu')
                flight_statuses[status] = flight_statuses.get(status, 0) + 1
            
            data_overview += "\n🛫 VOLS PAR STATUT :\n"
            for status, count in flight_statuses.items():
                status_display = status.replace('_', ' ').title()
                data_overview += f"• {status_display}: {count}\n"
            
            self.data_text.insert("1.0", data_overview)
            
            # État des ressources
            resources_overview = "=== ÉTAT DES RESSOURCES ===\n\n"
            
            # Capacité totale de transport
            total_capacity = sum(aircraft.get('capacite', 0) for aircraft in aircraft_list)
            operational_capacity = sum(aircraft.get('capacite', 0) for aircraft in aircraft_list 
                                     if aircraft.get('etat') in ['operationnel', 'au_sol'])
            
            resources_overview += "✈️ CAPACITÉ DE TRANSPORT :\n"
            resources_overview += f"• Capacité totale: {total_capacity} passagers\n"
            resources_overview += f"• Capacité opérationnelle: {operational_capacity} passagers\n"
            if total_capacity > 0:
                utilization = (operational_capacity / total_capacity) * 100
                resources_overview += f"• Taux d'utilisation: {utilization:.1f}%\n"
            
            # Autonomie moyenne
            autonomies = [aircraft.get('autonomie', 0) for aircraft in aircraft_list if aircraft.get('autonomie', 0) > 0]
            if autonomies:
                avg_autonomy = sum(autonomies) / len(autonomies)
                max_autonomy = max(autonomies)
                min_autonomy = min(autonomies)
                
                resources_overview += "\n🛣️ AUTONOMIE FLOTTE :\n"
                resources_overview += f"• Autonomie moyenne: {avg_autonomy:.0f} km\n"
                resources_overview += f"• Autonomie maximum: {max_autonomy} km\n"
                resources_overview += f"• Autonomie minimum: {min_autonomy} km\n"
            
            # Personnel par disponibilité
            available_personnel = sum(1 for p in personnel_list if p.get('disponible', True))
            unavailable_personnel = len(personnel_list) - available_personnel
            
            resources_overview += "\n👤 DISPONIBILITÉ PERSONNEL :\n"
            resources_overview += f"• Personnel disponible: {available_personnel}\n"
            resources_overview += f"• Personnel indisponible: {unavailable_personnel}\n"
            if len(personnel_list) > 0:
                availability_rate = (available_personnel / len(personnel_list)) * 100
                resources_overview += f"• Taux de disponibilité: {availability_rate:.1f}%\n"
            
            # Statistiques des réservations
            reservations_list = self.data_manager.get_reservations()
            active_reservations = sum(1 for r in reservations_list if r.get('statut') == 'active')
            
            resources_overview += "\n🎫 RÉSERVATIONS :\n"
            resources_overview += f"• Réservations actives: {active_reservations}\n"
            resources_overview += f"• Total réservations: {len(reservations_list)}\n"
            
            self.resources_text.insert("1.0", resources_overview)
                
        except Exception as e:
            print(f"❌ Erreur mise à jour vue d'ensemble: {e}")
    
    def refresh_fleet_data(self):
        """Met à jour les données de la flotte"""
        try:
            # Vider le tableau
            for item in self.fleet_tree.get_children():
                self.fleet_tree.delete(item)
            
            aircraft_list = self.data_manager.get_aircraft()
            airports = self.data_manager.get_airports()
            
            # Limiter l'affichage aux 10 premiers avions pour le dashboard
            for aircraft in aircraft_list[:10]:
                # Obtenir la localisation
                location = "Base principale"
                if 'localisation' in aircraft:
                    loc_coords = aircraft['localisation']
                    for airport in airports:
                        airport_coords = airport['coordonnees']
                        if (abs(airport_coords['latitude'] - loc_coords.get('latitude', 0)) < 0.1 and
                            abs(airport_coords['longitude'] - loc_coords.get('longitude', 0)) < 0.1):
                            location = f"{airport['ville']} ({airport['code_iata']})"
                            break
                
                values = (
                    aircraft.get('num_id', ''),
                    aircraft.get('modele', ''),
                    aircraft.get('compagnie_aerienne', ''),
                    str(aircraft.get('capacite', '')),
                    aircraft.get('etat', 'au_sol').replace('_', ' ').title(),
                    location
                )
                
                self.fleet_tree.insert('', 'end', values=values)
            
            # Ajouter une ligne d'information si plus de 10 avions
            if len(aircraft_list) > 10:
                remaining = len(aircraft_list) - 10
                self.fleet_tree.insert('', 'end', values=(
                    '...', f'+ {remaining} autres avions', '', '', '', 'Voir onglet Avions'
                ))
                
        except Exception as e:
            print(f"❌ Erreur mise à jour flotte: {e}")
    
    def refresh_all_data(self):
        """Actualise toutes les données du dashboard"""
        try:
            self.refresh_kpi_data()
            self.refresh_data_overview()
            self.refresh_fleet_data()
            
            # Mettre à jour l'heure de dernière mise à jour
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            
            print("✅ Dashboard entièrement actualisé")
            
        except Exception as e:
            print(f"❌ Erreur actualisation dashboard: {e}")


def create_dashboard_tab_content(parent_frame, data_manager):
    """
    Point d'entrée principal pour créer le contenu de l'onglet dashboard.
    
    Args:
        parent_frame: Frame parent Tkinter
        data_manager: Instance du gestionnaire de données
    
    Returns:
        SimpleDashboard: Instance du dashboard créé
    """
    try:
        dashboard = SimpleDashboard(parent_frame, data_manager)
        print("✅ Dashboard statique créé avec succès")
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
    Intègre le dashboard statique dans la fenêtre principale.
    
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
                main_window.data_manager
            )
            
            # Stocker la référence pour les mises à jour
            main_window.dashboard_instance = dashboard
            
            print("✅ Dashboard statique intégré dans MainWindow")
            return dashboard
        else:
            print("❌ Aucun dashboard_frame trouvé dans MainWindow")
            return None
            
    except Exception as e:
        print(f"❌ Erreur intégration dashboard: {e}")
        return None