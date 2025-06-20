"""
Vue de gestion des vols
Interface complète pour créer, modifier et surveiller les vols
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FlightManagementView(ttk.Frame):
    """Vue de gestion des vols"""
    
    def __init__(self, parent, data_controller):
        super().__init__(parent)
        self.data_controller = data_controller
        
        # Variables d'interface
        self.selected_flight_id = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Tous")
        
        self.setup_ui()
        self.refresh_data()
        
        logger.info("Vue gestion des vols initialisée")
    
    def setup_ui(self):
        """Configure l'interface de gestion des vols"""
        
        # Barre d'outils supérieure
        self.create_toolbar()
        
        # Frame principal avec deux panneaux
        main_paned = ttk.PanedWindow(self, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Panneau gauche : Liste des vols
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        self.create_flights_list(left_frame)
        
        # Panneau droit : Détails du vol sélectionné
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        self.create_flight_details(right_frame)
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Boutons d'action (gauche)
        buttons_frame = ttk.Frame(toolbar)
        buttons_frame.pack(side='left')
        
        ttk.Button(buttons_frame, text="➕ Nouveau Vol", 
                  command=self.show_add_flight_dialog).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="✏️ Modifier", 
                  command=self.modify_flight).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="❌ Annuler Vol", 
                  command=self.cancel_flight).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="⏰ Retarder", 
                  command=self.delay_flight_dialog).pack(side='left', padx=2)
        
        # Séparateur
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Recherche et filtres (centre)
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side='left', padx=10)
        
        ttk.Label(search_frame, text="🔍 Recherche:").pack(side='left')
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=15)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Label(search_frame, text="Filtre:").pack(side='left', padx=(10, 5))
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var,
                                   values=["Tous", "Programmés", "En Vol", "Retardés", "Annulés"],
                                   width=12, state='readonly')
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Boutons utilitaires (droite)
        utils_frame = ttk.Frame(toolbar)
        utils_frame.pack(side='right')
        
        ttk.Button(utils_frame, text="🔄 Actualiser", 
                  command=self.refresh_data).pack(side='left', padx=2)
        ttk.Button(utils_frame, text="📊 Planning", 
                  command=self.show_schedule_view).pack(side='left', padx=2)
    
    def create_flights_list(self, parent):
        """Crée la liste des vols"""
        list_frame = ttk.LabelFrame(parent, text="📋 Liste des Vols", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview pour la liste des vols
        columns = ('Numéro', 'Départ', 'Arrivée', 'Heure Départ', 'Heure Arrivée', 
                  'Avion', 'Statut', 'Passagers')
        self.flights_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        column_widths = {'Numéro': 80, 'Départ': 80, 'Arrivée': 80, 
                        'Heure Départ': 100, 'Heure Arrivée': 100,
                        'Avion': 100, 'Statut': 90, 'Passagers': 80}
        
        for col in columns:
            self.flights_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.flights_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.flights_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.flights_tree.xview)
        self.flights_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Événements
        self.flights_tree.bind('<<TreeviewSelect>>', self.on_flight_select)
        self.flights_tree.bind('<Double-1>', self.on_flight_double_click)
        
        # Pack avec scrollbars
        self.flights_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Menu contextuel
        self.create_context_menu()
    
    def create_context_menu(self):
        """Crée le menu contextuel pour la liste des vols"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Voir Détails", command=self.view_flight_details)
        self.context_menu.add_command(label="Modifier", command=self.modify_flight)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Retarder", command=self.delay_flight_dialog)
        self.context_menu.add_command(label="Annuler", command=self.cancel_flight)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Dupliquer", command=self.duplicate_flight)
        
        # Bind du clic droit
        self.flights_tree.bind('<Button-3>', self.show_context_menu)
    
    def create_flight_details(self, parent):
        """Crée le panneau de détails du vol"""
        details_frame = ttk.LabelFrame(parent, text="📄 Détails du Vol", padding=10)
        details_frame.pack(fill='both', expand=True)
        
        # Notebook pour organiser les détails
        details_notebook = ttk.Notebook(details_frame)
        details_notebook.pack(fill='both', expand=True)
        
        # Onglet Informations générales
        self.create_general_info_tab(details_notebook)
        
        # Onglet Passagers
        self.create_passengers_tab(details_notebook)
        
        # Onglet Personnel
        self.create_crew_tab(details_notebook)
        
        # Onglet Événements
        self.create_events_tab(details_notebook)
    
    def create_general_info_tab(self, parent):
        """Onglet informations générales"""
        info_frame = ttk.Frame(parent)
        parent.add(info_frame, text="ℹ️ Infos")
        
        # Variables pour les détails
        self.flight_details_vars = {
            'numero_vol': tk.StringVar(),
            'aeroport_depart': tk.StringVar(),
            'aeroport_arrivee': tk.StringVar(),
            'heure_depart': tk.StringVar(),
            'heure_arrivee': tk.StringVar(),
            'avion': tk.StringVar(),
            'statut': tk.StringVar(),
            'distance': tk.StringVar(),
            'duree': tk.StringVar(),
            'passagers_count': tk.StringVar(),
            'personnel_count': tk.StringVar()
        }
        
        # Affichage des informations
        info_labels = [
            ("Numéro de Vol:", 'numero_vol'),
            ("Aéroport de Départ:", 'aeroport_depart'),
            ("Aéroport d'Arrivée:", 'aeroport_arrivee'),
            ("Heure de Départ:", 'heure_depart'),
            ("Heure d'Arrivée:", 'heure_arrivee'),
            ("Avion Assigné:", 'avion'),
            ("Statut:", 'statut'),
            ("Distance:", 'distance'),
            ("Durée Estimée:", 'duree'),
            ("Nombre de Passagers:", 'passagers_count'),
            ("Membres d'Équipage:", 'personnel_count')
        ]
        
        for i, (label, var_name) in enumerate(info_labels):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=5, pady=2)
            ttk.Label(info_frame, textvariable=self.flight_details_vars[var_name],
                     font=('Arial', 9)).grid(
                row=row, column=col+1, sticky='w', padx=15, pady=2)
        
        # Boutons d'action
        action_frame = ttk.Frame(info_frame)
        action_frame.grid(row=len(info_labels)//2 + 1, column=0, columnspan=4, pady=20)
        
        ttk.Button(action_frame, text="✏️ Modifier Vol", 
                  command=self.modify_flight).pack(side='left', padx=5)
        ttk.Button(action_frame, text="👥 Gérer Passagers", 
                  command=self.manage_passengers).pack(side='left', padx=5)
        ttk.Button(action_frame, text="✈️ Changer Avion", 
                  command=self.change_aircraft).pack(side='left', padx=5)
    
    def create_passengers_tab(self, parent):
        """Onglet passagers"""
        passengers_frame = ttk.Frame(parent)
        parent.add(passengers_frame, text="👥 Passagers")
        
        # Liste des passagers
        columns = ('Nom', 'Prénom', 'Siège', 'Enregistré')
        self.passengers_tree = ttk.Treeview(passengers_frame, columns=columns, show='headings')
        
        for col in columns:
            self.passengers_tree.heading(col, text=col)
            self.passengers_tree.column(col, width=100)
        
        passengers_scrollbar = ttk.Scrollbar(passengers_frame, orient='vertical', 
                                           command=self.passengers_tree.yview)
        self.passengers_tree.configure(yscrollcommand=passengers_scrollbar.set)
        
        self.passengers_tree.pack(side='left', fill='both', expand=True)
        passengers_scrollbar.pack(side='right', fill='y')
        
        # Boutons de gestion des passagers
        pass_buttons_frame = ttk.Frame(passengers_frame)
        pass_buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(pass_buttons_frame, text="➕ Ajouter", 
                  command=self.add_passenger).pack(side='left', padx=2)
        ttk.Button(pass_buttons_frame, text="➖ Retirer", 
                  command=self.remove_passenger).pack(side='left', padx=2)
        ttk.Button(pass_buttons_frame, text="💺 Assigner Siège", 
                  command=self.assign_seat).pack(side='left', padx=2)
    
    def create_crew_tab(self, parent):
        """Onglet personnel"""
        crew_frame = ttk.Frame(parent)
        parent.add(crew_frame, text="👨‍✈️ Équipage")
        
        # Liste du personnel
        columns = ('Nom', 'Prénom', 'Poste', 'Disponible')
        self.crew_tree = ttk.Treeview(crew_frame, columns=columns, show='headings')
        
        for col in columns:
            self.crew_tree.heading(col, text=col)
            self.crew_tree.column(col, width=100)
        
        crew_scrollbar = ttk.Scrollbar(crew_frame, orient='vertical', 
                                     command=self.crew_tree.yview)
        self.crew_tree.configure(yscrollcommand=crew_scrollbar.set)
        
        self.crew_tree.pack(side='left', fill='both', expand=True)
        crew_scrollbar.pack(side='right', fill='y')
        
        # Boutons de gestion du personnel
        crew_buttons_frame = ttk.Frame(crew_frame)
        crew_buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(crew_buttons_frame, text="➕ Assigner", 
                  command=self.assign_crew).pack(side='left', padx=2)
        ttk.Button(crew_buttons_frame, text="➖ Retirer", 
                  command=self.remove_crew).pack(side='left', padx=2)
    
    def create_events_tab(self, parent):
        """Onglet événements du vol"""
        events_frame = ttk.Frame(parent)
        parent.add(events_frame, text="📅 Événements")
        
        # Liste des événements
        columns = ('Heure', 'Type', 'Description')
        self.events_tree = ttk.Treeview(events_frame, columns=columns, show='headings')
        
        for col in columns:
            self.events_tree.heading(col, text=col)
        
        self.events_tree.column('Heure', width=100)
        self.events_tree.column('Type', width=80)
        self.events_tree.column('Description', width=200)
        
        events_scrollbar = ttk.Scrollbar(events_frame, orient='vertical', 
                                       command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=events_scrollbar.set)
        
        self.events_tree.pack(side='left', fill='both', expand=True)
        events_scrollbar.pack(side='right', fill='y')
    
    # ===============================================
    # ÉVÉNEMENTS ET INTERACTIONS
    # ===============================================
    
    def on_flight_select(self, event):
        """Gestionnaire de sélection de vol"""
        selection = self.flights_tree.selection()
        if selection:
            item = selection[0]
            self.selected_flight_id = self.flights_tree.item(item)['tags'][0] if self.flights_tree.item(item)['tags'] else None
            self.update_flight_details()
    
    def on_flight_double_click(self, event):
        """Gestionnaire de double-clic sur un vol"""
        self.modify_flight()
    
    def on_search_change(self, event=None):
        """Gestionnaire de changement de recherche"""
        self.refresh_flights_list()
    
    def on_filter_change(self, event=None):
        """Gestionnaire de changement de filtre"""
        self.refresh_flights_list()
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel"""
        # Sélectionner l'item sous la souris
        item = self.flights_tree.identify_row(event.y)
        if item:
            self.flights_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def sort_by_column(self, col):
        """Trie la liste par colonne"""
        # À implémenter selon les besoins
        pass
    
    # ===============================================
    # GESTION DES DONNÉES
    # ===============================================
    
    def refresh_data(self):
        """Actualise toutes les données"""
        self.refresh_flights_list()
        self.update_flight_details()
    
    def refresh_flights_list(self):
        """Actualise la liste des vols"""
        # Vider la liste
        for item in self.flights_tree.get_children():
            self.flights_tree.delete(item)
        
        # Récupérer les vols
        all_flights = self.data_controller.get_all_vols()
        
        # Appliquer les filtres
        filtered_flights = self.apply_filters(all_flights)
        
        # Remplir la liste
        for flight_data in filtered_flights:
            flight_id = flight_data['id']
            vol = flight_data['vol']
            
            # Préparer les données d'affichage
            depart_code = getattr(vol.aeroport_depart, 'code_iata', 'N/A')
            arrivee_code = getattr(vol.aeroport_arrivee, 'code_iata', 'N/A')
            avion_id = getattr(vol.avion_utilise, 'num_id', 'N/A')
            
            values = (
                vol.numero_vol,
                depart_code,
                arrivee_code,
                vol.heure_depart.strftime('%H:%M'),
                vol.heure_arrivee_prevue.strftime('%H:%M'),
                avion_id,
                vol.statut.obtenir_nom_affichage(),
                len(vol.passagers)
            )
            
            # Insérer avec tag pour l'ID
            item = self.flights_tree.insert('', 'end', values=values, tags=(flight_id,))
            
            # Coloration selon le statut
            self.apply_status_colors(item, vol.statut)
    
    def apply_filters(self, flights):
        """Applique les filtres de recherche et de statut"""
        filtered = flights
        
        # Filtre de recherche
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [f for f in filtered 
                       if search_term in f['vol'].numero_vol.lower()]
        
        # Filtre de statut
        filter_status = self.filter_var.get()
        if filter_status != "Tous":
            status_map = {
                "Programmés": "programme",
                "En Vol": "en_vol", 
                "Retardés": "retarde",
                "Annulés": "annule"
            }
            if filter_status in status_map:
                filtered = [f for f in filtered 
                           if f['vol'].statut.value == status_map[filter_status]]
        
        return filtered
    
    def apply_status_colors(self, item, statut):
        """Applique les couleurs selon le statut"""
        colors = {
            'programme': ('black', '#e8f4fd'),
            'en_vol': ('black', '#e8f8f0'),
            'retarde': ('black', '#fff3cd'),
            'annule': ('black', '#f8d7da'),
            'termine': ('gray', '#f8f9fa')
        }
        
        if statut.value in colors:
            fg, bg = colors[statut.value]
            self.flights_tree.set(item, '#0', '')  # Couleur de fond
    
    def update_flight_details(self):
        """Met à jour les détails du vol sélectionné"""
        if not self.selected_flight_id:
            # Vider les détails
            for var in self.flight_details_vars.values():
                var.set("")
            return
        
        # Trouver le vol
        flight_data = None
        for f in self.data_controller.get_all_vols():
            if f['id'] == self.selected_flight_id:
                flight_data = f
                break
        
        if not flight_data:
            return
        
        vol = flight_data['vol']
        
        # Mettre à jour les variables
        self.flight_details_vars['numero_vol'].set(vol.numero_vol)
        self.flight_details_vars['aeroport_depart'].set(
            getattr(vol.aeroport_depart, 'nom', 'N/A'))
        self.flight_details_vars['aeroport_arrivee'].set(
            getattr(vol.aeroport_arrivee, 'nom', 'N/A'))
        self.flight_details_vars['heure_depart'].set(
            vol.heure_depart.strftime('%Y-%m-%d %H:%M'))
        self.flight_details_vars['heure_arrivee'].set(
            vol.heure_arrivee_prevue.strftime('%Y-%m-%d %H:%M'))
        self.flight_details_vars['avion'].set(
            getattr(vol.avion_utilise, 'num_id', 'N/A'))
        self.flight_details_vars['statut'].set(vol.statut.obtenir_nom_affichage())
        self.flight_details_vars['distance'].set(f"{vol.calculer_distance():.0f} km")
        self.flight_details_vars['duree'].set(str(vol.obtenir_duree_estimee()))
        self.flight_details_vars['passagers_count'].set(str(len(vol.passagers)))
        self.flight_details_vars['personnel_count'].set(str(len(vol.personnel)))
        
        # Mettre à jour les listes
        self.update_passengers_list(vol)
        self.update_crew_list(vol)
        self.update_events_list(vol)
    
    def update_passengers_list(self, vol):
        """Met à jour la liste des passagers"""
        # Vider la liste
        for item in self.passengers_tree.get_children():
            self.passengers_tree.delete(item)
        
        # Remplir avec les passagers du vol
        for passager in vol.passagers:
            nom = getattr(passager, 'nom', 'N/A')
            prenom = getattr(passager, 'prenom', 'N/A')
            siege = getattr(passager, 'siege_assigne', 'Non assigné')
            enregistre = "Oui" if getattr(passager, 'checkin_effectue', False) else "Non"
            
            self.passengers_tree.insert('', 'end', values=(nom, prenom, siege, enregistre))
    
    def update_crew_list(self, vol):
        """Met à jour la liste de l'équipage"""
        # Vider la liste
        for item in self.crew_tree.get_children():
            self.crew_tree.delete(item)
        
        # Remplir avec le personnel du vol
        for membre in vol.personnel:
            nom = getattr(membre, 'nom', 'N/A')
            prenom = getattr(membre, 'prenom', 'N/A')
            poste = getattr(membre, 'type_personnel', 'N/A')
            if hasattr(poste, 'obtenir_nom_affichage'):
                poste = poste.obtenir_nom_affichage()
            disponible = "Oui" if getattr(membre, 'disponible', True) else "Non"
            
            self.crew_tree.insert('', 'end', values=(nom, prenom, poste, disponible))
    
    def update_events_list(self, vol):
        """Met à jour la liste des événements du vol"""
        # Vider la liste
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Ajouter les événements programmés pour ce vol
        events = self.data_controller.simulator.get_scheduled_events('vol')
        for event in events:
            if event.target_id == self.selected_flight_id:
                heure = event.event_time.strftime('%H:%M')
                type_event = event.action.title()
                description = f"{event.action} - {event.data.get('numero_vol', '')}"
                
                self.events_tree.insert('', 'end', values=(heure, type_event, description))
    
    # ===============================================
    # ACTIONS ET DIALOGUES
    # ===============================================
    
    def show_add_flight_dialog(self):
        """Affiche le dialogue de création de vol"""
        messagebox.showinfo("Nouveau Vol", "Dialogue de création de vol à implémenter")
    
    def modify_flight(self):
        """Modifie le vol sélectionné"""
        if not self.selected_flight_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un vol à modifier")
            return
        messagebox.showinfo("Modifier Vol", "Dialogue de modification de vol à implémenter")
    
    def cancel_flight(self):
        """Annule le vol sélectionné"""
        if not self.selected_flight_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un vol à annuler")
            return
        
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment annuler ce vol ?"):
            # Logique d'annulation
            messagebox.showinfo("Vol Annulé", "Vol annulé avec succès")
            self.refresh_data()
    
    def delay_flight_dialog(self):
        """Affiche le dialogue de retard"""
        if not self.selected_flight_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un vol")
            return
        messagebox.showinfo("Retarder Vol", "Dialogue de retard à implémenter")
    
    def duplicate_flight(self):
        """Duplique le vol sélectionné"""
        if not self.selected_flight_id:
            return
        messagebox.showinfo("Dupliquer Vol", "Fonction de duplication à implémenter")
    
    def view_flight_details(self):
        """Affiche les détails complets du vol"""
        if not self.selected_flight_id:
            return
        messagebox.showinfo("Détails Vol", "Vue détaillée à implémenter")
    
    def manage_passengers(self):
        """Gère les passagers du vol"""
        messagebox.showinfo("Gestion Passagers", "Interface de gestion des passagers à implémenter")
    
    def change_aircraft(self):
        """Change l'avion assigné au vol"""
        messagebox.showinfo("Changer Avion", "Interface de changement d'avion à implémenter")
    
    def add_passenger(self):
        """Ajoute un passager au vol"""
        self.show_add_passenger_dialog()
        
    def remove_passenger(self):
        """Retire un passager du vol"""
        messagebox.showinfo("Retirer Passager", "Fonction de retrait à implémenter")
    
    def assign_seat(self):
        """Assigne un siège à un passager"""
        messagebox.showinfo("Assigner Siège", "Interface d'assignation de siège à implémenter")
    
    def assign_crew(self):
        """Assigne du personnel au vol"""
        messagebox.showinfo("Assigner Équipage", "Interface d'assignation d'équipage à implémenter")
    
    def remove_crew(self):
        """Retire du personnel du vol"""
        messagebox.showinfo("Retirer Équipage", "Fonction de retrait d'équipage à implémenter")
    
    def show_schedule_view(self):
        """Affiche une vue planning des vols"""
        schedule_window = tk.Toplevel(self)
        schedule_window.title("Planning des Vols")
        schedule_window.geometry("900x600")
        schedule_window.transient(self)
        
        # Récupérer le planning du jour
        current_date = self.data_controller.simulator.current_time.date()
        schedule = self.data_controller.get_flight_schedule(datetime.combine(current_date, datetime.min.time()))
        
        # Créer un treeview pour le planning
        columns = ('Heure', 'Vol', 'Route', 'Avion', 'Statut', 'Passagers')
        schedule_tree = ttk.Treeview(schedule_window, columns=columns, show='headings')
        
        for col in columns:
            schedule_tree.heading(col, text=col)
            schedule_tree.column(col, width=120)
        
        # Remplir le planning
        for item in schedule:
            vol = item['vol']
            route = f"{getattr(vol.aeroport_depart, 'code_iata', 'N/A')} → {getattr(vol.aeroport_arrivee, 'code_iata', 'N/A')}"
            
            schedule_tree.insert('', 'end', values=(
                vol.heure_depart.strftime('%H:%M'),
                vol.numero_vol,
                route,
                getattr(vol.avion_utilise, 'num_id', 'N/A'),
                vol.statut.obtenir_nom_affichage(),
                len(vol.passagers)
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(schedule_window, orient='vertical', command=schedule_tree.yview)
        schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        schedule_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Bouton fermer
        ttk.Button(schedule_window, text="Fermer", 
                  command=schedule_window.destroy).pack(pady=10)
        
    def show_add_flight_dialog(self):
        """Affiche le dialogue de création de vol"""
        from .creation_dialogs import FlightCreationDialog
        
        dialog = FlightCreationDialog(self, self.data_controller, 
                                    callback=lambda flight_id: self.refresh_data())
        # La fenêtre est modale, pas besoin de wait_window

    def show_add_passenger_dialog(self):
        """Affiche le dialogue de création de passager"""
        from .creation_dialogs import PassengerCreationDialog
        
        dialog = PassengerCreationDialog(self, self.data_controller,
                                    callback=lambda passager_id: self.refresh_data())   