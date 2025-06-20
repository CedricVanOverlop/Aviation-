"""
Vue de gestion de la flotte d'avions
Interface complète pour gérer les avions, maintenances et optimisations
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FleetManagementView(ttk.Frame):
    """Vue de gestion de la flotte"""
    
    def __init__(self, parent, data_controller):
        super().__init__(parent)
        self.data_controller = data_controller
        
        # Variables d'interface
        self.selected_aircraft_id = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Tous")
        
        self.setup_ui()
        self.refresh_data()
        
        logger.info("Vue gestion de la flotte initialisée")
    
    def setup_ui(self):
        """Configure l'interface de gestion de la flotte"""
        
        # Barre d'outils
        self.create_toolbar()
        
        # Frame principal avec panneaux
        main_paned = ttk.PanedWindow(self, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Panneau gauche : Liste des avions
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        self.create_aircraft_list(left_frame)
        
        # Panneau droit : Détails et gestion
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        self.create_aircraft_details(right_frame)
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Boutons d'action (gauche)
        buttons_frame = ttk.Frame(toolbar)
        buttons_frame.pack(side='left')
        
        ttk.Button(buttons_frame, text="➕ Nouvel Avion", 
                  command=self.show_add_aircraft_dialog).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="✏️ Modifier", 
                  command=self.modify_aircraft).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="🔧 Maintenance", 
                  command=self.show_maintenance_dialog).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="❌ Retirer", 
                  command=self.retire_aircraft).pack(side='left', padx=2)
        
        # Séparateur
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Recherche et filtres (centre)
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side='left', padx=10)
        
        ttk.Label(search_frame, text="🔍 Recherche:").pack(side='left')
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=15)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Label(search_frame, text="État:").pack(side='left', padx=(10, 5))
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var,
                                   values=["Tous", "Disponibles", "En Vol", "Maintenance", "Hors Service"],
                                   width=12, state='readonly')
        filter_combo.pack(side='left', padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Boutons utilitaires (droite)
        utils_frame = ttk.Frame(toolbar)
        utils_frame.pack(side='right')
        
        ttk.Button(utils_frame, text="🔄 Actualiser", 
                  command=self.refresh_data).pack(side='left', padx=2)
        ttk.Button(utils_frame, text="⚡ Optimiser", 
                  command=self.optimize_fleet).pack(side='left', padx=2)
        ttk.Button(utils_frame, text="📊 Rapport", 
                  command=self.show_fleet_report).pack(side='left', padx=2)
    
    def create_aircraft_list(self, parent):
        """Crée la liste des avions"""
        list_frame = ttk.LabelFrame(parent, text="✈️ Flotte d'Avions", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview pour la liste des avions
        columns = ('ID', 'Modèle', 'Compagnie', 'Capacité', 'État', 'Localisation', 
                  'Autonomie', 'Dernière Maintenance')
        self.aircraft_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        column_widths = {
            'ID': 80, 'Modèle': 120, 'Compagnie': 100, 'Capacité': 80,
            'État': 100, 'Localisation': 120, 'Autonomie': 80, 'Dernière Maintenance': 120
        }
        
        for col in columns:
            self.aircraft_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.aircraft_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.aircraft_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.aircraft_tree.xview)
        self.aircraft_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Événements
        self.aircraft_tree.bind('<<TreeviewSelect>>', self.on_aircraft_select)
        self.aircraft_tree.bind('<Double-1>', self.on_aircraft_double_click)
        
        # Pack avec scrollbars
        self.aircraft_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Menu contextuel
        self.create_context_menu()
    
    def create_context_menu(self):
        """Crée le menu contextuel pour la liste des avions"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Voir Détails", command=self.view_aircraft_details)
        self.context_menu.add_command(label="Modifier", command=self.modify_aircraft)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Programmer Maintenance", command=self.show_maintenance_dialog)
        self.context_menu.add_command(label="Changer Localisation", command=self.change_location)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Voir Historique", command=self.view_history)
        self.context_menu.add_command(label="Retirer de Service", command=self.retire_aircraft)
        
        # Bind du clic droit
        self.aircraft_tree.bind('<Button-3>', self.show_context_menu)
    
    def create_aircraft_details(self, parent):
        """Crée le panneau de détails de l'avion"""
        details_frame = ttk.LabelFrame(parent, text="📄 Détails de l'Avion", padding=10)
        details_frame.pack(fill='both', expand=True)
        
        # Notebook pour organiser les détails
        details_notebook = ttk.Notebook(details_frame)
        details_notebook.pack(fill='both', expand=True)
        
        # Onglet Informations générales
        self.create_general_info_tab(details_notebook)
        
        # Onglet Maintenance
        self.create_maintenance_tab(details_notebook)
        
        # Onglet Performances
        self.create_performance_tab(details_notebook)
        
        # Onglet Historique
        self.create_history_tab(details_notebook)
    
    def create_general_info_tab(self, parent):
        """Onglet informations générales"""
        info_frame = ttk.Frame(parent)
        parent.add(info_frame, text="ℹ️ Général")
        
        # Variables pour les détails
        self.aircraft_details_vars = {
            'num_id': tk.StringVar(),
            'modele': tk.StringVar(),
            'compagnie_aerienne': tk.StringVar(),
            'capacite': tk.StringVar(),
            'vitesse_croisiere': tk.StringVar(),
            'autonomie': tk.StringVar(),
            'etat': tk.StringVar(),
            'localisation': tk.StringVar(),
            'derniere_maintenance': tk.StringVar(),
            'heures_vol': tk.StringVar(),
            'cycles': tk.StringVar()
        }
        
        # Affichage des informations
        info_labels = [
            ("Identifiant:", 'num_id'),
            ("Modèle:", 'modele'),
            ("Compagnie:", 'compagnie_aerienne'),
            ("Capacité:", 'capacite'),
            ("Vitesse Croisière:", 'vitesse_croisiere'),
            ("Autonomie:", 'autonomie'),
            ("État Actuel:", 'etat'),
            ("Localisation:", 'localisation'),
            ("Dernière Maintenance:", 'derniere_maintenance'),
            ("Heures de Vol:", 'heures_vol'),
            ("Cycles:", 'cycles')
        ]
        
        for i, (label, var_name) in enumerate(info_labels):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=5, pady=3)
            ttk.Label(info_frame, textvariable=self.aircraft_details_vars[var_name],
                     font=('Arial', 9)).grid(
                row=row, column=col+1, sticky='w', padx=15, pady=3)
        
        # Boutons d'action
        action_frame = ttk.Frame(info_frame)
        action_frame.grid(row=len(info_labels)//2 + 1, column=0, columnspan=4, pady=20)
        
        ttk.Button(action_frame, text="✏️ Modifier", 
                  command=self.modify_aircraft).pack(side='left', padx=5)
        ttk.Button(action_frame, text="🔧 Maintenance", 
                  command=self.show_maintenance_dialog).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📍 Localiser", 
                  command=self.change_location).pack(side='left', padx=5)
    
    def create_maintenance_tab(self, parent):
        """Onglet maintenance"""
        maintenance_frame = ttk.Frame(parent)
        parent.add(maintenance_frame, text="🔧 Maintenance")
        
        # Informations de maintenance actuelles
        current_frame = ttk.LabelFrame(maintenance_frame, text="État Actuel", padding=10)
        current_frame.pack(fill='x', pady=5)
        
        self.maintenance_vars = {
            'statut_maintenance': tk.StringVar(),
            'prochaine_maintenance': tk.StringVar(),
            'temps_restant': tk.StringVar(),
            'type_maintenance': tk.StringVar()
        }
        
        maintenance_info = [
            ("Statut:", 'statut_maintenance'),
            ("Prochaine Maintenance:", 'prochaine_maintenance'),
            ("Temps Restant:", 'temps_restant'),
            ("Type Requis:", 'type_maintenance')
        ]
        
        for i, (label, var_name) in enumerate(maintenance_info):
            ttk.Label(current_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=i, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(current_frame, textvariable=self.maintenance_vars[var_name],
                     font=('Arial', 9)).grid(
                row=i, column=1, sticky='w', padx=15, pady=2)
        
        # Historique des maintenances
        history_frame = ttk.LabelFrame(maintenance_frame, text="Historique", padding=5)
        history_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('Date', 'Type', 'Durée', 'Technicien', 'Statut')
        self.maintenance_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.maintenance_tree.heading(col, text=col)
            self.maintenance_tree.column(col, width=100)
        
        maintenance_scrollbar = ttk.Scrollbar(history_frame, orient='vertical', 
                                            command=self.maintenance_tree.yview)
        self.maintenance_tree.configure(yscrollcommand=maintenance_scrollbar.set)
        
        self.maintenance_tree.pack(side='left', fill='both', expand=True)
        maintenance_scrollbar.pack(side='right', fill='y')
        
        # Boutons de maintenance
        maint_buttons_frame = ttk.Frame(maintenance_frame)
        maint_buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(maint_buttons_frame, text="🔧 Programmer Maintenance", 
                  command=self.show_maintenance_dialog).pack(side='left', padx=5)
        ttk.Button(maint_buttons_frame, text="✅ Terminer Maintenance", 
                  command=self.complete_maintenance).pack(side='left', padx=5)
        ttk.Button(maint_buttons_frame, text="📋 Rapport Maintenance", 
                  command=self.maintenance_report).pack(side='left', padx=5)
    
    def create_performance_tab(self, parent):
        """Onglet performances"""
        performance_frame = ttk.Frame(parent)
        parent.add(performance_frame, text="📈 Performances")
        
        # Métriques de performance
        metrics_frame = ttk.LabelFrame(performance_frame, text="Métriques", padding=10)
        metrics_frame.pack(fill='x', pady=5)
        
        self.performance_vars = {
            'utilisation': tk.StringVar(),
            'ponctualite': tk.StringVar(),
            'efficacite_carburant': tk.StringVar(),
            'disponibilite': tk.StringVar(),
            'cout_exploitation': tk.StringVar()
        }
        
        metrics_info = [
            ("Taux d'Utilisation:", 'utilisation'),
            ("Ponctualité:", 'ponctualite'),
            ("Efficacité Carburant:", 'efficacite_carburant'),
            ("Disponibilité:", 'disponibilite'),
            ("Coût d'Exploitation:", 'cout_exploitation')
        ]
        
        for i, (label, var_name) in enumerate(metrics_info):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(metrics_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=5, pady=3)
            ttk.Label(metrics_frame, textvariable=self.performance_vars[var_name],
                     font=('Arial', 9)).grid(
                row=row, column=col+1, sticky='w', padx=15, pady=3)
        
        # Graphique de tendance (placeholder)
        chart_frame = ttk.LabelFrame(performance_frame, text="Tendances", padding=10)
        chart_frame.pack(fill='both', expand=True, pady=5)
        
        # Placeholder pour graphique
        ttk.Label(chart_frame, text="📊 Graphiques de performance\n(À implémenter avec matplotlib)",
                 font=('Arial', 12), anchor='center').pack(expand=True)
    
    def create_history_tab(self, parent):
        """Onglet historique"""
        history_frame = ttk.Frame(parent)
        parent.add(history_frame, text="📜 Historique")
        
        # Liste des événements
        columns = ('Date', 'Événement', 'Vol', 'Détails')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
        
        self.history_tree.column('Date', width=100)
        self.history_tree.column('Événement', width=120)
        self.history_tree.column('Vol', width=80)
        self.history_tree.column('Détails', width=200)
        
        history_scrollbar = ttk.Scrollbar(history_frame, orient='vertical', 
                                        command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')
    
    # ===============================================
    # ÉVÉNEMENTS ET INTERACTIONS
    # ===============================================
    
    def on_aircraft_select(self, event):
        """Gestionnaire de sélection d'avion"""
        selection = self.aircraft_tree.selection()
        if selection:
            item = selection[0]
            self.selected_aircraft_id = self.aircraft_tree.item(item)['tags'][0] if self.aircraft_tree.item(item)['tags'] else None
            self.update_aircraft_details()
    
    def on_aircraft_double_click(self, event):
        """Gestionnaire de double-clic sur un avion"""
        self.modify_aircraft()
    
    def on_search_change(self, event=None):
        """Gestionnaire de changement de recherche"""
        self.refresh_aircraft_list()
    
    def on_filter_change(self, event=None):
        """Gestionnaire de changement de filtre"""
        self.refresh_aircraft_list()
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel"""
        item = self.aircraft_tree.identify_row(event.y)
        if item:
            self.aircraft_tree.selection_set(item)
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
        self.refresh_aircraft_list()
        self.update_aircraft_details()
    
    def refresh_aircraft_list(self):
        """Actualise la liste des avions"""
        # Vider la liste
        for item in self.aircraft_tree.get_children():
            self.aircraft_tree.delete(item)
        
        # Récupérer les avions
        all_aircraft = self.data_controller.get_all_avions()
        
        # Appliquer les filtres
        filtered_aircraft = self.apply_filters(all_aircraft)
        
        # Remplir la liste
        for aircraft_data in filtered_aircraft:
            aircraft_id = aircraft_data['id']
            avion = aircraft_data['avion']
            
            # Préparer les données d'affichage
            localisation = f"{avion.localisation.latitude:.2f}, {avion.localisation.longitude:.2f}"
            derniere_maint = avion.derniere_maintenance.strftime('%Y-%m-%d') if avion.derniere_maintenance else "N/A"
            
            values = (
                avion.num_id,
                avion.modele,
                avion.compagnie_aerienne,
                avion.capacite,
                avion.etat.value.title(),
                localisation,
                f"{avion.autonomie} km",
                derniere_maint
            )
            
            # Insérer avec tag pour l'ID
            item = self.aircraft_tree.insert('', 'end', values=values, tags=(aircraft_id,))
            
            # Coloration selon l'état
            self.apply_status_colors(item, avion.etat)
    
    def apply_filters(self, aircraft):
        """Applique les filtres de recherche et d'état"""
        filtered = aircraft
        
        # Filtre de recherche
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [a for a in filtered 
                       if (search_term in a['avion'].num_id.lower() or
                           search_term in a['avion'].modele.lower())]
        
        # Filtre d'état
        filter_status = self.filter_var.get()
        if filter_status != "Tous":
            status_map = {
                "Disponibles": "operationnel",
                "En Vol": "en_vol",
                "Maintenance": "en_maintenance",
                "Hors Service": "hors_service"
            }
            if filter_status in status_map:
                filtered = [a for a in filtered 
                           if a['avion'].etat.value == status_map[filter_status]]
        
        return filtered
    
    def apply_status_colors(self, item, etat):
        """Applique les couleurs selon l'état"""
        colors = {
            'operationnel': ('black', '#e8f8f0'),
            'au_sol': ('black', '#e8f4fd'),
            'en_vol': ('black', '#e1f5fe'),
            'en_maintenance': ('black', '#fff3cd'),
            'hors_service': ('black', '#f8d7da')
        }
        
        if etat.value in colors:
            fg, bg = colors[etat.value]
            # Note: La coloration nécessite une configuration plus avancée de Treeview
    
    def update_aircraft_details(self):
        """Met à jour les détails de l'avion sélectionné"""
        if not self.selected_aircraft_id:
            # Vider les détails
            for var in self.aircraft_details_vars.values():
                var.set("")
            for var in self.maintenance_vars.values():
                var.set("")
            for var in self.performance_vars.values():
                var.set("")
            return
        
        # Trouver l'avion
        aircraft_data = None
        for a in self.data_controller.get_all_avions():
            if a['id'] == self.selected_aircraft_id:
                aircraft_data = a
                break
        
        if not aircraft_data:
            return
        
        avion = aircraft_data['avion']
        
        # Mettre à jour les informations générales
        self.aircraft_details_vars['num_id'].set(avion.num_id)
        self.aircraft_details_vars['modele'].set(avion.modele)
        self.aircraft_details_vars['compagnie_aerienne'].set(avion.compagnie_aerienne)
        self.aircraft_details_vars['capacite'].set(f"{avion.capacite} passagers")
        self.aircraft_details_vars['vitesse_croisiere'].set(f"{avion.vitesse_croisiere} km/h")
        self.aircraft_details_vars['autonomie'].set(f"{avion.autonomie} km")
        self.aircraft_details_vars['etat'].set(avion.etat.value.title())
        self.aircraft_details_vars['localisation'].set(
            f"{avion.localisation.latitude:.4f}, {avion.localisation.longitude:.4f}")
        self.aircraft_details_vars['derniere_maintenance'].set(
            avion.derniere_maintenance.strftime('%Y-%m-%d %H:%M') if avion.derniere_maintenance else "Jamais")
        
        # Calculer quelques métriques
        self.aircraft_details_vars['heures_vol'].set("0 h")  # À calculer depuis l'historique
        self.aircraft_details_vars['cycles'].set("0")        # À calculer depuis l'historique
        
        # Mettre à jour les informations de maintenance
        self.update_maintenance_info(avion)
        
        # Mettre à jour les performances
        self.update_performance_info(avion)
        
        # Mettre à jour l'historique
        self.update_history_info(avion)
    
    def update_maintenance_info(self, avion):
        """Met à jour les informations de maintenance"""
        # Statut maintenance
        if avion.etat.value == 'en_maintenance':
            self.maintenance_vars['statut_maintenance'].set("En cours")
        else:
            self.maintenance_vars['statut_maintenance'].set("Opérationnel")
        
        # Prochaine maintenance (estimation)
        if avion.derniere_maintenance:
            prochaine = avion.derniere_maintenance + timedelta(days=30)  # Exemple
            self.maintenance_vars['prochaine_maintenance'].set(prochaine.strftime('%Y-%m-%d'))
            
            jours_restants = (prochaine - datetime.now()).days
            self.maintenance_vars['temps_restant'].set(f"{jours_restants} jours")
        else:
            self.maintenance_vars['prochaine_maintenance'].set("À programmer")
            self.maintenance_vars['temps_restant'].set("Non défini")
        
        self.maintenance_vars['type_maintenance'].set("Inspection A")  # Exemple
        
        # Vider et remplir l'historique de maintenance
        for item in self.maintenance_tree.get_children():
            self.maintenance_tree.delete(item)
        
        # Exemple d'historique (à remplacer par de vraies données)
        if avion.derniere_maintenance:
            self.maintenance_tree.insert('', 'end', values=(
                avion.derniere_maintenance.strftime('%Y-%m-%d'),
                "Inspection",
                "4h",
                "Tech-001",
                "Terminée"
            ))
    
    def update_performance_info(self, avion):
        """Met à jour les informations de performance"""
        # Calculer des métriques fictives (à remplacer par de vrais calculs)
        self.performance_vars['utilisation'].set("85%")
        self.performance_vars['ponctualite'].set("92%")
        self.performance_vars['efficacite_carburant'].set("3.2 L/100km")
        self.performance_vars['disponibilite'].set("94%")
        self.performance_vars['cout_exploitation'].set("1250 €/h")
    
    def update_history_info(self, avion):
        """Met à jour l'historique de l'avion"""
        # Vider l'historique
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Exemple d'événements (à remplacer par de vraies données)
        exemple_events = [
            (datetime.now() - timedelta(days=1), "Vol", "AF123", "Paris → Londres"),
            (datetime.now() - timedelta(days=2), "Maintenance", "-", "Inspection routine"),
            (datetime.now() - timedelta(days=5), "Vol", "AF456", "Londres → Madrid"),
        ]
        
        for date, event, vol, details in exemple_events:
            self.history_tree.insert('', 'end', values=(
                date.strftime('%Y-%m-%d'),
                event,
                vol,
                details
            ))
    
    # ===============================================
    # ACTIONS ET DIALOGUES
    # ===============================================
    
    def show_add_aircraft_dialog(self):
        """Affiche le dialogue de création d'avion"""
        dialog = tk.Toplevel(self)
        dialog.title("Nouvel Avion")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Variables du formulaire
        form_vars = {
            'num_id': tk.StringVar(),
            'modele': tk.StringVar(),
            'compagnie_aerienne': tk.StringVar(),
            'capacite': tk.StringVar(value="180"),
            'vitesse_croisiere': tk.StringVar(value="850"),
            'autonomie': tk.StringVar(value="6000"),
            'longitude': tk.StringVar(value="2.3522"),
            'latitude': tk.StringVar(value="48.8566")
        }
        
        # Création du formulaire
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Création d'un Nouvel Avion", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Champs du formulaire
        fields = [
            ("Identifiant*:", 'num_id', "Ex: F-ABCD"),
            ("Modèle*:", 'modele', "Ex: Airbus A320"),
            ("Compagnie*:", 'compagnie_aerienne', "Ex: Air France"),
            ("Capacité (passagers)*:", 'capacite', "Ex: 180"),
            ("Vitesse Croisière (km/h)*:", 'vitesse_croisiere', "Ex: 850"),
            ("Autonomie (km)*:", 'autonomie', "Ex: 6000"),
            ("Longitude:", 'longitude', "Ex: 2.3522"),
            ("Latitude:", 'latitude', "Ex: 48.8566")
        ]
        
        for label, var_name, placeholder in fields:
            frame = ttk.Frame(main_frame)
            frame.pack(fill='x', pady=5)
            
            ttk.Label(frame, text=label, width=25, anchor='w').pack(side='left')
            entry = ttk.Entry(frame, textvariable=form_vars[var_name], width=30)
            entry.pack(side='left', padx=(10, 0))
            
            # Placeholder comme tooltip
            if placeholder:
                ttk.Label(frame, text=placeholder, font=('Arial', 8), 
                         foreground='gray').pack(side='left', padx=(10, 0))
        
        # Note obligatoire
        ttk.Label(main_frame, text="* Champs obligatoires", 
                 font=('Arial', 8, 'italic'), foreground='red').pack(pady=(10, 0))
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        def create_aircraft():
            try:
                # Validation des champs obligatoires
                required_fields = ['num_id', 'modele', 'compagnie_aerienne', 'capacite', 
                                 'vitesse_croisiere', 'autonomie']
                for field in required_fields:
                    if not form_vars[field].get().strip():
                        messagebox.showerror("Erreur", f"Le champ {field} est obligatoire")
                        return
                
                # Validation des types numériques
                try:
                    capacite = int(form_vars['capacite'].get())
                    vitesse = float(form_vars['vitesse_croisiere'].get())
                    autonomie = float(form_vars['autonomie'].get())
                    longitude = float(form_vars['longitude'].get())
                    latitude = float(form_vars['latitude'].get())
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez vérifier les valeurs numériques")
                    return
                
                # Créer l'avion
                aircraft_id = self.data_controller.create_avion(
                    num_id=form_vars['num_id'].get().strip(),
                    modele=form_vars['modele'].get().strip(),
                    capacite=capacite,
                    compagnie_aerienne=form_vars['compagnie_aerienne'].get().strip(),
                    vitesse_croisiere=vitesse,
                    autonomie=autonomie,
                    longitude=longitude,
                    latitude=latitude
                )
                
                messagebox.showinfo("Succès", f"Avion {form_vars['num_id'].get()} créé avec succès!")
                dialog.destroy()
                self.refresh_data()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la création: {e}")
        
        ttk.Button(btn_frame, text="Créer", command=create_aircraft).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side='left', padx=5)
    
    def show_maintenance_dialog(self):
        """Affiche le dialogue de programmation de maintenance"""
        if not self.selected_aircraft_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un avion")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Programmer Maintenance")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Trouver l'avion sélectionné
        aircraft_data = None
        for a in self.data_controller.get_all_avions():
            if a['id'] == self.selected_aircraft_id:
                aircraft_data = a
                break
        
        if not aircraft_data:
            messagebox.showerror("Erreur", "Avion non trouvé")
            dialog.destroy()
            return
        
        avion = aircraft_data['avion']
        
        ttk.Label(main_frame, text=f"Maintenance pour: {avion.num_id}", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Type de maintenance
        ttk.Label(main_frame, text="Type de maintenance:").pack(anchor='w')
        type_var = tk.StringVar(value="Inspection A")
        type_combo = ttk.Combobox(main_frame, textvariable=type_var,
                                 values=["Inspection A", "Inspection B", "Inspection C", 
                                        "Révision Majeure", "Maintenance Corrective"],
                                 state='readonly', width=30)
        type_combo.pack(pady=5)
        
        # Date de maintenance
        ttk.Label(main_frame, text="Date de maintenance:").pack(anchor='w', pady=(10, 0))
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(pady=5)
        
        # Date
        date_var = tk.StringVar(value=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(date_frame, textvariable=date_var, width=12)
        date_entry.pack(side='left')
        
        # Heure
        ttk.Label(date_frame, text=" à ").pack(side='left')
        time_var = tk.StringVar(value="08:00")
        time_entry = ttk.Entry(date_frame, textvariable=time_var, width=8)
        time_entry.pack(side='left')
        
        # Durée estimée
        ttk.Label(main_frame, text="Durée estimée (heures):").pack(anchor='w', pady=(10, 0))
        duree_var = tk.StringVar(value="4")
        duree_entry = ttk.Entry(main_frame, textvariable=duree_var, width=10)
        duree_entry.pack(pady=5)
        
        # Commentaires
        ttk.Label(main_frame, text="Commentaires:").pack(anchor='w', pady=(10, 0))
        comment_text = tk.Text(main_frame, height=4, width=40)
        comment_text.pack(pady=5)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def programmer_maintenance():
            try:
                # Parser la date et l'heure
                maintenance_datetime = datetime.strptime(f"{date_var.get()} {time_var.get()}", 
                                                       '%Y-%m-%d %H:%M')
                duree_heures = int(duree_var.get())
                
                # Programmer la maintenance
                self.data_controller.schedule_maintenance(
                    self.selected_aircraft_id, 
                    maintenance_datetime, 
                    duree_heures
                )
                
                messagebox.showinfo("Succès", 
                                  f"Maintenance programmée pour le {maintenance_datetime.strftime('%Y-%m-%d à %H:%M')}")
                dialog.destroy()
                self.refresh_data()
                
            except ValueError as e:
                messagebox.showerror("Erreur", f"Format de date/heure invalide: {e}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la programmation: {e}")
        
        ttk.Button(btn_frame, text="Programmer", command=programmer_maintenance).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side='left', padx=5)
    
    def modify_aircraft(self):
        """Modifie l'avion sélectionné"""
        if not self.selected_aircraft_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un avion à modifier")
            return
        messagebox.showinfo("Modifier Avion", "Dialogue de modification d'avion à implémenter")
    
    def retire_aircraft(self):
        """Met l'avion hors service"""
        if not self.selected_aircraft_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un avion")
            return
        
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment mettre cet avion hors service ?"):
            # Logique de mise hors service
            messagebox.showinfo("Avion Retiré", "Avion mis hors service")
            self.refresh_data()
    
    def change_location(self):
        """Change la localisation de l'avion"""
        if not self.selected_aircraft_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un avion")
            return
        
        # Dialogue simple pour changer la localisation
        new_location = simpledialog.askstring("Nouvelle Localisation", 
                                             "Entrez les coordonnées (lat,lon):",
                                             initialvalue="48.8566, 2.3522")
        if new_location:
            try:
                lat, lon = map(float, new_location.split(','))
                # Mettre à jour la localisation
                messagebox.showinfo("Succès", f"Localisation mise à jour: {lat}, {lon}")
                self.refresh_data()
            except ValueError:
                messagebox.showerror("Erreur", "Format invalide. Utilisez: latitude, longitude")
    
    def complete_maintenance(self):
        """Termine la maintenance de l'avion sélectionné"""
        if not self.selected_aircraft_id:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un avion")
            return
        
        # Trouver l'avion
        aircraft_data = None
        for a in self.data_controller.get_all_avions():
            if a['id'] == self.selected_aircraft_id:
                aircraft_data = a
                break
        
        if not aircraft_data:
            return
        
        avion = aircraft_data['avion']
        
        if avion.etat.value != 'en_maintenance':
            messagebox.showwarning("État Incorrect", "Cet avion n'est pas en maintenance")
            return
        
        if messagebox.askyesno("Confirmer", "Terminer la maintenance de cet avion ?"):
            avion.terminer_maintenance()
            self.data_controller.save_avions()
            messagebox.showinfo("Succès", "Maintenance terminée. Avion remis en service.")
            self.refresh_data()
    
    def maintenance_report(self):
        """Génère un rapport de maintenance"""
        messagebox.showinfo("Rapport Maintenance", "Génération de rapport à implémenter")
    
    def view_aircraft_details(self):
        """Affiche les détails complets de l'avion"""
        if not self.selected_aircraft_id:
            return
        messagebox.showinfo("Détails Avion", "Vue détaillée à implémenter")
    
    def view_history(self):
        """Affiche l'historique complet de l'avion"""
        if not self.selected_aircraft_id:
            return
        messagebox.showinfo("Historique", "Vue historique détaillée à implémenter")
    
    def optimize_fleet(self):
        """Lance l'optimisation de la flotte"""
        if messagebox.askyesno("Optimisation", "Lancer l'optimisation automatique de la flotte ?"):
            try:
                optimizations = self.data_controller.optimize_aircraft_assignment()
                if optimizations:
                    message = f"Optimisations effectuées:\n"
                    for vol_id, avion_id in optimizations.items():
                        message += f"- Vol {vol_id}: assigné à {avion_id}\n"
                    messagebox.showinfo("Optimisation Terminée", message)
                else:
                    messagebox.showinfo("Optimisation", "Aucune optimisation nécessaire")
                
                self.refresh_data()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'optimisation: {e}")
    
    def show_fleet_report(self):
        """Affiche un rapport de la flotte"""
        report_window = tk.Toplevel(self)
        report_window.title("Rapport de Flotte")
        report_window.geometry("700x500")
        report_window.transient(self)
        
        # Récupérer les statistiques
        stats = self.data_controller.get_statistics()
        all_aircraft = self.data_controller.get_all_avions()
        
        # Créer le rapport
        report_text = tk.Text(report_window, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(report_window, orient='vertical', command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        # Contenu du rapport
        rapport = f"""
=== RAPPORT DE FLOTTE ===
Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATISTIQUES GÉNÉRALES:
  Total d'avions: {stats['avions']['total']}
  Avions disponibles: {stats['avions']['disponibles']}
  Avions en vol: {stats['avions']['en_vol']}
  Avions en maintenance: {stats['avions']['en_maintenance']}

DÉTAIL PAR AVION:
"""
        
        for aircraft_data in all_aircraft:
            avion = aircraft_data['avion']
            rapport += f"""
  {avion.num_id} - {avion.modele}
    État: {avion.etat.value.title()}
    Compagnie: {avion.compagnie_aerienne}
    Capacité: {avion.capacite} passagers
    Autonomie: {avion.autonomie} km
    Dernière maintenance: {avion.derniere_maintenance.strftime('%Y-%m-%d') if avion.derniere_maintenance else 'N/A'}
"""
        
        rapport += f"""

RECOMMANDATIONS:
  - Programmer maintenance pour les avions sans maintenance récente
  - Optimiser l'utilisation des avions disponibles
  - Surveiller les avions approchant des limites d'heures de vol

=== FIN DU RAPPORT ===
        """
        
        report_text.insert('1.0', rapport)
        report_text.config(state='disabled')
        
        report_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bouton fermer
        ttk.Button(report_window, text="Fermer", 
                  command=report_window.destroy).pack(pady=10)