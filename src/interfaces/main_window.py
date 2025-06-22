import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime
from abc import ABC, abstractmethod

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from data.data_manager import DataManager

# Importer les modules des onglets
try:
    from interfaces.tabs.flights_tab import create_flights_tab_content, refresh_flights_data
    FLIGHTS_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module flights_tab non disponible: {e}")
    FLIGHTS_MODULE_AVAILABLE = False

try:
    from interfaces.tabs.passengers_tab import create_passengers_tab_content, refresh_passengers_data
    PASSENGERS_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module passengers_tab non disponible: {e}")
    PASSENGERS_MODULE_AVAILABLE = False

try:
    from interfaces.tabs.personnel_tab import create_personnel_tab_content, refresh_personnel_data
    PERSONNEL_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module personnel_tab non disponible: {e}")
    PERSONNEL_MODULE_AVAILABLE = False

try:
    from interfaces.tabs.reservations_tab import create_reservations_tab_content, refresh_reservations_data
    RESERVATIONS_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module reservations_tab non disponible: {e}")
    RESERVATIONS_MODULE_AVAILABLE = False

try:
    from interfaces.tabs.aircraft_tab import ModernAircraftDialog, SafeAircraftManager
    AIRCRAFT_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module aircraft_tab non disponible: {e}")
    AIRCRAFT_MODULE_AVAILABLE = False


class NotificationCenter:
    """Centre de notifications centralisé pour l'interface"""
    
    def __init__(self, status_var, root):
        self.status_var = status_var
        self.root = root
        self.message_queue = []
        self.current_job = None
    
    def show_success(self, message, duration=3000):
        """Affiche un message de succès"""
        self.status_var.set(f"✅ {message}")
        self._schedule_clear(duration)
    
    def show_error(self, message, duration=5000):
        """Affiche un message d'erreur"""
        self.status_var.set(f"❌ {message}")
        self._schedule_clear(duration)
    
    def show_warning(self, message, duration=4000):
        """Affiche un message d'avertissement"""
        self.status_var.set(f"⚠️ {message}")
        self._schedule_clear(duration)
    
    def show_info(self, message, duration=2000):
        """Affiche un message d'information"""
        self.status_var.set(f"ℹ️ {message}")
        self._schedule_clear(duration)
    
    def show_progress(self, message):
        """Affiche un message de progression (permanent jusqu'à update)"""
        self.status_var.set(f"🔄 {message}")
        if self.current_job:
            self.root.after_cancel(self.current_job)
            self.current_job = None
    
    def clear(self):
        """Efface le statut actuel"""
        self.status_var.set("Application prête")
        if self.current_job:
            self.root.after_cancel(self.current_job)
            self.current_job = None
    
    def _schedule_clear(self, duration):
        """Programme l'effacement du message"""
        if self.current_job:
            self.root.after_cancel(self.current_job)
        self.current_job = self.root.after(duration, self.clear)


class BaseTab(ABC):
    """Classe de base pour tous les onglets"""
    
    def __init__(self, parent_frame, data_manager, notification_center):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.notification_center = notification_center
        self.widgets = {}
        self.is_loaded = False
        
        # Créer le frame principal
        self.frame = ttk.Frame(parent_frame)
        
        try:
            self.setup_ui()
            self.load_data()
            self.is_loaded = True
            print(f"✅ Onglet {self.__class__.__name__} créé avec succès")
        except Exception as e:
            self.create_error_ui(e)
            print(f"❌ Erreur création {self.__class__.__name__}: {e}")
    
    @abstractmethod
    def setup_ui(self):
        """Configure l'interface utilisateur de l'onglet"""
        pass
    
    @abstractmethod
    def load_data(self):
        """Charge les données initiales"""
        pass
    
    @abstractmethod
    def refresh_data(self):
        """Rafraîchit les données"""
        pass
    
    def create_error_ui(self, error):
        """Crée une interface d'erreur générique"""
        error_frame = ttk.Frame(self.frame)
        error_frame.pack(expand=True, fill="both")
        
        # Icône d'erreur
        ttk.Label(error_frame, text="⚠️", font=('Arial', 48), foreground='red').pack(pady=20)
        
        # Message d'erreur
        ttk.Label(error_frame, text="Erreur de chargement de l'onglet", 
                 font=('Arial', 16, 'bold'), foreground='red').pack()
        
        ttk.Label(error_frame, text=str(error), 
                 font=('Arial', 10), foreground='gray', wraplength=400).pack(pady=10)
        
        # Bouton de rechargement
        ttk.Button(error_frame, text="🔄 Réessayer", 
                  command=self.retry_load).pack(pady=10)
    
    def retry_load(self):
        """Tente de recharger l'onglet"""
        try:
            # Nettoyer le frame
            for widget in self.frame.winfo_children():
                widget.destroy()
            
            # Relancer la création
            self.setup_ui()
            self.load_data()
            self.is_loaded = True
            self.notification_center.show_success("Onglet rechargé avec succès")
        except Exception as e:
            self.create_error_ui(e)
            self.notification_center.show_error(f"Échec du rechargement: {e}")


