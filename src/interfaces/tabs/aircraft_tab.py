import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os
from datetime import datetime, timedelta
import re

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.aviation import Coordonnees
from Core.enums import EtatAvion


class FieldValidator:
    """Validateur de champs intelligent avec feedback en temps réel"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.existing_aircraft = data_manager.get_aircraft()
    
    def validate_aircraft_id(self, aircraft_id, is_editing=False, original_id=None):
        """Valide l'ID d'avion"""
        if not aircraft_id or not aircraft_id.strip():
            return False, "L'identifiant est obligatoire"
        
        aircraft_id = aircraft_id.strip().upper()
        
        # Format validation (lettres et chiffres, tirets autorisés)
        if not re.match(r'^[A-Z0-9\-]{3,15}$', aircraft_id):
            return False, "Format invalide (3-15 caractères, lettres/chiffres/tirets)"
        
        # Unicité (sauf si on modifie et c'est le même ID)
        if not is_editing or (original_id and aircraft_id != original_id):
            if any(a.get('num_id', '').upper() == aircraft_id for a in self.existing_aircraft):
                return False, f"L'ID '{aircraft_id}' existe déjà"
        
        return True, "✓ ID valide"
    
    def validate_model(self, model):
        """Valide le modèle d'avion"""
        if not model or not model.strip():
            return False, "Le modèle est obligatoire"
        
        model = model.strip()
        if len(model) < 2:
            return False, "Le modèle doit contenir au moins 2 caractères"
        
        if len(model) > 50:
            return False, "Le modèle ne peut pas dépasser 50 caractères"
        
        return True, "✓ Modèle valide"
    
    def validate_company(self, company):
        """Valide la compagnie aérienne"""
        if not company or not company.strip():
            return False, "La compagnie est obligatoire"
        
        company = company.strip()
        if len(company) < 2:
            return False, "La compagnie doit contenir au moins 2 caractères"
        
        return True, "✓ Compagnie valide"
    
    def validate_capacity(self, capacity_str):
        """Valide la capacité"""
        try:
            capacity = int(capacity_str)
            if capacity <= 0:
                return False, "La capacité doit être positive"
            if capacity > 1000:
                return False, "Capacité irréaliste (max 1000)"
            if capacity < 10:
                return False, "Capacité trop faible (min 10)"
            return True, f"✓ Capacité valide ({capacity} passagers)"
        except ValueError:
            return False, "La capacité doit être un nombre entier"
    
    def validate_speed(self, speed_str):
        """Valide la vitesse de croisière"""
        try:
            speed = float(speed_str)
            if speed <= 0:
                return False, "La vitesse doit être positive"
            if speed < 200:
                return False, "Vitesse trop faible pour un avion commercial"
            if speed > 3000:
                return False, "Vitesse irréaliste (max 3000 km/h)"
            return True, f"✓ Vitesse valide ({speed} km/h)"
        except ValueError:
            return False, "La vitesse doit être un nombre"
    
    def validate_autonomy(self, autonomy_str):
        """Valide l'autonomie"""
        try:
            autonomy = float(autonomy_str)
            if autonomy <= 0:
                return False, "L'autonomie doit être positive"
            if autonomy < 500:
                return False, "Autonomie trop faible (min 500 km)"
            if autonomy > 20000:
                return False, "Autonomie irréaliste (max 20000 km)"
            return True, f"✓ Autonomie valide ({autonomy} km)"
        except ValueError:
            return False, "L'autonomie doit être un nombre"


