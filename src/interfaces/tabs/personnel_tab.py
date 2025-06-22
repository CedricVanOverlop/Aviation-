import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os
from datetime import datetime

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.personnes import Personnel
from Core.enums import TypePersonnel, TypeSexe

class PersonnelDialog:
    """Dialogue pour créer ou modifier un membre du personnel"""
    
    def __init__(self, parent, data_manager, personnel_data=None):
        self.parent = parent
        self.data_manager = data_manager
        self.personnel_data = personnel_data
        self.is_editing = personnel_data is not None
        self.result = None
        
        # Créer la fenêtre dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modification du Personnel" if self.is_editing else "Création d'un Nouveau Membre du Personnel")
        self.dialog.geometry("650x800")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables pour les champs
        self.setup_variables()
        
        # Créer l'interface
        self.setup_ui()
        
        # Pré-remplir si modification
        if self.is_editing:
            self.populate_fields()
        
        # Focus sur le premier champ
        self.nom_entry.focus()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (800 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables pour les champs"""
        self.nom_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.sexe_var = tk.StringVar()
        self.adresse_var = tk.StringVar()
        self.telephone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.type_personnel_var = tk.StringVar()
        self.horaire_var = tk.StringVar()
        self.specialisation_var = tk.StringVar()
        self.numero_licence_var = tk.StringVar()
        self.heures_vol_var = tk.StringVar()
        self.departement_var = tk.StringVar()
        self.tour_controle_var = tk.StringVar()
        self.disponible_var = tk.BooleanVar(value=True)
        
        # Langues parlées (pour hôtesses/stewards)
        self.langues_vars = {}
        langues_communes = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Néerlandais", "Arabe", "Chinois"]
        for langue in langues_communes:
            self.langues_vars[langue] = tk.BooleanVar()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec défilement
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Modification du Personnel" if self.is_editing else "Création d'un Nouveau Membre du Personnel",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Section informations personnelles
        self.create_personal_info_section(main_frame)
        
        # Section professionnelle
        self.create_professional_section(main_frame)
        
        # Section spécialisations (conditionnelle)
        self.create_specialization_section(main_frame)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_personal_info_section(self, parent):
        """Crée la section des informations personnelles"""
        personal_frame = ttk.LabelFrame(parent, text="👤 Informations Personnelles", padding=15)
        personal_frame.pack(fill="x", pady=(0, 10))
        
        personal_frame.grid_columnconfigure(1, weight=1)
        
        # Nom
        ttk.Label(personal_frame, text="Nom*:").grid(row=0, column=0, sticky="w", pady=5)
        self.nom_entry = ttk.Entry(personal_frame, textvariable=self.nom_var, width=30)
        self.nom_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Prénom
        ttk.Label(personal_frame, text="Prénom*:").grid(row=1, column=0, sticky="w", pady=5)
        self.prenom_entry = ttk.Entry(personal_frame, textvariable=self.prenom_var, width=30)
        self.prenom_entry.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Sexe
        ttk.Label(personal_frame, text="Sexe*:").grid(row=2, column=0, sticky="w", pady=5)
        sexe_combo = ttk.Combobox(personal_frame, textvariable=self.sexe_var,
                                 values=["Masculin", "Féminin", "Autre"], state="readonly", width=15)
        sexe_combo.grid(row=2, column=1, sticky="w", padx=(10, 5), pady=5)
        self.sexe_var.set("Masculin")
        
        # Adresse
        ttk.Label(personal_frame, text="Adresse*:").grid(row=3, column=0, sticky="w", pady=5)
        self.adresse_entry = ttk.Entry(personal_frame, textvariable=self.adresse_var, width=50)
        self.adresse_entry.grid(row=3, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Téléphone
        ttk.Label(personal_frame, text="Téléphone:").grid(row=4, column=0, sticky="w", pady=5)
        self.telephone_entry = ttk.Entry(personal_frame, textvariable=self.telephone_var, width=20)
        self.telephone_entry.grid(row=4, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # Email
        ttk.Label(personal_frame, text="Email:").grid(row=5, column=0, sticky="w", pady=5)
        self.email_entry = ttk.Entry(personal_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=5, column=1, sticky="ew", padx=(10, 5), pady=5)
    
    def create_professional_section(self, parent):
        """Crée la section des informations professionnelles"""
        prof_frame = ttk.LabelFrame(parent, text="💼 Informations Professionnelles", padding=15)
        prof_frame.pack(fill="x", pady=(0, 10))
        
        prof_frame.grid_columnconfigure(1, weight=1)
        
        # Type de personnel
        ttk.Label(prof_frame, text="Poste*:").grid(row=0, column=0, sticky="w", pady=5)
        type_choices = ["Pilote", "Copilote", "Hôtesse de l'air", "Steward", "Mécanicien", "Contrôleur aérien", "Gestionnaire"]
        self.type_combo = ttk.Combobox(prof_frame, textvariable=self.type_personnel_var,
                                      values=type_choices, state="readonly", width=25)
        self.type_combo.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        self.type_combo.bind('<<ComboboxSelected>>', self.on_type_personnel_change)
        self.type_personnel_var.set("Pilote")
        
        # Horaire
        ttk.Label(prof_frame, text="Horaire:").grid(row=1, column=0, sticky="w", pady=5)
        horaire_combo = ttk.Combobox(prof_frame, textvariable=self.horaire_var,
                                    values=["Temps plein", "Temps partiel", "Variable", "Nuit"], 
                                    state="readonly", width=20)
        horaire_combo.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=5)
        self.horaire_var.set("Temps plein")
        
        # Spécialisation
        ttk.Label(prof_frame, text="Spécialisation:").grid(row=2, column=0, sticky="w", pady=5)
        self.specialisation_entry = ttk.Entry(prof_frame, textvariable=self.specialisation_var, width=30)
        self.specialisation_entry.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Disponibilité
        disponible_cb = ttk.Checkbutton(prof_frame, text="Disponible pour affectation",
                                       variable=self.disponible_var)
        disponible_cb.grid(row=3, column=1, sticky="w", padx=(10, 5), pady=10)
    
    def create_specialization_section(self, parent):
        """Crée la section des spécialisations selon le type de personnel"""
        self.spec_frame = ttk.LabelFrame(parent, text="🎯 Spécialisations", padding=15)
        self.spec_frame.pack(fill="x", pady=(0, 10))
        
        # Cette section sera mise à jour dynamiquement
        self.update_specialization_fields()
    
    def on_type_personnel_change(self, event=None):
        """Gestionnaire pour le changement de type de personnel"""
        self.update_specialization_fields()
    
    def update_specialization_fields(self):
        """Met à jour les champs de spécialisation selon le type de personnel"""
        # Nettoyer la frame
        for widget in self.spec_frame.winfo_children():
            widget.destroy()
        
        type_personnel = self.type_personnel_var.get()
        
        if "Pilote" in type_personnel or "Copilote" in type_personnel:
            self.create_pilot_fields()
        elif "Hôtesse" in type_personnel or "Steward" in type_personnel:
            self.create_cabin_crew_fields()
        elif "Contrôleur" in type_personnel:
            self.create_controller_fields()
        else:
            self.create_generic_fields()
    
    def create_pilot_fields(self):
        """Champs spécifiques aux pilotes"""
        self.spec_frame.grid_columnconfigure(1, weight=1)
        
        # Numéro de licence
        ttk.Label(self.spec_frame, text="Numéro de licence*:").grid(row=0, column=0, sticky="w", pady=5)
        self.licence_entry = ttk.Entry(self.spec_frame, textvariable=self.numero_licence_var, width=20)
        self.licence_entry.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # Heures de vol
        ttk.Label(self.spec_frame, text="Heures de vol:").grid(row=1, column=0, sticky="w", pady=5)
        self.heures_entry = ttk.Entry(self.spec_frame, textvariable=self.heures_vol_var, width=10)
        self.heures_entry.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=5)
    
    def create_cabin_crew_fields(self):
        """Champs spécifiques au personnel navigant"""
        self.spec_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self.spec_frame, text="Langues parlées:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Langues en grille 2x4
        row = 1
        col = 0
        for i, (langue, var) in enumerate(self.langues_vars.items()):
            cb = ttk.Checkbutton(self.spec_frame, text=langue, variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=10, pady=2)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
    
    def create_controller_fields(self):
        """Champs spécifiques aux contrôleurs aériens"""
        self.spec_frame.grid_columnconfigure(1, weight=1)
        
        # Tour de contrôle
        ttk.Label(self.spec_frame, text="Tour de contrôle:").grid(row=0, column=0, sticky="w", pady=5)
        self.tour_entry = ttk.Entry(self.spec_frame, textvariable=self.tour_controle_var, width=30)
        self.tour_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
    
    def create_generic_fields(self):
        """Champs pour les autres types de personnel"""
        self.spec_frame.grid_columnconfigure(1, weight=1)
        
        # Département
        ttk.Label(self.spec_frame, text="Département:").grid(row=0, column=0, sticky="w", pady=5)
        self.dept_entry = ttk.Entry(self.spec_frame, textvariable=self.departement_var, width=30)
        self.dept_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
    
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
        btn_cancel = ttk.Button(buttons_container, text="Annuler", command=self.cancel)
        btn_cancel.pack(side="right", padx=(10, 0))
        
        # Bouton Créer/Modifier
        btn_save = ttk.Button(buttons_container, 
                             text="Modifier" if self.is_editing else "Créer", 
                             command=self.save_personnel)
        btn_save.pack(side="right")
    
    def populate_fields(self):
        """Pré-remplit les champs pour la modification"""
        if not self.personnel_data:
            return
        
        self.nom_var.set(self.personnel_data.get('nom', ''))
        self.prenom_var.set(self.personnel_data.get('prenom', ''))
        
        # Sexe
        sexe_mapping = {
            'masculin': 'Masculin',
            'feminin': 'Féminin',
            'autre': 'Autre'
        }
        current_sexe = self.personnel_data.get('sexe', 'masculin')
        self.sexe_var.set(sexe_mapping.get(current_sexe, 'Masculin'))
        
        self.adresse_var.set(self.personnel_data.get('adresse', ''))
        self.telephone_var.set(self.personnel_data.get('numero_telephone', ''))
        self.email_var.set(self.personnel_data.get('email', ''))
        
        # Type de personnel
        type_mapping = {
            'pilote': 'Pilote',
            'copilote': 'Copilote',
            'hotesse': 'Hôtesse de l\'air',
            'steward': 'Steward',
            'mecanicien': 'Mécanicien',
            'controleur': 'Contrôleur aérien',
            'gestionnaire': 'Gestionnaire'
        }
        current_type = self.personnel_data.get('type_personnel', 'pilote')
        self.type_personnel_var.set(type_mapping.get(current_type, 'Pilote'))
        
        self.horaire_var.set(self.personnel_data.get('horaire', 'Temps plein'))
        self.specialisation_var.set(self.personnel_data.get('specialisation', ''))
        self.disponible_var.set(self.personnel_data.get('disponible', True))
        
        # Champs spécialisés
        self.numero_licence_var.set(self.personnel_data.get('numero_licence', ''))
        self.heures_vol_var.set(str(self.personnel_data.get('heures_vol', 0)))
        self.departement_var.set(self.personnel_data.get('departement', ''))
        self.tour_controle_var.set(self.personnel_data.get('tour_controle', ''))
        
        # Langues parlées
        langues_parlees = self.personnel_data.get('langues_parlees', [])
        for langue in langues_parlees:
            if langue in self.langues_vars:
                self.langues_vars[langue].set(True)
        
        # Mettre à jour les champs spécialisés
        self.update_specialization_fields()
    
    def validate_fields(self):
        """Valide tous les champs obligatoires"""
        errors = []
        
        if not self.nom_var.get().strip():
            errors.append("Le nom est obligatoire")
        
        if not self.prenom_var.get().strip():
            errors.append("Le prénom est obligatoire")
        
        if not self.adresse_var.get().strip():
            errors.append("L'adresse est obligatoire")
        
        # Validation email si fourni
        email = self.email_var.get().strip()
        if email and '@' not in email:
            errors.append("Format d'email invalide")
        
        # Validations spécifiques selon le type
        type_personnel = self.type_personnel_var.get()
        
        if "Pilote" in type_personnel:
            if not self.numero_licence_var.get().strip():
                errors.append("Le numéro de licence est obligatoire pour les pilotes")
            
            heures_vol = self.heures_vol_var.get().strip()
            if heures_vol:
                try:
                    float(heures_vol)
                except ValueError:
                    errors.append("Les heures de vol doivent être un nombre")
        
        return errors
    
    def save_personnel(self):
        """Sauvegarde le personnel"""
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Erreurs de Validation", 
                               "Veuillez corriger les erreurs suivantes:\n\n" + 
                               "\n".join(f"• {error}" for error in errors))
            return
        
        try:
            sexe_mapping = {
                'Masculin': 'masculin',
                'Féminin': 'feminin',
                'Autre': 'autre'
            }
            
            type_mapping = {
                'Pilote': 'pilote',
                'Copilote': 'copilote',
                'Hôtesse de l\'air': 'hotesse',
                'Steward': 'steward',
                'Mécanicien': 'mecanicien',
                'Contrôleur aérien': 'controleur',
                'Gestionnaire': 'gestionnaire'
            }
            
            # Langues parlées
            langues_selectionnees = [langue for langue, var in self.langues_vars.items() if var.get()]
            
            # Construire les données du personnel
            personnel_data = {
                'id_employe': str(uuid.uuid4()) if not self.is_editing else self.personnel_data.get('id_employe'),
                'nom': self.nom_var.get().strip(),
                'prenom': self.prenom_var.get().strip(),
                'sexe': sexe_mapping.get(self.sexe_var.get(), 'masculin'),
                'adresse': self.adresse_var.get().strip(),
                'numero_telephone': self.telephone_var.get().strip(),
                'email': self.email_var.get().strip(),
                'type_personnel': type_mapping.get(self.type_personnel_var.get(), 'pilote'),
                'horaire': self.horaire_var.get(),
                'specialisation': self.specialisation_var.get().strip(),
                'disponible': self.disponible_var.get(),
                'numero_licence': self.numero_licence_var.get().strip(),
                'heures_vol': float(self.heures_vol_var.get()) if self.heures_vol_var.get().strip() else 0.0,
                'departement': self.departement_var.get().strip(),
                'tour_controle': self.tour_controle_var.get().strip(),
                'langues_parlees': langues_selectionnees,
                'created_at': self.personnel_data.get('created_at', datetime.now().isoformat()) if self.is_editing else datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Sauvegarder
            if self.is_editing:
                success = self.safe_update_personnel(personnel_data)
                action = "modifié"
            else:
                success = self.safe_add_personnel(personnel_data)
                action = "créé"
            
            if success:
                self.result = personnel_data
                messagebox.showinfo("Succès", f"Personnel {action} avec succès!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", f"Impossible de {action.replace('é', 'er')} le personnel.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            print(f"❌ Erreur sauvegarde personnel: {e}")
    
    def safe_add_personnel(self, personnel_data):
        """Ajout sécurisé de personnel"""
        try:
            data = self.data_manager.load_data('personnel')
            if 'personnel' not in data:
                data['personnel'] = []
            
            data['personnel'].append(personnel_data)
            return self.data_manager.save_data('personnel', data)
        except Exception as e:
            print(f"❌ Erreur ajout personnel: {e}")
            return False
    
    def safe_update_personnel(self, personnel_data):
        """Mise à jour sécurisée de personnel"""
        try:
            data = self.data_manager.load_data('personnel')
            if 'personnel' not in data:
                return False
            
            # Trouver le personnel à modifier
            personnel_index = -1
            original_id = self.personnel_data.get('id_employe')
            
            for i, person in enumerate(data['personnel']):
                if person.get('id_employe') == original_id:
                    personnel_index = i
                    break
            
            if personnel_index == -1:
                print(f"❌ Personnel {original_id} non trouvé")
                return False
            
            # Mettre à jour
            data['personnel'][personnel_index] = personnel_data
            return self.data_manager.save_data('personnel', data)
        except Exception as e:
            print(f"❌ Erreur modification personnel: {e}")
            return False
    
    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy()


def create_personnel_tab_content(parent_frame, data_manager):
    """Crée le contenu de l'onglet personnel"""
    
    # Variables pour la recherche et le filtrage
    personnel_search_var = tk.StringVar()
    personnel_filter_var = tk.StringVar(value="Tous")
    
    # Barre d'outils
    toolbar = ttk.Frame(parent_frame)
    toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    
    # Variables pour stocker les références aux widgets
    personnel_tree = None
    
    def new_personnel_callback():
        new_personnel_dialog(parent_frame, data_manager, personnel_tree)
    
    def edit_personnel_callback():
        edit_personnel(parent_frame, data_manager, personnel_tree)
    
    def view_personnel_callback():
        view_personnel_details(personnel_tree)
    
    def delete_personnel_callback():
        delete_personnel(data_manager, personnel_tree)
    
    def filter_personnel_callback(event=None):
        filter_personnel(personnel_tree, data_manager, personnel_search_var, personnel_filter_var)
    
    ttk.Button(toolbar, text="➕ Nouveau Personnel", 
              command=new_personnel_callback, 
              style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
    ttk.Button(toolbar, text="✏️ Modifier", 
              command=edit_personnel_callback).grid(row=0, column=1, padx=(0, 5))
    ttk.Button(toolbar, text="👁️ Voir Détails", 
              command=view_personnel_callback).grid(row=0, column=2, padx=(0, 5))
    ttk.Button(toolbar, text="🗑️ Retirer", 
              command=delete_personnel_callback, 
              style='Danger.TButton').grid(row=0, column=3, padx=(0, 20))
    
    # Recherche
    ttk.Label(toolbar, text="🔍 Recherche:").grid(row=0, column=4, padx=(0, 5))
    search_entry = ttk.Entry(toolbar, textvariable=personnel_search_var, width=20)
    search_entry.grid(row=0, column=5, padx=(0, 5))
    search_entry.bind('<KeyRelease>', filter_personnel_callback)
    
    # Filtre par type
    ttk.Label(toolbar, text="Type:").grid(row=0, column=6, padx=(10, 5))
    filter_combo = ttk.Combobox(toolbar, textvariable=personnel_filter_var, width=15, state="readonly")
    filter_combo['values'] = ['Tous', 'Pilote', 'Copilote', 'Hôtesse de l\'air', 'Steward', 'Mécanicien', 'Contrôleur aérien', 'Gestionnaire']
    filter_combo.grid(row=0, column=7, padx=(0, 5))
    filter_combo.bind('<<ComboboxSelected>>', filter_personnel_callback)
    
    # Tableau du personnel
    columns = ('ID', 'Nom', 'Prénom', 'Type', 'Spécialisation', 'Horaire', 'Disponible', 'Contact')
    personnel_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
    personnel_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    # Configuration colonnes
    column_widths = {
        'ID': 100, 'Nom': 120, 'Prénom': 120, 'Type': 150, 
        'Spécialisation': 120, 'Horaire': 100, 'Disponible': 80, 'Contact': 200
    }
    for col in columns:
        personnel_tree.heading(col, text=col)
        personnel_tree.column(col, width=column_widths.get(col, 100))
    
    # Scrollbars
    personnel_v_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=personnel_tree.yview)
    personnel_v_scrollbar.grid(row=1, column=1, sticky="ns")
    personnel_tree.configure(yscrollcommand=personnel_v_scrollbar.set)
    
    personnel_h_scrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=personnel_tree.xview)
    personnel_h_scrollbar.grid(row=2, column=0, sticky="ew")
    personnel_tree.configure(xscrollcommand=personnel_h_scrollbar.set)
    
    # Configuration responsive
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Charger les données initiales
    refresh_personnel_data(personnel_tree, data_manager)
    
    # Double-clic pour modifier
    personnel_tree.bind('<Double-1>', lambda e: edit_personnel(parent_frame, data_manager, personnel_tree))
    
    return personnel_tree