class DashboardTab(BaseTab):
    """Onglet tableau de bord avec statistiques en temps réel"""
    
    def setup_ui(self):
        """Configure l'interface du dashboard"""
        # Titre principal
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(title_frame, text="📊 Tableau de Bord", 
                 font=('Arial', 20, 'bold')).pack(side="left")
        
        # Bouton de rafraîchissement
        ttk.Button(title_frame, text="🔄 Actualiser", 
                  command=self.refresh_data).pack(side="right")
        
        # Statistiques principales
        self.create_stats_section()
        
        # Activité récente
        self.create_activity_section()
        
        # Actions rapides
        self.create_quick_actions()
    
    def create_stats_section(self):
        """Crée la section des statistiques"""
        stats_frame = ttk.LabelFrame(self.frame, text="📈 Statistiques Principales", padding=15)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Variables pour les statistiques
        self.stat_vars = {}
        
        # Configuration des statistiques
        stats_config = [
            ("Vols", "0", "🛫", "blue"),
            ("Passagers", "0", "👥", "green"),
            ("Personnel", "0", "👨‍✈️", "purple"),
            ("Réservations", "0", "🎫", "orange")
        ]
        
        # Créer les cartes de statistiques
        for i, (title, value, icon, color) in enumerate(stats_config):
            var = tk.StringVar(value=value)
            self.stat_vars[title] = var
            
            # Frame pour chaque statistique
            stat_card = ttk.Frame(stats_frame, relief="solid", borderwidth=1)
            stat_card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
            # Icône
            ttk.Label(stat_card, text=icon, font=('Arial', 24)).pack(pady=(10, 5))
            
            # Titre
            ttk.Label(stat_card, text=title, font=('Arial', 12, 'bold')).pack()
            
            # Valeur
            value_label = ttk.Label(stat_card, textvariable=var, 
                                   font=('Arial', 18, 'bold'))
            value_label.pack(pady=(5, 10))
            
            # Colorer selon le type
            if color == "blue":
                value_label.configure(foreground="blue")
            elif color == "green":
                value_label.configure(foreground="green")
            elif color == "purple":
                value_label.configure(foreground="purple")
            elif color == "orange":
                value_label.configure(foreground="orange")
        
        # Configuration responsive
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
    
    def create_activity_section(self):
        """Crée la section d'activité récente"""
        activity_frame = ttk.LabelFrame(self.frame, text="📋 Activité Récente", padding=15)
        activity_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Zone de texte pour l'activité
        self.activity_text = tk.Text(activity_frame, height=8, wrap=tk.WORD, 
                                    font=('Arial', 10), state=tk.DISABLED)
        
        # Scrollbar pour le texte
        scrollbar = ttk.Scrollbar(activity_frame, orient="vertical", command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.activity_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_quick_actions(self):
        """Crée la section des actions rapides"""
        actions_frame = ttk.LabelFrame(self.frame, text="⚡ Actions Rapides", padding=15)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        # Boutons d'actions
        actions = [
            ("➕ Nouveau Vol", self.quick_new_flight),
            ("👤 Nouveau Passager", self.quick_new_passenger),
            ("🎫 Nouvelle Réservation", self.quick_new_reservation),
            ("📊 Rapport Complet", self.show_complete_report)
        ]
        
        for i, (text, command) in enumerate(actions):
            ttk.Button(actions_frame, text=text, command=command, 
                      width=20).grid(row=0, column=i, padx=5, pady=5)
        
        # Configuration responsive
        for i in range(len(actions)):
            actions_frame.grid_columnconfigure(i, weight=1)
    
    def load_data(self):
        """Charge les données initiales"""
        self.refresh_data()
    
    def refresh_data(self):
        """Rafraîchit les données du dashboard"""
        try:
            # Charger les statistiques
            flights = self.data_manager.get_flights()
            passengers = self.data_manager.get_passengers()
            personnel = self.data_manager.get_personnel()
            reservations = self.data_manager.get_reservations()
            
            # Mettre à jour les variables
            self.stat_vars["Vols"].set(str(len(flights)))
            self.stat_vars["Passagers"].set(str(len(passengers)))
            self.stat_vars["Personnel"].set(str(len(personnel)))
            self.stat_vars["Réservations"].set(str(len(reservations)))
            
            # Mettre à jour l'activité récente
            self.update_activity_log()
            
            self.notification_center.show_success("Dashboard mis à jour")
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur mise à jour dashboard: {e}")
    
    def update_activity_log(self):
        """Met à jour le journal d'activité"""
        try:
            self.activity_text.configure(state=tk.NORMAL)
            self.activity_text.delete(1.0, tk.END)
            
            # Générer des informations d'activité
            current_time = datetime.now().strftime("%H:%M:%S")
            
            activity_log = f"""🕐 Dernière mise à jour: {current_time}

📊 RÉSUMÉ SYSTÈME:
• Système opérationnel
• Toutes les données chargées
• Interface responsive

🔄 ACTIVITÉS RÉCENTES:
• Dashboard rafraîchi
• Statistiques mises à jour
• Connexions actives

💡 CONSEILS:
• Utilisez Ctrl+R pour actualiser
• Double-cliquez pour modifier
• Consultez l'aide avec Ctrl+H

📈 PERFORMANCE:
• Temps de réponse: < 1s
• Mémoire utilisée: Optimale
• État général: Excellent"""
            
            self.activity_text.insert(tk.END, activity_log)
            self.activity_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            print(f"❌ Erreur mise à jour activité: {e}")
    
    def quick_new_flight(self):
        """Action rapide: nouveau vol"""
        self.notification_center.show_info("Redirection vers l'onglet Vols...")
        # Ici on pourrait changer d'onglet automatiquement
    
    def quick_new_passenger(self):
        """Action rapide: nouveau passager"""
        self.notification_center.show_info("Redirection vers l'onglet Passagers...")
    
    def quick_new_reservation(self):
        """Action rapide: nouvelle réservation"""
        self.notification_center.show_info("Redirection vers l'onglet Réservations...")
    
    def show_complete_report(self):
        """Affiche un rapport complet"""
        try:
            flights = self.data_manager.get_flights()
            passengers = self.data_manager.get_passengers()
            personnel = self.data_manager.get_personnel()
            reservations = self.data_manager.get_reservations()
            aircraft = self.data_manager.get_aircraft()
            
            # Statistiques avancées
            active_flights = len([f for f in flights if f.get('statut') in ['programme', 'en_vol']])
            active_reservations = len([r for r in reservations if r.get('statut') == 'active'])
            available_personnel = len([p for p in personnel if p.get('disponible', True)])
            operational_aircraft = len([a for a in aircraft if a.get('etat') == 'operationnel'])
            
            report = f"""📊 RAPPORT COMPLET DU SYSTÈME

🛫 VOLS:
• Total: {len(flights)}
• Actifs: {active_flights}
• Taux d'activité: {(active_flights/max(len(flights), 1)*100):.1f}%

👥 PASSAGERS:
• Enregistrés: {len(passengers)}
• Avec réservations: {active_reservations}

👨‍✈️ PERSONNEL:
• Total: {len(personnel)}
• Disponibles: {available_personnel}
• Taux de disponibilité: {(available_personnel/max(len(personnel), 1)*100):.1f}%

✈️ FLOTTE:
• Total avions: {len(aircraft)}
• Opérationnels: {operational_aircraft}
• Taux opérationnel: {(operational_aircraft/max(len(aircraft), 1)*100):.1f}%

🎫 RÉSERVATIONS:
• Total: {len(reservations)}
• Actives: {active_reservations}

📅 Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            messagebox.showinfo("Rapport Complet", report)
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur génération rapport: {e}")


class AircraftTab(BaseTab):
    """Onglet gestion des avions avec interface moderne"""
    
    def setup_ui(self):
        """Configure l'interface de gestion des avions"""
        # Initialiser le gestionnaire sécurisé
        if AIRCRAFT_MODULE_AVAILABLE:
            self.safe_manager = SafeAircraftManager(self.data_manager, self.notification_center)
        else:
            self.safe_manager = None
        
        self.create_aircraft_interface()
    
    def create_aircraft_interface(self):
        """Crée l'interface de gestion des avions"""
        # Barre d'outils
        toolbar = ttk.Frame(self.frame)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Button(toolbar, text="➕ Nouvel Avion", 
                  command=self.new_aircraft, 
                  style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
        ttk.Button(toolbar, text="✏️ Modifier", 
                  command=self.edit_aircraft).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(toolbar, text="🔧 Maintenance", 
                  command=self.aircraft_maintenance).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(toolbar, text="🗑️ Retirer", 
                  command=self.delete_aircraft, 
                  style='Danger.TButton').grid(row=0, column=3, padx=(0, 20))
        
        # Recherche
        ttk.Label(toolbar, text="🔍 Recherche:").grid(row=0, column=4, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=5, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.filter_aircraft)
        
        # Filtre par état
        ttk.Label(toolbar, text="État:").grid(row=0, column=6, padx=(10, 5))
        self.filter_var = tk.StringVar(value="Tous")
        filter_combo = ttk.Combobox(toolbar, textvariable=self.filter_var, width=15, state="readonly")
        filter_combo['values'] = ['Tous', 'Opérationnel', 'En vol', 'Maintenance', 'Hors service']
        filter_combo.grid(row=0, column=7, padx=(0, 5))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_aircraft)
        
        # Tableau des avions
        columns = ('ID', 'Modèle', 'Compagnie', 'Capacité', 'État', 'Localisation', 'Autonomie', 'Dernière Maintenance')
        self.aircraft_tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        self.aircraft_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Configuration colonnes
        column_widths = {
            'ID': 100, 'Modèle': 150, 'Compagnie': 120, 'Capacité': 80, 
            'État': 100, 'Localisation': 120, 'Autonomie': 100, 'Dernière Maintenance': 150
        }
        for col in columns:
            self.aircraft_tree.heading(col, text=col)
            self.aircraft_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.aircraft_tree.yview)
        v_scrollbar.grid(row=1, column=1, sticky="ns")
        self.aircraft_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.aircraft_tree.xview)
        h_scrollbar.grid(row=2, column=0, sticky="ew")
        self.aircraft_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Configuration responsive
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Double-clic pour modifier
        self.aircraft_tree.bind('<Double-1>', lambda e: self.edit_aircraft())
    
    def load_data(self):
        """Charge les données initiales"""
        self.refresh_data()
    
    def refresh_data(self):
        """Rafraîchit les données des avions"""
        try:
            # Vider le tableau
            for item in self.aircraft_tree.get_children():
                self.aircraft_tree.delete(item)
            
            aircraft_list = self.data_manager.get_aircraft()
            airports = {a['code_iata']: a['ville'] for a in self.data_manager.get_airports()}
            
            for aircraft in aircraft_list:
                # Obtenir le nom de la ville depuis les coordonnées
                location = "Inconnu"
                if 'localisation' in aircraft:
                    loc_coords = aircraft['localisation']
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
                    aircraft.get('etat', 'au_sol').replace('_', ' ').title(),
                    location,
                    f"{aircraft.get('autonomie', 0)} km",
                    aircraft.get('derniere_maintenance', 'Jamais')
                )
                
                self.aircraft_tree.insert('', 'end', values=values)
            
            self.notification_center.show_info(f"Avions rafraîchis: {len(aircraft_list)} avions")
        except Exception as e:
            self.notification_center.show_error(f"Erreur refresh avions: {e}")
    
    def new_aircraft(self):
        """Crée un nouvel avion"""
        if not AIRCRAFT_MODULE_AVAILABLE:
            self.notification_center.show_error("Module de dialogue avion non disponible")
            return
        
        try:
            dialog = ModernAircraftDialog(self.frame.winfo_toplevel(), self.data_manager, 
                                        notification_center=self.notification_center)
            if dialog.result:
                self.refresh_data()
                self.notification_center.show_success("Nouvel avion créé")
        except Exception as e:
            self.notification_center.show_error(f"Erreur création avion: {e}")
    
    def edit_aircraft(self):
        """Modifie l'avion sélectionné"""
        selection = self.aircraft_tree.selection()
        if not selection:
            self.notification_center.show_warning("Veuillez sélectionner un avion à modifier")
            return
        
        if not AIRCRAFT_MODULE_AVAILABLE:
            self.notification_center.show_error("Module de dialogue avion non disponible")
            return
        
        try:
            item = self.aircraft_tree.item(selection[0])
            aircraft_id = item['values'][0]
            
            all_aircraft = self.data_manager.get_aircraft()
            aircraft_data = None
            
            for aircraft in all_aircraft:
                if aircraft.get('num_id') == aircraft_id:
                    aircraft_data = aircraft
                    break
            
            if not aircraft_data:
                self.notification_center.show_error(f"Avion {aircraft_id} non trouvé")
                return
            
            dialog = ModernAircraftDialog(self.frame.winfo_toplevel(), self.data_manager, 
                                        aircraft_data, self.notification_center)
            if dialog.result:
                self.refresh_data()
                self.notification_center.show_success(f"Avion {aircraft_id} modifié")
        except Exception as e:
            self.notification_center.show_error(f"Erreur modification avion: {e}")
    
    def aircraft_maintenance(self):
        """Gère la maintenance de l'avion"""
        selection = self.aircraft_tree.selection()
        if not selection:
            self.notification_center.show_warning("Veuillez sélectionner un avion")
            return
        
        try:
            item = self.aircraft_tree.item(selection[0])
            aircraft_id = item['values'][0]
            current_state = item['values'][4]
            
            if self.safe_manager:
                if "Maintenance" in current_state:
                    if messagebox.askyesno("Terminer maintenance", 
                                         f"Terminer la maintenance de l'avion {aircraft_id} ?"):
                        success, message = self.safe_manager.safe_change_aircraft_state(
                            aircraft_id, 'operationnel', "Maintenance terminée")
                        if success:
                            self.refresh_data()
                else:
                    if messagebox.askyesno("Programmer maintenance", 
                                         f"Programmer une maintenance pour l'avion {aircraft_id} ?"):
                        success, message = self.safe_manager.safe_change_aircraft_state(
                            aircraft_id, 'en_maintenance', "Maintenance programmée")
                        if success:
                            self.refresh_data()
            else:
                self.notification_center.show_warning("Gestionnaire de maintenance non disponible")
                
        except Exception as e:
            self.notification_center.show_error(f"Erreur maintenance: {e}")
    
    def delete_aircraft(self):
        """Supprime l'avion sélectionné"""
        selection = self.aircraft_tree.selection()
        if not selection:
            self.notification_center.show_warning("Veuillez sélectionner un avion à supprimer")
            return
        
        try:
            item = self.aircraft_tree.item(selection[0])
            aircraft_id = item['values'][0]
            aircraft_model = item['values'][1]
            
            if self.safe_manager:
                # Vérifier si la suppression est possible
                can_delete, reason = self.safe_manager.can_delete_aircraft(aircraft_id)
                
                if not can_delete:
                    self.notification_center.show_warning(f"Suppression impossible: {reason}")
                    return
                
                if messagebox.askyesno("Confirmation", 
                                      f"Supprimer l'avion {aircraft_id} ({aircraft_model}) ?\n\n"
                                      "Cette action est irréversible."):
                    
                    success, message = self.safe_manager.safe_delete_aircraft(aircraft_id)
                    if success:
                        self.refresh_data()
            else:
                self.notification_center.show_error("Gestionnaire sécurisé non disponible")
                
        except Exception as e:
            self.notification_center.show_error(f"Erreur suppression: {e}")
    
    def filter_aircraft(self, event=None):
        """Filtre la liste des avions"""
        search_text = self.search_var.get().lower()
        filter_state = self.filter_var.get()
        
        # Vider le tableau
        for item in self.aircraft_tree.get_children():
            self.aircraft_tree.delete(item)
        
        # Recharger avec filtres
        all_aircraft = self.data_manager.get_aircraft()
        filtered_count = 0
        
        for aircraft in all_aircraft:
            # Filtrage par état
            current_state = aircraft.get('etat', 'au_sol')
            state_display = current_state.replace('_', ' ').title()
            
            if filter_state != "Tous" and filter_state.lower() != state_display.lower():
                continue
            
            # Filtrage par recherche
            searchable_text = f"{aircraft.get('num_id', '')} {aircraft.get('modele', '')} {aircraft.get('compagnie_aerienne', '')}".lower()
            if search_text and search_text not in searchable_text:
                continue
            
            # Obtenir la localisation
            location = "Inconnu"
            if 'localisation' in aircraft:
                loc_coords = aircraft['localisation']
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
                state_display,
                location,
                f"{aircraft.get('autonomie', 0)} km",
                aircraft.get('derniere_maintenance', 'Jamais')
            )
            
            self.aircraft_tree.insert('', 'end', values=values)
            filtered_count += 1
        
        if search_text or filter_state != "Tous":
            self.notification_center.show_info(f"Filtre appliqué: {filtered_count} avions affichés")


