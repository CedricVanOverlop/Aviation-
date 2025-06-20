# Système de Gestion et Simulateur de Vols

## Description

Cette application développée en Python avec une interface graphique Tkinter permet de simuler et gérer toutes les opérations d'une compagnie aérienne. Elle offre un environnement complet pour la gestion des avions, aéroports, vols, passagers, réservations et personnel, ainsi que la simulation dynamique des vols avec suivi en temps réel.

## Architecture du Projet

```
├── src/                          # Code source principal
│   ├── core/                     # Logique métier et classes principales
│   │   ├── __init__.py
│   │   ├── aviation.py           # Classes Coordonnees, Avion, Aeroport, PisteAtterrissage
│   │   ├── enums.py              # Énumérations (TypeIntemperie, StatutVol, EtatAvion)
│   │   ├── gestion.py            # Gestion des retards, compagnie, etc.
│   │   ├── meteo.py              # Classe Meteo pour simulation météo
│   │   ├── personnes.py          # Classes Personne, Staff, Passager
│   │   ├── reservation.py        # Classe Reservation
│   │   └── vol.py                # Classe Vol et gestion des itinéraires
│   └── interfaces/               # Interface utilisateur avec Tkinter
│       ├── __init__.py
│       ├── composant.py          # Composants graphiques réutilisables
│       ├── flight_management.py # Fenêtres spécifiques à la gestion des vols
│       └── main_window.py        # Fenêtre principale de l'application
├── tests/                        # Tests unitaires automatisés
│   ├── __init__.py
│   ├── test_aviation.py
│   ├── test_enums.py
│   ├── test_gestion.py
│   ├── test_meteo.py
│   ├── test_personnes.py
│   ├── test_reservation.py
│   └── test_vol.py
├── main.py                       # Point d'entrée principal de l'application
├── run_tests.py                  # Script pour lancer les tests unitaires
└── README.md                     # Documentation du projet
```

## Fonctionnalités Détaillées

### 🛩️ Gestion des Avions
- Création et gestion complète des avions (capacité, modèle, autonomie, etc.)
- Suivi de l'état opérationnel et maintenance régulière
- Calcul automatique des besoins de maintenance
- Gestion des positions géographiques

### 🏢 Gestion des Aéroports
- Gestion des coordonnées géographiques et infrastructures
- Système de pistes d'atterrissage avec disponibilité
- Gestion des quais et terminaux
- Intégration des conditions météorologiques

### 🗺️ Gestion des Itinéraires
- Définition des trajets entre aéroports
- Calcul automatique des distances et durées de vol (algorithme Haversine)
- Gestion des vols directs et avec escales
- Optimisation des routes selon l'autonomie des avions

### 👥 Gestion des Passagers
- Enregistrement et gestion des profils passagers
- Système complet de réservation de vols
- Procédures de check-in et gestion des billets
- Historique détaillé des vols par passager
- Gestion des sièges et modifications de réservation

