import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from enum import Enum

class SimulationSpeed(Enum):
    """Vitesses de simulation disponibles"""
    PAUSE = 0
    REAL_TIME = 1
    SPEED_10X = 10
    SPEED_60X = 60  # 1 heure = 1 minute
    SPEED_100X = 100
    SPEED_360X = 360  # 1 jour = 4 minutes

class SimulationEngine:
    """Moteur de simulation temps réel pour les vols"""
    
    def __init__(self, data_manager):
        """
        Initialise le moteur de simulation.
        
        Args:
            data_manager: Instance du gestionnaire de données
        """
        self.data_manager = data_manager
        self.simulation_time = datetime.now()
        self.real_start_time = datetime.now()
        self.simulation_start_time = datetime.now()
        
        # Contrôles de simulation
        self.speed = SimulationSpeed.PAUSE
        self.is_running = False
        self.is_paused = True
        
        # Thread de simulation
        self._simulation_thread = None
        self._stop_event = threading.Event()
        
        # Callbacks pour les événements
        self.callbacks = {
            'time_update': [],
            'flight_update': [],
            'flight_departure': [],
            'flight_arrival': [],
            'flight_delay': [],
            'statistics_update': []
        }
        
        # Historique des événements
        self.event_log = []
        
        print("🕐 Moteur de simulation initialisé")
    
    def add_callback(self, event_type: str, callback: Callable):
        """
        Ajoute un callback pour un type d'événement.
        
        Args:
            event_type (str): Type d'événement
            callback (Callable): Fonction à appeler
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def remove_callback(self, event_type: str, callback: Callable):
        """Supprime un callback"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
    
    def trigger_callbacks(self, event_type: str, data: Any = None):
        """Déclenche tous les callbacks d'un type d'événement"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"❌ Erreur callback {event_type}: {e}")
    
    def set_simulation_time(self, new_time: datetime):
        """
        Définit l'heure de simulation.
        
        Args:
            new_time (datetime): Nouvelle heure de simulation
        """
        self.simulation_time = new_time
        self.real_start_time = datetime.now()
        self.simulation_start_time = new_time
        
        self.log_event("time_set", f"Heure simulation définie: {new_time}")
        self.trigger_callbacks('time_update', self.simulation_time)
    
    def set_speed(self, speed: SimulationSpeed):
        """
        Définit la vitesse de simulation.
        
        Args:
            speed (SimulationSpeed): Nouvelle vitesse
        """
        old_speed = self.speed
        self.speed = speed
        
        if speed == SimulationSpeed.PAUSE:
            self.pause()
        elif old_speed == SimulationSpeed.PAUSE and speed != SimulationSpeed.PAUSE:
            self.resume()
        
        # Réajuster les temps de référence
        if self.is_running and not self.is_paused:
            self.real_start_time = datetime.now()
            self.simulation_start_time = self.simulation_time
        
        self.log_event("speed_change", f"Vitesse changée: x{speed.value}")
        print(f"🕐 Vitesse simulation: x{speed.value}")
    
    def start(self):
        """Démarre la simulation"""
        if self.is_running:
            print("⚠️ Simulation déjà en cours")
            return
        
        self.is_running = True
        self.is_paused = (self.speed == SimulationSpeed.PAUSE)
        self._stop_event.clear()
        
        self.real_start_time = datetime.now()
        self.simulation_start_time = self.simulation_time
        
        self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._simulation_thread.start()
        
        self.log_event("simulation_start", "Simulation démarrée")
        print("▶️ Simulation démarrée")
    
    def pause(self):
        """Met en pause la simulation"""
        if not self.is_running or self.is_paused:
            return
        
        self.is_paused = True
        self.log_event("simulation_pause", "Simulation en pause")
        print("⏸️ Simulation en pause")
    
    def resume(self):
        """Reprend la simulation"""
        if not self.is_running or not self.is_paused:
            return
        
        self.is_paused = False
        self.real_start_time = datetime.now()
        self.simulation_start_time = self.simulation_time
        
        self.log_event("simulation_resume", "Simulation reprise")
        print("▶️ Simulation reprise")
    
    def stop(self):
        """Arrête la simulation"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.is_paused = True
        self._stop_event.set()
        
        if self._simulation_thread and self._simulation_thread.is_alive():
            self._simulation_thread.join(timeout=1.0)
        
        self.log_event("simulation_stop", "Simulation arrêtée")
        print("⏹️ Simulation arrêtée")
    
    def reset(self):
        """Remet à zéro la simulation"""
        self.stop()
        self.simulation_time = datetime.now()
        self.speed = SimulationSpeed.PAUSE
        self.event_log.clear()
        
        self.log_event("simulation_reset", "Simulation remise à zéro")
        print("🔄 Simulation remise à zéro")
    
    def fast_forward(self, hours: int):
        """
        Avance rapidement la simulation.
        
        Args:
            hours (int): Nombre d'heures à avancer
        """
        old_time = self.simulation_time
        self.simulation_time += timedelta(hours=hours)
        
        # Mise à jour des temps de référence
        if self.is_running and not self.is_paused:
            self.real_start_time = datetime.now()
            self.simulation_start_time = self.simulation_time
        
        self.log_event("fast_forward", f"Avance rapide: +{hours}h")
        self.trigger_callbacks('time_update', self.simulation_time)
        
        # Traiter tous les événements qui ont eu lieu pendant cette période
        self._process_time_jump(old_time, self.simulation_time)
        
        print(f"⏩ Avance rapide: +{hours}h → {self.simulation_time.strftime('%Y-%m-%d %H:%M')}")
    
    def _simulation_loop(self):
        """Boucle principale de simulation"""
        last_update = time.time()
        
        while self.is_running and not self._stop_event.is_set():
            current_time = time.time()
            
            if not self.is_paused and self.speed.value > 0:
                # Calcul du temps écoulé
                real_elapsed = current_time - last_update
                sim_elapsed = real_elapsed * self.speed.value
                
                # Mise à jour du temps de simulation
                old_sim_time = self.simulation_time
                self.simulation_time += timedelta(seconds=sim_elapsed)
                
                # Déclencher les callbacks de mise à jour
                self.trigger_callbacks('time_update', self.simulation_time)
                
                # Traitement des vols
                self._process_flights()
                
                last_update = current_time
            
            # Pause pour éviter une consommation CPU excessive
            time.sleep(0.1)
    
    def _process_flights(self):
        """Traite l'état de tous les vols actifs"""
        flights = self.data_manager.get_flights()
        updated_flights = []
        
        for flight in flights:
            original_status = flight.get('statut', 'programme')
            updated_flight = self._update_flight_status(flight)
            
            if updated_flight.get('statut') != original_status:
                # Le statut a changé, déclencher les callbacks appropriés
                self._handle_flight_status_change(updated_flight, original_status)
            
            updated_flights.append(updated_flight)
        
        # Sauvegarder les vols mis à jour
        if updated_flights:
            data = self.data_manager.load_data('flights')
            data['flights'] = updated_flights
            self.data_manager.save_data('flights', data)
    
    def _update_flight_status(self, flight: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour le statut d'un vol selon l'heure actuelle.
        
        Args:
            flight (Dict): Données du vol
            
        Returns:
            Dict: Vol mis à jour
        """
        current_status = flight.get('statut', 'programme')
        
        # Parser les heures (format ISO ou string)
        try:
            if isinstance(flight.get('heure_depart'), str):
                departure_time = datetime.fromisoformat(flight['heure_depart'])
            else:
                departure_time = flight.get('heure_depart')
            
            if isinstance(flight.get('heure_arrivee_prevue'), str):
                arrival_time = datetime.fromisoformat(flight['heure_arrivee_prevue'])
            else:
                arrival_time = flight.get('heure_arrivee_prevue')
        except:
            # Si problème de parsing, pas de mise à jour
            return flight
        
        # Logique de progression automatique
        if current_status == 'programme':
            # Passage à "en_attente" 30 min avant départ
            if self.simulation_time >= departure_time - timedelta(minutes=30):
                flight['statut'] = 'en_attente'
                
        elif current_status == 'en_attente':
            # Passage à "en_vol" à l'heure de départ
            if self.simulation_time >= departure_time:
                flight['statut'] = 'en_vol'
                flight['heure_depart_reelle'] = self.simulation_time.isoformat()
                
        elif current_status == 'en_vol':
            # Passage à "atterri" à l'heure d'arrivée
            if self.simulation_time >= arrival_time:
                flight['statut'] = 'atterri'
                flight['heure_arrivee_reelle'] = self.simulation_time.isoformat()
                
        elif current_status == 'atterri':
            # Passage à "termine" 30 min après atterrissage
            if self.simulation_time >= arrival_time + timedelta(minutes=30):
                flight['statut'] = 'termine'
        
        return flight
    
    def _handle_flight_status_change(self, flight: Dict[str, Any], old_status: str):
        """Gère les changements de statut de vol"""
        new_status = flight.get('statut')
        flight_number = flight.get('numero_vol', 'N/A')
        
        # Log de l'événement
        self.log_event(
            "flight_status_change", 
            f"Vol {flight_number}: {old_status} → {new_status}"
        )
        
        # Callbacks spécifiques
        if new_status == 'en_vol' and old_status == 'en_attente':
            self.trigger_callbacks('flight_departure', flight)
            print(f"🛫 Vol {flight_number} décollé")
            
        elif new_status == 'atterri' and old_status == 'en_vol':
            self.trigger_callbacks('flight_arrival', flight)
            print(f"🛬 Vol {flight_number} atterri")
        
        # Callback général de mise à jour
        self.trigger_callbacks('flight_update', flight)
    
    def _process_time_jump(self, start_time: datetime, end_time: datetime):
        """Traite tous les événements lors d'un saut dans le temps"""
        flights = self.data_manager.get_flights()
        
        for flight in flights:
            # Simuler la progression complète du vol
            temp_time = start_time
            while temp_time <= end_time:
                self.simulation_time = temp_time
                updated_flight = self._update_flight_status(flight)
                temp_time += timedelta(minutes=15)  # Par pas de 15 minutes
    
    def add_flight_delay(self, flight_number: str, delay_minutes: int, reason: str = ""):
        """
        Ajoute un retard à un vol.
        
        Args:
            flight_number (str): Numéro du vol
            delay_minutes (int): Retard en minutes
            reason (str): Raison du retard
        """
        flights = self.data_manager.get_flights()
        
        for i, flight in enumerate(flights):
            if flight.get('numero_vol') == flight_number:
                # Ajouter le retard aux heures
                try:
                    if isinstance(flight.get('heure_depart'), str):
                        departure = datetime.fromisoformat(flight['heure_depart'])
                    else:
                        departure = flight.get('heure_depart')
                    
                    if isinstance(flight.get('heure_arrivee_prevue'), str):
                        arrival = datetime.fromisoformat(flight['heure_arrivee_prevue'])
                    else:
                        arrival = flight.get('heure_arrivee_prevue')
                    
                    delay_delta = timedelta(minutes=delay_minutes)
                    
                    flight['heure_depart'] = (departure + delay_delta).isoformat()
                    flight['heure_arrivee_prevue'] = (arrival + delay_delta).isoformat()
                    flight['statut'] = 'retarde'
                    
                    if 'retards' not in flight:
                        flight['retards'] = []
                    
                    flight['retards'].append({
                        'duree_minutes': delay_minutes,
                        'raison': reason,
                        'heure_ajout': self.simulation_time.isoformat()
                    })
                    
                    # Sauvegarder
                    data = self.data_manager.load_data('flights')
                    data['flights'][i] = flight
                    self.data_manager.save_data('flights', data)
                    
                    self.log_event("flight_delay", f"Vol {flight_number}: +{delay_minutes}min - {reason}")
                    self.trigger_callbacks('flight_delay', flight)
                    
                    print(f"⏰ Vol {flight_number} retardé de {delay_minutes}min: {reason}")
                    return True
                    
                except Exception as e:
                    print(f"❌ Erreur ajout retard vol {flight_number}: {e}")
                    return False
        
        print(f"❌ Vol {flight_number} non trouvé")
        return False
    
    def log_event(self, event_type: str, message: str):
        """Enregistre un événement dans le log"""
        event = {
            'timestamp': self.simulation_time.isoformat(),
            'real_time': datetime.now().isoformat(),
            'type': event_type,
            'message': message
        }
        
        self.event_log.append(event)
        
        # Limiter la taille du log
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-500:]
    
    def get_simulation_info(self) -> Dict[str, Any]:
        """Retourne les informations de simulation"""
        return {
            'simulation_time': self.simulation_time.isoformat(),
            'speed': self.speed.name,
            'speed_value': self.speed.value,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'events_count': len(self.event_log),
            'uptime_seconds': (datetime.now() - self.real_start_time).total_seconds() if self.is_running else 0
        }
    
    def get_recent_events(self, count: int = 50) -> List[Dict[str, Any]]:
        """Retourne les événements récents"""
        return self.event_log[-count:] if self.event_log else []