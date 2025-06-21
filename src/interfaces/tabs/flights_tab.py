import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os
from datetime import datetime, timedelta
import math
import traceback

# Ajouter le chemin du module Core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from Core.vol import Vol
from Core.aviation import Coordonnees, Aeroport, Avion
from Core.enums import StatutVol

class FlightDialog:
    """Dialogue pour créer ou modifier un vol"""
    
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
        self.autonomie_color_var = tk.StringVar(value="gray")
        
        # Dates par défaut
        tomorrow = datetime.now() + timedelta(days=1)
        self.date_depart_var.set(tomorrow.strftime("%Y-%m-%d"))
        self.heure_depart_var.set("08:00")
        self.heure_arrivee_var.set("10:00")
    
    def load_reference_data(self):
        """Charge les données de référence"""
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
        
        self.statut_choices = [s.obtenir_nom_affichage() for s in StatutVol]
    
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
        self.depart_combo.bind('<KeyRelease>', self.calculate_flight_info)
        
        # Aéroport d'arrivée
        ttk.Label(basic_frame, text="Arrivée*:").grid(row=2, column=0, sticky="w", pady=5)
        self.arrivee_combo = ttk.Combobox(basic_frame, textvariable=self.aeroport_arrivee_var,
                                         values=self.airport_choices, width=50)
        self.arrivee_combo.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.arrivee_combo.bind('<<ComboboxSelected>>', self.calculate_flight_info)
        self.arrivee_combo.bind('<KeyRelease>', self.calculate_flight_info)
    
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
        
        # Dates et heures
        try:
            if self.flight_data.get('heure_depart'):
                if isinstance(self.flight_data['heure_depart'], str):
                    depart_time = datetime.fromisoformat(self.flight_data['heure_depart'])
                else:
                    depart_time = self.flight_data['heure_depart']
                
                self.date_depart_var.set(depart_time.strftime("%Y-%m-%d"))
                self.heure_depart_var.set(depart_time.strftime("%H:%M"))
            
            if self.flight_data.get('heure_arrivee_prevue'):
                if isinstance(self.flight_data['heure_arrivee_prevue'], str):
                    arrivee_time = datetime.fromisoformat(self.flight_data['heure_arrivee_prevue'])
                else:
                    arrivee_time = self.flight_data['heure_arrivee_prevue']
                
                self.heure_arrivee_var.set(arrivee_time.strftime("%H:%M"))
        except:
            pass
        
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
        
        # Recalculer les informations
        self.calculate_flight_info()
    
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
        """Sauvegarde le vol avec correction des bugs de mise à jour"""
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
            
            # Sauvegarder avec corrections de bugs
            if self.is_editing:
                # CORRECTION BUG: Mise à jour correcte en mode édition
                success = self.data_manager.update_flight(flight_data['numero_vol'], flight_data)
                action = "modifié"
            else:
                # CORRECTION BUG: Ajout correct avec nouveau vol
                success = self.data_manager.add_flight(flight_data)
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
    
    def cancel(self):
        """Annule le dialogue"""
        self.result = None
        self.dialog.destroy()


