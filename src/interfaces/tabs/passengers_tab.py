import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os
from datetime import datetime, timedelta

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.personnes import Passager
from Core.enums import TypeSexe

class PassengerDialog:
    """Dialogue pour créer ou modifier un passager"""
    
    def __init__(self, parent, data_manager, passenger_data=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Fenêtre parente
            data_manager: Gestionnaire de données
            passenger_data: Données du passager existant (pour modification)
        """
        self.parent = parent
        self.data_manager = data_manager
        self.passenger_data = passenger_data
        self.is_editing = passenger_data is not None
        self.result = None
        
        # Créer la fenêtre dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modification du Passager" if self.is_editing else "Création d'un Nouveau Passager")
        self.dialog.geometry("600x700")
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
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables pour les champs"""
        self.nom_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.sexe_var = tk.StringVar()
        self.adresse_var = tk.StringVar()
        self.telephone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.numero_passeport_var = tk.StringVar()
        self.date_naissance_var = tk.StringVar()
        
        # Date de naissance par défaut (30 ans)
        default_birth = datetime.now() - timedelta(days=30*365)
        self.date_naissance_var.set(default_birth.strftime("%Y-%m-%d"))
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec défilement
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Modification du Passager" if self.is_editing else "Création d'un Nouveau Passager",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Section informations personnelles
        self.create_personal_info_section(main_frame)
        
        # Section contact
        self.create_contact_section(main_frame)
        
        # Section documents
        self.create_documents_section(main_frame)
        
        # Section historique (si modification)
        if self.is_editing:
            self.create_history_section(main_frame)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_personal_info_section(self, parent):
        """Crée la section des informations personnelles"""
        personal_frame = ttk.LabelFrame(parent, text="👤 Informations Personnelles", padding=15)
        personal_frame.pack(fill="x", pady=(0, 10))
        
        # Configuration de la grille
        personal_frame.grid_columnconfigure(1, weight=1)
        
        # Nom
        ttk.Label(personal_frame, text="Nom*:").grid(row=0, column=0, sticky="w", pady=5)
        self.nom_entry = ttk.Entry(personal_frame, textvariable=self.nom_var, width=30)
        self.nom_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(personal_frame, text="Ex: MARTIN", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Prénom
        ttk.Label(personal_frame, text="Prénom*:").grid(row=1, column=0, sticky="w", pady=5)
        self.prenom_entry = ttk.Entry(personal_frame, textvariable=self.prenom_var, width=30)
        self.prenom_entry.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(personal_frame, text="Ex: Jean", foreground="gray").grid(row=1, column=2, sticky="w", padx=5)
        
        # Sexe
        ttk.Label(personal_frame, text="Sexe*:").grid(row=2, column=0, sticky="w", pady=5)
        sexe_combo = ttk.Combobox(personal_frame, textvariable=self.sexe_var,
                                 values=["Masculin", "Féminin", "Autre"], state="readonly", width=15)
        sexe_combo.grid(row=2, column=1, sticky="w", padx=(10, 5), pady=5)
        self.sexe_var.set("Masculin")
        
        # Date de naissance
        ttk.Label(personal_frame, text="Date de naissance:").grid(row=3, column=0, sticky="w", pady=5)
        self.date_naissance_entry = ttk.Entry(personal_frame, textvariable=self.date_naissance_var, width=15)
        self.date_naissance_entry.grid(row=3, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(personal_frame, text="Format: YYYY-MM-DD", foreground="gray").grid(row=3, column=2, sticky="w", padx=5)
        
        # Adresse
        ttk.Label(personal_frame, text="Adresse*:").grid(row=4, column=0, sticky="w", pady=5)
        self.adresse_entry = ttk.Entry(personal_frame, textvariable=self.adresse_var, width=50)
        self.adresse_entry.grid(row=4, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(personal_frame, text="Ex: 123 Rue de la Paix, Paris", foreground="gray").grid(row=4, column=2, sticky="w", padx=5)
    
    def create_contact_section(self, parent):
        """Crée la section des informations de contact"""
        contact_frame = ttk.LabelFrame(parent, text="📞 Contact", padding=15)
        contact_frame.pack(fill="x", pady=(0, 10))
        
        contact_frame.grid_columnconfigure(1, weight=1)
        
        # Téléphone
        ttk.Label(contact_frame, text="Téléphone:").grid(row=0, column=0, sticky="w", pady=5)
        self.telephone_entry = ttk.Entry(contact_frame, textvariable=self.telephone_var, width=20)
        self.telephone_entry.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(contact_frame, text="Ex: +33 1 23 45 67 89", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Email
        ttk.Label(contact_frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email_entry = ttk.Entry(contact_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        ttk.Label(contact_frame, text="Ex: jean.martin@email.com", foreground="gray").grid(row=1, column=2, sticky="w", padx=5)
    
    def create_documents_section(self, parent):
        """Crée la section des documents"""
        docs_frame = ttk.LabelFrame(parent, text="🛂 Documents", padding=15)
        docs_frame.pack(fill="x", pady=(0, 10))
        
        docs_frame.grid_columnconfigure(1, weight=1)
        
        # Numéro de passeport
        ttk.Label(docs_frame, text="Numéro de passeport:").grid(row=0, column=0, sticky="w", pady=5)
        self.passeport_entry = ttk.Entry(docs_frame, textvariable=self.numero_passeport_var, width=20)
        self.passeport_entry.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(docs_frame, text="Ex: 12AB34567", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Note sur la validation
        note_label = ttk.Label(docs_frame, text="Note: Aucune validation de passeport n'est effectuée", 
                              foreground="gray", font=('Arial', 9))
        note_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 0))
    
    def create_history_section(self, parent):
        """Crée la section historique (pour modification uniquement)"""
        history_frame = ttk.LabelFrame(parent, text="📊 Historique", padding=15)
        history_frame.pack(fill="x", pady=(0, 10))
        
        # Informations sur les réservations
        if self.passenger_data:
            # Compter les réservations
            all_reservations = self.data_manager.get_reservations()
            passenger_reservations = [r for r in all_reservations 
                                    if r.get('passager_id') == self.passenger_data.get('id_passager')]
            
            info_text = f"Nombre de réservations: {len(passenger_reservations)}"
            if passenger_reservations:
                # Dernière réservation
                last_reservation = max(passenger_reservations, 
                                     key=lambda x: x.get('created_at', ''))
                try:
                    last_date = datetime.fromisoformat(last_reservation.get('created_at', ''))
                    info_text += f"\nDernière réservation: {last_date.strftime('%Y-%m-%d')}"
                except:
                    pass
            
            ttk.Label(history_frame, text=info_text, font=('Arial', 10)).pack(anchor="w")
    
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
                             command=self.save_passenger)
        btn_save.pack(side="right")
    
    def populate_fields(self):
        """Pré-remplit les champs pour la modification"""
        if not self.passenger_data:
            return
        
        self.nom_var.set(self.passenger_data.get('nom', ''))
        self.prenom_var.set(self.passenger_data.get('prenom', ''))
        
        # Sexe
        sexe_mapping = {
            'masculin': 'Masculin',
            'feminin': 'Féminin',
            'autre': 'Autre'
        }
        current_sexe = self.passenger_data.get('sexe', 'masculin')
        self.sexe_var.set(sexe_mapping.get(current_sexe, 'Masculin'))
        
        self.adresse_var.set(self.passenger_data.get('adresse', ''))
        self.telephone_var.set(self.passenger_data.get('numero_telephone', ''))
        self.email_var.set(self.passenger_data.get('email', ''))
        self.numero_passeport_var.set(self.passenger_data.get('numero_passeport', ''))
        
        # Date de naissance
        try:
            if self.passenger_data.get('date_naissance'):
                if isinstance(self.passenger_data['date_naissance'], str):
                    birth_date = datetime.fromisoformat(self.passenger_data['date_naissance'])
                else:
                    birth_date = self.passenger_data['date_naissance']
                self.date_naissance_var.set(birth_date.strftime("%Y-%m-%d"))
        except:
            pass
    
    def validate_fields(self):
        """Valide tous les champs obligatoires"""
        errors = []
        
        # Vérifications de base
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
        
        # Validation date de naissance si fournie
        date_naissance = self.date_naissance_var.get().strip()
        if date_naissance:
            try:
                birth_date = datetime.strptime(date_naissance, "%Y-%m-%d")
                # Vérifier que la date n'est pas dans le futur
                if birth_date > datetime.now():
                    errors.append("La date de naissance ne peut pas être dans le futur")
                # Vérifier un âge raisonnable (0-120 ans)
                age = (datetime.now() - birth_date).days / 365.25
                if age > 120:
                    errors.append("Âge non valide (plus de 120 ans)")
            except ValueError:
                errors.append("Format de date de naissance invalide (YYYY-MM-DD)")
        
        return errors
    
    def save_passenger(self):
        """Sauvegarde le passager"""
        # Validation
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Erreurs de Validation", 
                               "Veuillez corriger les erreurs suivantes:\n\n" + 
                               "\n".join(f"• {error}" for error in errors))
            return
        
        try:
            # Mapping des énumérations
            sexe_mapping = {
                'Masculin': 'masculin',
                'Féminin': 'feminin',
                'Autre': 'autre'
            }
            
            # Date de naissance
            date_naissance = None
            if self.date_naissance_var.get().strip():
                date_naissance = datetime.strptime(self.date_naissance_var.get(), "%Y-%m-%d")
            
            # Construire les données du passager
            passenger_data = {
                'id_passager': str(uuid.uuid4()) if not self.is_editing else self.passenger_data.get('id_passager'),
                'nom': self.nom_var.get().strip(),
                'prenom': self.prenom_var.get().strip(),
                'sexe': sexe_mapping.get(self.sexe_var.get(), 'masculin'),
                'adresse': self.adresse_var.get().strip(),
                'numero_telephone': self.telephone_var.get().strip(),
                'email': self.email_var.get().strip(),
                'numero_passeport': self.numero_passeport_var.get().strip(),
                'date_naissance': date_naissance.isoformat() if date_naissance else None,
                'checkin_effectue': False,
                'reservations_count': 0
            }
            
            # Sauvegarder
            if self.is_editing:
                # Pour la modification
                all_passengers = self.data_manager.get_passengers()
                for i, passenger in enumerate(all_passengers):
                    if passenger.get('id_passager') == passenger_data['id_passager']:
                        passenger_data['updated_at'] = datetime.now().isoformat()
                        # Conserver le nombre de réservations
                        passenger_data['reservations_count'] = passenger.get('reservations_count', 0)
                        all_passengers[i] = {**passenger, **passenger_data}
                        break
                
                data = self.data_manager.load_data('passengers')
                data['passengers'] = all_passengers
                success = self.data_manager.save_data('passengers', data)
                action = "modifié"
            else:
                passenger_data['created_at'] = datetime.now().isoformat()
                data = self.data_manager.load_data('passengers')
                if 'passengers' not in data:
                    data['passengers'] = []
                data['passengers'].append(passenger_data)
                success = self.data_manager.save_data('passengers', data)
                action = "créé"
            
            if success:
                self.result = passenger_data
                messagebox.showinfo("Succès", f"Passager {action} avec succès!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", f"Impossible de {action.replace('é', 'er')} le passager.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            print(f"❌ Erreur sauvegarde passager: {e}")
    
    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy()


def create_passengers_tab_content(parent_frame, data_manager):
    """Crée le contenu de l'onglet passagers"""
    
    # Variables pour la recherche et le filtrage
    passengers_search_var = tk.StringVar()
    passengers_filter_var = tk.StringVar(value="Tous")
    
    # Barre d'outils
    toolbar = ttk.Frame(parent_frame)
    toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    
    # Variables pour stocker les références aux widgets
    passengers_tree = None
    
    def new_passenger_callback():
        new_passenger_dialog(parent_frame, data_manager, passengers_tree)
    
    def edit_passenger_callback():
        edit_passenger(parent_frame, data_manager, passengers_tree)
    
    def view_passenger_callback():
        view_passenger_details(passengers_tree, data_manager)
    
    def delete_passenger_callback():
        delete_passenger(data_manager, passengers_tree)
    
    def filter_passengers_callback(event=None):
        filter_passengers(passengers_tree, data_manager, passengers_search_var, passengers_filter_var)
    
    def create_reservation_callback():
        create_reservation_for_passenger(parent_frame, data_manager, passengers_tree)
    
    ttk.Button(toolbar, text="➕ Nouveau Passager", 
              command=new_passenger_callback, 
              style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
    ttk.Button(toolbar, text="✏️ Modifier", 
              command=edit_passenger_callback).grid(row=0, column=1, padx=(0, 5))
    ttk.Button(toolbar, text="🎫 Créer Réservation", 
              command=create_reservation_callback).grid(row=0, column=2, padx=(0, 5))
    ttk.Button(toolbar, text="👁️ Voir Détails", 
              command=view_passenger_callback).grid(row=0, column=3, padx=(0, 5))
    ttk.Button(toolbar, text="🗑️ Supprimer", 
              command=delete_passenger_callback, 
              style='Danger.TButton').grid(row=0, column=4, padx=(0, 20))
    
    # Recherche
    ttk.Label(toolbar, text="🔍 Recherche:").grid(row=0, column=5, padx=(0, 5))
    search_entry = ttk.Entry(toolbar, textvariable=passengers_search_var, width=20)
    search_entry.grid(row=0, column=6, padx=(0, 5))
    search_entry.bind('<KeyRelease>', filter_passengers_callback)
    
    # Filtre par sexe
    ttk.Label(toolbar, text="Sexe:").grid(row=0, column=7, padx=(10, 5))
    filter_combo = ttk.Combobox(toolbar, textvariable=passengers_filter_var, width=15, state="readonly")
    filter_combo['values'] = ['Tous', 'Masculin', 'Féminin', 'Autre']
    filter_combo.grid(row=0, column=8, padx=(0, 5))
    filter_combo.bind('<<ComboboxSelected>>', filter_passengers_callback)
    
    # Tableau des passagers
    columns = ('ID', 'Nom', 'Prénom', 'Sexe', 'Âge', 'Contact', 'Réservations', 'Check-in')
    passengers_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
    passengers_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    # Configuration colonnes
    column_widths = {
        'ID': 100, 'Nom': 120, 'Prénom': 120, 'Sexe': 80, 
        'Âge': 60, 'Contact': 200, 'Réservations': 100, 'Check-in': 80
    }
    for col in columns:
        passengers_tree.heading(col, text=col)
        passengers_tree.column(col, width=column_widths.get(col, 100))
    
    # Scrollbars
    passengers_v_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=passengers_tree.yview)
    passengers_v_scrollbar.grid(row=1, column=1, sticky="ns")
    passengers_tree.configure(yscrollcommand=passengers_v_scrollbar.set)
    
    passengers_h_scrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=passengers_tree.xview)
    passengers_h_scrollbar.grid(row=2, column=0, sticky="ew")
    passengers_tree.configure(xscrollcommand=passengers_h_scrollbar.set)
    
    # Configuration responsive
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Charger les données initiales
    refresh_passengers_data(passengers_tree, data_manager)
    
    # Double-clic pour modifier
    passengers_tree.bind('<Double-1>', lambda e: edit_passenger(parent_frame, data_manager, passengers_tree))
    
    return passengers_tree


def new_passenger_dialog(parent, data_manager, passengers_tree):
    """Ouvre le dialogue de création de passager"""
    dialog = PassengerDialog(parent, data_manager)
    if dialog.result:
        refresh_passengers_data(passengers_tree, data_manager)


def edit_passenger(parent, data_manager, passengers_tree):
    """Modifie le passager sélectionné"""
    selection = passengers_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un passager à modifier.")
        return
    
    item = passengers_tree.item(selection[0])
    passenger_id = item['values'][0]
    
    # Trouver les données complètes du passager
    all_passengers = data_manager.get_passengers()
    passenger_data = None
    for passenger in all_passengers:
        if passenger.get('id_passager', '').startswith(passenger_id.replace('...', '')):
            passenger_data = passenger
            break
    
    if not passenger_data:
        messagebox.showerror("Erreur", "Passager non trouvé.")
        return
    
    dialog = PassengerDialog(parent, data_manager, passenger_data)
    if dialog.result:
        refresh_passengers_data(passengers_tree, data_manager)


def view_passenger_details(passengers_tree, data_manager):
    """Affiche les détails du passager sélectionné"""
    selection = passengers_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un passager.")
        return
    
    item = passengers_tree.item(selection[0])
    passenger_id = item['values'][0]
    
    # Trouver les données complètes
    all_passengers = data_manager.get_passengers()
    passenger_data = None
    for passenger in all_passengers:
        if passenger.get('id_passager', '').startswith(passenger_id.replace('...', '')):
            passenger_data = passenger
            break
    
    if not passenger_data:
        messagebox.showerror("Erreur", "Passager non trouvé.")
        return
    
    # Construire les détails avec les réservations
    all_reservations = data_manager.get_reservations()
    passenger_reservations = [r for r in all_reservations 
                            if r.get('passager_id') == passenger_data.get('id_passager')]
    
    details = f"""Détails du Passager

Informations personnelles:
• Nom: {passenger_data.get('nom', 'N/A')}
• Prénom: {passenger_data.get('prenom', 'N/A')}
• Sexe: {passenger_data.get('sexe', 'N/A').capitalize()}
• Adresse: {passenger_data.get('adresse', 'N/A')}

Contact:
• Téléphone: {passenger_data.get('numero_telephone', 'N/A')}
• Email: {passenger_data.get('email', 'N/A')}

Documents:
• Passeport: {passenger_data.get('numero_passeport', 'N/A')}

Historique:
• Réservations: {len(passenger_reservations)}
• Check-in effectué: {'Oui' if passenger_data.get('checkin_effectue', False) else 'Non'}"""
    
    messagebox.showinfo("Détails du Passager", details)


def create_reservation_for_passenger(parent, data_manager, passengers_tree):
    """Crée une réservation pour le passager sélectionné"""
    selection = passengers_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un passager.")
        return
    
    item = passengers_tree.item(selection[0])
    passenger_name = f"{item['values'][2]} {item['values'][1]}"
    
    messagebox.showinfo("Créer Réservation", 
                       f"Fonctionnalité à venir:\nCréer une réservation pour {passenger_name}\n\n"
                       "Cette fonctionnalité sera disponible dans l'onglet Réservations.")


def delete_passenger(data_manager, passengers_tree):
    """Supprime le passager sélectionné"""
    selection = passengers_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un passager à supprimer.")
        return
    
    item = passengers_tree.item(selection[0])
    passenger_id = item['values'][0]
    passenger_name = f"{item['values'][2]} {item['values'][1]}"
    
    # Vérifier s'il y a des réservations actives
    all_reservations = data_manager.get_reservations()
    active_reservations = [r for r in all_reservations 
                          if r.get('passager_id', '').startswith(passenger_id.replace('...', '')) 
                          and r.get('statut') == 'active']
    
    if active_reservations:
        messagebox.showwarning("Suppression impossible", 
                              f"Impossible de supprimer {passenger_name}.\n"
                              f"Le passager a {len(active_reservations)} réservation(s) active(s).\n\n"
                              "Annulez d'abord les réservations.")
        return
    
    if messagebox.askyesno("Confirmation", 
                          f"Voulez-vous vraiment supprimer {passenger_name} ?\n\n"
                          "Cette action est irréversible."):
        
        # Supprimer de la liste
        all_passengers = data_manager.get_passengers()
        updated_passengers = []
        
        for passenger in all_passengers:
            if not passenger.get('id_passager', '').startswith(passenger_id.replace('...', '')):
                updated_passengers.append(passenger)
        
        # Sauvegarder
        data = data_manager.load_data('passengers')
        data['passengers'] = updated_passengers
        
        if data_manager.save_data('passengers', data):
            refresh_passengers_data(passengers_tree, data_manager)
            messagebox.showinfo("Succès", "Passager supprimé avec succès.")
        else:
            messagebox.showerror("Erreur", "Impossible de supprimer le passager.")


def filter_passengers(passengers_tree, data_manager, search_var, filter_var):
    """Filtre la liste des passagers"""
    search_text = search_var.get().lower()
    filter_sexe = filter_var.get()
    
    # Vider le tableau
    for item in passengers_tree.get_children():
        passengers_tree.delete(item)
    
    # Recharger avec filtres
    all_passengers = data_manager.get_passengers()
    
    for passenger in all_passengers:
        # Mapping du sexe pour l'affichage
        sexe_mapping = {
            'masculin': 'Masculin',
            'feminin': 'Féminin',
            'autre': 'Autre'
        }
        
        passenger_sexe = sexe_mapping.get(passenger.get('sexe', ''), 'Inconnu')
        
        # Filtrage par sexe
        if filter_sexe != "Tous" and passenger_sexe != filter_sexe:
            continue
        
        # Filtrage par recherche
        searchable_text = f"{passenger.get('nom', '')} {passenger.get('prenom', '')} {passenger.get('email', '')} {passenger.get('numero_passeport', '')}".lower()
        if search_text and search_text not in searchable_text:
            continue
        
        # Calculer l'âge
        age = "N/A"
        try:
            if passenger.get('date_naissance'):
                if isinstance(passenger['date_naissance'], str):
                    birth_date = datetime.fromisoformat(passenger['date_naissance'])
                else:
                    birth_date = passenger['date_naissance']
                
                age = int((datetime.now() - birth_date).days / 365.25)
        except:
            pass
        
        # Contact (priorité email puis téléphone)
        contact = ""
        if passenger.get('email'):
            contact = passenger.get('email')
        elif passenger.get('numero_telephone'):
            contact = passenger.get('numero_telephone')
        
        # Compter les réservations
        all_reservations = data_manager.get_reservations()
        passenger_reservations = [r for r in all_reservations 
                                if r.get('passager_id') == passenger.get('id_passager')]
        
        values = (
            passenger.get('id_passager', '')[:8] + '...' if len(passenger.get('id_passager', '')) > 8 else passenger.get('id_passager', ''),
            passenger.get('nom', ''),
            passenger.get('prenom', ''),
            passenger_sexe,
            str(age),
            contact,
            str(len(passenger_reservations)),
            "✓" if passenger.get('checkin_effectue', False) else "✗"
        )
        
        passengers_tree.insert('', 'end', values=values)


def refresh_passengers_data(passengers_tree, data_manager):
    """Rafraîchit les données des passagers"""
    # Vider le tableau
    for item in passengers_tree.get_children():
        passengers_tree.delete(item)
    
    # Recharger les données
    all_passengers = data_manager.get_passengers()
    all_reservations = data_manager.get_reservations()
    
    # Mapping des sexes pour l'affichage
    sexe_mapping = {
        'masculin': 'Masculin',
        'feminin': 'Féminin',
        'autre': 'Autre'
    }
    
    for passenger in all_passengers:
        passenger_sexe = sexe_mapping.get(passenger.get('sexe', ''), 'Inconnu')
        
        # Calculer l'âge
        age = "N/A"
        try:
            if passenger.get('date_naissance'):
                if isinstance(passenger['date_naissance'], str):
                    birth_date = datetime.fromisoformat(passenger['date_naissance'])
                else:
                    birth_date = passenger['date_naissance']
                
                age = int((datetime.now() - birth_date).days / 365.25)
        except:
            pass
        
        # Contact (priorité email puis téléphone)
        contact = ""
        if passenger.get('email'):
            contact = passenger.get('email')
        elif passenger.get('numero_telephone'):
            contact = passenger.get('numero_telephone')
        
        # Compter les réservations pour ce passager
        passenger_reservations = [r for r in all_reservations 
                                if r.get('passager_id') == passenger.get('id_passager')]
        
        values = (
            passenger.get('id_passager', '')[:8] + '...' if len(passenger.get('id_passager', '')) > 8 else passenger.get('id_passager', ''),
            passenger.get('nom', ''),
            passenger.get('prenom', ''),
            passenger_sexe,
            str(age),
            contact,
            str(len(passenger_reservations)),
            "✓" if passenger.get('checkin_effectue', False) else "✗"
        )
        
        passengers_tree.insert('', 'end', values=values)