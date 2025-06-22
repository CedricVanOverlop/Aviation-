
from tkinter import ttk, messagebox
import uuid
import sys
import os
from datetime import datetime, timedelta
import math
import tkinter as tk

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.vol import Vol
from Core.aviation import Coordonnees, Aeroport, Avion
from Core.enums import StatutVol


class SafeFlightManager:
    """Gestionnaire sécurisé pour les opérations sur les vols - CORRECTION BUGS"""
    
    def __init__(self, data_manager, notification_center=None):
        self.data_manager = data_manager
        self.notification_center = notification_center
    
    def can_delete_flight(self, flight_number):
        """Vérifie si un vol peut être supprimé"""
        try:
            # Vérifier les réservations actives
            reservations = self.data_manager.get_reservations()
            active_reservations = []
            
            for reservation in reservations:
                if (reservation.get('vol_numero') == flight_number and 
                    reservation.get('statut') == 'active'):
                    active_reservations.append(reservation)
            
            if active_reservations:
                return False, f"Vol a {len(active_reservations)} réservation(s) active(s)"
            
            return True, "Suppression autorisée"
            
        except Exception as e:
            return False, f"Erreur vérification: {e}"
    
    def safe_delete_flight(self, flight_number):
        """CORRECTION BUG: Suppression sécurisée d'un vol"""
        try:
            # Vérifier si la suppression est possible
            can_delete, reason = self.can_delete_flight(flight_number)
            if not can_delete:
                return False, reason
            
            # Charger les données
            data = self.data_manager.load_data('flights')
            if 'flights' not in data:
                return False, "Aucune donnée de vol trouvée"
            
            # Trouver et supprimer le vol
            original_count = len(data['flights'])
            data['flights'] = [f for f in data['flights'] if f.get('numero_vol') != flight_number]
            
            if len(data['flights']) == original_count:
                return False, f"Vol {flight_number} non trouvé"
            
            # Sauvegarder
            success = self.data_manager.save_data('flights', data)
            
            if success:
                message = f"Vol {flight_number} supprimé avec succès"
                if self.notification_center:
                    self.notification_center.show_success(message)
                return True, message
            else:
                return False, "Erreur lors de la sauvegarde"
                
        except Exception as e:
            error_msg = f"Erreur suppression vol: {e}"
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            return False, error_msg
    
    def safe_cancel_flight(self, flight_number):
        """CORRECTION BUG: Annulation sécurisée d'un vol"""
        try:
            # Charger les données
            data = self.data_manager.load_data('flights')
            if 'flights' not in data:
                return False, "Aucune donnée de vol trouvée"
            
            # Trouver et modifier le vol
            flight_index = -1
            for i, flight in enumerate(data['flights']):
                if flight.get('numero_vol') == flight_number:
                    flight_index = i
                    break
            
            if flight_index == -1:
                return False, f"Vol {flight_number} non trouvé"
            
            # Annuler le vol
            data['flights'][flight_index]['statut'] = 'annule'
            data['flights'][flight_index]['updated_at'] = datetime.now().isoformat()
            
            # Sauvegarder
            success = self.data_manager.save_data('flights', data)
            
            if success:
                # Annuler les réservations associées
                self._cancel_reservations(flight_number)
                
                message = f"Vol {flight_number} annulé"
                if self.notification_center:
                    self.notification_center.show_success(message)
                return True, message
            else:
                return False, "Erreur lors de la sauvegarde"
                
        except Exception as e:
            error_msg = f"Erreur annulation vol: {e}"
            if self.notification_center:
                self.notification_center.show_error(error_msg)
            return False, error_msg
    
    def _cancel_reservations(self, flight_number):
        """Annule les réservations associées à un vol"""
        try:
            data = self.data_manager.load_data('reservations')
            if 'reservations' not in data:
                return
            
            cancelled_count = 0
            for i, reservation in enumerate(data['reservations']):
                if (reservation.get('vol_numero') == flight_number and 
                    reservation.get('statut') == 'active'):
                    data['reservations'][i]['statut'] = 'annulee'
                    data['reservations'][i]['updated_at'] = datetime.now().isoformat()
                    cancelled_count += 1
            
            if cancelled_count > 0:
                self.data_manager.save_data('reservations', data)
                print(f"✅ {cancelled_count} réservations annulées pour vol {flight_number}")
                
        except Exception as e:
            print(f"❌ Erreur annulation réservations: {e}")