def create_flights_tab_content(parent_frame, data_manager):
    """Crée le contenu de l'onglet vols"""
    
    # Variables pour la recherche et le filtrage
    flights_search_var = tk.StringVar()
    flights_filter_var = tk.StringVar(value="Tous")
    
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
        view_flight_details(flights_tree)
    
    def delete_flight_callback():
        delete_flight(data_manager, flights_tree)
    
    def filter_flights_callback(event=None):
        filter_flights(flights_tree, data_manager, flights_search_var, flights_filter_var)
    
    ttk.Button(toolbar, text="➕ Nouveau Vol", 
              command=new_flight_callback, 
              style='Action.TButton').grid(row=0, column=0, padx=(0, 5))
    ttk.Button(toolbar, text="✏️ Modifier", 
              command=edit_flight_callback).grid(row=0, column=1, padx=(0, 5))
    ttk.Button(toolbar, text="👁️ Voir Détails", 
              command=view_flight_callback).grid(row=0, column=2, padx=(0, 5))
    ttk.Button(toolbar, text="🗑️ Supprimer Vol", 
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
    """CORRECTION: Modifie le vol sélectionné avec recherche d'ID améliorée"""
    selection = flights_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un vol à modifier.")
        return
    
    try:
        item = flights_tree.item(selection[0])
        flight_number = item['values'][0]  # Numéro de vol depuis le tableau
        
        print(f"🔧 Recherche vol pour modification: {flight_number}")
        
        # CORRECTION: Forcer le rechargement des données sans cache
        data_manager.clear_cache()
        all_flights = data_manager.get_flights()
        
        flight_data = None
        
        # CORRECTION: Recherche plus robuste
        for flight in all_flights:
            vol_number = flight.get('numero_vol', '')
            print(f"  Comparaison: '{flight_number}' vs '{vol_number}'")
            
            # Recherche exacte d'abord
            if vol_number == flight_number:
                flight_data = flight
                print(f"  ✓ Vol trouvé par correspondance exacte")
                break
            
            # Recherche partielle si ID tronqué dans l'affichage
            if flight_number in vol_number or vol_number in flight_number:
                flight_data = flight
                print(f"  ✓ Vol trouvé par correspondance partielle")
                break
        
        if not flight_data:
            print(f"❌ Aucun vol trouvé pour: {flight_number}")
            print(f"  Vols disponibles: {[f.get('numero_vol') for f in all_flights]}")
            messagebox.showerror("Erreur", 
                               f"Vol '{flight_number}' non trouvé.\n\n"
                               f"Vols disponibles: {len(all_flights)}")
            return
        
        print(f"✓ Vol trouvé: {flight_data.get('numero_vol')}")
        
        # Vérifier si le vol peut être modifié
        current_status = flight_data.get('statut', 'programme')
        if current_status in ['en_vol', 'atterri', 'termine']:
            messagebox.showwarning("Modification impossible", 
                                  f"Impossible de modifier un vol {current_status}.")
            return
        
        # Ouvrir le dialogue de modification
        dialog = FlightDialog(parent, data_manager, flight_data)
        if dialog.result:
            print(f"✅ Vol {flight_number} modifié avec succès")
            
            # CORRECTION: Rafraîchissement immédiat et forcé
            data_manager.clear_cache()
            refresh_flights_data(flights_tree, data_manager)
            
            # AJOUT: Déclencher aussi la mise à jour des statistiques
            try:
                if hasattr(parent, 'refresh_statistics'):
                    parent.refresh_statistics()
                elif hasattr(parent, 'parent') and hasattr(parent.parent, 'refresh_statistics'):
                    parent.parent.refresh_statistics()
            except:
                pass
            
            messagebox.showinfo("Succès", f"Vol {flight_number} modifié avec succès!")
        else:
            print(f"🚫 Modification du vol {flight_number} annulée")
    
    except Exception as e:
        error_msg = f"Erreur lors de la modification du vol: {e}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        messagebox.showerror("Erreur", error_msg)


def view_flight_details(flights_tree):
    """Affiche les détails du vol sélectionné"""
    selection = flights_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un vol.")
        return
    
    item = flights_tree.item(selection[0])
    values = item['values']
    
    details = f"""Détails du Vol
    
Numéro: {values[0]}
Départ: {values[1]}
Arrivée: {values[2]}
Date: {values[3]}
Heure Départ: {values[4]}
Heure Arrivée: {values[5]}
Avion: {values[6]}
Statut: {values[7]}"""
    
    messagebox.showinfo("Détails du Vol", details)


def delete_flight(data_manager, flights_tree):
    """CORRECTION: Supprime ou annule le vol avec méthode DataManager corrigée"""
    selection = flights_tree.selection()
    if not selection:
        messagebox.showwarning("Sélection", "Veuillez sélectionner un vol à supprimer.")
        return
    
    try:
        item = flights_tree.item(selection[0])
        flight_number = item['values'][0]
        current_status = item['values'][7]
        
        print(f"🗑️ Demande suppression vol: {flight_number} (statut: {current_status})")
        
        # Déterminer l'action selon le statut
        if current_status in ['Programmé', 'En attente', 'Retardé']:
            action = "annuler"
            message = f"Voulez-vous vraiment annuler le vol {flight_number} ?"
        else:
            action = "supprimer définitivement"
            message = f"Voulez-vous vraiment supprimer définitivement le vol {flight_number} ?\n\nCette action est irréversible."
        
        if messagebox.askyesno("Confirmation", message):
            if current_status in ['Programmé', 'En attente', 'Retardé']:
                # CORRECTION: Annuler (changer statut) au lieu de supprimer
                success = data_manager.update_flight(flight_number, {'statut': 'annule'})
                message_success = f"Vol {flight_number} annulé avec succès."
            else:
                # CORRECTION: Utiliser la méthode corrigée du DataManager
                success = data_manager.delete_flight(flight_number)
                message_success = f"Vol {flight_number} supprimé définitivement."
            
            if success:
                print(f"✅ {message_success}")
                
                # CORRECTION: Rafraîchissement immédiat forcé
                data_manager.clear_cache()
                refresh_flights_data(flights_tree, data_manager)
                
                # AJOUT: Mise à jour des statistiques
                try:
                    if hasattr(flights_tree, 'master') and hasattr(flights_tree.master, 'refresh_statistics'):
                        flights_tree.master.refresh_statistics()
                except:
                    pass
                
                messagebox.showinfo("Succès", message_success)
            else:
                messagebox.showerror("Erreur", f"Impossible de {action} le vol.")
        
    except Exception as e:
        error_msg = f"Erreur lors de la suppression: {e}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        messagebox.showerror("Erreur", error_msg)


def filter_flights(flights_tree, data_manager, search_var, filter_var):
    """Filtre la liste des vols - AMÉLIORATION"""
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
        
        # Ajouter à l'affichage
        try:
            if flight.get('heure_depart'):
                if isinstance(flight['heure_depart'], str):
                    depart_time = datetime.fromisoformat(flight['heure_depart'])
                else:
                    depart_time = flight['heure_depart']
                
                date_str = depart_time.strftime("%Y-%m-%d")
                heure_depart_str = depart_time.strftime("%H:%M")
            else:
                date_str = "N/A"
                heure_depart_str = "N/A"
            
            if flight.get('heure_arrivee_prevue'):
                if isinstance(flight['heure_arrivee_prevue'], str):
                    arrivee_time = datetime.fromisoformat(flight['heure_arrivee_prevue'])
                else:
                    arrivee_time = flight['heure_arrivee_prevue']
                
                heure_arrivee_str = arrivee_time.strftime("%H:%M")
            else:
                heure_arrivee_str = "N/A"
        except:
            date_str = "N/A"
            heure_depart_str = "N/A"
            heure_arrivee_str = "N/A"
        
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
    """CORRECTION: Rafraîchissement robuste avec gestion d'erreurs"""
    try:
        print("🔄 Rafraîchissement des données vols...")
        
        # CORRECTION: Vider le tableau
        for item in flights_tree.get_children():
            flights_tree.delete(item)
        
        # CORRECTION: Forcer le rechargement sans cache
        data_manager.clear_cache()
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
            flight_status = status_mapping.get(flight.get('statut', ''), 'Inconnu')
            
            try:
                # Gestion robuste des dates
                if flight.get('heure_depart'):
                    if isinstance(flight['heure_depart'], str):
                        depart_time = datetime.fromisoformat(flight['heure_depart'])
                    else:
                        depart_time = flight['heure_depart']
                    
                    date_str = depart_time.strftime("%Y-%m-%d")
                    heure_depart_str = depart_time.strftime("%H:%M")
                else:
                    date_str = "N/A"
                    heure_depart_str = "N/A"
                
                if flight.get('heure_arrivee_prevue'):
                    if isinstance(flight['heure_arrivee_prevue'], str):
                        arrivee_time = datetime.fromisoformat(flight['heure_arrivee_prevue'])
                    else:
                        arrivee_time = flight['heure_arrivee_prevue']
                    
                    heure_arrivee_str = arrivee_time.strftime("%H:%M")
                else:
                    heure_arrivee_str = "N/A"
                    
            except Exception as e:
                print(f"  ⚠️ Erreur parsing dates vol {flight.get('numero_vol')}: {e}")
                date_str = "N/A"
                heure_depart_str = "N/A"
                heure_arrivee_str = "N/A"
            
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
            try:
                item_id = flights_tree.insert('', 'end', values=values)
                if flight_status == 'Annulé':
                    flights_tree.set(item_id, 'Statut', '❌ Annulé')
                elif flight_status == 'Retardé':
                    flights_tree.set(item_id, 'Statut', '⏰ Retardé')
                elif flight_status == 'En vol':
                    flights_tree.set(item_id, 'Statut', '✈️ En vol')
            except Exception as e:
                print(f"  ⚠️ Erreur ajout vol à l'interface: {e}")
        
        print(f"✅ Vols rafraîchis: {len(all_flights)} vols affichés")
        
    except Exception as e:
        print(f"❌ Erreur refresh vols: {e}")
        traceback.print_exc()