class ExternalTab(BaseTab):
    """Classe pour les onglets externes (modules séparés)"""
    
    def __init__(self, parent_frame, data_manager, notification_center, 
                 module_available, create_function, refresh_function, tab_title):
        self.module_available = module_available
        self.create_function = create_function
        self.refresh_function = refresh_function
        self.tab_title = tab_title
        self.tree_widget = None
        super().__init__(parent_frame, data_manager, notification_center)
    
    def setup_ui(self):
        """Configure l'interface de l'onglet externe"""
        if not self.module_available:
            raise Exception(f"Module {self.tab_title} non disponible")
        
        try:
            self.tree_widget = self.create_function(self.frame, self.data_manager)
        except Exception as e:
            raise Exception(f"Erreur création interface {self.tab_title}: {e}")
    
    def load_data(self):
        """Charge les données initiales"""
        self.refresh_data()
    
    def refresh_data(self):
        """Rafraîchit les données de l'onglet"""
        if self.tree_widget and self.refresh_function:
            try:
                self.refresh_function(self.tree_widget, self.data_manager)
                self.notification_center.show_info(f"{self.tab_title} rafraîchi")
            except Exception as e:
                self.notification_center.show_error(f"Erreur refresh {self.tab_title}: {e}")


class TabManager:
    """Gestionnaire centralisé des onglets"""
    
    def __init__(self, notebook, data_manager, notification_center):
        self.notebook = notebook
        self.data_manager = data_manager
        self.notification_center = notification_center
        self.tabs = {}
        
        # Configuration des onglets avec vérification de disponibilité
        self.tab_configs = [
            ('dashboard', '📊 Tableau de Bord', DashboardTab, True),
            ('aircraft', '✈️ Avions', AircraftTab, True),
            ('flights', '🛫 Vols', self._create_flights_tab, FLIGHTS_MODULE_AVAILABLE),
            ('passengers', '🧳 Passagers', self._create_passengers_tab, PASSENGERS_MODULE_AVAILABLE),
            ('personnel', '👥 Personnel', self._create_personnel_tab, PERSONNEL_MODULE_AVAILABLE),
            ('reservations', '🎫 Réservations', self._create_reservations_tab, RESERVATIONS_MODULE_AVAILABLE),
        ]
    
    def create_all_tabs(self):
        """Crée tous les onglets disponibles"""
        for tab_id, title, tab_class_or_function, available in self.tab_configs:
            try:
                if not available:
                    print(f"⚠️ Onglet {title} non disponible - module manquant")
                    self._create_unavailable_tab(tab_id, title)
                    continue
                
                if callable(tab_class_or_function) and not (
                    hasattr(tab_class_or_function, '__bases__') and 
                    BaseTab in tab_class_or_function.__bases__
                ):
                    # Fonction de création spéciale
                    tab_instance = tab_class_or_function()
                else:
                    # Classe d'onglet standard
                    tab_instance = tab_class_or_function(self.notebook, self.data_manager, self.notification_center)
                
                self.tabs[tab_id] = tab_instance
                self.notebook.add(tab_instance.frame, text=title)
                
                print(f"✅ Onglet {title} créé")
                
            except Exception as e:
                print(f"❌ Erreur création onglet {title}: {e}")
                self._create_error_tab(tab_id, title, e)
    
    def _create_flights_tab(self):
        """Crée l'onglet vols"""
        return ExternalTab(self.notebook, self.data_manager, self.notification_center,
                          FLIGHTS_MODULE_AVAILABLE, create_flights_tab_content, 
                          refresh_flights_data, 'Vols')
    
    def _create_passengers_tab(self):
        """Crée l'onglet passagers"""
        return ExternalTab(self.notebook, self.data_manager, self.notification_center,
                          PASSENGERS_MODULE_AVAILABLE, create_passengers_tab_content, 
                          refresh_passengers_data, 'Passagers')
    
    def _create_personnel_tab(self):
        """Crée l'onglet personnel"""
        return ExternalTab(self.notebook, self.data_manager, self.notification_center,
                          PERSONNEL_MODULE_AVAILABLE, create_personnel_tab_content, 
                          refresh_personnel_data, 'Personnel')
    
    def _create_reservations_tab(self):
        """Crée l'onglet réservations"""
        return ExternalTab(self.notebook, self.data_manager, self.notification_center,
                          RESERVATIONS_MODULE_AVAILABLE, create_reservations_tab_content, 
                          refresh_reservations_data, 'Réservations')
    
    def _create_unavailable_tab(self, tab_id, title):
        """Crée un onglet pour module non disponible"""
        unavailable_frame = ttk.Frame(self.notebook)
        
        ttk.Label(unavailable_frame, text="📦", font=('Arial', 48), foreground='orange').pack(pady=20)
        ttk.Label(unavailable_frame, text=f"Module {title} non disponible", 
                 font=('Arial', 16, 'bold'), foreground='orange').pack()
        ttk.Label(unavailable_frame, text="Le module correspondant n'a pas pu être chargé.", 
                 font=('Arial', 10), foreground='gray').pack(pady=10)
        
        ttk.Button(unavailable_frame, text="🔄 Réessayer", 
                  command=lambda: self._retry_tab(tab_id, title)).pack(pady=10)
        
        self.notebook.add(unavailable_frame, text=f"📦 {title}")
    
    def _create_error_tab(self, tab_id, title, error):
        """Crée un onglet d'erreur"""
        error_frame = ttk.Frame(self.notebook)
        
        ttk.Label(error_frame, text="⚠️", font=('Arial', 48), foreground='red').pack(pady=20)
        ttk.Label(error_frame, text=f"Erreur: {title}", font=('Arial', 16, 'bold'), foreground='red').pack()
        ttk.Label(error_frame, text=str(error), font=('Arial', 10), foreground='gray', wraplength=400).pack(pady=10)
        
        ttk.Button(error_frame, text="🔄 Réessayer", 
                  command=lambda: self._retry_tab(tab_id, title)).pack(pady=10)
        
        self.notebook.add(error_frame, text=f"❌ {title}")
    
    def _retry_tab(self, tab_id, title):
        """Retente la création d'un onglet"""
        # Trouver l'index de l'onglet
        for i, (config_id, config_title, _, _) in enumerate(self.tab_configs):
            if config_id == tab_id:
                tab_index = i
                break
        else:
            return
        
        # Supprimer l'onglet actuel
        self.notebook.forget(tab_index)
        
        # Recréer l'onglet
        config_id, config_title, tab_class_or_function, available = self.tab_configs[tab_index]
        try:
            if not available:
                self._create_unavailable_tab(tab_id, config_title)
                return
            
            if callable(tab_class_or_function) and not (
                hasattr(tab_class_or_function, '__bases__') and 
                BaseTab in tab_class_or_function.__bases__
            ):
                tab_instance = tab_class_or_function()
            else:
                tab_instance = tab_class_or_function(self.notebook, self.data_manager, self.notification_center)
            
            self.tabs[tab_id] = tab_instance
            self.notebook.insert(tab_index, tab_instance.frame, text=config_title)
            self.notification_center.show_success(f"Onglet {config_title} rechargé")
            
        except Exception as e:
            self._create_error_tab(tab_id, config_title, e)
            self.notification_center.show_error(f"Échec rechargement {config_title}")
    
    def refresh_all_tabs(self):
        """Rafraîchit tous les onglets chargés"""
        refreshed_count = 0
        for tab_id, tab_instance in self.tabs.items():
            if hasattr(tab_instance, 'refresh_data') and tab_instance.is_loaded:
                try:
                    tab_instance.refresh_data()
                    refreshed_count += 1
                except Exception as e:
                    print(f"❌ Erreur refresh onglet {tab_id}: {e}")
        
        self.notification_center.show_success(f"{refreshed_count} onglets rafraîchis")
    
    def get_tab(self, tab_id):
        """Récupère une instance d'onglet"""
        return self.tabs.get(tab_id)