class FlightDialog:
    """Dialogue pour créer ou modifier un vol avec corrections de bugs"""
    
    def __init__(self, parent, data_manager, flight_data=None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Fenêtre parente
            data_manager: Gestionnaire de données
            flight_data: Données du vol existant (pour modification)
        """
        self.parent = parent
        self.data_manager = data_manager
        self.flight_data = flight_data
        self.is_editing = flight_data is not None
        self.result = None
        
        # Créer la fenêtre dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modification du Vol" if self.is_editing else "Création d'un Nouveau Vol")
        self.dialog.geometry("750x900")
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
        self.numero_vol_entry.focus()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (900 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables pour les champs"""
        self.numero_vol_var = tk.StringVar()
        self.aeroport_depart_var = tk.StringVar()
        self.aeroport_arrivee_var = tk.StringVar()
        self.avion_var = tk.StringVar()
        self.date_depart_var = tk.StringVar()
        self.heure_depart_var = tk.StringVar()
        self.heure_arrivee_var = tk.StringVar()
        self.statut_var = tk.StringVar()
        
        # Personnel assigné
        self.pilote_var = tk.StringVar()
        self.copilote_var = tk.StringVar()
        self.personnel_navigant_vars = []  # Liste des variables pour le personnel navigant
        
        # Informations calculées
        self.distance_var = tk.StringVar(value="0 km")
        self.duree_var = tk.StringVar(value="0h00")
        self.autonomie_ok_var = tk.StringVar(value="N/A")
        
        # Dates par défaut
        tomorrow = datetime.now() + timedelta(days=1)
        self.date_depart_var.set(tomorrow.strftime("%Y-%m-%d"))
        self.heure_depart_var.set("08:00")
        self.heure_arrivee_var.set("10:00")
    
    def load_reference_data(self):
        """Charge les données de référence"""
        try:
            self.airports = self.data_manager.get_airports()
            self.aircraft = self.data_manager.get_aircraft()
            self.personnel = self.data_manager.get_personnel()
            
            # Préparer les listes pour les combobox
            self.airport_choices = [f"{airport['code_iata']} - {airport['nom']} ({airport['ville']})" 
                                   for airport in self.airports]
            
            # Avions disponibles (opérationnels)
            self.aircraft_choices = []
            for aircraft in self.aircraft:
                if aircraft.get('etat') in ['operationnel', 'au_sol']:
                    choice = f"{aircraft['num_id']} - {aircraft['modele']} ({aircraft['capacite']} pax, {aircraft['autonomie']} km)"
                    self.aircraft_choices.append(choice)
            
            # Personnel par catégorie
            self.pilotes_choices = []
            self.copilotes_choices = []
            self.personnel_navigant_choices = []
            
            for person in self.personnel:
                if not person.get('disponible', True):
                    continue  # Ignorer le personnel non disponible
                    
                name = f"{person.get('prenom', '')} {person.get('nom', '')} (ID: {person.get('id_employe', '')[:8]})"
                person_type = person.get('type_personnel', '')
                
                if person_type == 'pilote':
                    self.pilotes_choices.append(name)
                elif person_type == 'copilote':
                    self.copilotes_choices.append(name)
                elif person_type in ['hotesse', 'steward']:
                    self.personnel_navigant_choices.append(name)
            
            self.statut_choices = ['Programmé', 'En attente', 'En vol', 'Atterri', 'Retardé', 'Annulé', 'Terminé']
            
        except Exception as e:
            print(f"❌ Erreur chargement données référence: {e}")
            # Données par défaut si erreur
            self.airports = []
            self.aircraft = []
            self.personnel = []
            self.airport_choices = []
            self.aircraft_choices = []
            self.pilotes_choices = []
            self.copilotes_choices = []
            self.personnel_navigant_choices = []
            self.statut_choices = ['Programmé', 'En attente', 'En vol', 'Atterri', 'Retardé', 'Annulé', 'Terminé']
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal avec défilement
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Titre
        title_label = ttk.Label(scrollable_frame, 
                               text="Modification du Vol" if self.is_editing else "Création d'un Nouveau Vol",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Section informations de base
        self.create_basic_info_section(scrollable_frame)
        
        # Section horaires
        self.create_schedule_section(scrollable_frame)
        
        # Section avion et calculs
        self.create_aircraft_section(scrollable_frame)
        
        # Section personnel
        self.create_crew_section(scrollable_frame)
        
        # Section statut
        self.create_status_section(scrollable_frame)
        
        # Boutons
        self.create_buttons(scrollable_frame)
    
    def create_basic_info_section(self, parent):
        """Crée la section des informations de base"""
        basic_frame = ttk.LabelFrame(parent, text="✈️ Informations de Base", padding=15)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        basic_frame.grid_columnconfigure(1, weight=1)
        
        # Numéro de vol
        ttk.Label(basic_frame, text="Numéro de vol*:").grid(row=0, column=0, sticky="w", pady=5)
        self.numero_vol_entry = ttk.Entry(basic_frame, textvariable=self.numero_vol_var, width=20)
        self.numero_vol_entry.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(basic_frame, text="Ex: AF001, BA123", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Aéroport de départ
        ttk.Label(basic_frame, text="Départ*:").grid(row=1, column=0, sticky="w", pady=5)
        self.depart_combo = ttk.Combobox(basic_frame, textvariable=self.aeroport_depart_var,
                                        values=self.airport_choices, width=50)
        self.depart_combo.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.depart_combo.bind('<<ComboboxSelected>>', self.calculate_flight_info)
        
        # Aéroport d'arrivée
        ttk.Label(basic_frame, text="Arrivée*:").grid(row=2, column=0, sticky="w", pady=5)
        self.arrivee_combo = ttk.Combobox(basic_frame, textvariable=self.aeroport_arrivee_var,
                                         values=self.airport_choices, width=50)
        self.arrivee_combo.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.arrivee_combo.bind('<<ComboboxSelected>>', self.calculate_flight_info)
    
    def create_schedule_section(self, parent):
        """Crée la section des horaires"""
        schedule_frame = ttk.LabelFrame(parent, text="🕐 Horaires", padding=15)
        schedule_frame.pack(fill="x", pady=(0, 10))
        
        schedule_frame.grid_columnconfigure(1, weight=1)
        
        # Date de départ
        ttk.Label(schedule_frame, text="Date de départ*:").grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = ttk.Entry(schedule_frame, textvariable=self.date_depart_var, width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(schedule_frame, text="Format: YYYY-MM-DD", foreground="gray").grid(row=0, column=2, sticky="w", padx=5)
        
        # Heure de départ
        ttk.Label(schedule_frame, text="Heure de départ*:").grid(row=1, column=0, sticky="w", pady=5)
        self.heure_depart_entry = ttk.Entry(schedule_frame, textvariable=self.heure_depart_var, width=10)
        self.heure_depart_entry.grid(row=1, column=1, sticky="w", padx=(10, 5), pady=5)
        self.heure_depart_entry.bind('<KeyRelease>', self.calculate_arrival_time)
        ttk.Label(schedule_frame, text="Format: HH:MM", foreground="gray").grid(row=1, column=2, sticky="w", padx=5)
        
        # Heure d'arrivée
        ttk.Label(schedule_frame, text="Heure d'arrivée*:").grid(row=2, column=0, sticky="w", pady=5)
        self.heure_arrivee_entry = ttk.Entry(schedule_frame, textvariable=self.heure_arrivee_var, width=10)
        self.heure_arrivee_entry.grid(row=2, column=1, sticky="w", padx=(10, 5), pady=5)
        ttk.Label(schedule_frame, text="Calculée automatiquement", foreground="gray").grid(row=2, column=2, sticky="w", padx=5)
    
    def create_aircraft_section(self, parent):
        """Crée la section avion et calculs"""
        aircraft_frame = ttk.LabelFrame(parent, text="🛩️ Avion et Calculs", padding=15)
        aircraft_frame.pack(fill="x", pady=(0, 10))
        
        aircraft_frame.grid_columnconfigure(1, weight=1)
        
        # Avion assigné
        ttk.Label(aircraft_frame, text="Avion*:").grid(row=0, column=0, sticky="w", pady=5)
        self.avion_combo = ttk.Combobox(aircraft_frame, textvariable=self.avion_var,
                                       values=self.aircraft_choices, width=50)
        self.avion_combo.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.avion_combo.bind('<<ComboboxSelected>>', self.check_aircraft_autonomy)
        
        # Informations calculées
        info_frame = ttk.Frame(aircraft_frame)
        info_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Distance
        distance_card = ttk.Frame(info_frame, relief="solid", borderwidth=1)
        distance_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(distance_card, text="📏 Distance", font=('Arial', 10, 'bold')).pack(pady=2)
        self.distance_label = ttk.Label(distance_card, textvariable=self.distance_var, font=('Arial', 12, 'bold'), 
                 foreground="blue")
        self.distance_label.pack(pady=2)
        
        # Durée
        duree_card = ttk.Frame(info_frame, relief="solid", borderwidth=1)
        duree_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(duree_card, text="⏱️ Durée", font=('Arial', 10, 'bold')).pack(pady=2)
        self.duree_label = ttk.Label(duree_card, textvariable=self.duree_var, font=('Arial', 12, 'bold'), 
                 foreground="blue")
        self.duree_label.pack(pady=2)
        
        # Autonomie
        autonomie_card = ttk.Frame(info_frame, relief="solid", borderwidth=1)
        autonomie_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Label(autonomie_card, text="⛽ Autonomie", font=('Arial', 10, 'bold')).pack(pady=2)
        self.autonomie_label = ttk.Label(autonomie_card, textvariable=self.autonomie_ok_var, font=('Arial', 12, 'bold'))
        self.autonomie_label.pack(pady=2)
    
    def create_crew_section(self, parent):
        """Crée la section du personnel"""
        crew_frame = ttk.LabelFrame(parent, text="👥 Équipage", padding=15)
        crew_frame.pack(fill="x", pady=(0, 10))
        
        crew_frame.grid_columnconfigure(1, weight=1)
        
        # Pilote
        ttk.Label(crew_frame, text="Pilote*:").grid(row=0, column=0, sticky="w", pady=5)
        self.pilote_combo = ttk.Combobox(crew_frame, textvariable=self.pilote_var,
                                        values=self.pilotes_choices, width=40)
        self.pilote_combo.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Copilote
        ttk.Label(crew_frame, text="Copilote:").grid(row=1, column=0, sticky="w", pady=5)
        self.copilote_combo = ttk.Combobox(crew_frame, textvariable=self.copilote_var,
                                          values=self.copilotes_choices, width=40)
        self.copilote_combo.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Personnel navigant
        ttk.Label(crew_frame, text="Personnel navigant:", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        # Frame pour le personnel navigant (jusqu'à 4 membres)
        self.navigant_frame = ttk.Frame(crew_frame)
        self.navigant_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(10, 0))
        self.navigant_frame.grid_columnconfigure((1, 3), weight=1)
        
        # Créer 4 combobox pour le personnel navigant
        for i in range(4):
            var = tk.StringVar()
            self.personnel_navigant_vars.append(var)
            
            ttk.Label(self.navigant_frame, text=f"Membre {i+1}:").grid(row=i//2, column=(i%2)*2, sticky="w", pady=2, padx=(0, 5))
            combo = ttk.Combobox(self.navigant_frame, textvariable=var,
                                values=self.personnel_navigant_choices, width=25)
            combo.grid(row=i//2, column=(i%2)*2+1, sticky="ew", pady=2, padx=(0, 10))
    
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
        self.statut_var.set("Programmé")  # Valeur par défaut
    
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
                             command=self.save_flight)
        btn_save.pack(side="right")
    
    def calculate_flight_info(self, event=None):
        """Calcule les informations de vol (distance, durée)"""
        depart_selection = self.aeroport_depart_var.get()
        arrivee_selection = self.aeroport_arrivee_var.get()
        
        if not depart_selection or not arrivee_selection or ' - ' not in depart_selection or ' - ' not in arrivee_selection:
            return
        
        try:
            # Extraire les codes IATA
            depart_code = depart_selection.split(' - ')[0]
            arrivee_code = arrivee_selection.split(' - ')[0]
            
            if depart_code == arrivee_code:
                self.distance_var.set("0 km")
                self.duree_var.set("0h00")
                return
            
            # Trouver les aéroports correspondants
            depart_airport = None
            arrivee_airport = None
            
            for airport in self.airports:
                if airport['code_iata'] == depart_code:
                    depart_airport = airport
                elif airport['code_iata'] == arrivee_code:
                    arrivee_airport = airport
            
            if not depart_airport or not arrivee_airport:
                return
            
            # Calculer la distance avec la formule de Haversine
            distance = self.calculate_distance(
                depart_airport['coordonnees'],
                arrivee_airport['coordonnees']
            )
            
            self.distance_var.set(f"{distance:.0f} km")
            
            # Calculer la durée estimée (vitesse moyenne 800 km/h)
            vitesse_moyenne = 800  # km/h
            duree_heures = distance / vitesse_moyenne
            heures = int(duree_heures)
            minutes = int((duree_heures - heures) * 60)
            
            self.duree_var.set(f"{heures}h{minutes:02d}")
            
            # Calculer automatiquement l'heure d'arrivée
            self.calculate_arrival_time()
            
            # Vérifier l'autonomie si un avion est sélectionné
            self.check_aircraft_autonomy()
            
        except Exception as e:
            print(f"Erreur calcul vol: {e}")
    
    def calculate_distance(self, coord1, coord2):
        """Calcule la distance entre deux coordonnées avec la formule de Haversine"""
        R = 6371  # Rayon de la Terre en km
        
        lat1, lon1 = math.radians(coord1['latitude']), math.radians(coord1['longitude'])
        lat2, lon2 = math.radians(coord2['latitude']), math.radians(coord2['longitude'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        distance = R * 2 * math.asin(math.sqrt(a))
        
        return distance
    
    def calculate_arrival_time(self, event=None):
        """Calcule l'heure d'arrivée basée sur l'heure de départ et la durée"""
        try:
            heure_depart = self.heure_depart_var.get()
            duree_str = self.duree_var.get()
            
            if not heure_depart or not duree_str or duree_str == "0h00":
                return
            
            # Parser l'heure de départ
            if ':' not in heure_depart:
                return
            
            depart_parts = heure_depart.split(':')
            if len(depart_parts) != 2:
                return
                
            heures_depart = int(depart_parts[0])
            minutes_depart = int(depart_parts[1])
            
            # Parser la durée
            if 'h' not in duree_str:
                return
                
            duree_parts = duree_str.replace('h', ':').split(':')
            if len(duree_parts) != 2:
                return
                
            heures_duree = int(duree_parts[0])
            minutes_duree = int(duree_parts[1])

            # Calculer l'heure d'arrivée
            total_minutes = (heures_depart * 60 + minutes_depart) + (heures_duree * 60 + minutes_duree)
            heures_arrivee = (total_minutes // 60) % 24
            minutes_arrivee = total_minutes % 60
            
            self.heure_arrivee_var.set(f"{heures_arrivee:02d}:{minutes_arrivee:02d}")
            
        except (ValueError, IndexError):
            pass  # Ignore les erreurs de parsing
    
    def check_aircraft_autonomy(self, event=None):
        """Vérifie l'autonomie de l'avion sélectionné"""
        avion_selection = self.avion_var.get()
        distance_str = self.distance_var.get()
        
        if not avion_selection or not distance_str or ' - ' not in avion_selection:
            self.autonomie_ok_var.set("N/A")
            self.autonomie_label.configure(foreground="gray")
            return
        
        try:
            # Extraire l'ID de l'avion
            avion_id = avion_selection.split(' - ')[0]
            
            # Trouver l'avion correspondant
            avion_data = None
            for aircraft in self.aircraft:
                if aircraft['num_id'] == avion_id:
                    avion_data = aircraft
                    break
            
            if not avion_data:
                return
            
            # Extraire la distance
            distance = float(distance_str.replace(' km', ''))
            autonomie = avion_data.get('autonomie', 0)
            
            # Calculer avec marge de sécurité (20%)
            distance_securite = distance * 1.2
            
            if distance_securite <= autonomie:
                self.autonomie_ok_var.set("✓ OK")
                self.autonomie_label.configure(foreground="green")
            else:
                self.autonomie_ok_var.set("✗ Insuffisante")
                self.autonomie_label.configure(foreground="red")
                
        except (ValueError, IndexError):
            self.autonomie_ok_var.set("Erreur")
            self.autonomie_label.configure(foreground="orange")
    
    def populate_fields(self):
        """Pré-remplit les champs pour la modification"""
        if not self.flight_data:
            return
        
        try:
            self.numero_vol_var.set(self.flight_data.get('numero_vol', ''))
            
            # Aéroports (chercher dans la liste)
            depart = self.flight_data.get('aeroport_depart', '')
            arrivee = self.flight_data.get('aeroport_arrivee', '')
            
            for choice in self.airport_choices:
                if depart in choice:
                    self.aeroport_depart_var.set(choice)
                if arrivee in choice:
                    self.aeroport_arrivee_var.set(choice)
            
            # Avion
            avion = self.flight_data.get('avion_utilise', '')
            for choice in self.aircraft_choices:
                if avion in choice:
                    self.avion_var.set(choice)
                    break
            
            # Dates et heures avec parsing robuste
            try:
                if self.flight_data.get('heure_depart'):
                    depart_time = self.parse_datetime_safe(self.flight_data['heure_depart'])
                    if depart_time:
                        self.date_depart_var.set(depart_time.strftime("%Y-%m-%d"))
                        self.heure_depart_var.set(depart_time.strftime("%H:%M"))
                
                if self.flight_data.get('heure_arrivee_prevue'):
                    arrivee_time = self.parse_datetime_safe(self.flight_data['heure_arrivee_prevue'])
                    if arrivee_time:
                        self.heure_arrivee_var.set(arrivee_time.strftime("%H:%M"))
            except Exception as e:
                print(f"❌ Erreur parsing dates: {e}")
            
            # Statut
            status_mapping = {
                'programme': 'Programmé',
                'en_attente': 'En attente',
                'en_vol': 'En vol',
                'atterri': 'Atterri',
                'retarde': 'Retardé',
                'annule': 'Annulé',
                'termine': 'Terminé'
            }
            current_status = self.flight_data.get('statut', 'programme')
            self.statut_var.set(status_mapping.get(current_status, 'Programmé'))
            
            # Personnel
            self.pilote_var.set(self.flight_data.get('pilote', ''))
            self.copilote_var.set(self.flight_data.get('copilote', ''))
            
            # Personnel navigant
            personnel_navigant = self.flight_data.get('personnel_navigant', [])
            for i, member in enumerate(personnel_navigant[:4]):
                if i < len(self.personnel_navigant_vars):
                    self.personnel_navigant_vars[i].set(member)
            
            # Recalculer les informations
            self.calculate_flight_info()
            
        except Exception as e:
            print(f"❌ Erreur population champs: {e}")
    
    def parse_datetime_safe(self, datetime_value):
        """Parse robuste d'une date/heure"""
        if not datetime_value:
            return None
        
        try:
            if isinstance(datetime_value, str):
                return datetime.fromisoformat(datetime_value)
            elif isinstance(datetime_value, datetime):
                return datetime_value
        except:
            pass
        
        return None
    
    def validate_fields(self):
        """Valide tous les champs obligatoires"""
        errors = []
        
        # Vérifications de base
        if not self.numero_vol_var.get().strip():
            errors.append("Le numéro de vol est obligatoire")
        
        if not self.aeroport_depart_var.get().strip():
            errors.append("L'aéroport de départ est obligatoire")
        
        if not self.aeroport_arrivee_var.get().strip():
            errors.append("L'aéroport d'arrivée est obligatoire")

        if not self.avion_var.get().strip():
            errors.append("L'avion est obligatoire")
        
        if not self.pilote_var.get().strip():
            errors.append("Le pilote est obligatoire")
        
        # Validation des dates et heures
        try:
            datetime.strptime(self.date_depart_var.get(), "%Y-%m-%d")
        except ValueError:
            errors.append("Format de date invalide (YYYY-MM-DD)")
        
        try:
            datetime.strptime(self.heure_depart_var.get(), "%H:%M")
        except ValueError:
            errors.append("Format d'heure de départ invalide (HH:MM)")
        
        try:
            datetime.strptime(self.heure_arrivee_var.get(), "%H:%M")
        except ValueError:
            errors.append("Format d'heure d'arrivée invalide (HH:MM)")
        
        # Vérification que départ != arrivée
        if self.aeroport_depart_var.get() == self.aeroport_arrivee_var.get():
            errors.append("L'aéroport de départ et d'arrivée doivent être différents")
        
        # Vérification autonomie
        if self.autonomie_ok_var.get() == "✗ Insuffisante":
            errors.append("L'autonomie de l'avion est insuffisante pour ce vol")
        
        # Vérification unicité du numéro de vol (sauf en modification)
        if not self.is_editing:
            vol_numero = self.numero_vol_var.get().strip()
            existing_flights = self.data_manager.get_flights()
            if any(f.get('numero_vol') == vol_numero for f in existing_flights):
                errors.append(f"Un vol avec le numéro '{vol_numero}' existe déjà")
        
        return errors
    
    def save_flight(self):
        """CORRECTION BUG: Sauvegarde sécurisée du vol"""
        # Validation
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Erreurs de Validation", 
                               "Veuillez corriger les erreurs suivantes:\n\n" + 
                               "\n".join(f"• {error}" for error in errors))
            return
        
        try:
            # Construction de la date/heure de départ complète
            date_str = self.date_depart_var.get()
            heure_depart_str = self.heure_depart_var.get()
            heure_arrivee_str = self.heure_arrivee_var.get()
            
            # Créer les objets datetime
            depart_datetime = datetime.strptime(f"{date_str} {heure_depart_str}", "%Y-%m-%d %H:%M")
            
            # Pour l'arrivée, gérer le cas où c'est le lendemain
            arrivee_datetime = datetime.strptime(f"{date_str} {heure_arrivee_str}", "%Y-%m-%d %H:%M")
            if arrivee_datetime <= depart_datetime:
                arrivee_datetime += timedelta(days=1)
            
            # Mapping des statuts
            status_mapping = {
                'Programmé': 'programme',
                'En attente': 'en_attente',
                'En vol': 'en_vol',
                'Atterri': 'atterri',
                'Retardé': 'retarde',
                'Annulé': 'annule',
                'Terminé': 'termine'
            }
            
            # Personnel navigant sélectionné
            personnel_navigant = [var.get() for var in self.personnel_navigant_vars if var.get().strip()]
            
            # Construire les données du vol
            flight_data = {
                'numero_vol': self.numero_vol_var.get().strip(),
                'aeroport_depart': self.aeroport_depart_var.get().split(' - ')[0],  # Code IATA
                'aeroport_arrivee': self.aeroport_arrivee_var.get().split(' - ')[0],  # Code IATA
                'avion_utilise': self.avion_var.get().split(' - ')[0],  # ID de l'avion
                'heure_depart': depart_datetime.isoformat(),
                'heure_arrivee_prevue': arrivee_datetime.isoformat(),
                'statut': status_mapping.get(self.statut_var.get(), 'programme'),
                'pilote': self.pilote_var.get(),
                'copilote': self.copilote_var.get() if self.copilote_var.get().strip() else None,
                'personnel_navigant': personnel_navigant,
                'distance_km': float(self.distance_var.get().replace(' km', '')),
                'duree_estimee': self.duree_var.get(),
                'autonomie_suffisante': self.autonomie_ok_var.get() == "✓ OK"
            }
            
            # CORRECTION BUG: Sauvegarde sécurisée
            if self.is_editing:
                success = self.safe_update_flight(flight_data)
                action = "modifié"
            else:
                success = self.safe_add_flight(flight_data)
                action = "créé"
            
            if success:
                self.result = flight_data
                messagebox.showinfo("Succès", f"Vol {action} avec succès!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Erreur", f"Impossible de {action.replace('é', 'er')} le vol.")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
            print(f"❌ Erreur sauvegarde vol: {e}")
    
    def safe_add_flight(self, flight_data):
        """CORRECTION BUG: Ajout sécurisé de vol"""
        try:
            # Charger les données existantes
            data = self.data_manager.load_data('flights')
            if 'flights' not in data:
                data['flights'] = []
            
            # Vérifier une dernière fois l'unicité
            if any(f.get('numero_vol') == flight_data['numero_vol'] for f in data['flights']):
                print(f"❌ Vol {flight_data['numero_vol']} existe déjà")
                return False
            
            # Ajouter les métadonnées
            flight_data['created_at'] = datetime.now().isoformat()
            flight_data['updated_at'] = datetime.now().isoformat()
            
            # Ajouter le vol
            data['flights'].append(flight_data)
            
            # Sauvegarder
            success = self.data_manager.save_data('flights', data)
            print(f"✅ Vol {flight_data['numero_vol']} ajouté" if success else f"❌ Erreur sauvegarde vol {flight_data['numero_vol']}")
            return success
            
        except Exception as e:
            print(f"❌ Erreur ajout vol: {e}")
            return False
    
    def safe_update_flight(self, flight_data):
        """CORRECTION BUG: Mise à jour sécurisée de vol"""
        try:
            # Charger les données existantes
            data = self.data_manager.load_data('flights')
            if 'flights' not in data:
                return False
            
            # Trouver le vol à modifier
            flight_index = -1
            original_number = self.flight_data.get('numero_vol')
            
            for i, flight in enumerate(data['flights']):
                if flight.get('numero_vol') == original_number:
                    flight_index = i
                    break
            
            if flight_index == -1:
                print(f"❌ Vol {original_number} non trouvé")
                return False
            
            # Conserver certaines données
            original_flight = data['flights'][flight_index]
            flight_data['created_at'] = original_flight.get('created_at', datetime.now().isoformat())
            flight_data['updated_at'] = datetime.now().isoformat()
            
            # Mettre à jour
            data['flights'][flight_index] = flight_data
            
            # Sauvegarder
            success = self.data_manager.save_data('flights', data)
            print(f"✅ Vol {flight_data['numero_vol']} modifié" if success else f"❌ Erreur modification vol {flight_data['numero_vol']}")
            return success
            
        except Exception as e:
            print(f"❌ Erreur modification vol: {e}")
            return False
    
    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy()


def create_flights_tab_content(parent_frame, data_manager):
    """Crée le contenu de l'onglet vols"""
    
    # Variables pour la recherche et le filtrage
    flights_search_var = tk.StringVar()
    flights_filter_var = tk.StringVar(value="Tous")
    
    # Gestionnaire sécurisé
    safe_manager = SafeFlightManager(data_manager)
    
    # Barre d'outils
    toolbar = ttk.Frame(parent_frame)
    toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    
    # Variables pour stocker les références aux widgets
    flights_tree = None
    
    def new_flight_callback():
        new_flight_dialog(parent_frame, data_manager, flights_tree)
    
    def edit_flight_callback():
        edit_flight(parent_frame, data_manager, flights_tree)
    
    def view_flight_callback():
        view_flight_details(flights_tree, data_manager)
    
    def delete_flight_callback():
        delete_flight(safe_manager, flights_tree)
    
    def filter_flights_callback(event=None):
        filter_flights(flights_tree, data_manager, flights_search_var, flights_filter_var)
    
    ttk.Button(toolbar, text="➕ Nouveau Vol", 
              command=new_flight_callback, 
              style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
    ttk.Button(toolbar, text="✏️ Modifier", 
              command=edit_flight_callback).grid(row=0, column=1, padx=(0, 5))
    ttk.Button(toolbar, text="👁️ Voir Détails", 
              command=view_flight_callback).grid(row=0, column=2, padx=(0, 5))
    ttk.Button(toolbar, text="🗑️ Supprimer/Annuler", 
              command=delete_flight_callback, 
              style='Danger.TButton').grid(row=0, column=3, padx=(0, 20))
    
    # Recherche
    ttk.Label(toolbar, text="🔍 Recherche:").grid(row=0, column=4, padx=(0, 5))
    search_entry = ttk.Entry(toolbar, textvariable=flights_search_var, width=20)
    search_entry.grid(row=0, column=5, padx=(0, 5))
    search_entry.bind('<KeyRelease>', filter_flights_callback)
    
    # Filtre par statut
    ttk.Label(toolbar, text="Statut:").grid(row=0, column=6, padx=(10, 5))
    filter_combo = ttk.Combobox(toolbar, textvariable=flights_filter_var, width=15, state="readonly")
    filter_combo['values'] = ['Tous', 'Programmé', 'En attente', 'En vol', 'Atterri', 'Retardé', 'Annulé', 'Terminé']
    filter_combo.grid(row=0, column=7, padx=(0, 5))
    filter_combo.bind('<<ComboboxSelected>>', filter_flights_callback)
    
    # Tableau des vols
    columns = ('Vol', 'Départ', 'Arrivée', 'Date', 'Heure Départ', 'Heure Arrivée', 'Avion', 'Statut')
    flights_tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
    flights_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    # Configuration colonnes
    column_widths = {
        'Vol': 80, 'Départ': 80, 'Arrivée': 80, 'Date': 100, 
        'Heure Départ': 100, 'Heure Arrivée': 100, 'Avion': 120, 'Statut': 100
    }
    for col in columns:
        flights_tree.heading(col, text=col)
        flights_tree.column(col, width=column_widths.get(col, 100))
    
    # Scrollbars
    flights_v_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=flights_tree.yview)
    flights_v_scrollbar.grid(row=1, column=1, sticky="ns")
    flights_tree.configure(yscrollcommand=flights_v_scrollbar.set)
    
    flights_h_scrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=flights_tree.xview)
    flights_h_scrollbar.grid(row=2, column=0, sticky="ew")
    flights_tree.configure(xscrollcommand=flights_h_scrollbar.set)
    
    # Configuration responsive
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)
    
    # Charger les données initiales
    refresh_flights_data(flights_tree, data_manager)
    
    # Double-clic pour modifier
    flights_tree.bind('<Double-1>', lambda e: edit_flight(parent_frame, data_manager, flights_tree))
    
    return flights_tree


def new_flight_dialog(parent, data_manager, flights_tree):
    """Ouvre le dialogue de création de vol"""
    dialog = FlightDialog(parent, data_manager)
    if dialog.result:
        refresh_flights_data(flights_tree, data_manager)


def edit_flight(parent, data_manager, flights_tree):
    """CORRECTION BUG: Modifie le vol sélectionné avec recherche robuste"""
    selection = flights_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un vol à modifier.")
        return
    
    try:
        item = flights_tree.item(selection[0])
        flight_number = item['values'][0]  # Numéro de vol depuis le tableau
        
        print(f"🔧 Recherche vol pour modification: {flight_number}")
        
        # CORRECTION BUG: Recherche robuste du vol
        all_flights = data_manager.get_flights()
        flight_data = None
        
        for flight in all_flights:
            if flight.get('numero_vol') == flight_number:
                flight_data = flight
                break
        
        if not flight_data:
            messagebox.showerror("Erreur", f"Vol '{flight_number}' non trouvé.")
            return
        
        # Vérifier si le vol peut être modifié
        current_status = flight_data.get('statut', 'programme')
        if current_status in ['en_vol', 'atterri', 'termine']:
            messagebox.showwarning("Modification impossible", 
                                  f"Impossible de modifier un vol {current_status}.")
            return
        
        # Ouvrir le dialogue de modification
        dialog = FlightDialog(parent, data_manager, flight_data)
        if dialog.result:
            refresh_flights_data(flights_tree, data_manager)
            messagebox.showinfo("Succès", f"Vol {flight_number} modifié avec succès!")
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")


def delete_flight(safe_manager, flights_tree):
    """CORRECTION BUG: Suppression/annulation intelligente de vol"""
    selection = flights_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un vol.")
        return
    
    try:
        item = flights_tree.item(selection[0])
        flight_number = item['values'][0]
        current_status = item['values'][7]
        
        # Vérifier les dépendances
        can_delete, reason = safe_manager.can_delete_flight(flight_number)
        
        if current_status in ['Programmé', 'En attente', 'Retardé']:
            # Proposer annulation
            message = f"Voulez-vous annuler le vol {flight_number} ?\n\n{reason}"
            if messagebox.askyesno("Annuler le vol", message):
                success, result_msg = safe_manager.safe_cancel_flight(flight_number)
                if success:
                    refresh_flights_data(flights_tree, safe_manager.data_manager)
                    messagebox.showinfo("Succès", result_msg)
                else:
                    messagebox.showerror("Erreur", result_msg)
        
        elif can_delete:
            # Proposer suppression
            message = f"Voulez-vous supprimer définitivement le vol {flight_number} ?\n\nCette action est irréversible."
            if messagebox.askyesno("Supprimer le vol", message):
                success, result_msg = safe_manager.safe_delete_flight(flight_number)
                if success:
                    refresh_flights_data(flights_tree, safe_manager.data_manager)
                    messagebox.showinfo("Succès", result_msg)
                else:
                    messagebox.showerror("Erreur", result_msg)
        else:
            messagebox.showwarning("Action impossible", f"Impossible de supprimer ce vol.\n\n{reason}")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")


def view_flight_details(flights_tree, data_manager):
    """Affiche les détails du vol sélectionné"""
    selection = flights_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un vol.")
        return
    
    item = flights_tree.item(selection[0])
    flight_number = item['values'][0]
    
    # Trouver les données complètes
    all_flights = data_manager.get_flights()
    flight_data = None
    
    for flight in all_flights:
        if flight.get('numero_vol') == flight_number:
            flight_data = flight
            break
    
    if not flight_data:
        messagebox.showerror("Erreur", "Vol non trouvé.")
        return
    
    details = f"""Détails du Vol {flight_number}

Route: {flight_data.get('aeroport_depart', 'N/A')} → {flight_data.get('aeroport_arrivee', 'N/A')}
Avion: {flight_data.get('avion_utilise', 'N/A')}
Distance: {flight_data.get('distance_km', 0)} km
Durée estimée: {flight_data.get('duree_estimee', 'N/A')}

Équipage:
• Pilote: {flight_data.get('pilote', 'Non assigné')}
• Copilote: {flight_data.get('copilote', 'Non assigné')}
• Personnel navigant: {len(flight_data.get('personnel_navigant', []))} membres

Statut: {flight_data.get('statut', 'N/A').replace('_', ' ').title()}"""
    
    messagebox.showinfo("Détails du Vol", details)


def filter_flights(flights_tree, data_manager, search_var, filter_var):
    """Filtre la liste des vols"""
    search_text = search_var.get().lower()
    filter_status = filter_var.get()
    
    # Vider le tableau
    for item in flights_tree.get_children():
        flights_tree.delete(item)
    
    # Recharger avec filtres
    all_flights = data_manager.get_flights()
    
    for flight in all_flights:
        # Mapping du statut pour l'affichage
        status_mapping = {
            'programme': 'Programmé',
            'en_attente': 'En attente',
            'en_vol': 'En vol',
            'atterri': 'Atterri',
            'retarde': 'Retardé',
            'annule': 'Annulé',
            'termine': 'Terminé'
        }
        
        flight_status = status_mapping.get(flight.get('statut', ''), 'Inconnu')
        
        # Filtrage par statut
        if filter_status != "Tous" and flight_status != filter_status:
            continue
        
        # Filtrage par recherche
        searchable_text = f"{flight.get('numero_vol', '')} {flight.get('aeroport_depart', '')} {flight.get('aeroport_arrivee', '')} {flight.get('avion_utilise', '')}".lower()
        if search_text and search_text not in searchable_text:
            continue
        
        # Ajouter à l'affichage avec parsing robuste des dates
        try:
            if flight.get('heure_depart'):
                depart_time = parse_datetime_robust(flight['heure_depart'])
                if depart_time:
                    date_str = depart_time.strftime("%Y-%m-%d")
                    heure_depart_str = depart_time.strftime("%H:%M")
                else:
                    date_str = "N/A"
                    heure_depart_str = "N/A"
            else:
                date_str = "N/A"
                heure_depart_str = "N/A"
            
            if flight.get('heure_arrivee_prevue'):
                arrivee_time = parse_datetime_robust(flight['heure_arrivee_prevue'])
                if arrivee_time:
                    heure_arrivee_str = arrivee_time.strftime("%H:%M")
                else:
                    heure_arrivee_str = "N/A"
            else:
                heure_arrivee_str = "N/A"
        except:
            date_str = "Erreur"
            heure_depart_str = "Erreur"
            heure_arrivee_str = "Erreur"
        
        values = (
            flight.get('numero_vol', ''),
            flight.get('aeroport_depart', ''),
            flight.get('aeroport_arrivee', ''),
            date_str,
            heure_depart_str,
            heure_arrivee_str,
            flight.get('avion_utilise', ''),
            flight_status
        )
        
        # Coloration selon le statut
        item_id = flights_tree.insert('', 'end', values=values)
        if flight_status == 'Annulé':
            flights_tree.set(item_id, 'Statut', '❌ Annulé')
        elif flight_status == 'Retardé':
            flights_tree.set(item_id, 'Statut', '⏰ Retardé')
        elif flight_status == 'En vol':
            flights_tree.set(item_id, 'Statut', '✈️ En vol')


def refresh_flights_data(flights_tree, data_manager):
    """CORRECTION BUG: Rafraîchit les données des vols"""
    try:
        print("🔄 Rafraîchissement des données vols...")
        
        # Vider le tableau
        for item in flights_tree.get_children():
            flights_tree.delete(item)
        
        all_flights = data_manager.get_flights()
        
        print(f"  📊 {len(all_flights)} vols chargés")
        
        # Mapping des statuts pour l'affichage
        status_mapping = {
            'programme': 'Programmé',
            'en_attente': 'En attente',
            'en_vol': 'En vol',
            'atterri': 'Atterri',
            'retarde': 'Retardé',
            'annule': 'Annulé',
            'termine': 'Terminé'
        }
        
        for flight in all_flights:
            try:
                flight_status = status_mapping.get(flight.get('statut', ''), 'Inconnu')
                
                # CORRECTION BUG: Gestion robuste des dates
                try:
                    if flight.get('heure_depart'):
                        depart_time = parse_datetime_robust(flight['heure_depart'])
                        if depart_time:
                            date_str = depart_time.strftime("%Y-%m-%d")
                            heure_depart_str = depart_time.strftime("%H:%M")
                        else:
                            date_str = "N/A"
                            heure_depart_str = "N/A"
                    else:
                        date_str = "N/A"
                        heure_depart_str = "N/A"
                    
                    if flight.get('heure_arrivee_prevue'):
                        arrivee_time = parse_datetime_robust(flight['heure_arrivee_prevue'])
                        if arrivee_time:
                            heure_arrivee_str = arrivee_time.strftime("%H:%M")
                        else:
                            heure_arrivee_str = "N/A"
                    else:
                        heure_arrivee_str = "N/A"
                        
                except Exception as e:
                    print(f"  ⚠️ Erreur parsing dates vol {flight.get('numero_vol', 'Inconnu')}: {e}")
                    date_str = "Erreur"
                    heure_depart_str = "Erreur"
                    heure_arrivee_str = "Erreur"
                
                values = (
                    flight.get('numero_vol', ''),
                    flight.get('aeroport_depart', ''),
                    flight.get('aeroport_arrivee', ''),
                    date_str,
                    heure_depart_str,
                    heure_arrivee_str,
                    flight.get('avion_utilise', ''),
                    flight_status
                )
                
                # Coloration selon le statut
                item_id = flights_tree.insert('', 'end', values=values)
                if flight_status == 'Annulé':
                    flights_tree.set(item_id, 'Statut', '❌ Annulé')
                elif flight_status == 'Retardé':
                    flights_tree.set(item_id, 'Statut', '⏰ Retardé')
                elif flight_status == 'En vol':
                    flights_tree.set(item_id, 'Statut', '✈️ En vol')
                elif flight_status == 'Atterri':
                    flights_tree.set(item_id, 'Statut', '🛬 Atterri')
                elif flight_status == 'Terminé':
                    flights_tree.set(item_id, 'Statut', '✅ Terminé')
                    
            except Exception as e:
                print(f"  ⚠️ Erreur traitement vol: {e}")
                continue
        
        print(f"✅ Vols rafraîchis: {len(all_flights)} vols affichés")
        
    except Exception as e:
        print(f"❌ Erreur refresh vols: {e}")


def parse_datetime_robust(datetime_value):
    """CORRECTION BUG: Parse robuste des dates/heures"""
    if not datetime_value:
        return None
    
    # Si c'est déjà un objet datetime
    if isinstance(datetime_value, datetime):
        return datetime_value
    
    # Si c'est une chaîne
    if isinstance(datetime_value, str):
        try:
            return datetime.fromisoformat(datetime_value)
        except:
            try:
                # Fallback : essayer le format standard
                return datetime.strptime(datetime_value, "%Y-%m-%d %H:%M:%S")
            except:
                pass
    
    return None