"""
Vues et interfaces utilisateur pour les différentes fonctionnalités
"""

from .dashboard import DashboardView
from .flight_management import FlightManagementView
from .fleet_management import FleetManagementView
from .simulation_panel import SimulationPanel
from .event_log import EventLogView
from .creation_dialogs import FlightCreationDialog, PersonnelCreationDialog, PassengerCreationDialog

__all__ = [
    'DashboardView',
    'FlightManagementView', 
    'FleetManagementView',
    'SimulationPanel',
    'EventLogView'
]