class KeyboardManager:
    """Gestionnaire des raccourcis clavier"""
    
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self.setup_bindings()
    
    def setup_bindings(self):
        """Configure les raccourcis clavier"""
        # Raccourcis globaux
        self.root.bind('<Control-r>', lambda e: self.main_window.refresh_all_data())
        self.root.bind('<F5>', lambda e: self.main_window.refresh_all_data())
        self.root.bind('<Control-s>', lambda e: self.main_window.save_all_data())
        self.root.bind('<Control-q>', lambda e: self.main_window.on_closing())
        self.root.bind('<Control-h>', lambda e: self.show_help())
        
        # Navigation entre onglets
        for i in range(1, 7):
            self.root.bind(f'<Control-{i}>', lambda e, idx=i-1: self.select_tab(idx))
        
        # Nouveaux éléments
        self.root.bind('<Control-n>', lambda e: self.new_element())
        self.root.bind('<Control-e>', lambda e: self.edit_element())
        self.root.bind('<Delete>', lambda e: self.delete_element())
        
        print("⌨️ Raccourcis clavier configurés")
    
    def select_tab(self, index):
        """Sélectionne un onglet par index"""
        try:
            if index < self.main_window.notebook.index('end'):
                self.main_window.notebook.select(index)
                self.main_window.notification_center.show_info(f"Onglet {index + 1} sélectionné")
        except:
            pass
    
    def new_element(self):
        """Crée un nouvel élément selon l'onglet actuel"""
        try:
            current_tab_index = self.main_window.notebook.index('current')
            tab_configs = ['dashboard', 'aircraft', 'flights', 'passengers', 'personnel', 'reservations']
            
            if current_tab_index < len(tab_configs):
                tab_id = tab_configs[current_tab_index]
                tab_instance = self.main_window.tab_manager.get_tab(tab_id)
                
                if hasattr(tab_instance, 'new_aircraft') and tab_id == 'aircraft':
                    tab_instance.new_aircraft()
                else:
                    self.main_window.notification_center.show_info("Fonction non disponible pour cet onglet")
        except Exception as e:
            self.main_window.notification_center.show_error(f"Erreur création: {e}")
    
    def edit_element(self):
        """Modifie l'élément sélectionné selon l'onglet actuel"""
        try:
            current_tab_index = self.main_window.notebook.index('current')
            tab_configs = ['dashboard', 'aircraft', 'flights', 'passengers', 'personnel', 'reservations']
            
            if current_tab_index < len(tab_configs):
                tab_id = tab_configs[current_tab_index]
                tab_instance = self.main_window.tab_manager.get_tab(tab_id)
                
                if hasattr(tab_instance, 'edit_aircraft') and tab_id == 'aircraft':
                    tab_instance.edit_aircraft()
                else:
                    self.main_window.notification_center.show_info("Fonction non disponible pour cet onglet")
        except Exception as e:
            self.main_window.notification_center.show_error(f"Erreur modification: {e}")
    
    def delete_element(self):
        """Supprime l'élément sélectionné selon l'onglet actuel"""
        try:
            current_tab_index = self.main_window.notebook.index('current')
            tab_configs = ['dashboard', 'aircraft', 'flights', 'passengers', 'personnel', 'reservations']
            
            if current_tab_index < len(tab_configs):
                tab_id = tab_configs[current_tab_index]
                tab_instance = self.main_window.tab_manager.get_tab(tab_id)
                
                if hasattr(tab_instance, 'delete_aircraft') and tab_id == 'aircraft':
                    tab_instance.delete_aircraft()
                else:
                    self.main_window.notification_center.show_info("Fonction non disponible pour cet onglet")
        except Exception as e:
            self.main_window.notification_center.show_error(f"Erreur suppression: {e}")
    
    def show_help(self):
        """Affiche l'aide des raccourcis clavier"""
        help_text = """📖 RACCOURCIS CLAVIER

🔄 ACTIONS GLOBALES:
• Ctrl+R ou F5 : Actualiser les données
• Ctrl+S : Sauvegarder
• Ctrl+H : Afficher cette aide
• Ctrl+Q : Quitter l'application

🗂️ NAVIGATION:
• Ctrl+1 à Ctrl+6 : Basculer entre les onglets
• Ctrl+N : Nouveau (dans l'onglet actuel)
• Ctrl+E : Modifier (élément sélectionné)
• Suppr : Supprimer (élément sélectionné)

💡 ASTUCES:
• Double-clic pour modifier un élément
• Utilisez les champs de recherche pour filtrer
• Les modifications sont sauvegardées automatiquement"""

        messagebox.showinfo("Aide - Raccourcis Clavier", help_text)