def new_personnel_dialog(parent, data_manager, personnel_tree):
    """Ouvre le dialogue de création de personnel"""
    dialog = PersonnelDialog(parent, data_manager)
    if dialog.result:
        refresh_personnel_data(personnel_tree, data_manager)


def edit_personnel(parent, data_manager, personnel_tree):
    """Modifie le personnel sélectionné"""
    selection = personnel_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un membre du personnel à modifier.")
        return
    
    try:
        item = personnel_tree.item(selection[0])
        personnel_id = item['values'][0]
        
        # Recherche robuste du personnel
        all_personnel = data_manager.get_personnel()
        personnel_data = None
        
        for person in all_personnel:
            if person.get('id_employe', '').startswith(personnel_id.replace('...', '')):
                personnel_data = person
                break
        
        if not personnel_data:
            messagebox.showerror("Erreur", "Personnel non trouvé.")
            return
        
        dialog = PersonnelDialog(parent, data_manager, personnel_data)
        if dialog.result:
            refresh_personnel_data(personnel_tree, data_manager)
            messagebox.showinfo("Succès", "Personnel modifié avec succès!")
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")


def view_personnel_details(personnel_tree):
    """Affiche les détails du personnel sélectionné"""
    selection = personnel_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un membre du personnel.")
        return
    
    item = personnel_tree.item(selection[0])
    values = item['values']
    
    details = f"""Détails du Personnel
    
ID: {values[0]}
Nom: {values[1]}
Prénom: {values[2]}
Type: {values[3]}
Spécialisation: {values[4]}
Horaire: {values[5]}
Disponible: {values[6]}
Contact: {values[7]}"""
    
    messagebox.showinfo("Détails du Personnel", details)


