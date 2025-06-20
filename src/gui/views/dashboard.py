"""
Vue du tableau de bord principal
Affichage en temps réel des statistiques et état de l'aéroport
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DashboardView(ttk.Frame):
    """Vue du tableau de bord principal"""
    
    def __init__(self, parent, data_controller):
        super().__init__(parent)
        self.data_controller = data_controller
        
        # Variables d'affichage
        self.stats_vars = {}
        self.last_update = datetime.now()
        
        self.setup_ui()
        self.update_data()
        
        logger.info("Dashboard initialisé")
    
    def setup_ui(self):
        """Configure l'interface du tableau de bord"""
        
        # Configuration du scrolling
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Première ligne : Statistiques principales
        self.create_main_stats_section(scrollable_frame)
        
        # Deuxième ligne : État des vols
        self.create_flights_section(scrollable_frame)
        
        # Troisième ligne : État de la flotte
        self.create_fleet_section(scrollable_frame)
        
        # Quatrième ligne : Personnel et alertes
        self.create_personnel_alerts_section(scrollable_frame)
        
        # Cinquième ligne : Événements récents
        self.create_recent_events_section(scrollable_frame)
        
        # Pack canvas et scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_main_stats_section(self, parent):
        """Section des statistiques principales"""
        main_frame = ttk.LabelFrame(parent, text="📊 Vue d'Ensemble", padding=10)
        main_frame.pack(fill='x', padx=10, pady=5)
        
        # Créer une grille de statistiques
        stats_config = [
            ("Vols Aujourd'hui", "flights_today", "🛫"),
            ("Vols en Cours", "flights_active", "✈️"),
            ("Avions Disponibles", "aircraft_available", "🟢"),
            ("Personnel Actif", "personnel_active", "👥"),
            ("Retards", "delays_count", "⚠️"),
            ("Maintenances", "maintenance_count", "🔧")
        ]
        
        for i, (label, var_name, icon) in enumerate(stats_config):
            row = i // 3
            col = i % 3
            
            stat_frame = ttk.Frame(main_frame)
            stat_frame.grid(row=row, column=col, padx=20, pady=10, sticky='ew')
            
            # Icône et label
            ttk.Label(stat_frame, text=icon, font=('Arial', 16)).pack()
            ttk.Label(stat_frame, text=label, font=('Arial', 10)).pack()
            
            # Valeur
            self.stats_vars[var_name] = tk.StringVar(value="0")
            ttk.Label(stat_frame, textvariable=self.stats_vars[var_name], 
                     font=('Arial', 20, 'bold')).pack()
        
        # Configuration de la grille
        for i in range(3):
            main_frame.columnconfigure(i, weight=1)
    
    def create_flights_section(self, parent):
        """Section état des vols"""
        flights_frame = ttk.LabelFrame(parent, text="🛫 État des Vols", padding=10)
        flights_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame pour les graphiques de statut
        status_frame = ttk.Frame(flights_frame)
        status_frame.pack(fill='x', pady=5)
        
        # Labels pour les statuts de vol
        statuses = [
            ("Programmés", "flights_scheduled", "#3498db"),
            ("En Vol", "flights_in_flight", "#2ecc71"),
            ("Retardés", "flights_delayed", "#f39c12"),
            ("Annulés", "flights_cancelled", "#e74c3c")
        ]
        
        for i, (label, var_name, color) in enumerate(statuses):
            frame = ttk.Frame(status_frame)
            frame.pack(side='left', fill='x', expand=True, padx=10)
            
            ttk.Label(frame, text=label, font=('Arial', 10)).pack()
            self.stats_vars[var_name] = tk.StringVar(value="0")
            label_widget = ttk.Label(frame, textvariable=self.stats_vars[var_name], 
                                   font=('Arial', 16, 'bold'))
            label_widget.pack()
        
        # Prochains vols
        next_flights_frame = ttk.LabelFrame(flights_frame, text="Prochains Départs", padding=5)
        next_flights_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview pour les prochains vols
        columns = ('Vol', 'Destination', 'Heure', 'Statut')
        self.next_flights_tree = ttk.Treeview(next_flights_frame, columns=columns, 
                                            show='headings', height=6)
        
        for col in columns:
            self.next_flights_tree.heading(col, text=col)
            self.next_flights_tree.column(col, width=120)
        
        # Scrollbar pour le treeview
        next_scrollbar = ttk.Scrollbar(next_flights_frame, orient='vertical', 
                                     command=self.next_flights_tree.yview)
        self.next_flights_tree.configure(yscrollcommand=next_scrollbar.set)
        
        self.next_flights_tree.pack(side='left', fill='both', expand=True)
        next_scrollbar.pack(side='right', fill='y')
    
    def create_fleet_section(self, parent):
        """Section état de la flotte"""
        fleet_frame = ttk.LabelFrame(parent, text="✈️ État de la Flotte", padding=10)
        fleet_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame pour les statuts des avions
        aircraft_status_frame = ttk.Frame(fleet_frame)
        aircraft_status_frame.pack(fill='x', pady=5)
        
        # Statuts des avions
        aircraft_statuses = [
            ("Disponibles", "aircraft_available", "#2ecc71"),
            ("En Vol", "aircraft_in_flight", "#3498db"),
            ("Maintenance", "aircraft_maintenance", "#f39c12"),
            ("Hors Service", "aircraft_out_of_service", "#e74c3c")
        ]
        
        for i, (label, var_name, color) in enumerate(aircraft_statuses):
            frame = ttk.Frame(aircraft_status_frame)
            frame.pack(side='left', fill='x', expand=True, padx=10)
            
            ttk.Label(frame, text=label, font=('Arial', 10)).pack()
            if var_name not in self.stats_vars:
                self.stats_vars[var_name] = tk.StringVar(value="0")
            label_widget = ttk.Label(frame, textvariable=self.stats_vars[var_name], 
                                   font=('Arial', 16, 'bold'))
            label_widget.pack()
        
        # Prochaines maintenances
        maintenance_frame = ttk.LabelFrame(fleet_frame, text="Prochaines Maintenances", padding=5)
        maintenance_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('Avion', 'Type', 'Programmée', 'Durée')
        self.maintenance_tree = ttk.Treeview(maintenance_frame, columns=columns, 
                                           show='headings', height=4)
        
        for col in columns:
            self.maintenance_tree.heading(col, text=col)
            self.maintenance_tree.column(col, width=120)
        
        maintenance_scrollbar = ttk.Scrollbar(maintenance_frame, orient='vertical', 
                                             command=self.maintenance_tree.yview)
        self.maintenance_tree.configure(yscrollcommand=maintenance_scrollbar.set)
        
        self.maintenance_tree.pack(side='left', fill='both', expand=True)
        maintenance_scrollbar.pack(side='right', fill='y')
    
    def create_personnel_alerts_section(self, parent):
        """Section personnel et alertes"""
        section_frame = ttk.Frame(parent)
        section_frame.pack(fill='x', padx=10, pady=5)
        
        # Personnel (gauche)
        personnel_frame = ttk.LabelFrame(section_frame, text="👥 Personnel", padding=10)
        personnel_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        personnel_stats = [
            ("Pilotes Disponibles", "pilots_available"),
            ("Personnel Navigant", "crew_available"),
            ("Équipes Actives", "teams_active")
        ]
        
        for label, var_name in personnel_stats:
            frame = ttk.Frame(personnel_frame)
            frame.pack(fill='x', pady=2)
            
            ttk.Label(frame, text=label + ":", width=20, anchor='w').pack(side='left')
            self.stats_vars[var_name] = tk.StringVar(value="0")
            ttk.Label(frame, textvariable=self.stats_vars[var_name], 
                     font=('Arial', 12, 'bold')).pack(side='left')
        
        # Alertes (droite)
        alerts_frame = ttk.LabelFrame(section_frame, text="⚠️ Alertes", padding=10)
        alerts_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Zone d'affichage des alertes
        self.alerts_text = tk.Text(alerts_frame, height=6, wrap='word', 
                                  font=('Arial', 9), state='disabled')
        alerts_scrollbar = ttk.Scrollbar(alerts_frame, orient='vertical', 
                                       command=self.alerts_text.yview)
        self.alerts_text.configure(yscrollcommand=alerts_scrollbar.set)
        
        self.alerts_text.pack(side='left', fill='both', expand=True)
        alerts_scrollbar.pack(side='right', fill='y')
    
    def create_recent_events_section(self, parent):
        """Section événements récents"""
        events_frame = ttk.LabelFrame(parent, text="📋 Événements Récents", padding=10)
        events_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview pour les événements
        columns = ('Heure', 'Type', 'Description')
        self.events_tree = ttk.Treeview(events_frame, columns=columns, 
                                       show='headings', height=8)
        
        # Configuration des colonnes
        self.events_tree.heading('Heure', text='Heure')
        self.events_tree.heading('Type', text='Type')
        self.events_tree.heading('Description', text='Description')
        
        self.events_tree.column('Heure', width=80)
        self.events_tree.column('Type', width=100)
        self.events_tree.column('Description', width=400)
        
        # Scrollbar pour les événements
        events_scrollbar = ttk.Scrollbar(events_frame, orient='vertical', 
                                       command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=events_scrollbar.set)
        
        self.events_tree.pack(side='left', fill='both', expand=True)
        events_scrollbar.pack(side='right', fill='y')
        
        # Bouton de rafraîchissement
        refresh_btn = ttk.Button(events_frame, text="🔄 Actualiser", 
                               command=self.update_data)
        refresh_btn.pack(pady=5)
    
    def update_data(self):
        """Met à jour toutes les données du tableau de bord"""
        try:
            # Récupérer les statistiques
            stats = self.data_controller.get_statistics()
            current_time = self.data_controller.simulator.current_time
            
            # Mettre à jour les statistiques principales
            self.update_main_stats(stats, current_time)
            
            # Mettre à jour les sections spécialisées
            self.update_flights_data(stats, current_time)
            self.update_fleet_data(stats)
            self.update_personnel_data(stats)
            self.update_alerts()
            self.update_recent_events()
            
            self.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Erreur mise à jour dashboard: {e}")
    
    def update_main_stats(self, stats, current_time):
        """Met à jour les statistiques principales"""
        
        # Calculer les vols d'aujourd'hui
        today_flights = 0
        for vol_data in self.data_controller.get_all_vols():
            vol = vol_data['vol']
            if vol.heure_depart.date() == current_time.date():
                today_flights += 1
        
        # Mettre à jour les variables
        self.stats_vars['flights_today'].set(str(today_flights))
        self.stats_vars['flights_active'].set(str(stats['vols']['en_cours']))
        self.stats_vars['aircraft_available'].set(str(stats['avions']['disponibles']))
        self.stats_vars['personnel_active'].set(str(stats['personnel']['disponible']))
        self.stats_vars['delays_count'].set(str(stats['vols']['retardes']))
        self.stats_vars['maintenance_count'].set(str(stats['avions']['en_maintenance']))
    
    def update_flights_data(self, stats, current_time):
        """Met à jour les données des vols"""
        
        # Statistiques par statut
        self.stats_vars['flights_scheduled'].set(str(stats['vols']['programmes']))
        self.stats_vars['flights_in_flight'].set(str(stats['vols']['en_cours']))
        self.stats_vars['flights_delayed'].set(str(stats['vols']['retardes']))
        self.stats_vars['flights_cancelled'].set(str(stats['vols']['annules']))
        
        # Prochains vols
        self.update_next_flights(current_time)
    
    def update_next_flights(self, current_time):
        """Met à jour la liste des prochains vols"""
        
        # Vider l'arbre
        for item in self.next_flights_tree.get_children():
            self.next_flights_tree.delete(item)
        
        # Récupérer les vols programmés
        next_flights = []
        for vol_data in self.data_controller.get_all_vols():
            vol = vol_data['vol']
            if (vol.heure_depart > current_time and 
                vol.heure_depart <= current_time + timedelta(hours=6)):
                next_flights.append(vol)
        
        # Trier par heure de départ
        next_flights.sort(key=lambda v: v.heure_depart)
        
        # Afficher les 10 prochains
        for vol in next_flights[:10]:
            destination = getattr(vol.aeroport_arrivee, 'code_iata', 'N/A')
            heure = vol.heure_depart.strftime('%H:%M')
            statut = vol.statut.obtenir_nom_affichage()
            
            self.next_flights_tree.insert('', 'end', values=(
                vol.numero_vol, destination, heure, statut
            ))
    
    def update_fleet_data(self, stats):
        """Met à jour les données de la flotte"""
        
        # Déjà mis à jour dans update_main_stats pour aircraft_available
        self.stats_vars['aircraft_in_flight'].set(str(stats['avions']['en_vol']))
        
        # Prochaines maintenances
        self.update_maintenance_schedule()
    
    def update_maintenance_schedule(self):
        """Met à jour le planning des maintenances"""
        
        # Vider l'arbre
        for item in self.maintenance_tree.get_children():
            self.maintenance_tree.delete(item)
        
        # Récupérer les maintenances programmées
        maintenance_schedule = self.data_controller.get_maintenance_schedule()
        
        for item in maintenance_schedule[:5]:  # 5 prochaines
            event = item['event']
            avion = item['avion']
            
            self.maintenance_tree.insert('', 'end', values=(
                avion.num_id,
                'Maintenance',
                event.event_time.strftime('%m/%d %H:%M'),
                event.data.get('duree_heures', 4)
            ))
    
    def update_personnel_data(self, stats):
        """Met à jour les données du personnel"""
        
        # Compter par type
        pilots = 0
        crew = 0
        active_teams = 0
        
        for personnel_data in self.data_controller.get_all_personnels():
            personnel = personnel_data['personnel']
            if personnel.disponible:
                if personnel.type_personnel.value == 'pilote':
                    pilots += 1
                elif personnel.type_personnel.value in ['hotesse', 'steward']:
                    crew += 1
        
        # Estimer les équipes actives (simplification)
        active_teams = stats['vols']['en_cours']
        
        self.stats_vars['pilots_available'].set(str(pilots))
        self.stats_vars['crew_available'].set(str(crew))
        self.stats_vars['teams_active'].set(str(active_teams))
    
    def update_alerts(self):
        """Met à jour les alertes"""
        
        self.alerts_text.config(state='normal')
        self.alerts_text.delete(1.0, tk.END)
        
        alerts = []
        
        # Vérifier les retards
        delayed_flights = len([v for v in self.data_controller.get_all_vols() 
                              if v['vol'].statut.value == 'retarde'])
        if delayed_flights > 0:
            alerts.append(f"⚠️ {delayed_flights} vol(s) retardé(s)")
        
        # Vérifier les maintenances urgentes
        maintenance_count = len(self.data_controller.get_maintenance_schedule())
        if maintenance_count > 5:
            alerts.append(f"🔧 {maintenance_count} maintenances programmées")
        
        # Vérifier la disponibilité des avions
        stats = self.data_controller.get_statistics()
        if stats['avions']['disponibles'] < 3:
            alerts.append("🚨 Peu d'avions disponibles")
        
        # Vérifier le personnel
        if stats['personnel']['disponible'] < 10:
            alerts.append("👥 Personnel insuffisant")
        
        # Afficher les alertes
        if alerts:
            for alert in alerts:
                self.alerts_text.insert(tk.END, alert + "\n")
        else:
            self.alerts_text.insert(tk.END, "✅ Aucune alerte active\n")
        
        self.alerts_text.config(state='disabled')
    
    def update_recent_events(self):
        """Met à jour les événements récents"""
        
        # Vider l'arbre
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        try:
            # Charger les événements récents
            events_log = self.data_controller.data_manager.load_data('events')
            
            # Prendre les 20 derniers événements
            recent_events = events_log[-20:] if events_log else []
            recent_events.reverse()  # Plus récents en premier
            
            for event in recent_events:
                timestamp = datetime.fromisoformat(event['timestamp'])
                heure = timestamp.strftime('%H:%M:%S')
                
                # Extraire le type d'événement
                message = event['message']
                if '[VOL]' in message:
                    event_type = "Vol"
                elif '[AVION]' in message:
                    event_type = "Avion"
                elif '[MAINTENANCE]' in message:
                    event_type = "Maintenance"
                else:
                    event_type = "Système"
                
                # Nettoyer le message
                clean_message = message.replace('[VOL]', '').replace('[AVION]', '').replace('[MAINTENANCE]', '').strip()
                
                self.events_tree.insert('', 'end', values=(
                    heure, event_type, clean_message
                ))
                
        except Exception as e:
            logger.error(f"Erreur chargement événements: {e}")
            # Insérer un message d'erreur
            self.events_tree.insert('', 'end', values=(
                datetime.now().strftime('%H:%M:%S'), 
                "Erreur", 
                "Impossible de charger les événements"
            ))
    
    def refresh_data(self):
        """Force la mise à jour des données (appelé depuis l'extérieur)"""
        self.update_data()
    
    def get_summary_info(self):
        """Retourne un résumé des informations pour la barre de statut"""
        try:
            stats = self.data_controller.get_statistics()
            return {
                'vols_actifs': stats['vols']['en_cours'],
                'avions_disponibles': stats['avions']['disponibles'],
                'retards': stats['vols']['retardes'],
                'derniere_maj': self.last_update.strftime('%H:%M:%S')
            }
        except:
            return {
                'vols_actifs': 0,
                'avions_disponibles': 0,
                'retards': 0,
                'derniere_maj': 'N/A'
            }