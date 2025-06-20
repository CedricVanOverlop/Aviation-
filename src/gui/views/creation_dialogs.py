"""
Dialogues de création pour vols, personnel et passagers
À intégrer dans les vues existantes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import uuid

class FlightCreationDialog:
    """Dialogue de création d'un nouveau vol"""
    
    def __init__(self, parent, data_controller, callback=None):
        self.data_controller = data_controller
        self.callback = callback
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Vol")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables du formulaire
        self.setup_variables()
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données
        self.load_data()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables du formulaire"""
        self.form_vars = {
            'numero_vol': tk.StringVar(),
            'aeroport_depart': tk.StringVar(),
            'aeroport_arrivee': tk.StringVar(),
            'date_depart': tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')),
            'heure_depart': tk.StringVar(value="10:00"),
            'date_arrivee': tk.StringVar(value=datetime.now().strftime('%Y-%m-%d')),
            'heure_arrivee': tk.StringVar(value="12:00"),
            'avion_utilise': tk.StringVar(),
            'auto_assign_aircraft': tk.BooleanVar(value=True)
        }
    
    def setup_ui(self):
        """Configure l'interface du dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Création d'un Nouveau Vol", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook pour organiser les champs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Onglet Informations générales
        self.create_general_tab(notebook)
        
        # Onglet Horaires
        self.create_schedule_tab(notebook)
        
        # Onglet Avion
        self.create_aircraft_tab(notebook)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_general_tab(self, parent):
        """Onglet informations générales"""
        general_frame = ttk.Frame(parent, padding=20)
        parent.add(general_frame, text="Général")
        
        # Numéro de vol
        ttk.Label(general_frame, text="Numéro de Vol*:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        
        numero_frame = ttk.Frame(general_frame)
        numero_frame.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        numero_entry = ttk.Entry(numero_frame, textvariable=self.form_vars['numero_vol'], width=15)
        numero_entry.grid(row=0, column=0)
        
        ttk.Button(numero_frame, text="Générer", width=8,
                  command=self.generate_flight_number).grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(numero_frame, text="Ex: AF123, LH456", 
                 font=('Arial', 8), foreground='gray').grid(row=1, column=0, columnspan=2, sticky='w')
        
        # Aéroports
        ttk.Label(general_frame, text="Aéroport de Départ*:", 
                 font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        
        self.depart_combo = ttk.Combobox(general_frame, textvariable=self.form_vars['aeroport_depart'],
                                        width=30, state='readonly')
        self.depart_combo.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(general_frame, text="Aéroport d'Arrivée*:", 
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        
        self.arrivee_combo = ttk.Combobox(general_frame, textvariable=self.form_vars['aeroport_arrivee'],
                                         width=30, state='readonly')
        self.arrivee_combo.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Bouton d'inversion
        ttk.Button(general_frame, text="🔄 Inverser", width=12,
                  command=self.swap_airports).grid(row=3, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Distance estimée (calculée automatiquement)
        ttk.Label(general_frame, text="Distance Estimée:", 
                 font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=5)
        
        self.distance_var = tk.StringVar(value="-- km")
        ttk.Label(general_frame, textvariable=self.distance_var,
                 font=('Arial', 10, 'italic')).grid(row=4, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Bind pour calculer la distance
        self.depart_combo.bind('<<ComboboxSelected>>', self.calculate_distance)
        self.arrivee_combo.bind('<<ComboboxSelected>>', self.calculate_distance)
    
    def create_schedule_tab(self, parent):
        """Onglet horaires"""
        schedule_frame = ttk.Frame(parent, padding=20)
        parent.add(schedule_frame, text="Horaires")
        
        # Départ
        ttk.Label(schedule_frame, text="Départ", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 10))
        
        ttk.Label(schedule_frame, text="Date*:").grid(row=1, column=0, sticky='w', pady=5)
        date_depart_entry = ttk.Entry(schedule_frame, textvariable=self.form_vars['date_depart'], width=15)
        date_depart_entry.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(schedule_frame, text="Heure*:").grid(row=2, column=0, sticky='w', pady=5)
        heure_depart_entry = ttk.Entry(schedule_frame, textvariable=self.form_vars['heure_depart'], width=10)
        heure_depart_entry.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Arrivée
        ttk.Label(schedule_frame, text="Arrivée", 
                 font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=3, sticky='w', pady=(20, 10))
        
        ttk.Label(schedule_frame, text="Date*:").grid(row=4, column=0, sticky='w', pady=5)
        date_arrivee_entry = ttk.Entry(schedule_frame, textvariable=self.form_vars['date_arrivee'], width=15)
        date_arrivee_entry.grid(row=4, column=1, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(schedule_frame, text="Heure*:").grid(row=5, column=0, sticky='w', pady=5)
        heure_arrivee_entry = ttk.Entry(schedule_frame, textvariable=self.form_vars['heure_arrivee'], width=10)
        heure_arrivee_entry.grid(row=5, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Boutons d'aide
        help_frame = ttk.Frame(schedule_frame)
        help_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(help_frame, text="Calculer Durée de Vol",
                  command=self.calculate_flight_duration).pack(side='left', padx=5)
        ttk.Button(help_frame, text="Horaires Suggérés",
                  command=self.suggest_schedule).pack(side='left', padx=5)
        
        # Durée du vol (affichée)
        self.duration_var = tk.StringVar(value="Durée: --")
        ttk.Label(schedule_frame, textvariable=self.duration_var,
                 font=('Arial', 10, 'italic')).grid(row=7, column=0, columnspan=3, pady=10)
        
        # Bind pour calculer automatiquement
        for var in ['date_depart', 'heure_depart', 'date_arrivee', 'heure_arrivee']:
            self.form_vars[var].trace('w', self.update_duration)
    
    def create_aircraft_tab(self, parent):
        """Onglet avion"""
        aircraft_frame = ttk.Frame(parent, padding=20)
        parent.add(aircraft_frame, text="Avion")
        
        # Option d'assignation automatique
        ttk.Checkbutton(aircraft_frame, text="Assignation automatique d'avion",
                       variable=self.form_vars['auto_assign_aircraft'],
                       command=self.toggle_aircraft_selection).grid(row=0, column=0, columnspan=2, sticky='w', pady=10)
        
        # Sélection manuelle d'avion
        ttk.Label(aircraft_frame, text="Avion spécifique:", 
                 font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        
        self.aircraft_combo = ttk.Combobox(aircraft_frame, textvariable=self.form_vars['avion_utilise'],
                                          width=30, state='readonly')
        self.aircraft_combo.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Informations sur l'avion sélectionné
        info_frame = ttk.LabelFrame(aircraft_frame, text="Informations Avion", padding=10)
        info_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=20)
        
        self.aircraft_info_vars = {
            'modele': tk.StringVar(),
            'capacite': tk.StringVar(),
            'autonomie': tk.StringVar(),
            'etat': tk.StringVar()
        }
        
        for i, (label, var_name) in enumerate([
            ("Modèle:", 'modele'),
            ("Capacité:", 'capacite'),
            ("Autonomie:", 'autonomie'),
            ("État:", 'etat')
        ]):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            ttk.Label(info_frame, textvariable=self.aircraft_info_vars[var_name],
                     font=('Arial', 9, 'bold')).grid(row=i, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Bind pour mettre à jour les infos
        self.aircraft_combo.bind('<<ComboboxSelected>>', self.update_aircraft_info)
        
        # Configuration initiale
        self.toggle_aircraft_selection()
    
    def create_buttons(self, parent):
        """Crée les boutons du dialogue"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=10)
        
        # Bouton de validation des données
        ttk.Button(button_frame, text="✓ Valider Données",
                  command=self.validate_data).pack(side='left', padx=5)
        
        # Spacer
        ttk.Frame(button_frame).pack(side='left', expand=True)
        
        # Boutons principaux
        ttk.Button(button_frame, text="Créer Vol",
                  command=self.create_flight).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Annuler",
                  command=self.cancel).pack(side='right', padx=5)
    
    def load_data(self):
        """Charge les données dans les combos"""
        # Charger les aéroports
        aeroports = []
        try:
            all_aeroports = self.data_controller.get_all_aeroports()
            for aeroport_data in all_aeroports:
                aeroport = aeroport_data['aeroport']
                aeroports.append(f"{aeroport.code_iata} - {aeroport.nom}")
        except:
            # Aéroports par défaut si pas de données
            aeroports = [
                "CDG - Charles de Gaulle",
                "ORY - Orly",
                "LHR - Londres Heathrow",
                "FRA - Francfort",
                "BCN - Barcelone"
            ]
        
        self.depart_combo['values'] = aeroports
        self.arrivee_combo['values'] = aeroports
        
        # Charger les avions disponibles
        aircraft_list = []
        try:
            all_aircraft = self.data_controller.get_all_avions()
            for aircraft_data in all_aircraft:
                avion = aircraft_data['avion']
                if avion.etat.est_operationnel():
                    aircraft_list.append(f"{avion.num_id} - {avion.modele}")
        except:
            pass
        
        self.aircraft_combo['values'] = aircraft_list
    
    def generate_flight_number(self):
        """Génère un numéro de vol automatiquement"""
        import random
        prefixes = ['AF', 'BA', 'LH', 'KL', 'IB', 'AZ', 'SN']
        prefix = random.choice(prefixes)
        number = random.randint(100, 9999)
        self.form_vars['numero_vol'].set(f"{prefix}{number}")
    
    def swap_airports(self):
        """Inverse les aéroports de départ et d'arrivée"""
        depart = self.form_vars['aeroport_depart'].get()
        arrivee = self.form_vars['aeroport_arrivee'].get()
        
        self.form_vars['aeroport_depart'].set(arrivee)
        self.form_vars['aeroport_arrivee'].set(depart)
        
        self.calculate_distance()
    
    def calculate_distance(self, event=None):
        """Calcule et affiche la distance entre les aéroports"""
        # Simulation simple - dans la vraie version, utiliser les coordonnées des aéroports
        depart = self.form_vars['aeroport_depart'].get()
        arrivee = self.form_vars['aeroport_arrivee'].get()
        
        if depart and arrivee and depart != arrivee:
            # Distance simulée
            import random
            distance = random.randint(200, 8000)
            self.distance_var.set(f"{distance} km")
        else:
            self.distance_var.set("-- km")
    
    def calculate_flight_duration(self):
        """Calcule la durée suggérée du vol"""
        distance_str = self.distance_var.get()
        if "km" in distance_str:
            try:
                distance = int(distance_str.replace(" km", ""))
                # Calcul simple : vitesse moyenne 800 km/h + 30 min de procédures
                duree_heures = (distance / 800) + 0.5
                
                # Proposer une heure d'arrivée
                try:
                    depart_dt = datetime.strptime(
                        f"{self.form_vars['date_depart'].get()} {self.form_vars['heure_depart'].get()}",
                        '%Y-%m-%d %H:%M'
                    )
                    arrivee_dt = depart_dt + timedelta(hours=duree_heures)
                    
                    self.form_vars['date_arrivee'].set(arrivee_dt.strftime('%Y-%m-%d'))
                    self.form_vars['heure_arrivee'].set(arrivee_dt.strftime('%H:%M'))
                    
                    messagebox.showinfo("Durée Calculée", 
                                      f"Durée estimée: {duree_heures:.1f}h\n"
                                      f"Heure d'arrivée suggérée: {arrivee_dt.strftime('%H:%M')}")
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez d'abord définir la date et l'heure de départ")
            except:
                messagebox.showerror("Erreur", "Impossible de calculer la durée")
    
    def suggest_schedule(self):
        """Suggère des horaires optimaux"""
        messagebox.showinfo("Horaires Suggérés",
                           "Suggestions d'horaires:\n\n"
                           "Matin: 08:00 - 10:00\n"
                           "Midi: 12:00 - 14:00\n" 
                           "Après-midi: 16:00 - 18:00\n"
                           "Soirée: 20:00 - 22:00")
    
    def update_duration(self, *args):
        """Met à jour l'affichage de la durée"""
        try:
            depart_dt = datetime.strptime(
                f"{self.form_vars['date_depart'].get()} {self.form_vars['heure_depart'].get()}",
                '%Y-%m-%d %H:%M'
            )
            arrivee_dt = datetime.strptime(
                f"{self.form_vars['date_arrivee'].get()} {self.form_vars['heure_arrivee'].get()}",
                '%Y-%m-%d %H:%M'
            )
            
            duree = arrivee_dt - depart_dt
            if duree.total_seconds() > 0:
                heures = duree.total_seconds() / 3600
                self.duration_var.set(f"Durée: {heures:.1f}h")
            else:
                self.duration_var.set("Durée: Invalide (arrivée avant départ)")
        except:
            self.duration_var.set("Durée: --")
    
    def toggle_aircraft_selection(self):
        """Active/désactive la sélection manuelle d'avion"""
        if self.form_vars['auto_assign_aircraft'].get():
            self.aircraft_combo.config(state='disabled')
        else:
            self.aircraft_combo.config(state='readonly')
    
    def update_aircraft_info(self, event=None):
        """Met à jour les informations de l'avion sélectionné"""
        aircraft_str = self.form_vars['avion_utilise'].get()
        
        if aircraft_str:
            # Extraire l'ID de l'avion
            aircraft_id = aircraft_str.split(' - ')[0]
            
            # Trouver l'avion dans les données
            try:
                all_aircraft = self.data_controller.get_all_avions()
                for aircraft_data in all_aircraft:
                    avion = aircraft_data['avion']
                    if avion.num_id == aircraft_id:
                        self.aircraft_info_vars['modele'].set(avion.modele)
                        self.aircraft_info_vars['capacite'].set(f"{avion.capacite} passagers")
                        self.aircraft_info_vars['autonomie'].set(f"{avion.autonomie} km")
                        self.aircraft_info_vars['etat'].set(avion.etat.value.title())
                        break
            except:
                pass
        else:
            # Vider les informations
            for var in self.aircraft_info_vars.values():
                var.set("")
    
    def validate_data(self):
        """Valide les données saisies"""
        errors = []
        
        # Vérifications obligatoires
        required_fields = [
            ('numero_vol', "Numéro de vol"),
            ('aeroport_depart', "Aéroport de départ"),
            ('aeroport_arrivee', "Aéroport d'arrivée"),
            ('date_depart', "Date de départ"),
            ('heure_depart', "Heure de départ"),
            ('date_arrivee', "Date d'arrivée"),
            ('heure_arrivee', "Heure d'arrivée")
        ]
        
        for field, label in required_fields:
            if not self.form_vars[field].get().strip():
                errors.append(f"• {label} est obligatoire")
        
        # Vérification des formats
        try:
            depart_dt = datetime.strptime(
                f"{self.form_vars['date_depart'].get()} {self.form_vars['heure_depart'].get()}",
                '%Y-%m-%d %H:%M'
            )
        except ValueError:
            errors.append("• Format de date/heure de départ invalide")
            depart_dt = None
        
        try:
            arrivee_dt = datetime.strptime(
                f"{self.form_vars['date_arrivee'].get()} {self.form_vars['heure_arrivee'].get()}",
                '%Y-%m-%d %H:%M'
            )
        except ValueError:
            errors.append("• Format de date/heure d'arrivée invalide")
            arrivee_dt = None
        
        # Vérification cohérence temporelle
        if depart_dt and arrivee_dt:
            if arrivee_dt <= depart_dt:
                errors.append("• L'heure d'arrivée doit être postérieure au départ")
            
            # Vérification durée raisonnable
            duree = arrivee_dt - depart_dt
            if duree.total_seconds() > 86400:  # Plus de 24h
                errors.append("• Durée de vol excessive (>24h)")
        
        # Vérification aéroports différents
        if (self.form_vars['aeroport_depart'].get() == 
            self.form_vars['aeroport_arrivee'].get()):
            errors.append("• Les aéroports de départ et d'arrivée doivent être différents")
        
        # Vérification avion si sélection manuelle
        if (not self.form_vars['auto_assign_aircraft'].get() and 
            not self.form_vars['avion_utilise'].get()):
            errors.append("• Veuillez sélectionner un avion ou activer l'assignation automatique")
        
        # Afficher les erreurs ou confirmer
        if errors:
            messagebox.showerror("Erreurs de validation", "\n".join(errors))
            return False
        else:
            messagebox.showinfo("Validation", "✓ Toutes les données sont valides")
            return True
    
    def create_flight(self):
        """Crée le vol"""
        if not self.validate_data():
            return
        
        try:
            # Préparer les données
            flight_data = {
                'numero_vol': self.form_vars['numero_vol'].get().strip(),
                'aeroport_depart': self.form_vars['aeroport_depart'].get(),
                'aeroport_arrivee': self.form_vars['aeroport_arrivee'].get(),
                'heure_depart': datetime.strptime(
                    f"{self.form_vars['date_depart'].get()} {self.form_vars['heure_depart'].get()}",
                    '%Y-%m-%d %H:%M'
                ),
                'heure_arrivee': datetime.strptime(
                    f"{self.form_vars['date_arrivee'].get()} {self.form_vars['heure_arrivee'].get()}",
                    '%Y-%m-%d %H:%M'
                ),
                'auto_assign_aircraft': self.form_vars['auto_assign_aircraft'].get(),
                'aircraft_id': self.form_vars['avion_utilise'].get().split(' - ')[0] if self.form_vars['avion_utilise'].get() else None
            }
            
            # Créer le vol via le contrôleur de données
            vol_id = self.data_controller.create_vol(**flight_data)
            
            self.result = vol_id
            messagebox.showinfo("Succès", f"Vol {flight_data['numero_vol']} créé avec succès!")
            
            # Callback si défini
            if self.callback:
                self.callback(vol_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du vol:\n{e}")
    
    def cancel(self):
        """Annule la création"""
        if messagebox.askyesno("Confirmer", "Abandonner la création du vol ?"):
            self.dialog.destroy()


class PersonnelCreationDialog:
    """Dialogue de création d'un nouveau membre du personnel"""
    
    def __init__(self, parent, data_controller, callback=None):
        self.data_controller = data_controller
        self.callback = callback
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Personnel")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables du formulaire
        self.setup_variables()
        
        # Créer l'interface
        self.setup_ui()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables du formulaire"""
        self.form_vars = {
            'nom': tk.StringVar(),
            'prenom': tk.StringVar(),
            'sexe': tk.StringVar(value="masculin"),
            'adresse': tk.StringVar(),
            'date_naissance': tk.StringVar(),
            'numero_telephone': tk.StringVar(),
            'email': tk.StringVar(),
            'type_personnel': tk.StringVar(value="pilote"),
            'horaire': tk.StringVar(value="Temps plein"),
            'specialisation': tk.StringVar(),
            'numero_licence': tk.StringVar(),
            'heures_vol': tk.StringVar(value="0"),
            'langues': tk.StringVar()
        }
    
    def setup_ui(self):
        """Configure l'interface du dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Nouveau Membre du Personnel", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook pour organiser les champs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Onglet Informations personnelles
        self.create_personal_tab(notebook)
        
        # Onglet Informations professionnelles
        self.create_professional_tab(notebook)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_personal_tab(self, parent):
        """Onglet informations personnelles"""
        personal_frame = ttk.Frame(parent, padding=20)
        parent.add(personal_frame, text="Personnel")
        
        fields = [
            ("Nom*:", 'nom', "Ex: Dupont"),
            ("Prénom*:", 'prenom', "Ex: Jean"),
            ("Adresse:", 'adresse', "Ex: 123 Rue de la Paix, Paris"),
            ("Date de Naissance:", 'date_naissance', "AAAA-MM-JJ"),
            ("Téléphone:", 'numero_telephone', "Ex: +33123456789"),
            ("Email:", 'email', "Ex: jean.dupont@airline.com")
        ]
        
        for i, (label, var_name, placeholder) in enumerate(fields):
            row = i
            
            ttk.Label(personal_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky='w', pady=5)
            
            if var_name == 'adresse':
                # Zone de texte pour l'adresse
                text_widget = tk.Text(personal_frame, height=3, width=35)
                text_widget.grid(row=row, column=1, sticky='w', padx=(10, 0), pady=5)
                
                # Binding pour synchroniser avec la variable
                def on_text_change(event, var=self.form_vars[var_name], widget=text_widget):
                    var.set(widget.get("1.0", tk.END).strip())
                text_widget.bind('<KeyRelease>', on_text_change)
            else:
                entry = ttk.Entry(personal_frame, textvariable=self.form_vars[var_name], width=35)
                entry.grid(row=row, column=1, sticky='w', padx=(10, 0), pady=5)
            
            # Placeholder
            ttk.Label(personal_frame, text=placeholder, font=('Arial', 8), 
                     foreground='gray').grid(row=row, column=2, sticky='w', padx=(5, 0), pady=5)
        
        # Sexe avec radiobuttons
        ttk.Label(personal_frame, text="Sexe*:", font=('Arial', 10, 'bold')).grid(
            row=len(fields), column=0, sticky='w', pady=5)
        
        sexe_frame = ttk.Frame(personal_frame)
        sexe_frame.grid(row=len(fields), column=1, sticky='w', padx=(10, 0), pady=5)
        
        for i, (value, text) in enumerate([("masculin", "Masculin"), ("feminin", "Féminin"), ("autre", "Autre")]):
            ttk.Radiobutton(sexe_frame, text=text, variable=self.form_vars['sexe'], 
                           value=value).pack(side='left', padx=(0, 10))
    
    def create_professional_tab(self, parent):
        """Onglet informations professionnelles"""
        prof_frame = ttk.Frame(parent, padding=20)
        parent.add(prof_frame, text="Professionnel")
        
        # Type de personnel
        ttk.Label(prof_frame, text="Poste*:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        
        type_combo = ttk.Combobox(prof_frame, textvariable=self.form_vars['type_personnel'],
                                 values=["pilote", "copilote", "hotesse", "steward", "mecanicien", 
                                        "controleur", "gestionnaire"], 
                                 width=20, state='readonly')
        type_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_type_change)
        
        # Horaire
        ttk.Label(prof_frame, text="Horaire:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5)
        
        horaire_combo = ttk.Combobox(prof_frame, textvariable=self.form_vars['horaire'],
                                    values=["Temps plein", "Temps partiel", "Contractuel", "Stagiaire"],
                                    width=20, state='readonly')
        horaire_combo.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Spécialisation
        ttk.Label(prof_frame, text="Spécialisation:", font=('Arial', 10)).grid(
            row=2, column=0, sticky='w', pady=5)
        
        ttk.Entry(prof_frame, textvariable=self.form_vars['specialisation'], width=30).grid(
            row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Frame pour les champs spécifiques selon le type
        self.specific_frame = ttk.LabelFrame(prof_frame, text="Informations Spécifiques", padding=10)
        self.specific_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=20)
        
        # Champs spécifiques (mis à jour selon le type)
        self.setup_specific_fields()
    
    def on_type_change(self, event=None):
        """Met à jour les champs spécifiques selon le type de personnel"""
        self.setup_specific_fields()
    
    def setup_specific_fields(self):
        """Configure les champs spécifiques selon le type de personnel"""
        # Vider le frame
        for widget in self.specific_frame.winfo_children():
            widget.destroy()
        
        personnel_type = self.form_vars['type_personnel'].get()
        
        if personnel_type in ["pilote", "copilote"]:
            # Champs pour pilotes
            ttk.Label(self.specific_frame, text="Numéro de Licence:").grid(row=0, column=0, sticky='w', pady=5)
            ttk.Entry(self.specific_frame, textvariable=self.form_vars['numero_licence'], width=20).grid(
                row=0, column=1, sticky='w', padx=(10, 0), pady=5)
            
            ttk.Label(self.specific_frame, text="Heures de Vol:").grid(row=1, column=0, sticky='w', pady=5)
            ttk.Entry(self.specific_frame, textvariable=self.form_vars['heures_vol'], width=10).grid(
                row=1, column=1, sticky='w', padx=(10, 0), pady=5)
            
        elif personnel_type in ["hotesse", "steward"]:
            # Champs pour personnel navigant
            ttk.Label(self.specific_frame, text="Langues parlées:").grid(row=0, column=0, sticky='w', pady=5)
            ttk.Entry(self.specific_frame, textvariable=self.form_vars['langues'], width=30).grid(
                row=0, column=1, sticky='w', padx=(10, 0), pady=5)
            ttk.Label(self.specific_frame, text="Séparez par des virgules", 
                     font=('Arial', 8), foreground='gray').grid(row=1, column=1, sticky='w', padx=(10, 0))
            
        elif personnel_type == "mecanicien":
            # Champs pour mécaniciens
            ttk.Label(self.specific_frame, text="Spécialisation:").grid(row=0, column=0, sticky='w', pady=5)
            spec_combo = ttk.Combobox(self.specific_frame, textvariable=self.form_vars['specialisation'],
                                     values=["Moteurs", "Avionique", "Structure", "Général"],
                                     width=20, state='readonly')
            spec_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
    
    def create_buttons(self, parent):
        """Crée les boutons du dialogue"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Créer Personnel",
                  command=self.create_personnel).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Annuler",
                  command=self.cancel).pack(side='right', padx=5)
    
    def create_personnel(self):
        """Crée le personnel"""
        # Validation
        if not self.validate_data():
            return
        
        try:
            # Préparer les données
            personnel_data = {
                'nom': self.form_vars['nom'].get().strip(),
                'prenom': self.form_vars['prenom'].get().strip(),
                'sexe': self.form_vars['sexe'].get(),
                'adresse': self.form_vars['adresse'].get().strip(),
                'metier': self.form_vars['type_personnel'].get(),
                'horaire': self.form_vars['horaire'].get(),
                'specialisation': self.form_vars['specialisation'].get().strip()
            }
            
            # Ajouter les champs optionnels s'ils sont remplis
            if self.form_vars['date_naissance'].get():
                try:
                    personnel_data['date_naissance'] = datetime.strptime(
                        self.form_vars['date_naissance'].get(), '%Y-%m-%d')
                except ValueError:
                    pass
            
            if self.form_vars['numero_telephone'].get():
                personnel_data['numero_telephone'] = self.form_vars['numero_telephone'].get()
            
            if self.form_vars['email'].get():
                personnel_data['email'] = self.form_vars['email'].get()
            
            # Créer le personnel via le contrôleur de données
            personnel_id = self.data_controller.create_personnel(**personnel_data)
            
            self.result = personnel_id
            messagebox.showinfo("Succès", 
                              f"Personnel {personnel_data['prenom']} {personnel_data['nom']} créé avec succès!")
            
            # Callback si défini
            if self.callback:
                self.callback(personnel_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du personnel:\n{e}")
    
    def validate_data(self):
        """Valide les données saisies"""
        errors = []
        
        # Champs obligatoires
        required_fields = [
            ('nom', "Nom"),
            ('prenom', "Prénom"),
            ('type_personnel', "Poste")
        ]
        
        for field, label in required_fields:
            if not self.form_vars[field].get().strip():
                errors.append(f"• {label} est obligatoire")
        
        # Validation email
        email = self.form_vars['email'].get().strip()
        if email and '@' not in email:
            errors.append("• Format d'email invalide")
        
        # Validation date de naissance
        date_naiss = self.form_vars['date_naissance'].get().strip()
        if date_naiss:
            try:
                datetime.strptime(date_naiss, '%Y-%m-%d')
            except ValueError:
                errors.append("• Format de date de naissance invalide (AAAA-MM-JJ)")
        
        # Validation heures de vol pour pilotes
        if (self.form_vars['type_personnel'].get() in ["pilote", "copilote"] and
            self.form_vars['heures_vol'].get()):
            try:
                float(self.form_vars['heures_vol'].get())
            except ValueError:
                errors.append("• Les heures de vol doivent être un nombre")
        
        if errors:
            messagebox.showerror("Erreurs de validation", "\n".join(errors))
            return False
        
        return True
    
    def cancel(self):
        """Annule la création"""
        if messagebox.askyesno("Confirmer", "Abandonner la création du personnel ?"):
            self.dialog.destroy()


class PassengerCreationDialog:
    """Dialogue de création d'un nouveau passager"""
    
    def __init__(self, parent, data_controller, callback=None):
        self.data_controller = data_controller
        self.callback = callback
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Passager")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Variables du formulaire
        self.setup_variables()
        
        # Créer l'interface
        self.setup_ui()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        """Initialise les variables du formulaire"""
        self.form_vars = {
            'nom': tk.StringVar(),
            'prenom': tk.StringVar(),
            'sexe': tk.StringVar(value="masculin"),
            'adresse': tk.StringVar(),
            'date_naissance': tk.StringVar(),
            'numero_telephone': tk.StringVar(),
            'email': tk.StringVar(),
            'numero_passeport': tk.StringVar(),
            'vol_numero': tk.StringVar(),
            'create_reservation': tk.BooleanVar(value=False)
        }
    
    def setup_ui(self):
        """Configure l'interface du dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Nouveau Passager", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Formulaire principal
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Informations personnelles
        self.create_personal_section(form_frame)
        
        # Séparateur
        ttk.Separator(form_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Informations de voyage
        self.create_travel_section(form_frame)
        
        # Boutons
        self.create_buttons(main_frame)
    
    def create_personal_section(self, parent):
        """Section informations personnelles"""
        # En-tête
        ttk.Label(parent, text="Informations Personnelles", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Grille pour les champs
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill='x')
        
        fields = [
            ("Nom*:", 'nom', "Ex: Dupont"),
            ("Prénom*:", 'prenom', "Ex: Marie"),
            ("Date de Naissance:", 'date_naissance', "AAAA-MM-JJ"),
            ("Téléphone:", 'numero_telephone', "Ex: +33123456789"),
            ("Email:", 'email', "Ex: marie.dupont@email.com"),
            ("Numéro de Passeport:", 'numero_passeport', "Ex: 12AB34567")
        ]
        
        for i, (label, var_name, placeholder) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(grid_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=5, pady=5)
            ttk.Entry(grid_frame, textvariable=self.form_vars[var_name], width=20).grid(
                row=row, column=col+1, sticky='w', padx=5, pady=5)
            
            # Placeholder en dessous pour économiser l'espace
            if i % 2 == 1 or i == len(fields) - 1:  # Dernier de la ligne
                ttk.Label(grid_frame, text=f"  {placeholder}", font=('Arial', 7), 
                         foreground='gray').grid(row=row, column=col+1, sticky='w', padx=5)
        
        # Adresse sur toute la largeur
        ttk.Label(grid_frame, text="Adresse:", font=('Arial', 9, 'bold')).grid(
            row=len(fields)//2 + 1, column=0, sticky='w', padx=5, pady=5)
        
        adresse_entry = ttk.Entry(grid_frame, textvariable=self.form_vars['adresse'], width=50)
        adresse_entry.grid(row=len(fields)//2 + 1, column=1, columnspan=5, sticky='ew', padx=5, pady=5)
        
        # Sexe
        ttk.Label(grid_frame, text="Sexe*:", font=('Arial', 9, 'bold')).grid(
            row=len(fields)//2 + 2, column=0, sticky='w', padx=5, pady=5)
        
        sexe_frame = ttk.Frame(grid_frame)
        sexe_frame.grid(row=len(fields)//2 + 2, column=1, columnspan=5, sticky='w', padx=5, pady=5)
        
        for value, text in [("masculin", "Masculin"), ("feminin", "Féminin"), ("autre", "Autre")]:
            ttk.Radiobutton(sexe_frame, text=text, variable=self.form_vars['sexe'], 
                           value=value).pack(side='left', padx=(0, 15))
    
    def create_travel_section(self, parent):
        """Section informations de voyage"""
        # En-tête
        ttk.Label(parent, text="Réservation de Vol (Optionnel)", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Option de création de réservation
        ttk.Checkbutton(parent, text="Créer une réservation immédiatement",
                       variable=self.form_vars['create_reservation'],
                       command=self.toggle_reservation_fields).pack(anchor='w', pady=5)
        
        # Frame pour les champs de réservation
        self.reservation_frame = ttk.Frame(parent)
        self.reservation_frame.pack(fill='x', pady=10)
        
        # Sélection du vol
        ttk.Label(self.reservation_frame, text="Vol:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5)
        
        self.vol_combo = ttk.Combobox(self.reservation_frame, textvariable=self.form_vars['vol_numero'],
                                     width=40, state='readonly')
        self.vol_combo.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Charger les vols disponibles
        self.load_available_flights()
        
        # Désactiver initialement
        self.toggle_reservation_fields()
    
    def load_available_flights(self):
        """Charge la liste des vols disponibles"""
        try:
            vols = []
            all_flights = self.data_controller.get_all_vols()
            
            for flight_data in all_flights:
                vol = flight_data['vol']
                if vol.statut.value in ['programme', 'en_attente']:  # Vols acceptant encore des passagers
                    depart = getattr(vol.aeroport_depart, 'code_iata', 'N/A')
                    arrivee = getattr(vol.aeroport_arrivee, 'code_iata', 'N/A')
                    date_str = vol.heure_depart.strftime('%Y-%m-%d %H:%M')
                    
                    vol_str = f"{vol.numero_vol} - {depart}→{arrivee} - {date_str}"
                    vols.append(vol_str)
            
            self.vol_combo['values'] = vols
            
        except Exception as e:
            print(f"Erreur lors du chargement des vols: {e}")
            self.vol_combo['values'] = []
    
    def toggle_reservation_fields(self):
        """Active/désactive les champs de réservation"""
        if self.form_vars['create_reservation'].get():
            self.vol_combo.config(state='readonly')
        else:
            self.vol_combo.config(state='disabled')
    
    def create_buttons(self, parent):
        """Crée les boutons du dialogue"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Créer Passager",
                  command=self.create_passenger).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Annuler",
                  command=self.cancel).pack(side='right', padx=5)
    
    def create_passenger(self):
        """Crée le passager"""
        if not self.validate_data():
            return
        
        try:
            # Préparer les données
            passenger_data = {
                'nom': self.form_vars['nom'].get().strip(),
                'prenom': self.form_vars['prenom'].get().strip(),
                'sexe': self.form_vars['sexe'].get(),
                'adresse': self.form_vars['adresse'].get().strip(),
                'numero_passeport': self.form_vars['numero_passeport'].get().strip()
            }
            
            # Ajouter les champs optionnels
            if self.form_vars['date_naissance'].get():
                try:
                    passenger_data['date_naissance'] = datetime.strptime(
                        self.form_vars['date_naissance'].get(), '%Y-%m-%d')
                except ValueError:
                    pass
            
            if self.form_vars['numero_telephone'].get():
                passenger_data['numero_telephone'] = self.form_vars['numero_telephone'].get()
            
            if self.form_vars['email'].get():
                passenger_data['email'] = self.form_vars['email'].get()
            
            # Créer le passager
            passager_id = self.data_controller.create_passager(**passenger_data)
            
            # Créer la réservation si demandée
            if self.form_vars['create_reservation'].get() and self.form_vars['vol_numero'].get():
                try:
                    vol_str = self.form_vars['vol_numero'].get()
                    vol_numero = vol_str.split(' - ')[0]  # Extraire le numéro de vol
                    
                    reservation_id = self.data_controller.create_reservation(passager_id, vol_numero)
                    messagebox.showinfo("Succès", 
                                      f"Passager {passenger_data['prenom']} {passenger_data['nom']} créé avec succès!\n"
                                      f"Réservation créée pour le vol {vol_numero}")
                except Exception as e:
                    messagebox.showwarning("Réservation", 
                                         f"Passager créé, mais erreur lors de la réservation:\n{e}")
            else:
                messagebox.showinfo("Succès", 
                                  f"Passager {passenger_data['prenom']} {passenger_data['nom']} créé avec succès!")
            
            self.result = passager_id
            
            # Callback si défini
            if self.callback:
                self.callback(passager_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création du passager:\n{e}")
    
    def validate_data(self):
        """Valide les données saisies"""
        errors = []
        
        # Champs obligatoires
        required_fields = [
            ('nom', "Nom"),
            ('prenom', "Prénom")
        ]
        
        for field, label in required_fields:
            if not self.form_vars[field].get().strip():
                errors.append(f"• {label} est obligatoire")
        
        # Validation email
        email = self.form_vars['email'].get().strip()
        if email and '@' not in email:
            errors.append("• Format d'email invalide")
        
        # Validation date de naissance
        date_naiss = self.form_vars['date_naissance'].get().strip()
        if date_naiss:
            try:
                datetime.strptime(date_naiss, '%Y-%m-%d')
            except ValueError:
                errors.append("• Format de date de naissance invalide (AAAA-MM-JJ)")
        
        # Validation réservation
        if self.form_vars['create_reservation'].get() and not self.form_vars['vol_numero'].get():
            errors.append("• Veuillez sélectionner un vol pour la réservation")
        
        if errors:
            messagebox.showerror("Erreurs de validation", "\n".join(errors))
            return False
        
        return True
    
    def cancel(self):
        """Annule la création"""
        if messagebox.askyesno("Confirmer", "Abandonner la création du passager ?"):
            self.dialog.destroy()


# Fonctions d'intégration pour les vues existantes

def integrate_flight_dialog(view):
    """Intègre le dialogue de création de vol dans une vue"""
    def show_add_flight_dialog():
        dialog = FlightCreationDialog(view, view.data_controller, 
                                     callback=lambda flight_id: view.refresh_data())
        view.wait_window(dialog.dialog)
    
    view.show_add_flight_dialog = show_add_flight_dialog
    return view

def integrate_personnel_dialog(view):
    """Intègre le dialogue de création de personnel dans une vue"""
    def show_add_personnel_dialog():
        dialog = PersonnelCreationDialog(view, view.data_controller,
                                        callback=lambda personnel_id: view.refresh_data())
        view.wait_window(dialog.dialog)
    
    view.show_add_personnel_dialog = show_add_personnel_dialog
    return view

def integrate_passenger_dialog(view):
    """Intègre le dialogue de création de passager dans une vue"""
    def show_add_passenger_dialog():
        dialog = PassengerCreationDialog(view, view.data_controller,
                                        callback=lambda passager_id: view.refresh_data())
        view.wait_window(dialog.dialog)
    
    view.show_add_passenger_dialog = show_add_passenger_dialog
    return view