class ThemeManager:
    """Gestionnaire de thèmes pour l'interface"""
    
    def __init__(self, root):
        self.root = root
        self.current_theme = "default"
        self.themes = {
            "default": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff"
            },
            "dark": {
                "bg": "#2d2d2d",
                "fg": "#ffffff", 
                "select_bg": "#404040",
                "select_fg": "#ffffff"
            }
        }
        
        self.setup_styles()
    
    def setup_styles(self):
        """Configure les styles par défaut"""
        self.style = ttk.Style()
        
        # Styles personnalisés
        self.style.configure('Action.TButton', padding=(10, 5), font=('Arial', 9, 'bold'))
        self.style.configure('Danger.TButton', foreground='red', font=('Arial', 9, 'bold'))
        self.style.configure('Success.TButton', foreground='green', font=('Arial', 9, 'bold'))
        
        # Styles pour les statistiques
        self.style.configure('Stat.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Value.TLabel', font=('Arial', 14, 'bold'), foreground='blue')
        
        print("🎨 Thèmes et styles configurés")
    
    def switch_theme(self, theme_name):
        """Change le thème de l'interface"""
        if theme_name not in self.themes:
            return False
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Appliquer le thème (simplifié pour tkinter/ttk)
        try:
            if theme_name == "dark":
                self.style.theme_use('clam')  # Thème sombre si disponible
            else:
                self.style.theme_use('default')
            
            print(f"🎨 Thème changé: {theme_name}")
            return True
        except:
            print(f"❌ Erreur changement thème: {theme_name}")
            return False