### ✈️ Gestion des Vols
- Planification et suivi en temps réel des vols
- Simulation dynamique de la progression des vols
- Mise à jour du statut des vols (à l'heure, retardé, annulé)
- Notification automatique des retards et annulations
- Calcul des compensations selon la réglementation

### 👨‍✈️ Gestion du Personnel
- Enregistrement des membres du personnel (pilotes, équipage)
- Gestion des disponibilités et affectations aux vols
- Suivi des heures de travail et limites réglementaires
- Système de qualification par métier

### 🌤️ Simulation Météorologique
- Modélisation des conditions météorologiques
- Impact sur les décisions de vol
- Recommandations automatiques selon les conditions
- Niveaux de risque et alertes

### 🖥️ Interface Utilisateur
- Interface graphique moderne et intuitive avec Tkinter
- Fenêtres dédiées pour chaque entité
- Composants réutilisables pour une expérience cohérente
- Tableaux de données interactifs
- Système de recherche et filtrage
- Notifications en temps réel

## Installation et Utilisation

### Prérequis
- Python 3.8 ou supérieur
- Tkinter (fourni avec Python)
- Modules standard Python (datetime, math, typing, etc.)

### Installation
1. Clonez ou téléchargez le projet
2. Assurez-vous que Python 3.8+ est installé
3. Aucune dépendance externe n'est requise

### Lancement de l'application
```bash
python main.py
```

### Exécution des tests unitaires
```bash
python run_tests.py
```

## Principales Classes du Système

### Module Core (Logique Métier)

#### 📍 Coordonnees
- Gestion des coordonnées GPS avec validation
- Calcul de distances avec la formule de Haversine
- Opérations de comparaison et conversion

#### ✈️ Avion
- Représentation complète d'un avion
- Gestion de l'état, capacité et maintenance
- Vérification des conditions de vol
- Suivi des heures de vol et localisation

#### 🏢 Aeroport
- Gestion des aéroports et infrastructures
- Système de pistes avec disponibilité
- Intégration météorologique
- Gestion du trafic aérien

#### 🎫 Vol
- Planification et suivi détaillé des vols
- Gestion des passagers et équipage
- Calculs de distance, durée et autonomie
- Système de retards et modifications

#### 👤 Personne, Staff, Passager
- Hiérarchie de classes pour les personnes
- Gestion spécialisée du personnel et passagers
- Système de disponibilité et affectations
- Historique et réservations

#### 📋 Reservation
- Gestion complète des réservations
- Système de check-in et assignation de sièges
- Notifications automatiques
- Modifications et annulations

#### 🏢 Compagnie
- Orchestration globale des opérations
- Gestion centralisée de tous les éléments
- Statistiques et rapports
- Recherche et filtrage

### Module Interfaces (Interface Utilisateur)

#### 🖼️ Composants Réutilisables
- FormFrame : Formulaires automatiques
- DataTable : Tableaux de données avec tri
- SearchFrame : Recherche en temps réel
- StatusBar : Barre de statut avec horloge
- Dialogues et notifications

#### 🏠 Fenêtre Principale
- Tableau de bord avec statistiques
- Onglets pour différentes vues
- Actions rapides et navigation
- Système d'alertes intégré

#### ✈️ Gestion des Vols
- Interface complète de gestion des vols
- Création et modification de vols
- Simulation et contrôle en temps réel
- Gestion des retards et annulations

## Tests Unitaires

Le projet inclut une suite complète de tests unitaires couvrant :

- ✅ **test_aviation.py** : Tests des classes d'aviation
- ✅ **test_enums.py** : Tests des énumérations
- ✅ **test_meteo.py** : Tests du système météorologique
- ✅ **test_personnes.py** : Tests des classes de personnes
- ✅ **test_reservation.py** : Tests du système de réservation
- ✅ **test_vol.py** : Tests de la gestion des vols
- ✅ **test_gestion.py** : Tests de la gestion d'entreprise

### Couverture des Tests
- Tests de validation des données
- Tests des cas limites et erreurs
- Tests d'intégration entre modules
- Tests des calculs et algorithmes
- Mocks pour les dépendances externes

## Améliorations Apportées

### 🏗️ Architecture
- Architecture modulaire claire et extensible
- Séparation nette entre logique métier et interface
- Composants réutilisables et maintenables
- Gestion robuste des erreurs

### 📚 Documentation
- Documentation complète avec docstrings
- Annotations de types Python
- Commentaires explicatifs
- Guide d'utilisation détaillé

### 🧪 Qualité du Code
- Suite complète de tests unitaires
- Validation rigoureuse des données
- Gestion d'erreurs appropriée
- Respect des bonnes pratiques Python

### 🎨 Interface Utilisateur
- Interface ergonomique et intuitive
- Composants réutilisables
- Gestion efficace des événements
- Feedback visuel et notifications

### ⚡ Performance
- Algorithmes optimisés (Haversine, recherche)
- Mise à jour en temps réel
- Gestion efficace de la mémoire
- Interface responsive

## Perspectives d'Extension

### 💾 Persistance des Données
- Intégration d'une base de données (SQLite, PostgreSQL)
- Sauvegarde et restauration automatiques
- Historique complet des opérations
- Synchronisation multi-utilisateurs

### 🌐 Interface Web
- Extension vers une interface web moderne
- API REST pour intégration externe
- Interface mobile responsive
- Tableau de bord en temps réel

### 🌍 Fonctionnalités Avancées
- Système de gestion tarifaire
- Intégration de paiement en ligne
- Gestion multi-compagnies
- Rapports et analytics avancés

### 🌤️ Simulation Avancée
- Modèles météorologiques complexes
- Simulation d'événements aléatoires
- Intelligence artificielle pour optimisation
- Prédiction et recommandations

### 🌐 Intégration Externe
- APIs de données météorologiques réelles
- Intégration avec systèmes de réservation
- Connexion aux systèmes aéroportuaires
- Notifications push et SMS

## Support et Maintenance

### 🛠️ Maintenabilité
- Code clair et bien documenté
- Architecture modulaire facilement extensible
- Tests automatisés pour la stabilité
- Gestion des versions et migrations

### 👥 Collaboration
- Structure adaptée au travail en équipe
- Séparation claire des responsabilités
- Documentation technique complète
- Standards de codage respectés

### 🔧 Débogage et Support
- Logs détaillés et traçabilité
- Gestion d'erreurs informative
- Outils de diagnostic intégrés
- Documentation de dépannage

## Utilisation

### Démarrage Rapide
1. Lancez l'application avec `python main.py`
2. Explorez le tableau de bord pour voir les statistiques
3. Utilisez "Gestion > Vols" pour créer votre premier vol
4. Testez la simulation avec différentes conditions météo

### Fonctionnalités Principales
- **Tableau de bord** : Vue d'ensemble et actions rapides
- **Gestion des vols** : Création, modification, suivi
- **Simulation** : Test des conditions et événements
- **Statistiques** : Analyse des performances

### Conseils d'Utilisation
- Commencez par créer des aéroports et avions
- Ajoutez du personnel avant de programmer des vols
- Utilisez la simulation pour tester différents scénarios
- Consultez régulièrement les statistiques

---

**© 2025 - Système de Gestion et Simulateur de Vols**  
*Projet Python Orienté Objet avec Interface Tkinter*
