"""
Vue du journal des événements en temps réel
Affichage détaillé de tous les événements de simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EventLogView(ttk.Frame):
    """Vue du journal des événements"""
    
    def __init__(self, parent, data_controller):
        super().__init__(parent)
        self.data_controller = data_controller
        
        # Variables d'interface
        self.auto_scroll = tk.BooleanVar(value=True)
        self.filter_type = tk.StringVar(value="Tous")
        self.search_var = tk.StringVar()
        self.max_events = tk.IntVar(value=1000)
        self.pause_updates = tk.BooleanVar(value=False)
        
        # Cache des événements
        self.events_cache = []
        self.filtered_events = []
        
        self.setup_ui()
        self.load_events()
        
        # Mise à jour périodique
        self.schedule_update()
        
        logger.info("Vue journal des événements initialisée")
    
    def setup_ui(self):
        """Configure l'interface du journal"""
        
        # Barre d'outils supérieure
        self.create_toolbar()
        
        # Frame principal avec panneaux
        main_paned = ttk.PanedWindow(self, orient='vertical')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Panneau supérieur : Liste des événements
        top_frame = ttk.Frame(main_paned)
        main_paned.add(top_frame, weight=3)
        self.create_events_list(top_frame)
        
        # Panneau inférieur : Détails de l'événement sélectionné
        bottom_frame = ttk.Frame(main_paned)
        main_paned.add(bottom_frame, weight=1)
        self.create_event_details(bottom_frame)
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Contrôles de base (gauche)
        controls_frame = ttk.Frame(toolbar)
        controls_frame.pack(side='left')
        
        # Bouton pause/play
        self.pause_btn = ttk.Button(controls_frame, text="⏸ Pause", 
                                   command=self.toggle_pause)
        self.pause_btn.pack(side='left', padx=2)
        
        ttk.Button(controls_frame, text="🔄 Actualiser", 
                  command=self.refresh_events).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="🗑️ Vider", 
                  command=self.clear_events).pack(side='left', padx=2)
        
        # Séparateur
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Filtres (centre)
        filter_frame = ttk.Frame(toolbar)
        filter_frame.pack(side='left', padx=10)
        
        ttk.Label(filter_frame, text="🔍 Recherche:").pack(side='left')
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=15)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Label(filter_frame, text="Type:").pack(side='left', padx=(10, 5))
        type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type,
                                 values=["Tous", "Vol", "Avion", "Maintenance", "Personnel", "Système"],
                                 width=10, state='readonly')
        type_combo.pack(side='left', padx=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Séparateur
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Options (centre-droite)
        options_frame = ttk.Frame(toolbar)
        options_frame.pack(side='left', padx=10)
        
        ttk.Checkbutton(options_frame, text="Auto-scroll", 
                       variable=self.auto_scroll).pack(side='left', padx=5)
        
        ttk.Label(options_frame, text="Max:").pack(side='left', padx=(10, 5))
        max_entry = ttk.Entry(options_frame, textvariable=self.max_events, width=6)
        max_entry.pack(side='left')
        max_entry.bind('<Return>', self.on_max_change)
        
        # Boutons utilitaires (droite)
        utils_frame = ttk.Frame(toolbar)
        utils_frame.pack(side='right')
        
        ttk.Button(utils_frame, text="💾 Exporter", 
                  command=self.export_events).pack(side='left', padx=2)
        ttk.Button(utils_frame, text="📊 Analyse", 
                  command=self.analyze_events).pack(side='left', padx=2)
        ttk.Button(utils_frame, text="⚙️ Config", 
                  command=self.show_config).pack(side='left', padx=2)
    
    def create_events_list(self, parent):
        """Crée la liste des événements"""
        list_frame = ttk.LabelFrame(parent, text="📋 Journal des Événements", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview pour les événements
        columns = ('Heure Sim', 'Heure Réelle', 'Type', 'Cible', 'Action', 'Vitesse', 'Détails')
        self.events_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        column_widths = {
            'Heure Sim': 120, 'Heure Réelle': 120, 'Type': 80,
            'Cible': 100, 'Action': 100, 'Vitesse': 60, 'Détails': 300
        }
        
        for col in columns:
            self.events_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.events_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.events_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.events_tree.xview)
        self.events_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Événements
        self.events_tree.bind('<<TreeviewSelect>>', self.on_event_select)
        self.events_tree.bind('<Double-1>', self.on_event_double_click)
        
        # Pack avec scrollbars
        self.events_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Menu contextuel
        self.create_context_menu()
        
        # Barre de statut pour les événements
        status_frame = ttk.Frame(list_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=2)
        
        self.events_count_var = tk.StringVar(value="0 événements")
        ttk.Label(status_frame, textvariable=self.events_count_var, font=('Arial', 8)).pack(side='left')
        
        self.last_update_var = tk.StringVar(value="Dernière MAJ: --")
        ttk.Label(status_frame, textvariable=self.last_update_var, font=('Arial', 8)).pack(side='right')
    
    def create_context_menu(self):
        """Crée le menu contextuel"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copier", command=self.copy_event)
        self.context_menu.add_command(label="Voir Détails", command=self.view_event_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Filtrer ce Type", command=self.filter_by_type)
        self.context_menu.add_command(label="Filtrer cette Cible", command=self.filter_by_target)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Aller à l'Heure", command=self.goto_time)
        
        # Bind du clic droit
        self.events_tree.bind('<Button-3>', self.show_context_menu)
    
    def create_event_details(self, parent):
        """Crée le panneau de détails de l'événement"""
        details_frame = ttk.LabelFrame(parent, text="📄 Détails de l'Événement", padding=10)
        details_frame.pack(fill='both', expand=True)
        
        # Notebook pour organiser les détails
        details_notebook = ttk.Notebook(details_frame)
        details_notebook.pack(fill='both', expand=True)
        
        # Onglet Informations
        self.create_info_tab(details_notebook)
        
        # Onglet Données brutes
        self.create_raw_data_tab(details_notebook)
        
        # Onglet Contexte
        self.create_context_tab(details_notebook)
    
    def create_info_tab(self, parent):
        """Onglet informations de l'événement"""
        info_frame = ttk.Frame(parent)
        parent.add(info_frame, text="ℹ️ Infos")
        
        # Variables pour les détails
        self.event_details_vars = {
            'timestamp': tk.StringVar(),
            'real_time': tk.StringVar(),
            'event_type': tk.StringVar(),
            'target_id': tk.StringVar(),
            'action': tk.StringVar(),
            'message': tk.StringVar(),
            'sim_speed': tk.StringVar(),
            'event_id': tk.StringVar()
        }
        
        # Affichage des informations
        info_labels = [
            ("Heure Simulation:", 'timestamp'),
            ("Heure Réelle:", 'real_time'),
            ("Type d'Événement:", 'event_type'),
            ("Cible:", 'target_id'),
            ("Action:", 'action'),
            ("Vitesse Simulation:", 'sim_speed'),
            ("ID Événement:", 'event_id'),
            ("Message:", 'message')
        ]
        
        for i, (label, var_name) in enumerate(info_labels):
            row = i // 2 if i < 6 else i - 3  # Les 6 premiers sur 2 colonnes, le message seul
            col = (i % 2) * 2 if i < 6 else 0
            colspan = 1 if i < 6 else 4
            
            ttk.Label(info_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=5, pady=3, columnspan=1)
            
            if var_name == 'message':
                # Message sur toute la largeur
                message_label = ttk.Label(info_frame, textvariable=self.event_details_vars[var_name],
                                        font=('Arial', 9), wraplength=400)
                message_label.grid(row=row, column=1, sticky='w', padx=15, pady=3, columnspan=3)
            else:
                ttk.Label(info_frame, textvariable=self.event_details_vars[var_name],
                         font=('Arial', 9)).grid(
                    row=row, column=col+1, sticky='w', padx=15, pady=3)
    
    def create_raw_data_tab(self, parent):
        """Onglet données brutes"""
        raw_frame = ttk.Frame(parent)
        parent.add(raw_frame, text="🔧 Données")
        
        # Zone de texte pour les données JSON
        self.raw_data_text = tk.Text(raw_frame, wrap='word', font=('Courier', 9))
        raw_scrollbar = ttk.Scrollbar(raw_frame, orient='vertical', command=self.raw_data_text.yview)
        self.raw_data_text.configure(yscrollcommand=raw_scrollbar.set)
        
        self.raw_data_text.pack(side='left', fill='both', expand=True)
        raw_scrollbar.pack(side='right', fill='y')
    
    def create_context_tab(self, parent):
        """Onglet contexte de l'événement"""
        context_frame = ttk.Frame(parent)
        parent.add(context_frame, text="🌐 Contexte")
        
        # Informations contextuelles
        self.context_text = tk.Text(context_frame, wrap='word', font=('Arial', 9))
        context_scrollbar = ttk.Scrollbar(context_frame, orient='vertical', command=self.context_text.yview)
        self.context_text.configure(yscrollcommand=context_scrollbar.set)
        
        self.context_text.pack(side='left', fill='both', expand=True)
        context_scrollbar.pack(side='right', fill='y')
    
    # ===============================================
    # GESTION DES ÉVÉNEMENTS
    # ===============================================
    
    def load_events(self):
        """Charge les événements depuis le stockage"""
        try:
            events_data = self.data_controller.data_manager.load_data('events')
            self.events_cache = events_data if events_data else []
            self.apply_filters()
            self.refresh_display()
            
        except Exception as e:
            logger.error(f"Erreur chargement événements: {e}")
            self.events_cache = []
            self.filtered_events = []
    
    def refresh_events(self):
        """Actualise les événements"""
        self.load_events()
        self.last_update_var.set(f"Dernière MAJ: {datetime.now().strftime('%H:%M:%S')}")
    
    def apply_filters(self):
        """Applique les filtres de recherche et de type"""
        filtered = self.events_cache.copy()
        
        # Filtre de recherche
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [e for e in filtered 
                       if search_term in e.get('message', '').lower()]
        
        # Filtre par type
        filter_type = self.filter_type.get()
        if filter_type != "Tous":
            filtered = [e for e in filtered 
                       if self.extract_event_type(e.get('message', '')) == filter_type]
        
        # Limiter le nombre d'événements
        max_events = self.max_events.get()
        if len(filtered) > max_events:
            filtered = filtered[-max_events:]
        
        self.filtered_events = filtered
        self.events_count_var.set(f"{len(filtered)} événements")
    
    def extract_event_type(self, message):
        """Extrait le type d'événement du message"""
        if '[VOL]' in message or 'Vol' in message:
            return "Vol"
        elif '[AVION]' in message or 'Avion' in message:
            return "Avion"
        elif '[MAINTENANCE]' in message or 'Maintenance' in message:
            return "Maintenance"
        elif 'Personnel' in message or 'Équipage' in message:
            return "Personnel"
        else:
            return "Système"
    
    def refresh_display(self):
        """Met à jour l'affichage de la liste"""
        # Vider la liste
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Remplir avec les événements filtrés
        for event in self.filtered_events:
            # Extraire les informations
            timestamp = event.get('timestamp', '')
            real_time = event.get('real_time', '')
            message = event.get('message', '')
            sim_speed = event.get('sim_speed', 1.0)
            
            # Parser le message pour extraire type, cible et action
            event_type = self.extract_event_type(message)
            target, action = self.parse_message(message)
            
            # Formater les heures
            try:
                sim_time = datetime.fromisoformat(timestamp).strftime('%H:%M:%S')
                real_time_fmt = datetime.fromisoformat(real_time).strftime('%H:%M:%S')
            except:
                sim_time = timestamp
                real_time_fmt = real_time
            
            # Nettoyer le message
            clean_message = self.clean_message(message)
            
            values = (
                sim_time,
                real_time_fmt,
                event_type,
                target,
                action,
                f"{sim_speed}x",
                clean_message
            )
            
            # Insérer avec coloration selon le type
            item = self.events_tree.insert('', 'end', values=values)
            self.apply_event_colors(item, event_type)
        
        # Auto-scroll vers le bas si activé
        if self.auto_scroll.get() and self.filtered_events:
            self.events_tree.see(self.events_tree.get_children()[-1])
    
    def parse_message(self, message):
        """Parse le message pour extraire la cible et l'action"""
        # Nettoyer les tags
        clean_msg = message.replace('[VOL]', '').replace('[AVION]', '').replace('[MAINTENANCE]', '').strip()
        
        # Extraire la cible et l'action
        if 'pour' in clean_msg:
            parts = clean_msg.split('pour')
            action = parts[0].strip()
            target = parts[1].strip() if len(parts) > 1 else "N/A"
        elif 'Vol' in clean_msg and any(x in clean_msg for x in ['décollé', 'atterri', 'retardé']):
            # Messages de vol
            if 'décollé' in clean_msg:
                action = "Décollage"
            elif 'atterri' in clean_msg:
                action = "Atterrissage"
            elif 'retardé' in clean_msg:
                action = "Retard"
            else:
                action = "Vol"
            
            # Extraire le numéro de vol
            words = clean_msg.split()
            target = next((word for word in words if word.startswith(('Vol', 'AF', 'FR', 'LH'))), "N/A")
        else:
            # Par défaut
            words = clean_msg.split()
            action = words[0] if words else "Action"
            target = words[-1] if len(words) > 1 else "N/A"
        
        return target, action
    
    def clean_message(self, message):
        """Nettoie le message pour l'affichage"""
        clean = message.replace('[VOL]', '').replace('[AVION]', '').replace('[MAINTENANCE]', '').strip()
        return clean[:100] + "..." if len(clean) > 100 else clean
    
    def apply_event_colors(self, item, event_type):
        """Applique les couleurs selon le type d'événement"""
        colors = {
            'Vol': '#e1f5fe',
            'Avion': '#e8f5e8',
            'Maintenance': '#fff3e0',
            'Personnel': '#f3e5f5',
            'Système': '#fafafa'
        }
        # Note: La coloration Treeview nécessite une configuration avancée
    
    # ===============================================
    # ÉVÉNEMENTS D'INTERFACE
    # ===============================================
    
    def on_event_select(self, event):
        """Gestionnaire de sélection d'événement"""
        selection = self.events_tree.selection()
        if selection:
            item = selection[0]
            index = self.events_tree.index(item)
            if 0 <= index < len(self.filtered_events):
                self.update_event_details(self.filtered_events[index])
    
    def on_event_double_click(self, event):
        """Gestionnaire de double-clic"""
        self.view_event_details()
    
    def on_search_change(self, event=None):
        """Gestionnaire de changement de recherche"""
        self.apply_filters()
        self.refresh_display()
    
    def on_filter_change(self, event=None):
        """Gestionnaire de changement de filtre"""
        self.apply_filters()
        self.refresh_display()
    
    def on_max_change(self, event=None):
        """Gestionnaire de changement du nombre max"""
        self.apply_filters()
        self.refresh_display()
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel"""
        item = self.events_tree.identify_row(event.y)
        if item:
            self.events_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def sort_by_column(self, col):
        """Trie par colonne"""
        # À implémenter
        pass
    
    # ===============================================
    # GESTION DES DÉTAILS
    # ===============================================
    
    def update_event_details(self, event_data):
        """Met à jour les détails de l'événement sélectionné"""
        # Onglet Informations
        self.event_details_vars['timestamp'].set(event_data.get('timestamp', 'N/A'))
        self.event_details_vars['real_time'].set(event_data.get('real_time', 'N/A'))
        self.event_details_vars['event_type'].set(self.extract_event_type(event_data.get('message', '')))
        
        target, action = self.parse_message(event_data.get('message', ''))
        self.event_details_vars['target_id'].set(target)
        self.event_details_vars['action'].set(action)
        self.event_details_vars['message'].set(event_data.get('message', ''))
        self.event_details_vars['sim_speed'].set(f"{event_data.get('sim_speed', 1.0)}x")
        self.event_details_vars['event_id'].set(event_data.get('event_id', 'N/A'))
        
        # Onglet Données brutes
        self.raw_data_text.delete(1.0, tk.END)
        import json
        formatted_data = json.dumps(event_data, indent=2, ensure_ascii=False, default=str)
        self.raw_data_text.insert(1.0, formatted_data)
        
        # Onglet Contexte
        self.update_context_info(event_data)
    
    def update_context_info(self, event_data):
        """Met à jour les informations contextuelles"""
        self.context_text.delete(1.0, tk.END)
        
        context_info = f"""CONTEXTE DE L'ÉVÉNEMENT

Heure de simulation: {event_data.get('timestamp', 'N/A')}
Heure réelle: {event_data.get('real_time', 'N/A')}
Vitesse de simulation: {event_data.get('sim_speed', 1.0)}x

MESSAGE ORIGINAL:
{event_data.get('message', 'N/A')}

ANALYSE:
Type détecté: {self.extract_event_type(event_data.get('message', ''))}
"""
        
        # Ajouter des informations contextuelles selon le type
        event_type = self.extract_event_type(event_data.get('message', ''))
        
        if event_type == "Vol":
            context_info += """
CONTEXTE VOL:
- Les événements de vol incluent les décollages, atterrissages, retards
- Vérifiez les conditions météo et la disponibilité des pistes
- Impact possible sur les vols suivants
"""
        elif event_type == "Avion":
            context_info += """
CONTEXTE AVION:
- Changements d'état de l'avion (maintenance, vol, au sol)
- Impact sur la disponibilité de la flotte
- Vérifiez les maintenances programmées
"""
        elif event_type == "Maintenance":
            context_info += """
CONTEXTE MAINTENANCE:
- Opérations de maintenance programmées ou urgentes
- Impact sur la disponibilité de l'avion
- Durée estimée et personnel requis
"""
        
        self.context_text.insert(1.0, context_info)
    
    # ===============================================
    # ACTIONS ET COMMANDES
    # ===============================================
    
    def toggle_pause(self):
        """Bascule la pause des mises à jour"""
        self.pause_updates.set(not self.pause_updates.get())
        if self.pause_updates.get():
            self.pause_btn.config(text="▶ Play")
        else:
            self.pause_btn.config(text="⏸ Pause")
            self.refresh_events()
    
    def clear_events(self):
        """Vide le journal des événements"""
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment vider le journal des événements ?"):
            try:
                self.data_controller.data_manager.save_data('events', [])
                self.events_cache = []
                self.filtered_events = []
                self.refresh_display()
                messagebox.showinfo("Succès", "Journal vidé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du vidage: {e}")
    
    def copy_event(self):
        """Copie l'événement sélectionné"""
        selection = self.events_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.events_tree.item(item)['values']
        
        # Copier dans le presse-papier
        text = "\t".join(str(v) for v in values)
        self.clipboard_clear()
        self.clipboard_append(text)
        
        messagebox.showinfo("Copié", "Événement copié dans le presse-papier")
    
    def view_event_details(self):
        """Affiche une fenêtre de détails de l'événement"""
        selection = self.events_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.events_tree.index(item)
        if 0 <= index < len(self.filtered_events):
            event_data = self.filtered_events[index]
            
            # Créer une fenêtre de détails
            details_window = tk.Toplevel(self)
            details_window.title("Détails de l'Événement")
            details_window.geometry("600x400")
            details_window.transient(self)
            
            # Afficher les détails
            text_widget = tk.Text(details_window, wrap='word', font=('Courier', 10))
            scrollbar = ttk.Scrollbar(details_window, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            import json
            details_text = json.dumps(event_data, indent=2, ensure_ascii=False, default=str)
            text_widget.insert(1.0, details_text)
            text_widget.config(state='disabled')
            
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
    
    def filter_by_type(self):
        """Filtre par le type de l'événement sélectionné"""
        selection = self.events_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        event_type = self.events_tree.item(item)['values'][2]  # Colonne Type
        self.filter_type.set(event_type)
        self.apply_filters()
        self.refresh_display()
    
    def filter_by_target(self):
        """Filtre par la cible de l'événement sélectionné"""
        selection = self.events_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        target = self.events_tree.item(item)['values'][3]  # Colonne Cible
        self.search_var.set(target)
        self.apply_filters()
        self.refresh_display()
    
    def goto_time(self):
        """Va à l'heure de l'événement sélectionné dans la simulation"""
        selection = self.events_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.events_tree.index(item)
        if 0 <= index < len(self.filtered_events):
            event_data = self.filtered_events[index]
            timestamp = event_data.get('timestamp')
            
            if timestamp:
                try:
                    target_time = datetime.fromisoformat(timestamp)
                    if messagebox.askyesno("Confirmer", 
                                         f"Aller au temps de simulation: {target_time.strftime('%Y-%m-%d %H:%M:%S')} ?"):
                        self.data_controller.simulator.set_time(target_time)
                        messagebox.showinfo("Succès", "Temps de simulation modifié")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de changer le temps: {e}")
    
    def export_events(self):
        """Exporte les événements vers un fichier"""
        filename = filedialog.asksaveasfilename(
            title="Exporter les événements",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    import json
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.filtered_events, f, indent=2, ensure_ascii=False, default=str)
                
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Timestamp', 'Real Time', 'Message', 'Sim Speed'])
                        for event in self.filtered_events:
                            writer.writerow([
                                event.get('timestamp', ''),
                                event.get('real_time', ''),
                                event.get('message', ''),
                                event.get('sim_speed', '')
                            ])
                
                else:  # txt
                    with open(filename, 'w', encoding='utf-8') as f:
                        for event in self.filtered_events:
                            f.write(f"{event.get('timestamp', '')} | {event.get('message', '')}\n")
                
                messagebox.showinfo("Succès", f"Événements exportés vers {filename}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def analyze_events(self):
        """Analyse les événements et affiche des statistiques"""
        if not self.filtered_events:
            messagebox.showwarning("Aucun événement", "Aucun événement à analyser")
            return
        
        # Analyser les événements
        stats = {
            'total': len(self.filtered_events),
            'by_type': {},
            'by_hour': {},
            'speed_distribution': {}
        }
        
        for event in self.filtered_events:
            # Par type
            event_type = self.extract_event_type(event.get('message', ''))
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1
            
            # Par heure
            try:
                timestamp = datetime.fromisoformat(event.get('timestamp', ''))
                hour = timestamp.hour
                stats['by_hour'][hour] = stats['by_hour'].get(hour, 0) + 1
            except:
                pass
            
            # Par vitesse
            speed = event.get('sim_speed', 1.0)
            stats['speed_distribution'][speed] = stats['speed_distribution'].get(speed, 0) + 1
        
        # Afficher les statistiques
        analysis_window = tk.Toplevel(self)
        analysis_window.title("Analyse des Événements")
        analysis_window.geometry("500x600")
        analysis_window.transient(self)
        
        text_widget = tk.Text(analysis_window, wrap='word', font=('Courier', 10))
        scrollbar = ttk.Scrollbar(analysis_window, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        analysis_text = f"""ANALYSE DES ÉVÉNEMENTS

Total d'événements: {stats['total']}

RÉPARTITION PAR TYPE:
"""
        
        for event_type, count in sorted(stats['by_type'].items()):
            percentage = (count / stats['total']) * 100
            analysis_text += f"  {event_type}: {count} ({percentage:.1f}%)\n"
        
        analysis_text += f"\nRÉPARTITION PAR HEURE:\n"
        for hour in sorted(stats['by_hour'].keys()):
            count = stats['by_hour'][hour]
            analysis_text += f"  {hour:02d}h: {count} événements\n"
        
        analysis_text += f"\nRÉPARTITION PAR VITESSE DE SIMULATION:\n"
        for speed in sorted(stats['speed_distribution'].keys()):
            count = stats['speed_distribution'][speed]
            analysis_text += f"  {speed}x: {count} événements\n"
        
        text_widget.insert(1.0, analysis_text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def show_config(self):
        """Affiche la configuration du journal"""
        config_window = tk.Toplevel(self)
        config_window.title("Configuration du Journal")
        config_window.geometry("400x300")
        config_window.resizable(False, False)
        config_window.transient(self)
        config_window.grab_set()
        
        main_frame = ttk.Frame(config_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Configuration du Journal", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Options de configuration
        ttk.Checkbutton(main_frame, text="Mise à jour automatique", 
                       variable=tk.BooleanVar(value=True)).pack(anchor='w', pady=5)
        ttk.Checkbutton(main_frame, text="Auto-scroll", 
                       variable=self.auto_scroll).pack(anchor='w', pady=5)
        
        # Nombre max d'événements
        max_frame = ttk.Frame(main_frame)
        max_frame.pack(fill='x', pady=10)
        ttk.Label(max_frame, text="Nombre max d'événements:").pack(side='left')
        ttk.Entry(max_frame, textvariable=self.max_events, width=10).pack(side='right')
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="OK", command=config_window.destroy).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Réinitialiser", 
                  command=lambda: self.max_events.set(1000)).pack(side='left', padx=5)
    
    # ===============================================
    # MISE À JOUR AUTOMATIQUE
    # ===============================================
    
    def schedule_update(self):
        """Programme la mise à jour automatique"""
        if not self.pause_updates.get():
            self.refresh_events()
        
        # Programmer la prochaine mise à jour
        self.after(2000, self.schedule_update)  # Toutes les 2 secondes
    
    def update_data(self):
        """Méthode appelée par le contrôleur principal"""
        if not self.pause_updates.get():
            self.load_events()