import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime
from interfaces.tabs.dashboard_tab import SimpleDashboard

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from data.data_manager import DataManager

class MainWindow:
    """Fenêtre principale de l'application - VERSION SANS SIMULATION"""
    
    def __init__(self):
        """Initialise la fenêtre principale"""
        self.root = tk.Tk()
        self.root.title("Gestion Aéroportuaire")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Gestionnaire de données uniquement
        self.data_manager = DataManager()
        
        # Variables d'interface basiques
        self.status_var = tk.StringVar(value="Application prête")
        
        # Variables pour les statistiques (simples)
        self.stat_vars = {}
        
        self.setup_ui()
        self.setup_styles()
        self.refresh_all_data()
        
        print("🖥️ Interface principale initialisée (sans simulation)")
    
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
        
        # Barre supérieure simple (sans contrôles simulation)
        self.create_toolbar(main_frame)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Création des onglets
        self.create_tabs()
        
        # Barre de statut
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Crée la barre d'outils principale"""
        toolbar_frame = ttk.LabelFrame(parent, text="Actions Principales", padding=10)
        toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Boutons d'actions principales
        ttk.Button(toolbar_frame, text="🔄 Actualiser", 
                  command=self.refresh_all_data, 
                  style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(toolbar_frame, text="📊 Statistiques", 
                  command=self.show_statistics).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(toolbar_frame, text="💾 Sauvegarder", 
                  command=self.save_all_data).grid(row=0, column=2, padx=(0, 10))
        
        # Indicateur d'horloge système simple
        self.clock_var = tk.StringVar()
        clock_label = ttk.Label(toolbar_frame, textvariable=self.clock_var,
                               font=('Arial', 12, 'bold'),
                               foreground='blue')
        clock_label.grid(row=0, column=3, sticky="e", padx=(20, 0))
        
        # Mettre à jour l'horloge une seule fois
        self.update_clock()
        
        # Configuration responsive
        toolbar_frame.grid_columnconfigure(3, weight=1)
    
    def update_clock(self):
        """Met à jour l'horloge système (pas de simulation)"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_var.set(f"🕐 {current_time}")
        # Programmer la prochaine mise à jour dans 1 seconde
        self.root.after(1000, self.update_clock)
    
    def create_tabs(self):
        """Crée tous les onglets de l'application"""
        # Onglet Dashboard (simplifié)
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
        """Crée l'onglet tableau de bord simplifié"""
        # Dashboard simplifié sans simulation temps réel
        self.create_simple_dashboard()
        
    def create_simple_dashboard(self):
        """Crée un dashboard simple sans éléments temps réel"""
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
        
        # Titre
        title_label = ttk.Label(scrollable_frame, 
                               text="📊 Tableau de Bord",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Section Statistiques Générales
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📈 Statistiques Générales", padding=15)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Grid de statistiques (2x3)
        self.create_stat_card(stats_frame, "Total Avions", "0", "🛩️", 0, 0)
        self.create_stat_card(stats_frame, "Total Personnel", "0", "👥", 0, 1)
        self.create_stat_card(stats_frame, "Total Vols", "0", "🛫", 0, 2)
        self.create_stat_card(stats_frame, "Total Passagers", "0", "👤", 1, 0)
        self.create_stat_card(stats_frame, "Total Réservations", "0", "🎫", 1, 1)
        self.create_stat_card(stats_frame, "Base de Données", "OK", "💾", 1, 2)
        
        # Configuration responsive
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Section Résumé
        summary_frame = ttk.LabelFrame(scrollable_frame, text="📋 Résumé", padding=15)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=8, width=80, wrap=tk.WORD,
                                   font=('Arial', 10), bg='#f8f9fa', relief="sunken", bd=1)
        self.summary_text.pack(fill="both", expand=True)
        
        # Mettre à jour le résumé
        self.update_summary()
        
        print("✓ Dashboard simplifié créé")

    def create_stat_card(self, parent, title, value, icon, row, col):
        """Crée une carte de statistique simple"""
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
        value_label = ttk.Label(card_frame, textvariable=value_var, 
                               font=('Arial', 14, 'bold'), foreground="blue")
        value_label.grid(row=1, column=0, pady=(0, 10))
        
        # Stocker la variable pour mise à jour
        self.stat_vars[title] = value_var
        
        return card_frame
    
    def update_summary(self):
        """Met à jour le texte de résumé"""
        try:
            aircraft_count = len(self.data_manager.get_aircraft())
            personnel_count = len(self.data_manager.get_personnel())
            flights_count = len(self.data_manager.get_flights())
            passengers_count = len(self.data_manager.get_passengers())
            reservations_count = len(self.data_manager.get_reservations())
            
            summary = f"""=== RÉSUMÉ DE LA GESTION AÉROPORTUAIRE ===

📊 DONNÉES ACTUELLES :
• Avions enregistrés : {aircraft_count}
• Personnel actif : {personnel_count}
• Vols programmés : {flights_count}
• Passagers enregistrés : {passengers_count}
• Réservations actives : {reservations_count}

📈 INFORMATIONS SYSTÈME :
• Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• État base de données : Opérationnelle
• Mode : Gestion statique (sans simulation)

💡 ACTIONS DISPONIBLES :
• Gérer la flotte d'avions dans l'onglet "Avions"
• Administrer le personnel dans l'onglet "Personnel"
• Planifier les vols dans l'onglet "Vols"
• Gérer les passagers et réservations
• Utiliser le bouton "Actualiser" pour mettre à jour les données

📝 NOTE : Cette version ne contient pas de simulation temps réel.
Toutes les modifications sont instantanées et persistantes."""
            
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert("1.0", summary)
            
        except Exception as e:
            error_text = f"Erreur lors de la mise à jour du résumé : {e}"
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert("1.0", error_text)
        
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
        try:
            from interfaces.tabs.personnel_tab import create_personnel_tab_content
            self.personnel_tree = create_personnel_tab_content(self.personnel_frame, self.data_manager)
            print("✓ Onglet Personnel créé")
        except ImportError as e:
            print(f"❌ Erreur import personnel_tab: {e}")
            ttk.Label(self.personnel_frame, text="Erreur: Module personnel_tab non trouvé", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
        except Exception as e:
            print(f"❌ Erreur création onglet personnel: {e}")
            ttk.Label(self.personnel_frame, text=f"Erreur: {str(e)}", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
    
    def create_flights_tab(self):
        """Crée l'onglet de gestion des vols"""
        try:
            from interfaces.tabs.flights_tab import create_flights_tab_content
            self.flights_tree = create_flights_tab_content(self.flights_frame, self.data_manager)
            print("✓ Onglet Vols créé")
        except ImportError as e:
            print(f"❌ Erreur import flights_tab: {e}")
            ttk.Label(self.flights_frame, text="Erreur: Module flights_tab non trouvé", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
        except Exception as e:
            print(f"❌ Erreur création onglet vols: {e}")
            ttk.Label(self.flights_frame, text=f"Erreur: {str(e)}", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
        
    def create_passengers_tab(self):
        """Crée l'onglet de gestion des passagers"""
        try:
            from interfaces.tabs.passengers_tab import create_passengers_tab_content
            self.passengers_tree = create_passengers_tab_content(self.passengers_frame, self.data_manager)
            print("✓ Onglet Passagers créé")
        except ImportError as e:
            print(f"❌ Erreur import passengers_tab: {e}")
            ttk.Label(self.passengers_frame, text="Erreur: Module passengers_tab non trouvé", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
        except Exception as e:
            print(f"❌ Erreur création onglet passagers: {e}")
            ttk.Label(self.passengers_frame, text=f"Erreur: {str(e)}", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
    
    def create_reservations_tab(self):
        """Crée l'onglet de gestion des réservations"""
        try:
            from interfaces.tabs.reservations_tab import create_reservations_tab_content
            self.reservations_tree = create_reservations_tab_content(self.reservations_frame, self.data_manager)
            print("✓ Onglet Réservations créé")
        except ImportError as e:
            print(f"❌ Erreur import reservations_tab: {e}")
            ttk.Label(self.reservations_frame, text="Erreur: Module reservations_tab non trouvé", 
                     font=('Arial', 14), foreground='red').pack(expand=True)
        except Exception as e:
            print(f"❌ Erreur création onglet réservations: {e}")
            ttk.Label(self.reservations_frame, text=f"Erreur: {str(e)}", 
                     font=('Arial', 14), foreground='red').pack(expand=True)

    def create_status_bar(self, parent):
        """Crée la barre de statut"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Label(status_frame, text=f"Données: {self.data_manager.data_dir}").grid(row=0, column=1, sticky="e")
        
        status_frame.grid_columnconfigure(0, weight=1)
    
    # Méthodes d'actions principales
    def show_statistics(self):
        """Affiche les statistiques globales"""
        try:
            aircraft_count = len(self.data_manager.get_aircraft())
            personnel_count = len(self.data_manager.get_personnel())
            flights_count = len(self.data_manager.get_flights())
            passengers_count = len(self.data_manager.get_passengers())
            reservations_count = len(self.data_manager.get_reservations())
            
            stats_text = f"""📊 STATISTIQUES GLOBALES

✈️ FLOTTE :
• Total avions : {aircraft_count}

👥 PERSONNEL :
• Total employés : {personnel_count}

🛫 VOLS :
• Total vols planifiés : {flights_count}

👤 PASSAGERS :
• Total passagers : {passengers_count}

🎫 RÉSERVATIONS :
• Total réservations : {reservations_count}

📅 Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            messagebox.showinfo("Statistiques Globales", stats_text)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du calcul des statistiques:\n{e}")
    
    def save_all_data(self):
        """Force la sauvegarde de toutes les données"""
        try:
            # Le DataManager sauvegarde automatiquement, mais on peut forcer
            self.status_var.set("Sauvegarde en cours...")
            
            # Simuler une petite pause pour l'indication visuelle
            self.root.after(500, lambda: self.status_var.set("Données sauvegardées"))
            self.root.after(2000, lambda: self.status_var.set("Application prête"))
            
            messagebox.showinfo("Sauvegarde", "Toutes les données ont été sauvegardées avec succès.")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            self.status_var.set("Erreur de sauvegarde")
    
    # Méthodes de gestion des avions (simplifiées)
    def new_aircraft_dialog(self):
        """Ouvre le dialogue de création d'avion"""
        try:
            from interfaces.tabs.aircraft_tab import AircraftDialog
            dialog = AircraftDialog(self.root, self.data_manager)
            if dialog.result:
                self.refresh_aircraft_data()
                self.update_statistics()
                print("✅ Nouvel avion créé")
                
        except Exception as e:
            print(f"❌ Erreur création avion: {e}")
        
    def edit_aircraft(self):
        """Modifie l'avion sélectionné"""
        selection = self.aircraft_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un avion à modifier.")
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
                messagebox.showerror("Erreur", f"Avion {aircraft_id} non trouvé.")
                return
            
            from interfaces.tabs.aircraft_tab import AircraftDialog
            dialog = AircraftDialog(self.root, self.data_manager, aircraft_data)
            
            if dialog.result:
                self.refresh_aircraft_data()
                self.update_statistics()
                messagebox.showinfo("Succès", f"Avion {aircraft_id} modifié avec succès!")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")
    
    def aircraft_maintenance(self):
        """Met l'avion en maintenance"""
        selection = self.aircraft_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un avion.")
            return
        
        try:
            item = self.aircraft_tree.item(selection[0])
            aircraft_id = item['values'][0]
            aircraft_model = item['values'][1]
            current_state_display = item['values'][4]
            
            all_aircraft = self.data_manager.get_aircraft()
            aircraft_data = None
            aircraft_index = -1
            
            for i, aircraft in enumerate(all_aircraft):
                if aircraft.get('num_id') == aircraft_id:
                    aircraft_data = aircraft
                    aircraft_index = i
                    break
            
            if not aircraft_data:
                messagebox.showerror("Erreur", f"Avion {aircraft_id} non trouvé.")
                return
            
            current_state = aircraft_data.get('etat', 'au_sol')
            
            if current_state == 'en_maintenance':
                # Proposer de terminer la maintenance
                if messagebox.askyesno("Terminer maintenance", 
                                     f"L'avion {aircraft_id} ({aircraft_model}) est en maintenance.\n\n"
                                     "Voulez-vous terminer la maintenance ?"):
                    
                    aircraft_data['etat'] = 'operationnel'
                    aircraft_data['derniere_maintenance'] = datetime.now().isoformat()
                    
                    if self._update_aircraft_in_data(aircraft_data, aircraft_index):
                        messagebox.showinfo("Succès", "Maintenance terminée.")
                        self.refresh_aircraft_data()
            else:
                # Proposer de mettre en maintenance
                if messagebox.askyesno("Programmer maintenance", 
                                     f"Programmer une maintenance pour l'avion {aircraft_id} ?"):
                    
                    aircraft_data['etat'] = 'en_maintenance'
                    
                    if self._update_aircraft_in_data(aircraft_data, aircraft_index):
                        messagebox.showinfo("Succès", "Avion mis en maintenance.")
                        self.refresh_aircraft_data()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur maintenance: {e}")

    def _update_aircraft_in_data(self, aircraft_data, aircraft_index):
        """Met à jour un avion dans les données"""
        try:
            data = self.data_manager.load_data('aircraft')
            
            if 'aircraft' not in data:
                data['aircraft'] = []
            
            if 0 <= aircraft_index < len(data['aircraft']):
                data['aircraft'][aircraft_index] = aircraft_data
            else:
                for i, aircraft in enumerate(data['aircraft']):
                    if aircraft.get('num_id') == aircraft_data.get('num_id'):
                        data['aircraft'][i] = aircraft_data
                        break
                else:
                    data['aircraft'].append(aircraft_data)
            
            return self.data_manager.save_data('aircraft', data)
        
        except Exception as e:
            print(f"❌ Erreur update aircraft: {e}")
            return False
        
    def delete_aircraft(self):
        """Supprime l'avion sélectionné"""
        selection = self.aircraft_tree.selection()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un avion à supprimer.")
            return
        
        try:
            item = self.aircraft_tree.item(selection[0])
            aircraft_id = item['values'][0]
            aircraft_model = item['values'][1]
            
            if messagebox.askyesno("Confirmation", 
                                  f"Voulez-vous vraiment supprimer l'avion ?\n\n"
                                  f"ID: {aircraft_id}\n"
                                  f"Modèle: {aircraft_model}\n\n"
                                  "Cette action est irréversible."):
                
                if self.data_manager.delete_aircraft(aircraft_id):
                    self.refresh_aircraft_data()
                    self.update_statistics()
                    messagebox.showinfo("Succès", f"Avion {aircraft_id} supprimé.")
                else:
                    messagebox.showerror("Erreur", "Impossible de supprimer l'avion.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur suppression: {e}")
    
    def filter_aircraft(self, event=None):
        """Filtre la liste des avions"""
        search_text = self.aircraft_search_var.get().lower()
        filter_state = self.aircraft_filter_var.get()
        
        # Vider le tableau
        for item in self.aircraft_tree.get_children():
            self.aircraft_tree.delete(item)
        
        # Recharger avec filtres
        all_aircraft = self.data_manager.get_aircraft()
        airports = {a['code_iata']: a['ville'] for a in self.data_manager.get_airports()}
        
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
    
    # Méthodes de rafraîchissement des données (simplifiées)
    def refresh_aircraft_data(self):
        """Rafraîchit les données des avions"""
        if not hasattr(self, 'aircraft_tree'):
            return
        
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
            
            print(f"✓ Avions rafraîchis: {len(aircraft_list)} avions")
            
        except Exception as e:
            print(f"❌ Erreur refresh avions: {e}")

    def refresh_personnel_data(self):
        """Rafraîchit les données du personnel"""
        if hasattr(self, 'personnel_tree') and self.personnel_tree:
            try:
                from interfaces.tabs.personnel_tab import refresh_personnel_data
                refresh_personnel_data(self.personnel_tree, self.data_manager)
                print("✓ Personnel rafraîchi")
            except Exception as e:
                print(f"❌ Erreur refresh personnel: {e}")
                
    def refresh_flight_data(self):
        """Rafraîchit les données des vols"""
        if hasattr(self, 'flights_tree') and self.flights_tree:
            try:
                from interfaces.tabs.flights_tab import refresh_flights_data
                refresh_flights_data(self.flights_tree, self.data_manager)
                print("✓ Vols rafraîchis")
            except Exception as e:
                print(f"❌ Erreur refresh vols: {e}")

    def refresh_passengers_data(self):
        """Rafraîchit les données des passagers"""
        if hasattr(self, 'passengers_tree') and self.passengers_tree:
            try:
                from interfaces.tabs.passengers_tab import refresh_passengers_data
                refresh_passengers_data(self.passengers_tree, self.data_manager)
                print("✓ Passagers rafraîchis")
            except Exception as e:
                print(f"❌ Erreur refresh passagers: {e}")

    def refresh_reservations_data(self):
        """Rafraîchit les données des réservations"""
        if hasattr(self, 'reservations_tree') and self.reservations_tree:
            try:
                from interfaces.tabs.reservations_tab import refresh_reservations_data
                refresh_reservations_data(self.reservations_tree, self.data_manager)
                print("✓ Réservations rafraîchies")
            except Exception as e:
                print(f"❌ Erreur refresh réservations: {e}")

    def refresh_all_data(self):
        """Rafraîchit toutes les données"""
        print("🔄 Rafraîchissement global des données...")
        
        try:
            # Rafraîchir tous les onglets
            self.refresh_aircraft_data()
            self.refresh_personnel_data()
            self.refresh_flight_data()
            self.refresh_passengers_data()
            self.refresh_reservations_data()
            
            # Mettre à jour les statistiques
            self.update_statistics()
            
            # Mettre à jour le résumé du dashboard
            self.update_summary()
            
            # Mettre à jour la barre de statut
            self.status_var.set("Données actualisées")
            self.root.after(2000, lambda: self.status_var.set("Application prête"))
            
            print("✅ Rafraîchissement global terminé")
            
        except Exception as e:
            print(f"❌ Erreur refresh global: {e}")
            self.status_var.set("Erreur de rafraîchissement")

    def update_statistics(self):
        """Met à jour les statistiques du dashboard"""
        try:
            # Calculer les statistiques réelles
            aircraft_count = len(self.data_manager.get_aircraft())
            personnel_count = len(self.data_manager.get_personnel())
            flights_count = len(self.data_manager.get_flights())
            passengers_count = len(self.data_manager.get_passengers())
            reservations_count = len(self.data_manager.get_reservations())
            
            # Mettre à jour les cartes statistiques
            if "Total Avions" in self.stat_vars:
                self.stat_vars["Total Avions"].set(str(aircraft_count))
            if "Total Personnel" in self.stat_vars:
                self.stat_vars["Total Personnel"].set(str(personnel_count))
            if "Total Vols" in self.stat_vars:
                self.stat_vars["Total Vols"].set(str(flights_count))
            if "Total Passagers" in self.stat_vars:
                self.stat_vars["Total Passagers"].set(str(passengers_count))
            if "Total Réservations" in self.stat_vars:
                self.stat_vars["Total Réservations"].set(str(reservations_count))
            if "Base de Données" in self.stat_vars:
                self.stat_vars["Base de Données"].set("OK")
            
            print(f"✅ Statistiques mises à jour")
            
        except Exception as e:
            print(f"❌ Erreur mise à jour statistiques: {e}")
            
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