def delete_personnel(data_manager, personnel_tree):
    """Supprime le personnel sélectionné"""
    selection = personnel_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un membre du personnel à supprimer.")
        return
    
    try:
        item = personnel_tree.item(selection[0])
        personnel_id = item['values'][0]
        personnel_name = f"{item['values'][2]} {item['values'][1]}"
        
        if messagebox.askyesno("Confirmation", 
                              f"Voulez-vous vraiment supprimer {personnel_name} ?"):
            
            # Supprimer de la liste
            data = data_manager.load_data('personnel')
            if 'personnel' not in data:
                return
            
            original_count = len(data['personnel'])
            data['personnel'] = [p for p in data['personnel'] 
                               if not p.get('id_employe', '').startswith(personnel_id.replace('...', ''))]
            
            if len(data['personnel']) == original_count:
                messagebox.showerror("Erreur", "Personnel non trouvé.")
                return
            
            if data_manager.save_data('personnel', data):
                refresh_personnel_data(personnel_tree, data_manager)
                messagebox.showinfo("Succès", "Personnel supprimé avec succès.")
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")


def filter_personnel(personnel_tree, data_manager, search_var, filter_var):
    """Filtre la liste du personnel"""
    search_text = search_var.get().lower()
    filter_type = filter_var.get()
    
    # Vider le tableau
    for item in personnel_tree.get_children():
        personnel_tree.delete(item)
    
    # Recharger avec filtres
    all_personnel = data_manager.get_personnel()
    
    for person in all_personnel:
        # Mapping du type pour l'affichage
        type_mapping = {
            'pilote': 'Pilote',
            'copilote': 'Copilote',
            'hotesse': 'Hôtesse de l\'air',
            'steward': 'Steward',
            'mecanicien': 'Mécanicien',
            'controleur': 'Contrôleur aérien',
            'gestionnaire': 'Gestionnaire'
        }
        
        person_type = type_mapping.get(person.get('type_personnel', ''), 'Inconnu')
        
        # Filtrage par type
        if filter_type != "Tous" and person_type != filter_type:
            continue
        
        # Filtrage par recherche
        searchable_text = f"{person.get('nom', '')} {person.get('prenom', '')} {person_type} {person.get('specialisation', '')}".lower()
        if search_text and search_text not in searchable_text:
            continue
        
        # Ajouter à l'affichage
        contact = ""
        if person.get('email'):
            contact = person.get('email')
        elif person.get('numero_telephone'):
            contact = person.get('numero_telephone')
        
        values = (
            person.get('id_employe', '')[:8] + '...' if len(person.get('id_employe', '')) > 8 else person.get('id_employe', ''),
            person.get('nom', ''),
            person.get('prenom', ''),
            person_type,
            person.get('specialisation', ''),
            person.get('horaire', ''),
            "✓" if person.get('disponible', True) else "✗",
            contact
        )
        
        personnel_tree.insert('', 'end', values=values)