class FormField:
    """Composant de champ de formulaire standardisé avec validation"""
    
    def __init__(self, parent, label_text, field_type="entry", validator=None, 
                 placeholder="", choices=None, width=30, required=True):
        self.parent = parent
        self.label_text = label_text
        self.field_type = field_type
        self.validator = validator
        self.required = required
        
        # Variables
        self.var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.is_valid = tk.BooleanVar(value=not required)  # Non requis = valide par défaut
        
        # Widgets
        self.label = None
        self.widget = None
        self.status_label = None
        
        self.create_widgets(placeholder, choices, width)
        self.setup_validation()
    
    def create_widgets(self, placeholder, choices, width):
        """Crée les widgets du champ"""
        # Label avec indicateur obligatoire
        label_text = self.label_text
        if self.required:
            label_text += "*"
        self.label = ttk.Label(self.parent, text=label_text)
        
        # Widget selon le type
        if self.field_type == "entry":
            self.widget = ttk.Entry(self.parent, textvariable=self.var, width=width)
            if placeholder:
                self.widget.insert(0, placeholder)
                self.widget.bind('<FocusIn>', self._clear_placeholder)
                
        elif self.field_type == "combobox":
            self.widget = ttk.Combobox(self.parent, textvariable=self.var, 
                                     values=choices or [], width=width-3)
            
        elif self.field_type == "spinbox":
            self.widget = tk.Spinbox(self.parent, textvariable=self.var, 
                                   from_=0, to=999999, width=width-5)
        
        # Label de statut pour feedback
        self.status_label = ttk.Label(self.parent, textvariable=self.status_var,
                                    font=('Arial', 9))
    
    def setup_validation(self):
        """Configure la validation en temps réel"""
        if self.validator:
            self.var.trace('w', self._validate)
            if not self.required:
                self._validate()  # Validation initiale pour champs optionnels
    
    def _validate(self, *args):
        """Valide le champ en temps réel"""
        value = self.var.get().strip()
        
        # Si le champ n'est pas requis et est vide, c'est valide
        if not self.required and not value:
            self.is_valid.set(True)
            self.status_var.set("")
            self.status_label.configure(foreground="gray")
            return
        
        # Validation avec le validateur
        if self.validator:
            try:
                is_valid, message = self.validator(value)
                self.is_valid.set(is_valid)
                self.status_var.set(message)
                
                if is_valid:
                    self.status_label.configure(foreground="green")
                else:
                    self.status_label.configure(foreground="red")
            except Exception as e:
                self.is_valid.set(False)
                self.status_var.set(f"Erreur validation: {e}")
                self.status_label.configure(foreground="red")
    
    def _clear_placeholder(self, event):
        """Efface le placeholder lors du focus"""
        if self.widget.get() and self.widget.get().startswith("Ex:"):
            self.widget.delete(0, tk.END)
    
    def grid(self, row, column=0, **kwargs):
        """Place le champ dans la grille"""
        # Label
        self.label.grid(row=row, column=column, sticky="w", pady=5)
        
        # Widget principal
        self.widget.grid(row=row, column=column+1, sticky="ew", padx=(10, 5), pady=5)
        
        # Label de statut
        self.status_label.grid(row=row+1, column=column+1, sticky="w", padx=(10, 5))
        
        return row + 2  # Retourne la prochaine ligne disponible
    
    def get_value(self):
        """Récupère la valeur du champ"""
        return self.var.get().strip()
    
    def set_value(self, value):
        """Définit la valeur du champ"""
        self.var.set(str(value) if value is not None else "")
        if self.validator:
            self._validate()
    
    def is_field_valid(self):
        """Vérifie si le champ est valide"""
        return self.is_valid.get()


