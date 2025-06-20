import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os
from datetime import datetime, timedelta

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.reservation import Reservation
from Core.enums import StatutReservation

class ReservationDialog:
    """Dialogue pour créer ou modifier une réservation"""
    
    def __init__(self, parent, data_manager, reservation_data=None, passenger_id=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Fenêtre parente
            data_manager: Gestionnaire de données
            reservation_data: Données de réservation existante (pour modification)
            passenger_id: ID du passager pré-sélectionné (pour création depuis onglet passagers)
        """
        self.parent = parent
        self.data_manager = data_manager
        self.reservation_data = reservation_data
        self.passenger_id = passenger_id
        self.is_editing = reservation_data is not None
        self.result = None
        
        # Créer la fenêtre dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modification de Réservation" if self.is_editing else "Création d'une Nouvelle Réservation")
        self.dialog.geometry("700x800")  # Augmenté de 750 à 800
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
        
        # Pré-remplir si modification ou passager pré-sélectionné
        if self.is_editing:
            self.populate_fields()
        elif self.passenger_id:
            self.preselect_passenger()
        
        # Focus sur le premier champ
        if self.passenger_id:
            self.vol_combo.focus()
        else:
            self.passager_combo.focus()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (800 // 2)  # Ajusté pour 800px
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables pour les champs"""
        self.passager_var = tk.StringVar()
        self.vol_var = tk.StringVar()
        self.siege_var = tk.StringVar()
        self.statut_var = tk.StringVar()
        self.checkin_var = tk.BooleanVar()
        
        # Informations calculées
        self.vol_info_var = tk.StringVar(value="Sélectionnez un vol")
        self.passager_info_var = tk.StringVar(value="Sélectionnez un passager")
        self.checkin_available_var = tk.StringVar(value="Non disponible")
        self.checkin_color_var = tk.StringVar(value="gray")
    
    def load_reference_data(self):
        """Charge les données de référence"""
        self.passengers = self.data_manager.get_passengers()
        self.flights = self.data_manager.get_flights()
        
        # Préparer les listes pour les combobox
        self.passenger_choices = []
        for passenger in self.passengers:
            choice = f"{passenger.get('prenom', '')} {passenger.get('nom', '')} (ID: {passenger.get('id_passager', '')[:8]})"
            self.passenger_choices.append(choice)
        
        # Vols disponibles (non annulés, non terminés)
        self.flight_choices = []
        for flight in self.flights:
            if flight.get('statut') not in ['annule', 'termine']:
                try:
                    if flight.get('heure_depart'):
                        if isinstance(flight['heure_depart'], str):
                            depart_time = datetime.fromisoformat(flight['heure_depart'])
                        else:
                            depart_time = flight['heure_depart']
                        
                        date_str = depart_time.strftime("%Y-%m-%d %H:%M")
                    else:
                        date_str = "N/A"
                except:
                    date_str = "N/A"
                
                choice = f"{flight.get('numero_vol', '')} - {flight.get('aeroport_depart', '')} → {flight.get('aeroport_arrivee', '')} ({date_str})"
                self.flight_choices.append(choice)
        
        self.statut_choices = [s.obtenir_nom_affichage() for s in StatutReservation]
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Modification de Réservation" if self.is_editing else "Création d'une Nouvelle Réservation",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Section sélection
        self.create_selection_section(main_frame)
        
        # Section informations
        self.create_info_section(main_frame)
        
        # Section siège
        self.create_seat_section(main_frame)
        
        # Section check-in
        self.create_checkin_section(main_frame)
        
        # Section statut
        self.create_status_section(main_frame)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_selection_section(self, parent):
        """Crée la section de sélection passager/vol"""
        selection_frame = ttk.LabelFrame(parent, text="🎫 Sélection", padding=15)
        selection_frame.pack(fill="x", pady=(0, 10))
        
        selection_frame.grid_columnconfigure(1, weight=1)
        
        # Passager
        ttk.Label(selection_frame, text="Passager*:").grid(row=0, column=0, sticky="w", pady=5)
        self.passager_combo = ttk.Combobox(selection_frame, textvariable=self.passager_var,
                                          values=self.passenger_choices, width=50)
        self.passager_combo.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.passager_combo.bind('<<ComboboxSelected>>', self.on_passenger_selected)
        self.passager_combo.bind('<KeyRelease>', self.on_passenger_typed)
        
        # Vol
        ttk.Label(selection_frame, text="Vol*:").grid(row=1, column=0, sticky="w", pady=5)
        self.vol_combo = ttk.Combobox(selection_frame, textvariable=self.vol_var,
                                     values=self.flight_choices, width=50)
        self.vol_combo.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.vol_combo.bind('<<ComboboxSelected>>', self.on_flight_selected)
        self.vol_combo.bind('<KeyRelease>', self.on_flight_typed)
    
    def create_info_section(self, parent):
        """Crée la section d'informations"""
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Informations", padding=15)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Informations passager
        passager_card = ttk.Frame(info_frame, relief="solid", borderwidth=1)
        passager_card.pack(fill="x", pady=(0, 5))
        ttk.Label(passager_card, text="👤 Passager", font=('Arial', 10, 'bold')).pack(pady=2)
        self.passager_info_label = ttk.Label(passager_card, textvariable=self.passager_info_var, 
                                           font=('Arial', 10), foreground="blue")
        self.passager_info_label.pack(pady=2)
        
        # Informations vol
        vol_card = ttk.Frame(info_frame, relief="solid", borderwidth=1)
        vol_card.pack(fill="x", pady=(5, 0))
        ttk.Label(vol_card, text="✈️ Vol", font=('Arial', 10, 'bold')).pack(pady=2)
        self.vol_info_label = ttk.Label(vol_card, textvariable=self.vol_info_var, 
                                       font=('Arial', 10), foreground="blue")
        self.vol_info_label.pack(pady=2)
    
    def create_seat_section(self, parent):
        """Crée la section du siège"""
        seat_frame = ttk.LabelFrame(parent, text="💺 Siège", padding=15)
        seat_frame.pack(fill="x", pady=(0, 10))
        
        seat_frame.grid_columnconfigure(1, weight=1)
        
        # Numéro de siège
        ttk.Label(seat_frame, text="Numéro de siège:").grid(row=0, column=0, sticky="w", pady=5)
        self.siege_entry = ttk.Entry(seat_frame, textvariable=self.siege_var, width=10)
        self.siege_entry.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(seat_frame, text="Ex: 12A, 3B, 25F", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Validation en temps réel
        self.siege_entry.bind('<KeyRelease>', self.validate_seat_format)
        
        # Indicateur de format
        self.seat_status_label = ttk.Label(seat_frame, text="", font=('Arial', 9))
        self.seat_status_label.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(2, 0))
    
    def create_checkin_section(self, parent):
        """Crée la section du check-in"""
        checkin_frame = ttk.LabelFrame(parent, text="✅ Check-in", padding=15)
        checkin_frame.pack(fill="x", pady=(0, 10))
        
        checkin_frame.grid_columnconfigure(1, weight=1)
        
        # État du check-in
        ttk.Label(checkin_frame, text="Disponibilité:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
        self.checkin_status_label = ttk.Label(checkin_frame, textvariable=self.checkin_available_var, 
                                            font=('Arial', 10, 'bold'))
        self.checkin_status_label.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Case à cocher check-in
        self.checkin_checkbox = ttk.Checkbutton(checkin_frame, text="Check-in effectué",
                                               variable=self.checkin_var, state="disabled")
        self.checkin_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Note explicative
        note_label = ttk.Label(checkin_frame, 
                              text="Le check-in est disponible 24h avant le départ et se ferme 30min avant",
                              font=('Arial', 9), foreground="gray")
        note_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
    
    def create_status_section(self, parent):
        """Crée la section du statut"""
        status_frame = ttk.LabelFrame(parent, text="📊 Statut", padding=15)
        status_frame.pack(fill="x", pady=(0, 10))
        
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Statut
        ttk.Label(status_frame, text="Statut:").grid(row=0, column=0, sticky="w", pady=5)
        self.statut_combo = ttk.Combobox(status_frame, textvariable=self.statut_var,
                                        values=self.statut_choices, state="readonly", width=20)
        self.statut_combo.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        self.statut_var.set("Active")  # Valeur par défaut
    
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
        btn_cancel = ttk.Button(buttons_container, text="Annuler", command=self.cancel, width=12)
        btn_cancel.pack(side="right", padx=(10, 0))
        
        # Bouton Créer/Modifier
        btn_save = ttk.Button(buttons_container, 
                             text="Modifier" if self.is_editing else "Créer", 
                             command=self.save_reservation, width=12)
        btn_save.pack(side="right")
        
        # Style pour rendre les boutons plus visibles
        btn_save.configure(style='Action.TButton')
        
        print(f"✓ Boutons créés dans reservation dialog: {'Modifier' if self.is_editing else 'Créer'} et Annuler")
    
    def on_passenger_selected(self, event=None):
        """Gestionnaire de sélection de passager"""
        self.update_passenger_info()
    
    def on_passenger_typed(self, event=None):
        """Gestionnaire de saisie manuelle de passager"""
        typed = self.passager_var.get().upper()
        if len(typed) >= 2:
            matches = [choice for choice in self.passenger_choices 
                      if typed.lower() in choice.lower()]
            if matches:
                self.passager_combo['values'] = matches
        else:
            self.passager_combo['values'] = self.passenger_choices
        
        self.update_passenger_info()
    
    def on_flight_selected(self, event=None):
        """Gestionnaire de sélection de vol"""
        self.update_flight_info()
        self.update_checkin_availability()
    
    def on_flight_typed(self, event=None):
        """Gestionnaire de saisie manuelle de vol"""
        typed = self.vol_var.get().upper()
        if len(typed) >= 2:
            matches = [choice for choice in self.flight_choices 
                      if typed.lower() in choice.lower()]
            if matches:
                self.vol_combo['values'] = matches
        else:
            self.vol_combo['values'] = self.flight_choices
        
        self.update_flight_info()
        self.update_checkin_availability()
    
    def update_passenger_info(self):
        """Met à jour les informations du passager"""
        selection = self.passager_var.get()
        
        if not selection or ' (ID: ' not in selection:
            self.passager_info_var.set("Sélectionnez un passager")
            return
        
        # Extraire l'ID du passager
        try:
            passenger_id_part = selection.split(' (ID: ')[1].replace(')', '')
            
            # Trouver le passager correspondant
            for passenger in self.passengers:
                if passenger.get('id_passager', '').startswith(passenger_id_part):
                    info = f"Email: {passenger.get('email', 'N/A')} | Tél: {passenger.get('numero_telephone', 'N/A')}"
                    self.passager_info_var.set(info)
                    return
        except:
            pass
        
        self.passager_info_var.set("Passager non trouvé")
    
    def update_flight_info(self):
        """Met à jour les informations du vol"""
        selection = self.vol_var.get()
        
        if not selection or ' - ' not in selection:
            self.vol_info_var.set("Sélectionnez un vol")
            return
        
        # Extraire le numéro de vol
        try:
            flight_number = selection.split(' - ')[0]
            
            # Trouver le vol correspondant
            for flight in self.flights:
                if flight.get('numero_vol') == flight_number:
                    try:
                        if flight.get('heure_depart'):
                            if isinstance(flight['heure_depart'], str):
                                depart_time = datetime.fromisoformat(flight['heure_depart'])
                            else:
                                depart_time = flight['heure_depart']
                            
                            date_str = depart_time.strftime("%Y-%m-%d à %H:%M")
                        else:
                            date_str = "N/A"
                    except:
                        date_str = "N/A"
                    
                    info = f"Avion: {flight.get('avion_utilise', 'N/A')} | Départ: {date_str}"
                    self.vol_info_var.set(info)
                    return
        except:
            pass
        
        self.vol_info_var.set("Vol non trouvé")
    
    def update_checkin_availability(self):
        """Met à jour la disponibilité du check-in"""
        selection = self.vol_var.get()
        
        if not selection or ' - ' not in selection:
            self.checkin_available_var.set("Non disponible")
            self.checkin_status_label.configure(foreground="gray")
            self.checkin_checkbox.configure(state="disabled")
            return
        
        try:
            # Extraire le numéro de vol
            flight_number = selection.split(' - ')[0]
            
            # Trouver le vol correspondant
            for flight in self.flights:
                if flight.get('numero_vol') == flight_number:
                    if flight.get('heure_depart'):
                        if isinstance(flight['heure_depart'], str):
                            depart_time = datetime.fromisoformat(flight['heure_depart'])
                        else:
                            depart_time = flight['heure_depart']
                        
                        now = datetime.now()
                        time_to_departure = depart_time - now
                        
                        # Check-in disponible 24h avant, fermé 30min avant
                        if time_to_departure <= timedelta(hours=24) and time_to_departure >= timedelta(minutes=30):
                            self.checkin_available_var.set("✓ Disponible")
                            self.checkin_status_label.configure(foreground="green")
                            self.checkin_checkbox.configure(state="normal")
                        elif time_to_departure > timedelta(hours=24):
                            hours_remaining = int(time_to_departure.total_seconds() // 3600)
                            self.checkin_available_var.set(f"Dans {hours_remaining - 24}h")
                            self.checkin_status_label.configure(foreground="orange")
                            self.checkin_checkbox.configure(state="disabled")
                        else:
                            self.checkin_available_var.set("✗ Fermé")
                            self.checkin_status_label.configure(foreground="red")
                            self.checkin_checkbox.configure(state="disabled")
                        return
        except:
            pass
        
        self.checkin_available_var.set("Non disponible")
        self.checkin_status_label.configure(foreground="gray")
        self.checkin_checkbox.configure(state="disabled")
    
    def validate_seat_format(self, event=None):
        """Valide le format du siège en temps réel"""
        seat = self.siege_var.get().strip().upper()
        
        if not seat:
            self.seat_status_label.configure(text="", foreground="gray")
            return
        
        # Vérifier le format (chiffres + lettre)
        import re
        if re.match(r'^\d{1,3}[A-Z]$', seat):
            self.seat_status_label.configure(text="✓ Format valide", foreground="green")
            self.siege_var.set(seat)  # Forcer majuscules
        else:
            self.seat_status_label.configure(text="✗ Format invalide (ex: 12A)", foreground="red")
    
    def preselect_passenger(self):
        """Pré-sélectionne un passager (quand appelé depuis l'onglet passagers)"""
        for choice in self.passenger_choices:
            if self.passenger_id in choice:
                self.passager_var.set(choice)
                self.update_passenger_info()
                break
    
    def populate_fields(self):
        """Pré-remplit les champs pour la modification"""
        if not self.reservation_data:
            return
        
        # Passager
        passenger_id = self.reservation_data.get('passager_id', '')
        for choice in self.passenger_choices:
            if passenger_id in choice:
                self.passager_var.set(choice)
                break
        
        # Vol
        vol_numero = self.reservation_data.get('vol_numero', '')
        for choice in self.flight_choices:
            if vol_numero in choice:
                self.vol_var.set(choice)
                break
        
        # Siège
        self.siege_var.set(self.reservation_data.get('siege_assigne', ''))
        
        # Check-in
        self.checkin_var.set(self.reservation_data.get('checkin_effectue', False))
        
        # Statut
        status_mapping = {
            'active': 'Active',
            'annulee': 'Annulée',
            'terminee': 'Terminée',
            'expiree': 'Expirée'
        }
        current_status = self.reservation_data.get('statut', 'active')
        self.statut_var.set(status_mapping.get(current_status, 'Active'))
        
        # Mettre à jour les informations
        self.update_passenger_info()
        self.update_flight_info()
        self.update_checkin_availability()
        self.validate_seat_format()
    
    def validate_fields(self):
        """Valide tous les champs obligatoires"""
        errors = []
        
        # Vérifications de base
        if not self.passager_var.get().strip():
            errors.append("Le passager est obligatoire")
        
        if not self.vol_var.get().strip():
            errors.append("Le vol est obligatoire")
        
        # Validation du format de siège si fourni
        seat = self.siege_var.get().strip()
        if seat:
            import re
            if not re.match(r'^\d{1,3}[A-Z]$', seat):
                errors.append("Format de siège invalide (ex: 12A, 3B)")
        
        # Vérification que le passager existe
        passenger_selection = self.passager_var.get()
        if passenger_selection and ' (ID: ' in passenger_selection:
            passenger_id_part = passenger_selection.split(' (ID: ')[1].replace(')', '')
            passenger_found = any(p.get('id_passager', '').startswith(passenger_id_part) 
                                for p in self.passengers)
            if not passenger_found:
                errors.append("Passager sélectionné non valide")
        
        # Vérification que le vol existe
        vol_selection = self.vol_var.get()
        if vol_selection and ' - ' in vol_selection:
            flight_number = vol_selection.split(' - ')[0]
            flight_found = any(f.get('numero_vol') == flight_number for f in self.flights)
            if not flight_found:
                errors.append("Vol sélectionné non valide")
        
        # Vérification unicité (passager + vol) pour création
        if not self.is_editing:
            if passenger_selection and vol_selection:
                try:
                    passenger_id_part = passenger_selection.split(' (ID: ')[1].replace(')', '')
                    flight_number = vol_selection.split(' - ')[0]
                    
                    # Trouver l'ID complet du passager
                    full_passenger_id = None
                    for p in self.passengers:
                        if p.get('id_passager', '').startswith(passenger_id_part):
                            full_passenger_id = p.get('id_passager')
                            break
                    
                    if full_passenger_id:
                        existing_reservations = self.data_manager.get_reservations()
                        duplicate = any(r.get('passager_id') == full_passenger_id 
                                      and r.get('vol_numero') == flight_number 
                                      and r.get('statut') == 'active'
                                      for r in existing_reservations)
                        if duplicate:
                            errors.append("Ce passager a déjà une réservation active pour ce vol")
                except:
                    pass
        
        return errors
    
    def save_reservation(self):
        """Sauvegarde la réservation"""
        # Validation
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Erreurs de Validation", 
                               "Veuillez corriger les erreurs suivantes:\n\n" + 
                               "\n".join(f"• {error}" for error in errors))
            return
        
        try:
            # Extraire les IDs
            passenger_selection = self.passager_var.get()
            vol_selection = self.vol_var.get()
            
            passenger_id_part = passenger_selection.split(' (ID: ')[1].replace(')', '')
            flight_number = vol_selection.split(' - ')[0]
            
            # Trouver l'ID complet du passager
            full_passenger_id = None
            for passenger in self.passengers:
                if passenger.get('id_passager', '').startswith(passenger_id_part):
                    full_passenger_id = passenger.get('id_passager')
                    break
            
            if not full_passenger_id:
                messagebox.showerror("Erreur", "Passager non trouvé.")
                return
            
            # Mapping des statuts
            status_mapping = {
                'Active': 'active',
                'Annulée': 'annulee',
                'Terminée': 'terminee',
                'Expirée': 'expiree'
            }
            
            # Construire les données de réservation
            reservation_data = {
                'id_reservation': str(uuid.uuid4()) if not self.is_editing else self.reservation_data.get('id_reservation'),
                'passager_id': full_passenger_id,
                'vol_numero': flight_number,
                'siege_assigne': self.siege_var.get().strip().upper() if self.siege_var.get().strip() else None,
                'checkin_effectue': self.checkin_var.get(),
                'statut': status_mapping.get(self.statut_var.get(), 'active'),
                'date_creation': datetime.now().isoformat() if not self.is_editing else self.reservation_data.get('date_creation'),
                'validite': (datetime.now() + timedelta(days=1)).isoformat()  # Valide 24h
            }
            
            # Sauvegarder
            if self.is_editing:
                # Pour la modification
                all_reservations = self.data_manager.get_reservations()
                for i, reservation in enumerate(all_reservations):
                    if reservation.get('id_reservation') == reservation_data['id_reservation']:
                        reservation_data['updated_at'] = datetime.now().isoformat()
                        all_reservations[i] = {**reservation, **reservation_data}
                        break
                
                data = self.data_manager.load_data('reservations')
                data['reservations'] = all_reservations
                success = self.data_manager.save_data('reservations', data)
                action = "modifiée"
            else:
                reservation_data['created_at'] = datetime.now().isoformat()
                data = self.data_manager.load_data('reservations')
                if 'reservations' not in data:
                    data['reservations'] = []
                data['reservations'].append(reservation_data)
                success = self.data_manager.save_data('reservations', data)
                action = "créée"
            
            if success:
                self.result = reservation_data
                messagebox.showinfo("Succès", f"Réservation {action} avec succès!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", f"Impossible de {action.replace('ée', 'er')} la réservation.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            print(f"❌ Erreur sauvegarde réservation: {e}")
    
    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy()


def create_reservations_tab_content(parent_frame, data_manager):
    """Crée le contenu de l'onglet réservations"""
    
    # Variables pour la recherche et le filtrage
    reservations_search_var = tk.StringVar()
    reservations_filter_var = tk.StringVar(value="Tous")
    
    # Barre d'outils
    toolbar = ttk.Frame(parent_frame)
    toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    
    # Variables pour stocker les références aux widgets
    reservations_tree = None
    
    def new_reservation_callback():
        new_reservation_dialog(parent_frame, data_manager, reservations_tree)
    
    def edit_reservation_callback():
        edit_reservation(parent_frame, data_manager, reservations_tree)
    
    def view_reservation_callback():
        view_reservation_details(reservations_tree, data_manager)
    
    def cancel_reservation_callback():
        cancel_reservation(data_manager, reservations_tree)
    
    def checkin_reservation_callback():
        toggle_checkin(data_manager, reservations_tree)
    
    def filter_reservations_callback(event=None):
        filter_reservations(reservations_tree, data_manager, reservations_search_var, reservations_filter_var)
    
    ttk.Button(toolbar, text="➕ Nouvelle Réservation", 
              command=new_reservation_callback, 
              style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
    ttk.Button(toolbar, text="✏️ Modifier", 
              command=edit_reservation_callback).grid(row=0, column=1, padx=(0, 5))
    ttk.Button(toolbar, text="✅ Check-in", 
              command=checkin_reservation_callback).grid(row=0, column=2, padx=(0, 5))
    ttk.Button(toolbar, text="🎯 Valider", 
              command=lambda: validate_reservation(data_manager, reservations_tree)).grid(row=0, column=3, padx=(0, 5))
    ttk.Button(toolbar, text="👁️ Voir Détails", 
              command=view_reservation_callback).grid(row=0, column=4, padx=(0, 5))
    ttk.Button(toolbar, text="❌ Annuler", 
              command=cancel_reservation_callback, 
              style='Danger.TButton').grid(row=0, column=5, padx=(0, 20))
    
    # Recherche
    ttk.Label(toolbar, text="🔍 Recherche:").grid(row=0, column=6, padx=(0, 5))
    search_entry = ttk.Entry(toolbar, textvariable=reservations_search_var, width=20)
    search_entry.grid(row=0, column=7, padx=(0, 5))
    search_entry.bind('<KeyRelease>', filter_reservations_callback)
    
    # Filtre par statut
    ttk.Label(toolbar, text="Statut:").grid(row=0, column=8, padx=(10, 5))
    filter_combo = ttk.Combobox(toolbar, textvariable=reservations_filter_var, width=15, state="readonly")
    filter_combo['values'] = ['Tous', 'Active', 'Annulée', 'Terminée', 'Expirée']
    filter_combo.grid(row=0, column=9, padx=(0, 5))
    filter_combo.bind('<<ComboboxSelected>>', filter_reservations_callback)
    
    # Tableau des réservations
    columns = ('ID', 'Passager', 'Vol', 'Route', 'Date Vol', 'Siège', 'Check-in', 'Statut')
    reservations_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
    reservations_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    # Configuration colonnes
    column_widths = {
        'ID': 100, 'Passager': 150, 'Vol': 80, 'Route': 120, 
        'Date Vol': 120, 'Siège': 60, 'Check-in': 80, 'Statut': 100
    }
    for col in columns:
        reservations_tree.heading(col, text=col)
        reservations_tree.column(col, width=column_widths.get(col, 100))
    
    # Scrollbars
    reservations_v_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=reservations_tree.yview)
    reservations_v_scrollbar.grid(row=1, column=1, sticky="ns")
    reservations_tree.configure(yscrollcommand=reservations_v_scrollbar.set)
    
    reservations_h_scrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=reservations_tree.xview)
    reservations_h_scrollbar.grid(row=2, column=0, sticky="ew")
    reservations_tree.configure(xscrollcommand=reservations_h_scrollbar.set)
    
    # Configuration responsive
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Charger les données initiales
    refresh_reservations_data(reservations_tree, data_manager)
    
    # Double-clic pour modifier
    reservations_tree.bind('<Double-1>', lambda e: edit_reservation(parent_frame, data_manager, reservations_tree))
    
    return reservations_tree


def new_reservation_dialog(parent, data_manager, reservations_tree):
    """Ouvre le dialogue de création de réservation"""
    dialog = ReservationDialog(parent, data_manager)
    if dialog.result:
        refresh_reservations_data(reservations_tree, data_manager)


def edit_reservation(parent, data_manager, reservations_tree):
    """Modifie la réservation sélectionnée"""
    selection = reservations_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une réservation à modifier.")
        return
    
    item = reservations_tree.item(selection[0])
    reservation_id = item['values'][0]
    
    # Trouver les données complètes de la réservation
    all_reservations = data_manager.get_reservations()
    reservation_data = None
    for reservation in all_reservations:
        if reservation.get('id_reservation', '').startswith(reservation_id.replace('...', '')):
            reservation_data = reservation
            break
    
    if not reservation_data:
        messagebox.showerror("Erreur", "Réservation non trouvée.")
        return
    
    dialog = ReservationDialog(parent, data_manager, reservation_data)
    if dialog.result:
        refresh_reservations_data(reservations_tree, data_manager)


def view_reservation_details(reservations_tree, data_manager):
    """Affiche les détails de la réservation sélectionnée"""
    selection = reservations_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une réservation.")
        return
    
    item = reservations_tree.item(selection[0])
    reservation_id = item['values'][0]
    
    # Trouver les données complètes
    all_reservations = data_manager.get_reservations()
    reservation_data = None
    for reservation in all_reservations:
        if reservation.get('id_reservation', '').startswith(reservation_id.replace('...', '')):
            reservation_data = reservation
            break
    
    if not reservation_data:
        messagebox.showerror("Erreur", "Réservation non trouvée.")
        return
    
    # Trouver les informations du passager et du vol
    passengers = data_manager.get_passengers()
    flights = data_manager.get_flights()
    
    passenger_info = "Non trouvé"
    for passenger in passengers:
        if passenger.get('id_passager') == reservation_data.get('passager_id'):
            passenger_info = f"{passenger.get('prenom', '')} {passenger.get('nom', '')} ({passenger.get('email', 'N/A')})"
            break
    
    flight_info = "Non trouvé"
    for flight in flights:
        if flight.get('numero_vol') == reservation_data.get('vol_numero'):
            try:
                if flight.get('heure_depart'):
                    if isinstance(flight['heure_depart'], str):
                        depart_time = datetime.fromisoformat(flight['heure_depart'])
                    else:
                        depart_time = flight['heure_depart']
                    date_str = depart_time.strftime("%Y-%m-%d à %H:%M")
                else:
                    date_str = "N/A"
            except:
                date_str = "N/A"
            
            flight_info = f"{flight.get('aeroport_depart', '')} → {flight.get('aeroport_arrivee', '')} le {date_str}"
            break
    
    # Construire les détails
    try:
        if reservation_data.get('date_creation'):
            creation_date = datetime.fromisoformat(reservation_data['date_creation']).strftime("%Y-%m-%d %H:%M")
        else:
            creation_date = "N/A"
    except:
        creation_date = "N/A"
    
    details = f"""Détails de la Réservation

ID: {reservation_data.get('id_reservation', 'N/A')}

Passager: {passenger_info}

Vol: {reservation_data.get('vol_numero', 'N/A')}
Route: {flight_info}

Siège: {reservation_data.get('siege_assigne', 'Non assigné')}
Check-in: {'Effectué' if reservation_data.get('checkin_effectue', False) else 'Non effectué'}
Statut: {reservation_data.get('statut', 'N/A').capitalize()}

Date de création: {creation_date}"""
    
    messagebox.showinfo("Détails de la Réservation", details)


def validate_reservation(data_manager, reservations_tree):
    """Valide/Confirme la réservation sélectionnée (marque comme terminée)"""
    selection = reservations_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une réservation à valider.")
        return
    
    item = reservations_tree.item(selection[0])
    reservation_id = item['values'][0]
    passenger_name = item['values'][1]
    flight_number = item['values'][2]
    current_status = item['values'][7]
    
    # Vérifier que la réservation est active
    if current_status != "Active":
        messagebox.showwarning("Validation impossible", 
                              f"Impossible de valider une réservation {current_status.lower()}.")
        return
    
    # Vérifier que le check-in a été effectué
    checkin_status = item['values'][6]
    if checkin_status == "✗":
        messagebox.showwarning("Check-in requis", 
                              "Le check-in doit être effectué avant de valider la réservation.")
        return
    
    if messagebox.askyesno("Confirmation", 
                          f"Valider la réservation ?\n\n"
                          f"Passager: {passenger_name}\n"
                          f"Vol: {flight_number}\n\n"
                          "Cette action marquera la réservation comme terminée."):
        
        # Marquer comme terminée
        all_reservations = data_manager.get_reservations()
        for reservation in all_reservations:
            if reservation.get('id_reservation', '').startswith(reservation_id.replace('...', '')):
                reservation['statut'] = 'terminee'
                reservation['updated_at'] = datetime.now().isoformat()
                break
        
        # Sauvegarder
        data = data_manager.load_data('reservations')
        data['reservations'] = all_reservations
        
        if data_manager.save_data('reservations', data):
            refresh_reservations_data(reservations_tree, data_manager)
            messagebox.showinfo("Succès", "Réservation validée avec succès.")
        else:
            messagebox.showerror("Erreur", "Impossible de valider la réservation.")


def cancel_reservation(data_manager, reservations_tree):
    """Annule la réservation sélectionnée"""
    selection = reservations_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une réservation à annuler.")
        return
    
    item = reservations_tree.item(selection[0])
    reservation_id = item['values'][0]
    passenger_name = item['values'][1]
    flight_number = item['values'][2]
    
    if messagebox.askyesno("Confirmation", 
                          f"Voulez-vous vraiment annuler la réservation ?\n\n"
                          f"Passager: {passenger_name}\n"
                          f"Vol: {flight_number}"):
        
        # Marquer comme annulée
        all_reservations = data_manager.get_reservations()
        for reservation in all_reservations:
            if reservation.get('id_reservation', '').startswith(reservation_id.replace('...', '')):
                reservation['statut'] = 'annulee'
                reservation['updated_at'] = datetime.now().isoformat()
                break
        
        # Sauvegarder
        data = data_manager.load_data('reservations')
        data['reservations'] = all_reservations
        
        if data_manager.save_data('reservations', data):
            refresh_reservations_data(reservations_tree, data_manager)
            messagebox.showinfo("Succès", "Réservation annulée avec succès.")
        else:
            messagebox.showerror("Erreur", "Impossible d'annuler la réservation.")


def toggle_checkin(data_manager, reservations_tree):
    """Effectue ou annule le check-in"""
    selection = reservations_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner une réservation.")
        return
    
    item = reservations_tree.item(selection[0])
    reservation_id = item['values'][0]
    current_checkin = item['values'][6]
    
    # Trouver la réservation et vérifier la disponibilité du check-in
    all_reservations = data_manager.get_reservations()
    reservation_data = None
    for reservation in all_reservations:
        if reservation.get('id_reservation', '').startswith(reservation_id.replace('...', '')):
            reservation_data = reservation
            break
    
    if not reservation_data:
        messagebox.showerror("Erreur", "Réservation non trouvée.")
        return
    
    # Vérifier si le check-in est disponible
    flights = data_manager.get_flights()
    flight_data = None
    for flight in flights:
        if flight.get('numero_vol') == reservation_data.get('vol_numero'):
            flight_data = flight
            break
    
    if not flight_data:
        messagebox.showerror("Erreur", "Vol non trouvé.")
        return
    
    # Vérifier la fenêtre de check-in
    try:
        if flight_data.get('heure_depart'):
            if isinstance(flight_data['heure_depart'], str):
                depart_time = datetime.fromisoformat(flight_data['heure_depart'])
            else:
                depart_time = flight_data['heure_depart']
            
            now = datetime.now()
            time_to_departure = depart_time - now
            
            # Check-in disponible 24h avant, fermé 30min avant
            checkin_available = (time_to_departure <= timedelta(hours=24) and 
                               time_to_departure >= timedelta(minutes=30))
            
            if not checkin_available and current_checkin == "✗":
                if time_to_departure > timedelta(hours=24):
                    messagebox.showwarning("Check-in indisponible", 
                                         "Le check-in n'est pas encore ouvert.\n"
                                         "Il sera disponible 24h avant le départ.")
                else:
                    messagebox.showwarning("Check-in fermé", 
                                         "Le check-in est fermé.\n"
                                         "Il se ferme 30 minutes avant le départ.")
                return
    except:
        messagebox.showerror("Erreur", "Impossible de vérifier l'heure de départ.")
        return
    
    # Vérifier qu'un siège est assigné pour le check-in
    if current_checkin == "✗" and not reservation_data.get('siege_assigne'):
        messagebox.showwarning("Siège requis", 
                              "Un siège doit être assigné avant le check-in.\n"
                              "Modifiez la réservation pour assigner un siège.")
        return
    
    # Effectuer ou annuler le check-in
    new_checkin_status = not reservation_data.get('checkin_effectue', False)
    action = "effectué" if new_checkin_status else "annulé"
    
    if messagebox.askyesno("Confirmation", f"Check-in {action} ?"):
        # Mettre à jour le check-in
        for reservation in all_reservations:
            if reservation.get('id_reservation', '').startswith(reservation_id.replace('...', '')):
                reservation['checkin_effectue'] = new_checkin_status
                reservation['updated_at'] = datetime.now().isoformat()
                break
        
        # Sauvegarder
        data = data_manager.load_data('reservations')
        data['reservations'] = all_reservations
        
        if data_manager.save_data('reservations', data):
            refresh_reservations_data(reservations_tree, data_manager)
            messagebox.showinfo("Succès", f"Check-in {action} avec succès.")
        else:
            messagebox.showerror("Erreur", f"Impossible de {action.replace('é', 'er')} le check-in.")


def filter_reservations(reservations_tree, data_manager, search_var, filter_var):
    """Filtre la liste des réservations"""
    search_text = search_var.get().lower()
    filter_status = filter_var.get()
    
    # Vider le tableau
    for item in reservations_tree.get_children():
        reservations_tree.delete(item)
    
    # Recharger avec filtres
    all_reservations = data_manager.get_reservations()
    passengers = data_manager.get_passengers()
    flights = data_manager.get_flights()
    
    for reservation in all_reservations:
        # Mapping du statut pour l'affichage
        status_mapping = {
            'active': 'Active',
            'annulee': 'Annulée',
            'terminee': 'Terminée',
            'expiree': 'Expirée'
        }
        
        reservation_status = status_mapping.get(reservation.get('statut', ''), 'Inconnu')
        
        # Filtrage par statut
        if filter_status != "Tous" and reservation_status != filter_status:
            continue
        
        # Trouver les informations du passager et du vol pour la recherche
        passenger_name = "Inconnu"
        for passenger in passengers:
            if passenger.get('id_passager') == reservation.get('passager_id'):
                passenger_name = f"{passenger.get('prenom', '')} {passenger.get('nom', '')}"
                break
        
        flight_route = "N/A"
        flight_date = "N/A"
        for flight in flights:
            if flight.get('numero_vol') == reservation.get('vol_numero'):
                flight_route = f"{flight.get('aeroport_depart', '')} → {flight.get('aeroport_arrivee', '')}"
                try:
                    if flight.get('heure_depart'):
                        if isinstance(flight['heure_depart'], str):
                            depart_time = datetime.fromisoformat(flight['heure_depart'])
                        else:
                            depart_time = flight['heure_depart']
                        flight_date = depart_time.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                break
        
        # Filtrage par recherche
        searchable_text = f"{passenger_name} {reservation.get('vol_numero', '')} {flight_route} {reservation.get('siege_assigne', '')}".lower()
        if search_text and search_text not in searchable_text:
            continue
        
        # Ajouter à l'affichage
        values = (
            reservation.get('id_reservation', '')[:8] + '...' if len(reservation.get('id_reservation', '')) > 8 else reservation.get('id_reservation', ''),
            passenger_name,
            reservation.get('vol_numero', ''),
            flight_route,
            flight_date,
            reservation.get('siege_assigne', 'N/A'),
            "✓" if reservation.get('checkin_effectue', False) else "✗",
            reservation_status
        )
        
        # Coloration selon le statut
        item_id = reservations_tree.insert('', 'end', values=values)
        if reservation_status == 'Annulée':
            reservations_tree.set(item_id, 'Statut', '❌ Annulée')
        elif reservation_status == 'Terminée':
            reservations_tree.set(item_id, 'Statut', '✅ Terminée')
        elif reservation.get('checkin_effectue', False):
            reservations_tree.set(item_id, 'Check-in', '✅ Fait')


def refresh_reservations_data(reservations_tree, data_manager):
    """Rafraîchit les données des réservations"""
    # Vider le tableau
    for item in reservations_tree.get_children():
        reservations_tree.delete(item)
    
    # Recharger les données
    all_reservations = data_manager.get_reservations()
    passengers = data_manager.get_passengers()
    flights = data_manager.get_flights()
    
    # Mapping des statuts pour l'affichage
    status_mapping = {
        'active': 'Active',
        'annulee': 'Annulée',
        'terminee': 'Terminée',
        'expiree': 'Expirée'
    }
    
    for reservation in all_reservations:
        reservation_status = status_mapping.get(reservation.get('statut', ''), 'Inconnu')
        
        # Trouver les informations du passager
        passenger_name = "Inconnu"
        for passenger in passengers:
            if passenger.get('id_passager') == reservation.get('passager_id'):
                passenger_name = f"{passenger.get('prenom', '')} {passenger.get('nom', '')}"
                break
        
        # Trouver les informations du vol
        flight_route = "N/A"
        flight_date = "N/A"
        for flight in flights:
            if flight.get('numero_vol') == reservation.get('vol_numero'):
                flight_route = f"{flight.get('aeroport_depart', '')} → {flight.get('aeroport_arrivee', '')}"
                try:
                    if flight.get('heure_depart'):
                        if isinstance(flight['heure_depart'], str):
                            depart_time = datetime.fromisoformat(flight['heure_depart'])
                        else:
                            depart_time = flight['heure_depart']
                        flight_date = depart_time.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                break
        
        values = (
            reservation.get('id_reservation', '')[:8] + '...' if len(reservation.get('id_reservation', '')) > 8 else reservation.get('id_reservation', ''),
            passenger_name,
            reservation.get('vol_numero', ''),
            flight_route,
            flight_date,
            reservation.get('siege_assigne', 'N/A'),
            "✓" if reservation.get('checkin_effectue', False) else "✗",
            reservation_status
        )
        
        # Coloration selon le statut
        item_id = reservations_tree.insert('', 'end', values=values)
        if reservation_status == 'Annulée':
            reservations_tree.set(item_id, 'Statut', '❌ Annulée')
        elif reservation_status == 'Terminée':
            reservations_tree.set(item_id, 'Statut', '✅ Terminée')
        elif reservation.get('checkin_effectue', False):
            reservations_tree.set(item_id, 'Check-in', '✅ Fait')