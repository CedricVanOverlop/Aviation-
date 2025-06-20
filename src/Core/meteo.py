from .enums import TypeIntemperie

class Meteo:
    """Classe représentant les conditions météorologiques avec évaluation sécuritaire"""
    
    # Seuils de sécurité constants
    SEUIL_VENT_DANGER = 60.0      # km/h - Opérations interdites
    SEUIL_VENT_ATTENTION = 40.0   # km/h - Attention requise
    SEUIL_VENT_MODERE = 20.0       # km/h - Conditions modérées
    
    VISIBILITE_MIN_VFR = 5.0       # km - Vol à vue minimum
    VISIBILITE_MIN_IFR = 1.0       # km - Vol aux instruments minimum

    def __init__(self, temperature, vitesse_vent, intemperie, 
                 visibilite=10.0, pression=1013.25):
        """
        Initialise les conditions météorologiques.
        
        Args:
            temperature (float): Température en °C
            vitesse_vent (float): Vitesse du vent en km/h
            intemperie (TypeIntemperie ou str): Type d'intempérie
            visibilite (float): Visibilité en km (défaut: 10km)
            pression (float): Pression en hPa (défaut: 1013.25hPa)
        """
        self.temperature = float(temperature)
        self.vitesse_vent = max(0.0, float(vitesse_vent))  # Vent ne peut pas être négatif
        
        # Gestion flexible du type d'intempérie
        if isinstance(intemperie, str):
            # Conversion string vers enum
            try:
                self.intemperie = TypeIntemperie(intemperie.lower())
            except ValueError:
                # Si la valeur n'existe pas, utiliser AUCUNE par défaut
                self.intemperie = TypeIntemperie.AUCUNE
        elif isinstance(intemperie, TypeIntemperie):
            self.intemperie = intemperie
        else:
            self.intemperie = TypeIntemperie.AUCUNE
            
        self.visibilite = max(0.0, float(visibilite))
        self.pression = float(pression)

    def statut_vent(self):
        """
        Évalue le statut du vent pour la sécurité des vols.
        
        Returns:
            str: "danger", "attention", "modere", ou "ok"
        """
        if self.vitesse_vent >= self.SEUIL_VENT_DANGER:
            return "danger"
        elif self.vitesse_vent >= self.SEUIL_VENT_ATTENTION:
            return "attention"
        elif self.vitesse_vent >= self.SEUIL_VENT_MODERE:
            return "modere"
        else:
            return "ok"
    
    def est_pluvieux(self):
        """
        Vérifie s'il y a des précipitations.
        
        Returns:
            bool: True s'il y a des précipitations
        """
        return self.intemperie in [
            TypeIntemperie.PLUIE, 
            TypeIntemperie.NEIGE, 
            TypeIntemperie.ORAGE,
            TypeIntemperie.GRELE
        ]
    
    def est_vol_possible(self, is_ifr=False):
        """
        Évalue si les conditions permettent le vol.
        
        Args:
            is_ifr (bool): True pour vol IFR, False pour vol VFR
            
        Returns:
            bool: True si le vol est possible
        """
        # Vérification intempéries dangereuses
        if self.intemperie.est_risquee():
            return False
            
        # Vérification vent
        if self.vitesse_vent >= self.SEUIL_VENT_DANGER:
            return False
            
        # Vérification visibilité selon type de vol
        if is_ifr:
            return self.visibilite >= self.VISIBILITE_MIN_IFR
        else:
            return self.visibilite >= self.VISIBILITE_MIN_VFR
    
    def obtenir_niveau_risque(self):
        """
        Retourne le niveau de risque général.
        
        Returns:
            str: "eleve", "modere", ou "faible"
        """
        if (self.intemperie.est_risquee() or 
            self.vitesse_vent >= self.SEUIL_VENT_DANGER):
            return "eleve"
        elif (self.vitesse_vent >= self.SEUIL_VENT_ATTENTION or
              self.visibilite < self.VISIBILITE_MIN_VFR or
              self.est_pluvieux()):
            return "modere"
        else:
            return "faible"
    
    def obtenir_recommandation_vent(self):
        """Retourne une recommandation basée sur le vent"""
        statut = self.statut_vent()
        recommandations = {
            "danger": "Vent dangereux. Opérations aériennes interdites.",
            "attention": "Vent fort. Attention particulière requise.",
            "modere": "Vent modéré. Opérations légèrement affectées.",
            "ok": "Conditions de vent favorables."
        }
        return recommandations.get(statut, "Conditions inconnues")
    
    def obtenir_recommandation_visibilite(self):
        """Retourne une recommandation basée sur la visibilité"""
        if self.visibilite < self.VISIBILITE_MIN_IFR:
            return "Visibilité critique. Tous vols interdits."
        elif self.visibilite < self.VISIBILITE_MIN_VFR:
            return "Visibilité faible. Vols IFR uniquement."
        else:
            return "Excellente visibilité. Tous types de vols possibles."
    
    def obtenir_recommandation_vol(self):
        """Retourne une recommandation générale pour les vols"""
        if self.est_vol_possible(is_ifr=False):
            return "Conditions excellentes pour tous types de vols."
        elif self.est_vol_possible(is_ifr=True):
            return "Conditions acceptables pour vols IFR uniquement."
        else:
            return "Conditions défavorables. Vols déconseillés."
    
    def obtenir_rapport_complet(self):
        """
        Retourne un rapport météo complet.
        
        Returns:
            dict: Rapport détaillé des conditions
        """
        return {
            'temperature': self.temperature,
            'vitesse_vent': self.vitesse_vent,
            'statut_vent': self.statut_vent(),
            'intemperie': self.intemperie.obtenir_nom_affichage(),
            'est_pluvieux': self.est_pluvieux(),
            'visibilite': self.visibilite,
            'pression': self.pression,
            'niveau_risque': self.obtenir_niveau_risque(),
            'vol_vfr_possible': self.est_vol_possible(is_ifr=False),
            'vol_ifr_possible': self.est_vol_possible(is_ifr=True),
            'recommandation_vent': self.obtenir_recommandation_vent(),
            'recommandation_visibilite': self.obtenir_recommandation_visibilite(),
            'recommandation_generale': self.obtenir_recommandation_vol()
        }
    
    # Méthodes compatibles avec l'ancien code
    def wind_status(self):
        """Alias pour compatibilité (équivalent à statut_vent)"""
        return self.statut_vent()
    
    def __str__(self):
        """Représentation textuelle conviviale"""
        return (f"Météo: {self.temperature}°C, Vent: {self.vitesse_vent}km/h ({self.statut_vent()}), "
                f"Intempérie: {self.intemperie.obtenir_nom_affichage()}, "
                f"Visibilité: {self.visibilite}km")
    
    def __repr__(self):
        """Représentation pour débogage"""
        return (f"Meteo(temperature={self.temperature}, vitesse_vent={self.vitesse_vent}, "
                f"intemperie={self.intemperie}, visibilite={self.visibilite}, "
                f"pression={self.pression})")
    
    def __eq__(self, other):
        """Compare deux objets Meteo"""
        if not isinstance(other, Meteo):
            return NotImplemented
        return (abs(self.temperature - other.temperature) < 0.1 and
                abs(self.vitesse_vent - other.vitesse_vent) < 0.1 and
                self.intemperie == other.intemperie and
                abs(self.visibilite - other.visibilite) < 0.1)
    
    def __hash__(self):
        """Hash pour utilisation dans sets/dicts"""
        return hash((round(self.temperature, 1),
                     round(self.vitesse_vent, 1),
                     self.intemperie,
                     round(self.visibilite, 1)))