class ModernAircraftDialog:
    """Dialogue moderne pour créer ou modifier un avion avec corrections de bugs"""
    
    def __init__(self, parent, data_manager, aircraft_data=None, notification_center=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Fenêtre parente
            data_manager: Gestionnaire de données
            aircraft_data: Données d'avion existant (pour modification)
            notification_center: Centre de notifications (optionnel)
        """
        self.parent = parent
        self.data_manager = data_manager
        self.aircraft_data = aircraft_data
        self.notification_center = notification_center
        self.is_editing = aircraft_data is not None
        self.result = None
        
        # Validateur
        self.validator = FieldValidator(data_manager)
        
        # Données de référence
        self.load_reference_data()
        
        # Créer la fenêtre dialogue
        self.create_dialog()
        
        # Variables de validation globale
        self.form_valid = tk.BooleanVar(value=False)
        
        # Configuration de l'interface
        self.setup_ui()
        
        # Pré-remplir si modification
        if self.is_editing:
            self.populate_fields()
        
        # Validation initiale
        self.validate_form()
        
        # Focus initial
        if hasattr(self, 'id_field'):
            self.id_field.widget.focus()
    
    def create_dialog(self):
        """Crée la fenêtre de dialogue responsive"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("✏️ Modifier un Avion" if self.is_editing else "➕ Créer un Nouvel Avion")
        
        # Taille adaptive selon l'écran
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # 60% de la largeur, 80% de la hauteur, mais avec des limites
        width = max(700, min(900, int(screen_width * 0.6)))
        height = max(600, min(800, int(screen_height * 0.8)))
        
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(True, True)  # Permettre le redimensionnement
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configuration responsive
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Raccourcis clavier
        self.dialog.bind('<Control-s>', lambda e: self.save_aircraft())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        self.dialog.bind('<Control-Return>', lambda e: self.save_aircraft())
    
    def load_reference_data(self):
        """Charge les données de référence"""
        try:
            self.airports = self.data_manager.get_airports()
            self.aircraft_models = self.data_manager.get_aircraft_models()
            
            # Préparer les listes pour les combobox
            self.airport_choices = [f"{airport['code_iata']} - {airport['nom']} ({airport['ville']})" 
                                   for airport in self.airports]
            
            self.model_choices = [f"{model['modele']} - {model['description']}" 
                                 for model in self.aircraft_models]
            
            self.state_choices = ['Opérationnel', 'Au sol', 'En maintenance', 'Hors service']
            
        except Exception as e:
            print(f"❌ Erreur chargement données référence: {e}")
            # Données par défaut si erreur
            self.airports = []
            self.aircraft_models = []
            self.airport_choices = []
            self.model_choices = []
            self.state_choices = ['Opérationnel', 'Au sol', 'En maintenance', 'Hors service']
    
    def setup_ui(self):
        """Configure l'interface utilisateur moderne"""
        # Frame principal avec scroll
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configuration du scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configuration responsive
        canvas.grid_rowconfigure(0, weight=1)
        canvas.grid_columnconfigure(0, weight=1)
        
        # Support de la molette de souris
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Titre avec icône
        title_text = "✏️ Modification d'un Avion" if self.is_editing else "➕ Création d'un Nouvel Avion"
        title_label = ttk.Label(self.scrollable_frame, text=title_text,
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Section modèles prédéfinis
        self.create_predefined_section()
        
        # Séparateur
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Section détails avion
        self.create_aircraft_details_section()
        
        # Section localisation
        self.create_location_section()
        
        # Section statut
        self.create_status_section()
        
        # Boutons
        self.create_buttons()
    
    def create_predefined_section(self):
        """Crée la section des modèles prédéfinis"""
        predefined_frame = ttk.LabelFrame(self.scrollable_frame, text="🛩️ Modèles Prédéfinis", padding=15)
        predefined_frame.pack(fill="x", pady=(0, 10))
        
        predefined_frame.grid_columnconfigure(1, weight=1)
        
        # Checkbox pour utiliser un modèle prédéfini
        self.use_predefined_var = tk.BooleanVar(value=False)
        use_predefined_cb = ttk.Checkbutton(predefined_frame, 
                                           text="Utiliser un modèle prédéfini",
                                           variable=self.use_predefined_var,
                                           command=self.on_predefined_toggle)
        use_predefined_cb.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Combobox des modèles
        ttk.Label(predefined_frame, text="Modèle:").grid(row=1, column=0, sticky="w", pady=5)
        self.predefined_model_var = tk.StringVar()
        self.predefined_combo = ttk.Combobox(predefined_frame, 
                                           textvariable=self.predefined_model_var,
                                           values=self.model_choices,
                                           state="disabled",
                                           width=50)
        self.predefined_combo.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.predefined_combo.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        # Bouton pour appliquer le modèle
        self.apply_model_btn = ttk.Button(predefined_frame, 
                                         text="📋 Appliquer ce modèle",
                                         command=self.apply_predefined_model,
                                         state="disabled")
        self.apply_model_btn.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
    
    def create_aircraft_details_section(self):
        """Crée la section des détails avec validation en temps réel"""
        details_frame = ttk.LabelFrame(self.scrollable_frame, text="✈️ Détails de l'Avion", padding=15)
        details_frame.pack(fill="x", pady=(0, 10))
        
        details_frame.grid_columnconfigure(1, weight=1)
        
        current_row = 0
        
        # ID avec validation unique
        original_id = self.aircraft_data.get('num_id') if self.is_editing else None
        id_validator = lambda value: self.validator.validate_aircraft_id(
            value, self.is_editing, original_id)
        
        self.id_field = FormField(details_frame, "Identifiant", "entry", 
                                 id_validator, "Ex: F-ABCD", width=20)
        current_row = self.id_field.grid(current_row)
        
        # Modèle
        self.model_field = FormField(details_frame, "Modèle", "entry", 
                                   self.validator.validate_model, "Ex: Airbus A320", width=30)
        current_row = self.model_field.grid(current_row)
        
        # Compagnie
        self.company_field = FormField(details_frame, "Compagnie", "entry", 
                                     self.validator.validate_company, "Ex: Air France", width=30)
        current_row = self.company_field.grid(current_row)
        
        # Capacité
        self.capacity_field = FormField(details_frame, "Capacité (passagers)", "spinbox", 
                                      self.validator.validate_capacity, width=15)
        current_row = self.capacity_field.grid(current_row)
        
        # Vitesse de croisière
        self.speed_field = FormField(details_frame, "Vitesse Croisière (km/h)", "spinbox", 
                                   self.validator.validate_speed, width=15)
        current_row = self.speed_field.grid(current_row)
        
        # Autonomie
        self.autonomy_field = FormField(details_frame, "Autonomie (km)", "spinbox", 
                                      self.validator.validate_autonomy, width=15)
        current_row = self.autonomy_field.grid(current_row)
        
        # Observer les changements pour validation globale
        for field in [self.id_field, self.model_field, self.company_field, 
                     self.capacity_field, self.speed_field, self.autonomy_field]:
            field.is_valid.trace('w', self.validate_form)
    
    def create_location_section(self):
        """Crée la section de localisation"""
        location_frame = ttk.LabelFrame(self.scrollable_frame, text="📍 Localisation", padding=15)
        location_frame.pack(fill="x", pady=(0, 10))
        
        location_frame.grid_columnconfigure(1, weight=1)
        
        # Aéroport de base
        ttk.Label(location_frame, text="Aéroport de base*:").grid(row=0, column=0, sticky="w", pady=5)
        self.airport_var = tk.StringVar()
        self.airport_combo = ttk.Combobox(location_frame, textvariable=self.airport_var,
                                         values=self.airport_choices, width=50)
        self.airport_combo.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Coordonnées (affichage automatique)
        ttk.Label(location_frame, text="Coordonnées:").grid(row=1, column=0, sticky="w", pady=5)
        self.coords_var = tk.StringVar(value="Sélectionnez un aéroport")
        self.coords_label = ttk.Label(location_frame, textvariable=self.coords_var, foreground="gray")
        self.coords_label.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # Bind pour mise à jour automatique des coordonnées
        self.airport_combo.bind('<<ComboboxSelected>>', self.update_coordinates)
        self.airport_combo.bind('<KeyRelease>', self.update_coordinates)
        
        # Validation de l'aéroport
        self.airport_valid = tk.BooleanVar(value=False)
        self.airport_status_var = tk.StringVar()
        self.airport_status_label = ttk.Label(location_frame, textvariable=self.airport_status_var, font=('Arial', 9))
        self.airport_status_label.grid(row=2, column=1, sticky="w", padx=(10, 5))
        
        self.airport_var.trace('w', self.validate_airport)
        self.airport_valid.trace('w', self.validate_form)
    
    def create_status_section(self):
        """Crée la section du statut"""
        status_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 État et Maintenance", padding=15)
        status_frame.pack(fill="x", pady=(0, 10))
        
        status_frame.grid_columnconfigure(1, weight=1)
        
        # État
        ttk.Label(status_frame, text="État:").grid(row=0, column=0, sticky="w", pady=5)
        self.state_var = tk.StringVar(value="Opérationnel")
        self.state_combo = ttk.Combobox(status_frame, textvariable=self.state_var,
                                       values=self.state_choices, state="readonly", width=20)
        self.state_combo.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # Informations de maintenance (si édition)
        if self.is_editing and self.aircraft_data:
            maintenance_info = self.aircraft_data.get('derniere_maintenance', 'Jamais')
            ttk.Label(status_frame, text="Dernière maintenance:").grid(row=1, column=0, sticky="w", pady=5)
            ttk.Label(status_frame, text=maintenance_info, foreground="blue").grid(row=1, column=1, sticky="w", padx=(10, 5), pady=5)
    
    def create_buttons(self):
        """Crée les boutons avec état intelligent"""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Note sur les champs obligatoires
        ttk.Label(button_frame, text="* Champs obligatoires", 
                 foreground="red", font=('Arial', 9)).pack(anchor="w", pady=(0, 10))
        
        # Frame pour les boutons
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack(anchor="e")
        
        # Bouton Annuler
        btn_cancel = ttk.Button(buttons_container, text="❌ Annuler", 
                               command=self.cancel, width=15)
        btn_cancel.pack(side="right", padx=(10, 0))
        
        # Bouton Sauvegarder (état intelligent)
        save_text = "💾 Modifier" if self.is_editing else "➕ Créer"
        self.save_btn = ttk.Button(buttons_container, text=save_text, 
                                  command=self.save_aircraft, width=15)
        self.save_btn.pack(side="right")
        
        # État initial du bouton
        self.update_save_button_state()
        
        # Note sur les raccourcis
        shortcuts_label = ttk.Label(button_frame, 
                                   text="💡 Ctrl+S pour sauvegarder, Échap pour annuler", 
                                   font=('Arial', 8), foreground='gray')
        shortcuts_label.pack(anchor="e", pady=(5, 0))
    
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
            model_name = selection.split(" - ")[0]
            
            for model in self.aircraft_models:
                if model['modele'] == model_name:
                    details = (f"📊 Spécifications du modèle:\n\n"
                              f"• Capacité: {model['capacite']} passagers\n"
                              f"• Vitesse: {model['vitesse_croisiere']} km/h\n"
                              f"• Autonomie: {model['autonomie']} km\n"
                              f"• Type: {model['compagnie_type']}\n\n"
                              f"Cliquez sur 'Appliquer' pour utiliser ces valeurs.")
                    
                    messagebox.showinfo("Détails du Modèle", details)
                    break
    
    def apply_predefined_model(self):
        """Applique les données du modèle prédéfini"""
        selection = self.predefined_model_var.get()
        if not selection:
            if self.notification_center:
                self.notification_center.show_warning("Veuillez sélectionner un modèle")
            else:
                messagebox.showwarning("Sélection", "Veuillez sélectionner un modèle.")
            return
        
        model_name = selection.split(" - ")[0]
        
        for model in self.aircraft_models:
            if model['modele'] == model_name:
                # Appliquer les valeurs
                self.model_field.set_value(model['modele'])
                self.capacity_field.set_value(str(model['capacite']))
                self.speed_field.set_value(str(model['vitesse_croisiere']))
                self.autonomy_field.set_value(str(model['autonomie']))
                
                # Générer un ID automatique si vide
                if not self.id_field.get_value():
                    prefix = model['modele'].replace(' ', '').replace('-', '')[:3].upper()
                    unique_id = f"{prefix}-{str(uuid.uuid4())[:4].upper()}"
                    self.id_field.set_value(unique_id)
                
                success_msg = f"Modèle {model['modele']} appliqué avec succès!"
                if self.notification_center:
                    self.notification_center.show_success(success_msg)
                else:
                    messagebox.showinfo("Succès", success_msg)
                break
    
    def update_coordinates(self, event=None):
        """Met à jour l'affichage des coordonnées"""
        selection = self.airport_var.get()
        
        if ' - ' in selection:
            code_iata = selection.split(' - ')[0]
            
            for airport in self.airports:
                if airport['code_iata'] == code_iata:
                    coords = airport['coordonnees']
                    coord_text = f"Lat: {coords['latitude']:.4f}, Lon: {coords['longitude']:.4f}"
                    self.coords_var.set(coord_text)
                    self.coords_label.configure(foreground="blue")
                    return
        
        self.coords_var.set("Aéroport non trouvé")
        self.coords_label.configure(foreground="red")
    
    def validate_airport(self, *args):
        """Valide la sélection d'aéroport"""
        selection = self.airport_var.get()
        
        if not selection:
            self.airport_valid.set(False)
            self.airport_status_var.set("L'aéroport est obligatoire")
            self.airport_status_label.configure(foreground="red")
            return
        
        # Vérifier si l'aéroport existe
        if ' - ' in selection:
            code_iata = selection.split(' - ')[0]
            airport_found = any(a['code_iata'] == code_iata for a in self.airports)
            
            if airport_found:
                self.airport_valid.set(True)
                self.airport_status_var.set("✓ Aéroport valide")
                self.airport_status_label.configure(foreground="green")
            else:
                self.airport_valid.set(False)
                self.airport_status_var.set("✗ Aéroport invalide")
                self.airport_status_label.configure(foreground="red")
        else:
            self.airport_valid.set(False)
            self.airport_status_var.set("✗ Format invalide")
            self.airport_status_label.configure(foreground="red")
    
    def validate_form(self, *args):
        """Validation globale du formulaire"""
        # Vérifier tous les champs obligatoires
        required_fields = [
            self.id_field,
            self.model_field,
            self.company_field,
            self.capacity_field,
            self.speed_field,
            self.autonomy_field
        ]
        
        all_valid = all(field.is_field_valid() for field in required_fields)
        all_valid = all_valid and self.airport_valid.get()
        
        self.form_valid.set(all_valid)
        self.update_save_button_state()
    
    def update_save_button_state(self):
        """Met à jour l'état du bouton de sauvegarde"""
        if hasattr(self, 'save_btn'):
            if self.form_valid.get():
                self.save_btn.config(state="normal", style='Action.TButton')
            else:
                self.save_btn.config(state="disabled")
    
    def populate_fields(self):
        """Pré-remplit les champs pour la modification"""
        if not self.aircraft_data:
            return
        
        # Remplir les champs basiques
        self.id_field.set_value(self.aircraft_data.get('num_id', ''))
        self.model_field.set_value(self.aircraft_data.get('modele', ''))
        self.company_field.set_value(self.aircraft_data.get('compagnie_aerienne', ''))
        self.capacity_field.set_value(str(self.aircraft_data.get('capacite', '')))
        self.speed_field.set_value(str(self.aircraft_data.get('vitesse_croisiere', '')))
        self.autonomy_field.set_value(str(self.aircraft_data.get('autonomie', '')))
        
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
    
    def get_coordinates_for_airport(self, airport_selection):
        """Récupère les coordonnées pour un aéroport sélectionné"""
        if not airport_selection or ' - ' not in airport_selection:
            return None
        
        code_iata = airport_selection.split(' - ')[0]
        
        for airport in self.airports:
            if airport['code_iata'] == code_iata:
                coords = airport['coordonnees']
                return {
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude']
                }
        
        return None
    
    def save_aircraft(self):
        """Sauvegarde l'avion avec gestion d'erreurs robuste"""
        # Validation finale
        if not self.form_valid.get():
            error_msg = "Veuillez corriger les erreurs dans le formulaire avant de sauvegarder."
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            else:
                messagebox.showerror("Erreurs de Validation", error_msg)
            return
        
        try:
            # Récupérer les coordonnées de l'aéroport
            coordinates = self.get_coordinates_for_airport(self.airport_var.get())
            if not coordinates:
                error_msg = "Impossible de récupérer les coordonnées de l'aéroport sélectionné."
                if self.notification_center:
                    self.notification_center.show_error(error_msg)
                else:
                    messagebox.showerror("Erreur", error_msg)
                return
            
            # Mapping des états
            state_mapping = {
                'Opérationnel': 'operationnel',
                'Au sol': 'au_sol',
                'En maintenance': 'en_maintenance',
                'Hors service': 'hors_service'
            }
            
            # Construire les données de l'avion
            aircraft_data = {
                'num_id': self.id_field.get_value(),
                'modele': self.model_field.get_value(),
                'compagnie_aerienne': self.company_field.get_value(),
                'capacite': int(self.capacity_field.get_value()),
                'vitesse_croisiere': float(self.speed_field.get_value()),
                'autonomie': float(self.autonomy_field.get_value()),
                'localisation': coordinates,
                'etat': state_mapping.get(self.state_var.get(), 'operationnel'),
                'vol_actuel': None,
                'derniere_maintenance': self.aircraft_data.get('derniere_maintenance') if self.is_editing else None
            }
            
            # CORRECTION BUG: Sauvegarde sécurisée
            if self.is_editing:
                success = self.safe_update_aircraft(aircraft_data)
                action = "modifié"
            else:
                success = self.safe_add_aircraft(aircraft_data)
                action = "créé"
            
            if success:
                self.result = aircraft_data
                success_msg = f"Avion {action} avec succès!"
                
                if self.notification_center:
                    self.notification_center.show_success(success_msg)
                else:
                    messagebox.showinfo("Succès", success_msg)
                
                self.dialog.destroy()
            else:
                error_msg = f"Impossible de {action.replace('é', 'er')} l'avion. Vérifiez les données."
                if self.notification_center:
                    self.notification_center.show_error(error_msg)
                else:
                    messagebox.showerror("Erreur", error_msg)
        
        except ValueError as e:
            error_msg = f"Erreur de validation des données : {e}"
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            else:
                messagebox.showerror("Erreur", error_msg)
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde : {e}"
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            else:
                messagebox.showerror("Erreur", error_msg)
            print(f"❌ Erreur sauvegarde avion: {e}")
    
    def safe_add_aircraft(self, aircraft_data):
        """CORRECTION BUG: Ajout sécurisé d'avion"""
        try:
            # Vérifier une dernière fois l'unicité de l'ID
            existing_aircraft = self.data_manager.get_aircraft()
            if any(a.get('num_id') == aircraft_data['num_id'] for a in existing_aircraft):
                raise ValueError(f"Un avion avec l'ID '{aircraft_data['num_id']}' existe déjà")
            
            # Charger les données existantes
            data = self.data_manager.load_data('aircraft')
            if 'aircraft' not in data:
                data['aircraft'] = []
            
            # Ajouter les métadonnées
            aircraft_data['created_at'] = datetime.now().isoformat()
            aircraft_data['updated_at'] = datetime.now().isoformat()
            
            # Ajouter l'avion
            data['aircraft'].append(aircraft_data)
            
            # Sauvegarder
            success = self.data_manager.save_data('aircraft', data)
            
            if success:
                print(f"✅ Avion {aircraft_data['num_id']} ajouté avec succès")
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur ajout avion sécurisé: {e}")
            return False
    
    def safe_update_aircraft(self, aircraft_data):
        """CORRECTION BUG: Mise à jour sécurisée d'avion"""
        try:
            # Charger les données existantes
            data = self.data_manager.load_data('aircraft')
            if 'aircraft' not in data:
                print("❌ Aucune donnée d'avion trouvée")
                return False
            
            # Trouver l'avion à modifier
            aircraft_index = -1
            original_id = self.aircraft_data.get('num_id')
            
            for i, aircraft in enumerate(data['aircraft']):
                if aircraft.get('num_id') == original_id:
                    aircraft_index = i
                    break
            
            if aircraft_index == -1:
                print(f"❌ Avion {original_id} non trouvé pour modification")
                return False
            
            # Vérifier l'unicité du nouvel ID (si changé)
            new_id = aircraft_data['num_id']
            if new_id != original_id:
                if any(a.get('num_id') == new_id for a in data['aircraft']):
                    raise ValueError(f"Un avion avec l'ID '{new_id}' existe déjà")
            
            # Conserver certaines données existantes
            original_aircraft = data['aircraft'][aircraft_index]
            aircraft_data['created_at'] = original_aircraft.get('created_at', datetime.now().isoformat())
            aircraft_data['updated_at'] = datetime.now().isoformat()
            
            # Mettre à jour
            data['aircraft'][aircraft_index] = aircraft_data
            
            # Sauvegarder
            success = self.data_manager.save_data('aircraft', data)
            
            if success:
                print(f"✅ Avion {aircraft_data['num_id']} modifié avec succès")
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur modification avion sécurisée: {e}")
            return False
    
    def cancel(self):
        """Annule le dialogue avec confirmation si des changements ont été faits"""
        # Vérifier s'il y a des changements non sauvegardés
        if self.has_unsaved_changes():
            if messagebox.askyesno("Modifications non sauvegardées", 
                                  "Vous avez des modifications non sauvegardées.\n\n"
                                  "Voulez-vous vraiment quitter sans sauvegarder ?"):
                self.result = None
                self.dialog.destroy()
        else:
            self.result = None
            self.dialog.destroy()
    
    def has_unsaved_changes(self):
        """Vérifie s'il y a des changements non sauvegardés"""
        if not self.is_editing:
            # Pour un nouvel avion, vérifier si des champs sont remplis
            return any([
                self.id_field.get_value(),
                self.model_field.get_value(),
                self.company_field.get_value(),
                self.capacity_field.get_value(),
                self.speed_field.get_value(),
                self.autonomy_field.get_value()
            ])
        else:
            # Pour une modification, comparer avec les valeurs originales
            if not self.aircraft_data:
                return False
            
            return (
                self.id_field.get_value() != self.aircraft_data.get('num_id', '') or
                self.model_field.get_value() != self.aircraft_data.get('modele', '') or
                self.company_field.get_value() != self.aircraft_data.get('compagnie_aerienne', '') or
                self.capacity_field.get_value() != str(self.aircraft_data.get('capacite', '')) or
                self.speed_field.get_value() != str(self.aircraft_data.get('vitesse_croisiere', '')) or
                self.autonomy_field.get_value() != str(self.aircraft_data.get('autonomie', ''))
            )


class SafeAircraftManager:
    """Gestionnaire sécurisé pour les opérations sur les avions - CORRECTION BUGS"""
    
    def __init__(self, data_manager, notification_center=None):
        self.data_manager = data_manager
        self.notification_center = notification_center
    
    def can_delete_aircraft(self, aircraft_id):
        """Vérifie si un avion peut être supprimé (pas de vols actifs, etc.)"""
        try:
            # Vérifier les vols en cours ou futurs
            flights = self.data_manager.get_flights()
            active_flights = []
            
            for flight in flights:
                if (flight.get('avion_utilise') == aircraft_id and 
                    flight.get('statut') in ['programme', 'en_attente', 'en_vol']):
                    active_flights.append(flight.get('numero_vol', 'Vol inconnu'))
            
            if active_flights:
                return False, f"Avion assigné aux vols actifs: {', '.join(active_flights)}"
            
            # Vérifier les réservations futures (optionnel)
            # ... autres vérifications ...
            
            return True, "Suppression autorisée"
            
        except Exception as e:
            return False, f"Erreur vérification: {e}"
    
    def safe_delete_aircraft(self, aircraft_id):
        """CORRECTION BUG: Suppression sécurisée d'avion"""
        try:
            # Vérifier si la suppression est possible
            can_delete, reason = self.can_delete_aircraft(aircraft_id)
            if not can_delete:
                return False, reason
            
            # Charger les données
            data = self.data_manager.load_data('aircraft')
            if 'aircraft' not in data:
                return False, "Aucune donnée d'avion trouvée"
            
            # Trouver et supprimer l'avion
            original_count = len(data['aircraft'])
            data['aircraft'] = [a for a in data['aircraft'] if a.get('num_id') != aircraft_id]
            
            if len(data['aircraft']) == original_count:
                return False, f"Avion {aircraft_id} non trouvé"
            
            # Sauvegarder
            success = self.data_manager.save_data('aircraft', data)
            
            if success:
                message = f"Avion {aircraft_id} supprimé avec succès"
                if self.notification_center:
                    self.notification_center.show_success(message)
                print(f"✅ {message}")
                return True, message
            else:
                return False, "Erreur lors de la sauvegarde"
                
        except Exception as e:
            error_msg = f"Erreur suppression avion: {e}"
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def safe_change_aircraft_state(self, aircraft_id, new_state, reason=""):
        """Change l'état d'un avion de manière sécurisée"""
        try:
            # Charger les données
            data = self.data_manager.load_data('aircraft')
            if 'aircraft' not in data:
                return False, "Aucune donnée d'avion trouvée"
            
            # Trouver l'avion
            aircraft_index = -1
            for i, aircraft in enumerate(data['aircraft']):
                if aircraft.get('num_id') == aircraft_id:
                    aircraft_index = i
                    break
            
            if aircraft_index == -1:
                return False, f"Avion {aircraft_id} non trouvé"
            
            aircraft = data['aircraft'][aircraft_index]
            old_state = aircraft.get('etat', 'au_sol')
            
            # Vérifications selon le changement d'état
            if new_state == 'en_maintenance':
                # Vérifier qu'il n'est pas en vol
                if old_state == 'en_vol':
                    return False, "Impossible de mettre en maintenance un avion en vol"
                
                # Marquer la date de maintenance
                aircraft['derniere_maintenance'] = datetime.now().isoformat()
            
            elif new_state == 'operationnel':
                # Si on sort de maintenance, mettre à jour la date
                if old_state == 'en_maintenance':
                    aircraft['derniere_maintenance'] = datetime.now().isoformat()
            
            # Appliquer le changement
            aircraft['etat'] = new_state
            aircraft['updated_at'] = datetime.now().isoformat()
            
            if reason:
                if 'maintenance_log' not in aircraft:
                    aircraft['maintenance_log'] = []
                aircraft['maintenance_log'].append({
                    'date': datetime.now().isoformat(),
                    'action': f"État changé: {old_state} → {new_state}",
                    'reason': reason
                })
            
            # Sauvegarder
            success = self.data_manager.save_data('aircraft', data)
            
            if success:
                message = f"État de l'avion {aircraft_id} changé: {old_state} → {new_state}"
                if self.notification_center:
                    self.notification_center.show_success(message)
                print(f"✅ {message}")
                return True, message
            else:
                return False, "Erreur lors de la sauvegarde"
                
        except Exception as e:
            error_msg = f"Erreur changement état avion: {e}"
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            print(f"❌ {error_msg}")
            return False, error_msg


# Alias pour compatibilité avec l'ancien code
AircraftDialog = ModernAircraftDialog