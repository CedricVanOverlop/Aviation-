import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.aviation import Coordonnees
from Core.enums import EtatAvion

class AircraftDialog:
    """Dialogue pour créer ou modifier un avion"""
    
    def __init__(self, parent, data_manager, aircraft_data=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Fenêtre parente
            data_manager: Gestionnaire de données
            aircraft_data: Données d'avion existant (pour modification)
        """
        self.parent = parent
        self.data_manager = data_manager
        self.aircraft_data = aircraft_data
        self.is_editing = aircraft_data is not None
        self.result = None
        
        # Créer la fenêtre dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modification d'un Avion" if self.is_editing else "Création d'un Nouvel Avion")
        self.dialog.geometry("650x850")  # Agrandissement de la fenêtre
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables pour les champs
        self.setup_variables()
        
        # Charger les données de référence
        self.load_reference_data()
        
        # Créer l'interface
        self.setup_ui()
        
        # Pré-remplir si modification
        if self.is_editing:
            self.populate_fields()
        
        # Focus sur le premier champ
        self.id_entry.focus()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (650 // 2)  # Ajustement pour la nouvelle taille
        y = (self.dialog.winfo_screenheight() // 2) - (750 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables pour les champs"""
        self.id_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.company_var = tk.StringVar()
        self.capacity_var = tk.StringVar()
        self.cruise_speed_var = tk.StringVar()
        self.autonomy_var = tk.StringVar()
        self.airport_var = tk.StringVar()
        self.state_var = tk.StringVar()
        self.use_predefined_var = tk.BooleanVar(value=False)
        self.predefined_model_var = tk.StringVar()
    
    def load_reference_data(self):
        """Charge les données de référence"""
        self.airports = self.data_manager.get_airports()
        self.aircraft_models = self.data_manager.get_aircraft_models()
        
        # Préparer les listes pour les combobox
        self.airport_choices = [f"{airport['code_iata']} - {airport['nom']} ({airport['ville']})" 
                               for airport in self.airports]
        
        self.model_choices = [f"{model['modele']} - {model['description']}" 
                             for model in self.aircraft_models]
        
        self.state_choices = ['Opérationnel', 'Au sol', 'En maintenance', 'Hors service']
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec défilement
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Modification d'un Avion" if self.is_editing else "Création d'un Nouvel Avion",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Section modèle prédéfini
        self.create_predefined_section(main_frame)
        
        # Séparateur
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Section détails de l'avion
        self.create_aircraft_details_section(main_frame)
        
        # Section localisation
        self.create_location_section(main_frame)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_predefined_section(self, parent):
        """Crée la section des modèles prédéfinis"""
        predefined_frame = ttk.LabelFrame(parent, text="🛩️ Modèles Prédéfinis", padding=15)
        predefined_frame.pack(fill="x", pady=(0, 10))
        
        # Checkbox pour utiliser un modèle prédéfini
        use_predefined_cb = ttk.Checkbutton(predefined_frame, 
                                           text="Utiliser un modèle prédéfini",
                                           variable=self.use_predefined_var,
                                           command=self.on_predefined_toggle)
        use_predefined_cb.pack(anchor="w", pady=(0, 10))
        
        # Combobox des modèles
        ttk.Label(predefined_frame, text="Modèle:").pack(anchor="w")
        self.predefined_combo = ttk.Combobox(predefined_frame, 
                                           textvariable=self.predefined_model_var,
                                           values=self.model_choices,
                                           state="disabled",
                                           width=60)
        self.predefined_combo.pack(fill="x", pady=(5, 10))
        self.predefined_combo.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        # Bouton pour appliquer le modèle
        self.apply_model_btn = ttk.Button(predefined_frame, 
                                         text="📋 Appliquer ce modèle",
                                         command=self.apply_predefined_model,
                                         state="disabled")
        self.apply_model_btn.pack(anchor="w")
    
    def create_aircraft_details_section(self, parent):
        """Crée la section des détails de l'avion"""
        details_frame = ttk.LabelFrame(parent, text="✈️ Détails de l'Avion", padding=15)
        details_frame.pack(fill="x", pady=(0, 10))
        
        # Configuration de la grille
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Identifiant
        ttk.Label(details_frame, text="Identifiant*:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_entry = ttk.Entry(details_frame, textvariable=self.id_var, width=20)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(details_frame, text="Ex: F-ABCD", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Modèle
        ttk.Label(details_frame, text="Modèle*:").grid(row=1, column=0, sticky="w", pady=5)
        self.model_entry = ttk.Entry(details_frame, textvariable=self.model_var, width=30)
        self.model_entry.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(details_frame, text="Ex: Airbus A320", foreground="gray").grid(row=1, column=2, sticky="w", padx=5)
        
        # Compagnie
        ttk.Label(details_frame, text="Compagnie*:").grid(row=2, column=0, sticky="w", pady=5)
        self.company_entry = ttk.Entry(details_frame, textvariable=self.company_var, width=30)
        self.company_entry.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(details_frame, text="Ex: Air France", foreground="gray").grid(row=2, column=2, sticky="w", padx=5)
        
        # Capacité
        ttk.Label(details_frame, text="Capacité (passagers)*:").grid(row=3, column=0, sticky="w", pady=5)
        self.capacity_entry = ttk.Entry(details_frame, textvariable=self.capacity_var, width=10)
        self.capacity_entry.grid(row=3, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(details_frame, text="Ex: 180", foreground="gray").grid(row=3, column=2, sticky="w", padx=5)
        
        # Vitesse de croisière
        ttk.Label(details_frame, text="Vitesse Croisière (km/h)*:").grid(row=4, column=0, sticky="w", pady=5)
        self.cruise_speed_entry = ttk.Entry(details_frame, textvariable=self.cruise_speed_var, width=10)
        self.cruise_speed_entry.grid(row=4, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(details_frame, text="Ex: 850", foreground="gray").grid(row=4, column=2, sticky="w", padx=5)
        
        # Autonomie
        ttk.Label(details_frame, text="Autonomie (km)*:").grid(row=5, column=0, sticky="w", pady=5)
        self.autonomy_entry = ttk.Entry(details_frame, textvariable=self.autonomy_var, width=10)
        self.autonomy_entry.grid(row=5, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(details_frame, text="Ex: 6000", foreground="gray").grid(row=5, column=2, sticky="w", padx=5)
        
        # État
        ttk.Label(details_frame, text="État:").grid(row=6, column=0, sticky="w", pady=5)
        self.state_combo = ttk.Combobox(details_frame, textvariable=self.state_var,
                                       values=self.state_choices, state="readonly", width=20)
        self.state_combo.grid(row=6, column=1, sticky="w", padx=(10, 5), pady=5)
        self.state_var.set("Opérationnel")  # Valeur par défaut
    
    def create_location_section(self, parent):
        """Crée la section de localisation"""
        location_frame = ttk.LabelFrame(parent, text="📍 Localisation", padding=15)
        location_frame.pack(fill="x", pady=(0, 10))
        
        location_frame.grid_columnconfigure(1, weight=1)
        
        # Aéroport de base
        ttk.Label(location_frame, text="Aéroport de base*:").grid(row=0, column=0, sticky="w", pady=5)
        self.airport_combo = ttk.Combobox(location_frame, textvariable=self.airport_var,
                                         values=self.airport_choices, width=50)
        self.airport_combo.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Coordinates (automatiquement remplies)
        ttk.Label(location_frame, text="Coordonnées:").grid(row=1, column=0, sticky="w", pady=5)
        self.coords_label = ttk.Label(location_frame, text="Sélectionnez un aéroport", foreground="gray")
        self.coords_label.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # Bind pour mise à jour automatique des coordonnées
        self.airport_combo.bind('<<ComboboxSelected>>', self.on_airport_selected)
        self.airport_combo.bind('<KeyRelease>', self.on_airport_typed)
    
    def create_buttons(self, parent):
        """Crée les boutons du dialogue"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Note sur les champs obligatoires
        ttk.Label(button_frame, text="* Champs obligatoires", 
                 foreground="red", font=('Arial', 9)).pack(anchor="w", pady=(0, 10))
        
        # Boutons
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack(anchor="e")
        
        # Bouton Annuler
        btn_cancel = ttk.Button(buttons_container, text="Annuler", 
                               command=self.cancel)
        btn_cancel.pack(side="right", padx=(10, 0))
        
        # Bouton Créer/Modifier
        btn_save = ttk.Button(buttons_container, 
                             text="Modifier" if self.is_editing else "Créer", 
                             command=self.save_aircraft)
        btn_save.pack(side="right")
        
        # Rendre les boutons plus visibles
        btn_save.configure(style='Action.TButton')
        
        print("✓ Boutons créés dans aircraft_dialog")
    
    def on_predefined_toggle(self):
        """Gestionnaire pour l'activation/désactivation des modèles prédéfinis"""
        if self.use_predefined_var.get():
            self.predefined_combo.config(state="readonly")
            self.apply_model_btn.config(state="normal")
        else:
            self.predefined_combo.config(state="disabled")
            self.apply_model_btn.config(state="disabled")
            self.predefined_model_var.set("")
    
    def on_model_selected(self, event=None):
        """Gestionnaire de sélection de modèle prédéfini"""
        selection = self.predefined_model_var.get()
        if selection:
            # Extraire le nom du modèle
            model_name = selection.split(" - ")[0]
            
            # Trouver le modèle complet
            for model in self.aircraft_models:
                if model['modele'] == model_name:
                    # Afficher les détails du modèle sélectionné
                    details = (f"Capacité: {model['capacite']} passagers\n"
                              f"Vitesse: {model['vitesse_croisiere']} km/h\n"
                              f"Autonomie: {model['autonomie']} km\n"
                              f"Type: {model['compagnie_type']}")
                    
                    messagebox.showinfo("Détails du Modèle", 
                                       f"Modèle: {model['modele']}\n\n{details}")
                    break
    
    def apply_predefined_model(self):
        """Applique les données du modèle prédéfini"""
        selection = self.predefined_model_var.get()
        if not selection:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un modèle.")
            return
        
        # Extraire le nom du modèle
        model_name = selection.split(" - ")[0]
        
        # Trouver et appliquer le modèle
        for model in self.aircraft_models:
            if model['modele'] == model_name:
                self.model_var.set(model['modele'])
                self.capacity_var.set(str(model['capacite']))
                self.cruise_speed_var.set(str(model['vitesse_croisiere']))
                self.autonomy_var.set(str(model['autonomie']))
                
                # Générer un ID automatique si vide
                if not self.id_var.get():
                    prefix = model['modele'].replace(' ', '').replace('-', '')[:3].upper()
                    unique_id = f"{prefix}-{str(uuid.uuid4())[:4].upper()}"
                    self.id_var.set(unique_id)
                
                messagebox.showinfo("Succès", f"Modèle {model['modele']} appliqué avec succès!")
                break
    
    def on_airport_selected(self, event=None):
        """Gestionnaire de sélection d'aéroport"""
        self.update_coordinates()
    
    def on_airport_typed(self, event=None):
        """Gestionnaire de saisie manuelle d'aéroport"""
        # Recherche automatique pendant la saisie
        typed = self.airport_var.get().upper()
        if len(typed) >= 3:
            matches = [choice for choice in self.airport_choices 
                      if typed in choice.upper()]
            if matches:
                self.airport_combo['values'] = matches
        else:
            self.airport_combo['values'] = self.airport_choices
        
        self.update_coordinates()
    
    def update_coordinates(self):
        """Met à jour l'affichage des coordonnées"""
        selection = self.airport_var.get()
        
        # Extraire le code IATA
        if ' - ' in selection:
            code_iata = selection.split(' - ')[0]
            
            # Trouver l'aéroport correspondant
            for airport in self.airports:
                if airport['code_iata'] == code_iata:
                    coords = airport['coordonnees']
                    coord_text = f"Lat: {coords['latitude']:.4f}, Lon: {coords['longitude']:.4f}"
                    self.coords_label.config(text=coord_text, foreground="blue")
                    return
        
        self.coords_label.config(text="Aéroport non trouvé", foreground="red")
    
    def populate_fields(self):
        """Pré-remplit les champs pour la modification"""
        if not self.aircraft_data:
            return
        
        self.id_var.set(self.aircraft_data.get('num_id', ''))
        self.model_var.set(self.aircraft_data.get('modele', ''))
        self.company_var.set(self.aircraft_data.get('compagnie_aerienne', ''))
        self.capacity_var.set(str(self.aircraft_data.get('capacite', '')))
        self.cruise_speed_var.set(str(self.aircraft_data.get('vitesse_croisiere', '')))
        self.autonomy_var.set(str(self.aircraft_data.get('autonomie', '')))
        
        # État
        state_mapping = {
            'operationnel': 'Opérationnel',
            'au_sol': 'Au sol',
            'en_maintenance': 'En maintenance',
            'hors_service': 'Hors service'
        }
        current_state = self.aircraft_data.get('etat', 'operationnel')
        self.state_var.set(state_mapping.get(current_state, 'Opérationnel'))
        
        # Localisation (trouver l'aéroport correspondant)
        if 'localisation' in self.aircraft_data:
            coords = self.aircraft_data['localisation']
            for airport in self.airports:
                airport_coords = airport['coordonnees']
                if (abs(airport_coords['latitude'] - coords.get('latitude', 0)) < 0.1 and
                    abs(airport_coords['longitude'] - coords.get('longitude', 0)) < 0.1):
                    airport_choice = f"{airport['code_iata']} - {airport['nom']} ({airport['ville']})"
                    self.airport_var.set(airport_choice)
                    self.update_coordinates()
                    break
    
    def validate_fields(self):
        """Valide tous les champs obligatoires"""
        errors = []
        
        # Vérifications de base
        if not self.id_var.get().strip():
            errors.append("L'identifiant est obligatoire")
        
        if not self.model_var.get().strip():
            errors.append("Le modèle est obligatoire")
        
        if not self.company_var.get().strip():
            errors.append("La compagnie est obligatoire")
        
        if not self.airport_var.get().strip():
            errors.append("L'aéroport de base est obligatoire")
        
        # Vérifications numériques
        try:
            capacity = int(self.capacity_var.get())
            if capacity <= 0:
                errors.append("La capacité doit être un nombre positif")
        except ValueError:
            errors.append("La capacité doit être un nombre entier")
        
        try:
            speed = float(self.cruise_speed_var.get())
            if speed <= 0:
                errors.append("La vitesse de croisière doit être positive")
        except ValueError:
            errors.append("La vitesse de croisière doit être un nombre")
        
        try:
            autonomy = float(self.autonomy_var.get())
            if autonomy <= 0:
                errors.append("L'autonomie doit être positive")
        except ValueError:
            errors.append("L'autonomie doit être un nombre")
        
        # Vérification unicité de l'ID (sauf en modification)
        if not self.is_editing:
            aircraft_id = self.id_var.get().strip()
            existing_aircraft = self.data_manager.get_aircraft()
            if any(a.get('num_id') == aircraft_id for a in existing_aircraft):
                errors.append(f"Un avion avec l'ID '{aircraft_id}' existe déjà")
        
        # Vérification aéroport valide
        airport_selection = self.airport_var.get()
        if airport_selection and ' - ' in airport_selection:
            code_iata = airport_selection.split(' - ')[0]
            if not any(a['code_iata'] == code_iata for a in self.airports):
                errors.append("Aéroport sélectionné invalide")
        elif airport_selection:
            errors.append("Format d'aéroport invalide")
        
        return errors
    
    def save_aircraft(self):
        """Sauvegarde l'avion"""
        # Validation
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Erreurs de Validation", 
                               "Veuillez corriger les erreurs suivantes:\n\n" + 
                               "\n".join(f"• {error}" for error in errors))
            return
        
        try:
            # Obtenir les coordonnées de l'aéroport
            airport_selection = self.airport_var.get()
            code_iata = airport_selection.split(' - ')[0]
            
            coordinates = None
            for airport in self.airports:
                if airport['code_iata'] == code_iata:
                    coords = airport['coordonnees']
                    coordinates = {
                        'latitude': coords['latitude'],
                        'longitude': coords['longitude']
                    }
                    break
            
            # Mapping des états
            state_mapping = {
                'Opérationnel': 'operationnel',
                'Au sol': 'au_sol',
                'En maintenance': 'en_maintenance',
                'Hors service': 'hors_service'
            }
            
            # Construire les données de l'avion
            aircraft_data = {
                'num_id': self.id_var.get().strip(),
                'modele': self.model_var.get().strip(),
                'compagnie_aerienne': self.company_var.get().strip(),
                'capacite': int(self.capacity_var.get()),
                'vitesse_croisiere': float(self.cruise_speed_var.get()),
                'autonomie': float(self.autonomy_var.get()),
                'localisation': coordinates,
                'etat': state_mapping.get(self.state_var.get(), 'operationnel'),
                'vol_actuel': None,
                'derniere_maintenance': None
            }
            
            # Sauvegarder
            if self.is_editing:
                success = self.data_manager.update_aircraft(aircraft_data['num_id'], aircraft_data)
                action = "modifié"
            else:
                success = self.data_manager.add_aircraft(aircraft_data)
                action = "créé"
            
            if success:
                self.result = aircraft_data
                messagebox.showinfo("Succès", f"Avion {action} avec succès!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", f"Impossible de {action.replace('é', 'er')} l'avion.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            print(f"❌ Erreur sauvegarde avion: {e}")
    
    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy() 