def refresh_personnel_data(personnel_tree, data_manager):
    """Rafraîchit les données du personnel"""
    try:
        print("🔄 Rafraîchissement des données personnel...")
        
        # Vider le tableau
        for item in personnel_tree.get_children():
            personnel_tree.delete(item)
        
        all_personnel = data_manager.get_personnel()
        print(f"  📊 {len(all_personnel)} membres du personnel chargés")
        
        # Mapping des types pour l'affichage
        type_mapping = {
            'pilote': 'Pilote',
            'copilote': 'Copilote',
            'hotesse': 'Hôtesse de l\'air',
            'steward': 'Steward',
            'mecanicien': 'Mécanicien',
            'controleur': 'Contrôleur aérien',
            'gestionnaire': 'Gestionnaire'
        }
        
        for person in all_personnel:
            try:
                person_type = type_mapping.get(person.get('type_personnel', ''), 'Inconnu')
                
                # Contact (priorité email puis téléphone)
                contact = ""
                if person.get('email'):
                    contact = person.get('email')
                elif person.get('numero_telephone'):
                    contact = person.get('numero_telephone')
                
                values = (
                    person.get('id_employe', '')[:8] + '...' if len(person.get('id_employe', '')) > 8 else person.get('id_employe', ''),
                    person.get('nom', ''),
                    person.get('prenom', ''),
                    person_type,
                    person.get('specialisation', ''),
                    person.get('horaire', ''),
                    "✓" if person.get('disponible', True) else "✗",
                    contact
                )
                
                personnel_tree.insert('', 'end', values=values)
                
            except Exception as e:
                print(f"  ⚠️ Erreur traitement personnel: {e}")
                continue
        
        print(f"✅ Personnel rafraîchi: {len(all_personnel)} membres affichés")
        
    except Exception as e:
        print(f"❌ Erreur refresh personnel: {e}")