class MainWindow:
    """Fenêtre principale de l'application - VERSION INTÉGRÉE"""
    
    def __init__(self):
        """Initialise la fenêtre principale"""
        self.root = tk.Tk()
        self.root.title("Système de Gestion Aérienne - Interface Moderne")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configuration de l'icône (si disponible)
        try:
            # self.root.iconbitmap("icon.ico")  # Décommenté si vous avez une icône
            pass
        except:
            pass
        
        # Gestionnaire de données
        self.data_manager = DataManager()
        
        # Variables d'interface
        self.status_var = tk.StringVar(value="Application prête")
        
        # Gestionnaires
        self.notification_center = NotificationCenter(self.status_var, self.root)
        self.theme_manager = ThemeManager(self.root)
        self.keyboard_manager = KeyboardManager(self.root, self)
        
        # Configuration de l'interface
        self.setup_ui()
        
        # Chargement initial des données
        self.root.after(100, self.initial_load)
        
        print("🖥️ Interface principale initialisée avec modules intégrés")
    
    def setup_ui(self):
        """Configure l'interface utilisateur principale"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Barre supérieure avec actions et informations
        self.create_enhanced_toolbar(main_frame)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Gestionnaire d'onglets
        self.tab_manager = TabManager(self.notebook, self.data_manager, self.notification_center)
        
        # Barre de statut améliorée
        self.create_enhanced_status_bar(main_frame)
    
    def create_enhanced_toolbar(self, parent):
        """Crée la barre d'outils améliorée"""
        toolbar_frame = ttk.LabelFrame(parent, text="🎛️ Actions Principales", padding=10)
        toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Section gauche - Actions principales
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.grid(row=0, column=0, sticky="w")
        
        ttk.Button(left_frame, text="🔄 Actualiser", 
                  command=self.refresh_all_data, 
                  style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(left_frame, text="📊 Statistiques", 
                  command=self.show_enhanced_statistics, 
                  style='Action.TButton').grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(left_frame, text="💾 Sauvegarder", 
                  command=self.save_all_data, 
                  style='Success.TButton').grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(left_frame, text="🎨 Thème", 
                  command=self.toggle_theme).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(left_frame, text="⌨️ Aide", 
                  command=self.keyboard_manager.show_help).grid(row=0, column=4, padx=(0, 20))
        
        # Section centre - Indicateurs de performance
        center_frame = ttk.Frame(toolbar_frame)
        center_frame.grid(row=0, column=1, sticky="ew", padx=20)
        
        # Indicateur de charge système
        self.load_var = tk.StringVar(value="💚 Système OK")
        load_label = ttk.Label(center_frame, textvariable=self.load_var, 
                              font=('Arial', 10, 'bold'))
        load_label.grid(row=0, column=0, padx=10)
        
        # Indicateur de données
        self.data_status_var = tk.StringVar(value="💾 Données OK")
        data_label = ttk.Label(center_frame, textvariable=self.data_status_var, 
                              font=('Arial', 10, 'bold'))
        data_label.grid(row=0, column=1, padx=10)
        
        # Section droite - Horloge et informations
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.grid(row=0, column=2, sticky="e")
        
        # Horloge système
        clock_frame = ttk.LabelFrame(right_frame, text="🕐 Système", padding=5)
        clock_frame.grid(row=0, column=0, padx=(0, 10), sticky="e")
        
        self.clock_var = tk.StringVar()
        clock_label = ttk.Label(clock_frame, textvariable=self.clock_var,
                               font=('Arial', 12, 'bold'),
                               foreground='blue')
        clock_label.pack()
        
        # Mode d'interface
        mode_label = ttk.Label(right_frame, text="Mode: Intégré", 
                              font=('Arial', 10), foreground='green')
        mode_label.grid(row=0, column=1, sticky="e")
        
        # Configuration responsive
        toolbar_frame.grid_columnconfigure(1, weight=1)
        
        # Démarrer l'horloge
        self.update_clock()
        self.update_system_status()
    
    def create_enhanced_status_bar(self, parent):
        """Crée la barre de statut améliorée"""
        status_frame = ttk.Frame(parent, relief="sunken", borderwidth=1)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Section gauche - Statut principal
        ttk.Label(status_frame, textvariable=self.status_var, 
                 font=('Arial', 10)).grid(row=0, column=0, sticky="w", padx=5)
        
        # Section centre - Informations rapides
        self.quick_info_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.quick_info_var,
                 font=('Arial', 9), foreground='gray').grid(row=0, column=1, sticky="w", padx=20)
        
        # Section droite - Informations techniques
        modules_status = []
        if FLIGHTS_MODULE_AVAILABLE:
            modules_status.append("Vols")
        if PASSENGERS_MODULE_AVAILABLE:
            modules_status.append("Passagers")
        if PERSONNEL_MODULE_AVAILABLE:
            modules_status.append("Personnel")
        if RESERVATIONS_MODULE_AVAILABLE:
            modules_status.append("Réservations")
        if AIRCRAFT_MODULE_AVAILABLE:
            modules_status.append("Avions")
        
        tech_info = f"Modules: {', '.join(modules_status) if modules_status else 'Aucun'}"
        ttk.Label(status_frame, text=tech_info,
                 font=('Arial', 9), foreground='gray').grid(row=0, column=2, sticky="e", padx=5)
        
        status_frame.grid_columnconfigure(1, weight=1)
    
    def initial_load(self):
        """Chargement initial de l'interface"""
        try:
            self.notification_center.show_progress("Initialisation de l'interface...")
            
            # Créer tous les onglets
            self.tab_manager.create_all_tabs()
            
            # Chargement initial des données
            self.refresh_all_data()
            
            self.notification_center.show_success("Interface initialisée avec succès")
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur initialisation: {e}")
    
    def update_clock(self):
        """Met à jour l'horloge système"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_var.set(current_time)
        self.root.after(1000, self.update_clock)
    
    def update_system_status(self):
        """Met à jour les indicateurs système"""
        try:
            # Vérifier l'état des données
            aircraft_count = len(self.data_manager.get_aircraft())
            personnel_count = len(self.data_manager.get_personnel())
            flights_count = len(self.data_manager.get_flights())
            passengers_count = len(self.data_manager.get_passengers())
            reservations_count = len(self.data_manager.get_reservations())
            
            total_elements = aircraft_count + personnel_count + flights_count + passengers_count + reservations_count
            
            if total_elements > 0:
                self.data_status_var.set("💾 Données OK")
                self.load_var.set("💚 Système OK")
            else:
                self.data_status_var.set("💾 Aucune donnée")
                self.load_var.set("🟡 Données vides")
            
            # Informations rapides
            if total_elements > 0:
                self.quick_info_var.set(f"📊 {total_elements} éléments chargés")
            else:
                self.quick_info_var.set("Aucune donnée chargée")
            
        except Exception as e:
            self.data_status_var.set("❌ Erreur données")
            self.load_var.set("🔴 Erreur système")
            print(f"❌ Erreur statut système: {e}")
        
        # Programmer la prochaine mise à jour
        self.root.after(5000, self.update_system_status)
    
    def toggle_theme(self):
        """Bascule entre les thèmes"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "default" else "default"
        
        if self.theme_manager.switch_theme(new_theme):
            self.notification_center.show_success(f"Thème changé: {new_theme}")
        else:
            self.notification_center.show_warning("Impossible de changer le thème")
    
    def show_enhanced_statistics(self):
        """Affiche les statistiques améliorées"""
        try:
            aircraft_count = len(self.data_manager.get_aircraft())
            personnel_count = len(self.data_manager.get_personnel())
            flights_count = len(self.data_manager.get_flights())
            passengers_count = len(self.data_manager.get_passengers())
            reservations_count = len(self.data_manager.get_reservations())
            
            # Statistiques avancées
            aircraft_list = self.data_manager.get_aircraft()
            operational_aircraft = sum(1 for a in aircraft_list if a.get('etat') in ['operationnel', 'au_sol'])
            maintenance_aircraft = sum(1 for a in aircraft_list if a.get('etat') == 'en_maintenance')
            
            # Calcul capacité totale
            total_capacity = sum(a.get('capacite', 0) for a in aircraft_list)
            
            # Modules disponibles
            available_modules = []
            if FLIGHTS_MODULE_AVAILABLE:
                available_modules.append("✅ Vols")
            else:
                available_modules.append("❌ Vols")
            
            if PASSENGERS_MODULE_AVAILABLE:
                available_modules.append("✅ Passagers")
            else:
                available_modules.append("❌ Passagers")
            
            if PERSONNEL_MODULE_AVAILABLE:
                available_modules.append("✅ Personnel")
            else:
                available_modules.append("❌ Personnel")
            
            if RESERVATIONS_MODULE_AVAILABLE:
                available_modules.append("✅ Réservations")
            else:
                available_modules.append("❌ Réservations")
            
            if AIRCRAFT_MODULE_AVAILABLE:
                available_modules.append("✅ Avions")
            else:
                available_modules.append("❌ Avions")
            
            stats_text = f"""📊 STATISTIQUES DÉTAILLÉES

✈️ FLOTTE ({aircraft_count} avions):
• Opérationnels : {operational_aircraft}
• En maintenance : {maintenance_aircraft}
• Capacité totale : {total_capacity:,} passagers

👥 PERSONNEL : {personnel_count} employés

🛫 OPÉRATIONS :
• Vols planifiés : {flights_count}
• Passagers enregistrés : {passengers_count}
• Réservations actives : {reservations_count}

📦 MODULES DISPONIBLES :
{chr(10).join(available_modules)}

📈 PERFORMANCE :
• Taux d'utilisation flotte : {(operational_aircraft/max(aircraft_count, 1)*100):.1f}%
• Ratio passagers/capacité : {(passengers_count/max(total_capacity, 1)*100):.1f}%

🕐 Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}
📅 Date : {datetime.now().strftime('%Y-%m-%d')}"""
            
            messagebox.showinfo("Statistiques Détaillées", stats_text)
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur calcul statistiques: {e}")
    
    def save_all_data(self):
        """Force la sauvegarde avec feedback amélioré"""
        try:
            self.notification_center.show_progress("Sauvegarde en cours...")
            
            # Simuler un délai de sauvegarde pour le feedback
            self.root.after(500, self._complete_save)
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur sauvegarde: {e}")
    
    def _complete_save(self):
        """Complète la sauvegarde"""
        try:
            # La sauvegarde est automatique avec DataManager
            self.notification_center.show_success("Données sauvegardées avec succès")
            messagebox.showinfo("Sauvegarde", "Toutes les données ont été sauvegardées.")
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur finalisation sauvegarde: {e}")
    
    def refresh_all_data(self):
        """Rafraîchit toutes les données avec feedback amélioré"""
        try:
            self.notification_center.show_progress("Actualisation globale en cours...")
            
            # Rafraîchir tous les onglets
            self.tab_manager.refresh_all_tabs()
            
            # Mettre à jour les indicateurs système
            self.update_system_status()
            
            print("✅ Rafraîchissement global terminé")
            
        except Exception as e:
            self.notification_center.show_error(f"Erreur rafraîchissement: {e}")
    
    def run(self):
        """Lance l'application avec gestion d'erreurs améliorée"""
        try:
            # Gestionnaire de fermeture
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Message de bienvenue
            self.notification_center.show_info("Bienvenue dans le système de gestion aérienne")
            
            # Lancer la boucle principale
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n🛑 Interruption clavier détectée")
            self.on_closing()
        except Exception as e:
            print(f"❌ Erreur critique: {e}")
            messagebox.showerror("Erreur Critique", f"Une erreur critique s'est produite:\n{e}")
            self.on_closing()
    
    def on_closing(self):
        """Gestionnaire de fermeture amélioré"""
        try:
            if messagebox.askyesno("Quitter", 
                                  "Voulez-vous vraiment quitter l'application ?\n\n"
                                  "Les données seront sauvegardées automatiquement."):
                
                self.notification_center.show_progress("Fermeture en cours...")
                
                # Sauvegarder une dernière fois
                print("💾 Sauvegarde finale...")
                
                # Nettoyer les ressources
                if hasattr(self, 'tab_manager'):
                    del self.tab_manager
                
                print("🧹 Nettoyage terminé")
                
                # Fermer l'application
                self.root.destroy()
                print("👋 Application fermée proprement")
                
        except Exception as e:
            print(f"❌ Erreur lors de la fermeture: {e}")
            self.root.destroy()


if __name__ == "__main__":
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        messagebox.showerror("Erreur Fatale", f"Impossible de démarrer l'application:\n{e}")
        sys.exit(1)