"""
Panneau de contrôle de la simulation temporelle
Affiché en permanence en haut de l'interface principale
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SimulationPanel(ttk.Frame):
    """Panneau de contrôle de la simulation temporelle"""
    
    def __init__(self, parent, simulator, sim_running_var, sim_speed_var, current_time_var):
        super().__init__(parent)
        
        self.simulator = simulator
        self.sim_running_var = sim_running_var
        self.sim_speed_var = sim_speed_var
        self.current_time_var = current_time_var
        
        # Variables d'affichage
        self.status_var = tk.StringVar(value="Arrêtée")
        self.next_event_var = tk.StringVar(value="Aucun événement")
        self.events_count_var = tk.StringVar(value="0")
        
        self.setup_ui()
        self.update_display()
        
        logger.info("Panneau de simulation initialisé")
    
    def setup_ui(self):
        """Configure l'interface du panneau"""
        
        # Frame principal avec bordure
        main_frame = ttk.LabelFrame(self, text="🎮 Contrôle de Simulation", padding=10)
        main_frame.pack(fill='x', padx=5, pady=2)
        
        # Première ligne : Temps et statut
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill='x', pady=(0, 5))
        
        # Temps de simulation (gauche)
        ttk.Label(time_frame, text="⏰ Temps simulé:", font=('Arial', 10, 'bold')).pack(side='left')
        time_label = ttk.Label(time_frame, textvariable=self.current_time_var, 
                              font=('Arial', 12, 'bold'), foreground='blue')
        time_label.pack(side='left', padx=(5, 20))
        
        # Statut (centre)
        ttk.Label(time_frame, text="Statut:", font=('Arial', 10)).pack(side='left')
        status_label = ttk.Label(time_frame, textvariable=self.status_var, 
                               font=('Arial', 10, 'bold'))
        status_label.pack(side='left', padx=(5, 20))
        
        # Événements programmés (droite)
        ttk.Label(time_frame, text="Événements:", font=('Arial', 10)).pack(side='left')
        events_label = ttk.Label(time_frame, textvariable=self.events_count_var, 
                               font=('Arial', 10, 'bold'))
        events_label.pack(side='left', padx=5)
        
        # Deuxième ligne : Contrôles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x')
        
        # Boutons de contrôle (gauche)
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side='left')
        
        self.start_btn = ttk.Button(buttons_frame, text="▶ Démarrer", 
                                   command=self.start_simulation, width=12)
        self.start_btn.pack(side='left', padx=2)
        
        self.pause_btn = ttk.Button(buttons_frame, text="⏸ Pause", 
                                   command=self.pause_simulation, width=12)
        self.pause_btn.pack(side='left', padx=2)
        
        self.stop_btn = ttk.Button(buttons_frame, text="⏹ Arrêter", 
                                  command=self.stop_simulation, width=12)
        self.stop_btn.pack(side='left', padx=2)
        
        # Séparateur
        ttk.Separator(controls_frame, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Contrôle de vitesse (centre)
        speed_frame = ttk.Frame(controls_frame)
        speed_frame.pack(side='left', padx=10)
        
        ttk.Label(speed_frame, text="Vitesse:", font=('Arial', 10)).pack(side='left')
        
        self.speed_combo = ttk.Combobox(speed_frame, textvariable=self.sim_speed_var,
                                       values=[0.1, 0.5, 1, 2, 5, 10, 30, 60], 
                                       width=8, state='readonly')
        self.speed_combo.pack(side='left', padx=5)
        self.speed_combo.bind('<<ComboboxSelected>>', self.on_speed_change)
        
        ttk.Label(speed_frame, text="x", font=('Arial', 10)).pack(side='left')
        
        # Boutons de vitesse rapide
        speed_buttons_frame = ttk.Frame(speed_frame)
        speed_buttons_frame.pack(side='left', padx=(10, 0))
        
        ttk.Button(speed_buttons_frame, text="0.5x", width=4,
                  command=lambda: self.set_speed(0.5)).pack(side='left', padx=1)
        ttk.Button(speed_buttons_frame, text="1x", width=4,
                  command=lambda: self.set_speed(1)).pack(side='left', padx=1)
        ttk.Button(speed_buttons_frame, text="10x", width=4,
                  command=lambda: self.set_speed(10)).pack(side='left', padx=1)
        ttk.Button(speed_buttons_frame, text="60x", width=4,
                  command=lambda: self.set_speed(60)).pack(side='left', padx=1)
        
        # Séparateur
        ttk.Separator(controls_frame, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Contrôles avancés (droite)
        advanced_frame = ttk.Frame(controls_frame)
        advanced_frame.pack(side='right')
        
        ttk.Button(advanced_frame, text="⏩ Avance Rapide", 
                  command=self.fast_forward_dialog, width=15).pack(side='left', padx=2)
        ttk.Button(advanced_frame, text="🔄 Reset", 
                  command=self.reset_simulation, width=10).pack(side='left', padx=2)
        
        # Troisième ligne : Prochain événement
        event_frame = ttk.Frame(main_frame)
        event_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(event_frame, text="📅 Prochain événement:", font=('Arial', 9)).pack(side='left')
        event_label = ttk.Label(event_frame, textvariable=self.next_event_var, 
                              font=('Arial', 9), foreground='gray')
        event_label.pack(side='left', padx=5)
    
    def start_simulation(self):
        """Démarre la simulation"""
        self.simulator.start()
        self.sim_running_var.set(True)
        self.update_button_states()
        logger.info("Simulation démarrée depuis le panneau")
    
    def pause_simulation(self):
        """Met en pause la simulation"""
        self.simulator.pause()
        self.sim_running_var.set(False)
        self.update_button_states()
        logger.info("Simulation mise en pause")
    
    def stop_simulation(self):
        """Arrête la simulation"""
        self.simulator.stop()
        self.sim_running_var.set(False)
        self.update_button_states()
        logger.info("Simulation arrêtée")
    
    def reset_simulation(self):
        """Remet la simulation à zéro"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Confirmer", "Réinitialiser la simulation ?\nTous les événements programmés seront perdus."):
            self.simulator.stop()
            self.simulator.reset_to_default()
            self.sim_running_var.set(False)
            self.update_button_states()
            self.update_display()
            logger.info("Simulation réinitialisée")
    
    def on_speed_change(self, event=None):
        """Gestionnaire de changement de vitesse"""
        try:
            speed = float(self.sim_speed_var.get())
            self.simulator.set_speed(speed)
            logger.debug(f"Vitesse de simulation changée: {speed}x")
        except ValueError:
            logger.warning("Vitesse de simulation invalide")
    
    def set_speed(self, speed):
        """Définit directement la vitesse"""
        self.sim_speed_var.set(speed)
        self.simulator.set_speed(speed)
        logger.debug(f"Vitesse définie: {speed}x")
    
    def fast_forward_dialog(self):
        """Ouvre le dialogue d'avance rapide"""
        dialog = tk.Toplevel(self)
        dialog.title("Avance Rapide")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Contenu du dialogue
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Avancer la simulation jusqu'à:", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        # Options d'avance rapide
        option_var = tk.StringVar(value="duration")
        
        # Option 1: Durée
        duration_frame = ttk.Frame(main_frame)
        duration_frame.pack(fill='x', pady=5)
        
        ttk.Radiobutton(duration_frame, text="Avancer de:", variable=option_var, 
                       value="duration").pack(side='left')
        
        duration_var = tk.StringVar(value="1")
        duration_entry = ttk.Entry(duration_frame, textvariable=duration_var, width=5)
        duration_entry.pack(side='left', padx=5)
        
        unit_var = tk.StringVar(value="heures")
        unit_combo = ttk.Combobox(duration_frame, textvariable=unit_var,
                                 values=["minutes", "heures", "jours"], 
                                 width=10, state='readonly')
        unit_combo.pack(side='left', padx=5)
        
        # Option 2: Heure spécifique
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill='x', pady=5)
        
        ttk.Radiobutton(time_frame, text="Aller à:", variable=option_var, 
                       value="specific").pack(side='left')
        
        # Date
        date_var = tk.StringVar(value=self.simulator.current_time.strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(time_frame, textvariable=date_var, width=12)
        date_entry.pack(side='left', padx=5)
        
        # Heure
        time_var = tk.StringVar(value="12:00:00")
        time_entry = ttk.Entry(time_frame, textvariable=time_var, width=10)
        time_entry.pack(side='left', padx=5)
        
        # Option traitement des événements
        process_events = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Traiter les événements programmés", 
                       variable=process_events).pack(pady=15)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def execute_fast_forward():
            try:
                if option_var.get() == "duration":
                    # Avancer d'une durée
                    duration = float(duration_var.get())
                    unit = unit_var.get()
                    
                    if unit == "minutes":
                        delta = timedelta(minutes=duration)
                    elif unit == "heures":
                        delta = timedelta(hours=duration)
                    else:  # jours
                        delta = timedelta(days=duration)
                    
                    target_time = self.simulator.current_time + delta
                    
                else:
                    # Aller à une heure spécifique
                    target_datetime = datetime.strptime(f"{date_var.get()} {time_var.get()}", 
                                                      '%Y-%m-%d %H:%M:%S')
                    target_time = target_datetime
                
                # Exécuter l'avance rapide
                events_processed = self.simulator.fast_forward_to(target_time, process_events.get())
                
                # Mettre à jour l'affichage
                self.update_display()
                
                from tkinter import messagebox
                messagebox.showinfo("Avance Rapide", 
                                  f"Avance effectuée jusqu'à {target_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                  f"{events_processed} événements traités.")
                dialog.destroy()
                
            except ValueError as e:
                from tkinter import messagebox
                messagebox.showerror("Erreur", f"Format invalide: {e}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Erreur", f"Erreur lors de l'avance rapide: {e}")
        
        ttk.Button(btn_frame, text="Exécuter", command=execute_fast_forward).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=dialog.destroy).pack(side='left', padx=5)
    
    def update_button_states(self):
        """Met à jour l'état des boutons selon la simulation"""
        if self.simulator.is_running:
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal')
            self.stop_btn.config(state='normal')
            self.status_var.set("En cours")
        else:
            self.start_btn.config(state='normal')
            self.pause_btn.config(state='disabled')
            self.stop_btn.config(state='disabled')
            self.status_var.set("Arrêtée")
    
    def update_display(self):
        """Met à jour l'affichage du panneau"""
        try:
            # Mettre à jour le temps
            current_time = self.simulator.current_time
            self.current_time_var.set(current_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            # Mettre à jour le statut
            self.update_button_states()
            
            # Mettre à jour les événements
            scheduled_events = self.simulator.get_scheduled_events()
            self.events_count_var.set(str(len(scheduled_events)))
            
            # Prochain événement
            next_event_info = self.simulator.get_next_event_info()
            if next_event_info:
                event_text = f"{next_event_info['action']} à {next_event_info['scheduled_time'][:16]}"
                self.next_event_var.set(event_text)
            else:
                self.next_event_var.set("Aucun événement programmé")
            
            # Mettre à jour la vitesse affichée
            current_speed = self.simulator.speed_multiplier
            self.sim_speed_var.set(current_speed)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour panneau simulation: {e}")
    
    def get_simulation_info(self):
        """Retourne les informations de simulation pour autres composants"""
        return {
            'is_running': self.simulator.is_running,
            'current_time': self.simulator.current_time,
            'speed': self.simulator.speed_multiplier,
            'events_count': len(self.simulator.get_scheduled_events())
        }