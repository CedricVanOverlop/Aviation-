"""
Simulateur de temps avec accélération et gestion d'événements programmés
Permet de simuler le passage du temps à vitesse variable
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class ScheduledEvent:
    """Représente un événement programmé dans la simulation"""
    
    def __init__(self, event_time: datetime, event_type: str, 
                 target_id: str, action: str, data: Dict = None):
        self.id = str(uuid.uuid4())
        self.event_time = event_time
        self.event_type = event_type  # 'vol', 'avion', 'maintenance', 'personnel'
        self.target_id = target_id
        self.action = action  # 'decoller', 'atterrir', 'maintenance_start', etc.
        self.data = data or {}
        self.executed = False
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convertit l'événement en dictionnaire"""
        return {
            'id': self.id,
            'event_time': self.event_time.isoformat(),
            'event_type': self.event_type,
            'target_id': self.target_id,
            'action': self.action,
            'data': self.data,
            'executed': self.executed,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduledEvent':
        """Crée un événement depuis un dictionnaire"""
        event = cls(
            event_time=datetime.fromisoformat(data['event_time']),
            event_type=data['event_type'],
            target_id=data['target_id'],
            action=data['action'],
            data=data.get('data', {})
        )
        event.id = data['id']
        event.executed = data.get('executed', False)
        event.created_at = datetime.fromisoformat(data['created_at'])
        return event
    
    def __str__(self):
        return f"Event({self.event_type}/{self.action} @ {self.event_time.strftime('%H:%M:%S')})"
    
    def __lt__(self, other):
        return self.event_time < other.event_time

class TimeSimulator:
    """Simulateur de temps avec accélération et événements programmés"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_time = datetime.now()
        self.speed_multiplier = 1.0
        self.is_running = False
        self.last_real_time = datetime.now()
        
        # Gestion des événements
        self.scheduled_events: List[ScheduledEvent] = []
        self.event_handlers: Dict[str, Callable] = {}
        self.callbacks: List[Callable] = []
        
        # Thread de simulation
        self._simulation_thread = None
        self._stop_event = threading.Event()
        
        # Statistiques
        self.stats = {
            'events_executed': 0,
            'total_sim_time': timedelta(),
            'start_time': None
        }
        
        self.load_state()
        logger.info("Simulateur temporel initialisé")
    
    def load_state(self):
        """Charge l'état de la simulation depuis le stockage"""
        try:
            state = self.data_manager.load_data('simulation')
            self.current_time = datetime.fromisoformat(state['current_time'])
            self.speed_multiplier = state['speed_multiplier']
            self.is_running = state['is_running']
            
            # Charger les événements programmés
            self.scheduled_events = []
            for event_data in state.get('events_scheduled', []):
                try:
                    event = ScheduledEvent.from_dict(event_data)
                    self.scheduled_events.append(event)
                except Exception as e:
                    logger.warning(f"Impossible de charger l'événement: {e}")
            
            self.scheduled_events.sort()
            logger.info(f"État de simulation chargé: {len(self.scheduled_events)} événements programmés")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'état: {e}")
            self.reset_to_default()
    
    def save_state(self):
        """Sauvegarde l'état de la simulation"""
        try:
            state = {
                'current_time': self.current_time.isoformat(),
                'speed_multiplier': self.speed_multiplier,
                'is_running': self.is_running,
                'last_update': datetime.now().isoformat(),
                'events_scheduled': [event.to_dict() for event in self.scheduled_events if not event.executed]
            }
            self.data_manager.save_data('simulation', state)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'état: {e}")
    
    def reset_to_default(self):
        """Remet le simulateur à l'état par défaut"""
        self.current_time = datetime.now()
        self.speed_multiplier = 1.0
        self.is_running = False
        self.scheduled_events = []
        logger.info("Simulateur remis à l'état par défaut")
    
    def start(self):
        """Démarre la simulation"""
        if self.is_running:
            logger.warning("La simulation est déjà en cours")
            return
        
        self.is_running = True
        self.last_real_time = datetime.now()
        self.stats['start_time'] = datetime.now()
        self._stop_event.clear()
        
        # Démarrer le thread de simulation
        self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._simulation_thread.start()
        
        logger.info(f"Simulation démarrée (vitesse: {self.speed_multiplier}x)")
    
    def stop(self):
        """Arrête la simulation"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._simulation_thread and self._simulation_thread.is_alive():
            self._simulation_thread.join(timeout=1.0)
        
        self.save_state()
        logger.info("Simulation arrêtée")
    
    def pause(self):
        """Met en pause la simulation (alias pour stop)"""
        self.stop()
    
    def _simulation_loop(self):
        """Boucle principale de simulation (dans un thread séparé)"""
        while not self._stop_event.is_set() and self.is_running:
            try:
                self.update()
                time.sleep(0.1)  # 10 FPS
            except Exception as e:
                logger.error(f"Erreur dans la boucle de simulation: {e}")
                break
    
    def update(self):
        """Met à jour le temps simulé et traite les événements"""
        if not self.is_running:
            return
        
        # Calculer l'avancement du temps
        now = datetime.now()
        real_elapsed = (now - self.last_real_time).total_seconds()
        sim_elapsed = real_elapsed * self.speed_multiplier
        
        self.current_time += timedelta(seconds=sim_elapsed)
        self.last_real_time = now
        
        # Traiter les événements programmés
        self.process_scheduled_events()
        
        # Appeler les callbacks
        for callback in self.callbacks:
            try:
                callback(self.current_time)
            except Exception as e:
                logger.error(f"Erreur dans callback: {e}")
        
        # Sauvegarder périodiquement
        if int(now.timestamp()) % 30 == 0:  # Toutes les 30 secondes réelles
            self.save_state()
    
    def set_speed(self, multiplier: float):
        """Définit la vitesse de simulation"""
        old_speed = self.speed_multiplier
        self.speed_multiplier = max(0.1, min(100.0, multiplier))
        
        if abs(old_speed - self.speed_multiplier) > 0.001:
            logger.info(f"Vitesse de simulation changée: {old_speed}x → {self.speed_multiplier}x")
    
    def set_time(self, new_time: datetime):
        """Définit manuellement le temps de simulation"""
        old_time = self.current_time
        self.current_time = new_time
        self.last_real_time = datetime.now()
        
        logger.info(f"Temps de simulation modifié: {old_time} → {new_time}")
        
        # Vérifier si des événements doivent être traités
        self.process_scheduled_events()
    
    def add_callback(self, callback: Callable):
        """Ajoute une fonction à appeler à chaque mise à jour"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Retire une fonction des callbacks"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Enregistre un gestionnaire pour un type d'événement"""
        self.event_handlers[event_type] = handler
        logger.debug(f"Gestionnaire enregistré pour: {event_type}")
    
    def schedule_event(self, event_time: datetime, event_type: str, 
                      target_id: str, action: str, data: Dict = None) -> str:
        """Programme un événement à une heure donnée"""
        event = ScheduledEvent(event_time, event_type, target_id, action, data)
        
        # Insérer à la bonne position (liste triée)
        inserted = False
        for i, existing_event in enumerate(self.scheduled_events):
            if event.event_time <= existing_event.event_time:
                self.scheduled_events.insert(i, event)
                inserted = True
                break
        
        if not inserted:
            self.scheduled_events.append(event)
        
        logger.debug(f"Événement programmé: {event}")
        return event.id
    
    def cancel_event(self, event_id: str) -> bool:
        """Annule un événement programmé"""
        for event in self.scheduled_events:
            if event.id == event_id and not event.executed:
                self.scheduled_events.remove(event)
                logger.debug(f"Événement annulé: {event_id}")
                return True
        return False
    
    def get_scheduled_events(self, event_type: str = None, 
                           time_range: tuple = None) -> List[ScheduledEvent]:
        """Retourne les événements programmés selon des critères"""
        events = [e for e in self.scheduled_events if not e.executed]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if time_range:
            start_time, end_time = time_range
            events = [e for e in events if start_time <= e.event_time <= end_time]
        
        return events
    
    def process_scheduled_events(self):
        """Traite les événements programmés qui doivent être exécutés"""
        events_to_execute = []
        
        for event in self.scheduled_events:
            if not event.executed and self.current_time >= event.event_time:
                events_to_execute.append(event)
        
        # Exécuter les événements
        for event in events_to_execute:
            self.execute_event(event)
    
    def execute_event(self, event: ScheduledEvent):
        """Exécute un événement programmé"""
        try:
            # Marquer comme exécuté
            event.executed = True
            
            # Log de l'événement
            message = f"[{event.event_type.upper()}] {event.action} pour {event.target_id}"
            self.log_event(message, event)
            
            # Appeler le gestionnaire approprié
            if event.event_type in self.event_handlers:
                handler = self.event_handlers[event.event_type]
                handler(event)
            else:
                logger.warning(f"Aucun gestionnaire pour le type d'événement: {event.event_type}")
            
            # Mettre à jour les statistiques
            self.stats['events_executed'] += 1
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'événement {event.id}: {e}")
    
    def log_event(self, message: str, event: ScheduledEvent = None):
        """Enregistre un événement dans le journal"""
        try:
            events_log = self.data_manager.load_data('events')
            
            log_entry = {
                'timestamp': self.current_time.isoformat(),
                'real_time': datetime.now().isoformat(),
                'message': message,
                'event_id': event.id if event else None,
                'sim_speed': self.speed_multiplier
            }
            
            events_log.append(log_entry)
            
            # Limiter la taille du log
            max_events = 1000
            if len(events_log) > max_events:
                events_log = events_log[-max_events:]
            
            self.data_manager.save_data('events', events_log)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du log: {e}")
    
    def schedule_recurring_event(self, start_time: datetime, interval: timedelta,
                                event_type: str, target_id: str, action: str,
                                data: Dict = None, max_occurrences: int = None) -> List[str]:
        """Programme un événement récurrent"""
        event_ids = []
        current_time = start_time
        occurrences = 0
        
        while max_occurrences is None or occurrences < max_occurrences:
            event_id = self.schedule_event(current_time, event_type, target_id, action, data)
            event_ids.append(event_id)
            current_time += interval
            occurrences += 1
            
            # Sécurité pour éviter les boucles infinies
            if occurrences > 10000:
                logger.warning("Limite de récurrence atteinte (10000)")
                break
        
        logger.info(f"Événements récurrents programmés: {len(event_ids)}")
        return event_ids
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de simulation"""
        uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta()
        
        return {
            'current_time': self.current_time.isoformat(),
            'is_running': self.is_running,
            'speed_multiplier': self.speed_multiplier,
            'events_scheduled': len([e for e in self.scheduled_events if not e.executed]),
            'events_executed': self.stats['events_executed'],
            'uptime_seconds': uptime.total_seconds(),
            'next_event': self.get_next_event_info()
        }
    
    def get_next_event_info(self) -> Optional[Dict]:
        """Retourne des informations sur le prochain événement"""
        pending_events = [e for e in self.scheduled_events if not e.executed]
        if not pending_events:
            return None
        
        next_event = min(pending_events, key=lambda e: e.event_time)
        time_until = next_event.event_time - self.current_time
        
        return {
            'event_type': next_event.event_type,
            'action': next_event.action,
            'target_id': next_event.target_id,
            'scheduled_time': next_event.event_time.isoformat(),
            'time_until_seconds': time_until.total_seconds()
        }
    
    def cleanup_executed_events(self, keep_last: int = 100):
        """Nettoie les événements exécutés anciens"""
        executed_events = [e for e in self.scheduled_events if e.executed]
        executed_events.sort(key=lambda e: e.event_time, reverse=True)
        
        # Garder seulement les N derniers événements exécutés
        events_to_keep = executed_events[:keep_last]
        pending_events = [e for e in self.scheduled_events if not e.executed]
        
        self.scheduled_events = pending_events + events_to_keep
        logger.info(f"Nettoyage effectué: {len(executed_events) - len(events_to_keep)} événements supprimés")
    
    def fast_forward_to(self, target_time: datetime, 
                       process_events: bool = True) -> int:
        """Avance rapidement jusqu'à un moment donné"""
        if target_time <= self.current_time:
            logger.warning("Le temps cible est dans le passé")
            return 0
        
        original_time = self.current_time
        events_processed = 0
        
        if process_events:
            # Traiter tous les événements jusqu'au temps cible
            while self.current_time < target_time:
                # Trouver le prochain événement
                next_events = [e for e in self.scheduled_events 
                             if not e.executed and e.event_time > self.current_time]
                
                if not next_events:
                    # Aucun événement, aller directement au temps cible
                    self.current_time = target_time
                    break
                
                next_event = min(next_events, key=lambda e: e.event_time)
                
                if next_event.event_time > target_time:
                    # Le prochain événement est après le temps cible
                    self.current_time = target_time
                    break
                
                # Avancer jusqu'à cet événement et le traiter
                self.current_time = next_event.event_time
                self.execute_event(next_event)
                events_processed += 1
        else:
            # Avancer directement sans traiter les événements
            self.current_time = target_time
        
        self.last_real_time = datetime.now()
        elapsed = self.current_time - original_time
        
        logger.info(f"Avance rapide effectuée: +{elapsed}, {events_processed} événements traités")
        return events_processed