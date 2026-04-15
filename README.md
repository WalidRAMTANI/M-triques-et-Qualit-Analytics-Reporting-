# Groupe 7 — Métriques Qualité AAV

**Plateforme d'Analytics et de Reporting pour la Gestion Pédagogique des Acquis d'Apprentissage Visés (AAV)**

API REST construite avec **FastAPI** et **SQLAlchemy**, associée à une interface graphique desktop native développée avec **Flet**, pour le suivi, l'analyse et le reporting de la progression des apprenants dans un système structuré autour des AAV (Acquis d'Apprentissage Visés).

---

## Demarrage Express

### Windows (PowerShell)

**1. Installer les dependances**
```powershell
python -m venv venv; .\venv\Scripts\pip.exe install -r requirements.txt; .\venv\Scripts\python.exe app/populate_gui_data.py
```

**2. Lancer l'API (backend)**
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --port 8000
```

**3. Lancer l'application (dans un second terminal)**
```powershell
.\venv\Scripts\python.exe gui\src\main.py
```

---

### macOS / Linux / WSL

**1. Installer les dependances**
```bash
python3 -m venv venv_linux && ./venv_linux/bin/pip install -r requirements.txt && ./venv_linux/bin/python app/populate_gui_data.py
```

**2. Lancer l'API (backend)**
```bash
./venv_linux/bin/uvicorn app.main:app --port 8000
```

**3. Lancer l'application (dans un second terminal)**
```bash
./venv_linux/bin/python gui/src/main.py
```

> L'API est accessible sur http://127.0.0.1:8000/docs une fois demarre.
> Le backend doit etre lance avant l'interface graphique.

---

## Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Architecture](#architecture)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Interface Graphique Flet](#interface-graphique-flet)
- [API Endpoints](#api-endpoints)
- [Tests](#tests)
- [Structure du projet](#structure-du-projet)
- [Stack technologique](#stack-technologique)
- [Notes techniques](#notes-techniques)
- [Développeurs](#développeurs)

---

## Vue d'ensemble

Ce projet fournit une solution complète pour les équipes pédagogiques :

- **Monitorer** la progression des apprenants vers les objectifs d'apprentissage (AAV)
- **Détecter** automatiquement les AAV problématiques (trop difficiles, fragiles, ignorés)
- **Analyser** les patterns d'apprentissage et les points de blocage
- **Générer** des rapports détaillés en JSON, CSV et PDF
- **Visualiser** l'ontologie des compétences via des graphes de dépendances
- **Simuler** des tentatives d'apprenants pour valider les parcours pédagogiques

---

## Fonctionnalités principales

### Système d'Alertes Intelligentes

- Détection automatique des AAV **problématiques**
- Catégories d'alerte :
  - **Difficiles** : AAV avec faible taux de succès
  - **Fragiles** : AAV où les apprenants progressent mais rechutent
  - **Inutilisés** : AAV sans tentatives récentes
  - **Bloquants** : AAV prérequis critiques non maîtrisés

### Calcul de Métriques

- **Taux de succès** : pourcentage d'apprenants ayant maîtrisé l'AAV
- **Couverture pédagogique** : pourcentage d'AAV utilisés dans les activités
- **Utilisabilité** : nombre de tentatives et d'apprenants engagés
- **Progression** : évolution du niveau de maîtrise dans le temps

### Génération de Rapports

- Formats supportés : **JSON**, **CSV**, **PDF** (généré nativement sans dépendances externes)
- Types de rapports :
  - Par AAV (détails complets, métriques, apprenants concernés)
  - Par apprenant (progression personnalisée, lacunes identifiées)
  - Par discipline (couverture, efficacité pédagogique)

### Gestion des AAV

- Création d'AAV avec validation Pydantic côté client (formulaire Flet)
- Liaison des dépendances parent/enfant (AAV Composite / Atomique)
- Gestion des prérequis avec visualisation en graphe

### Suivi des Apprenants

- Sélection d'un apprenant via liste déroulante
- Consultation de la fiche de maîtrise (niveau par AAV)
- Simulation de tentatives pédagogiques avec calcul automatique du niveau

---

## Architecture

### Architecture en couches

```
+-----------------------------------------+
|   Interface Graphique Desktop (Flet)    |
|   (Pages: AAVs, Apprenants, Graphes...) |
+-----------------------------------------+
              |  HTTP / REST
+-----------------------------------------+
|     API REST - FastAPI                  |
|  (Routers: aavs, attempts, statuts...)  |
+-----------------------------------------+
|     Services Metier                     |
|  (Calculs, generation, detection)       |
+-----------------------------------------+
|     Data Access Layer                   |
|  (SQLAlchemy ORM)                       |
+-----------------------------------------+
|     Base de donnees SQLite              |
|  (platonAAV.db)                         |
+-----------------------------------------+
```

### Flux de données

```
Action Utilisateur (Flet GUI)
    |
Validation Pydantic Client-Side
    |
Requete HTTP (httpx / requests)
    |
Router FastAPI (aavs.py, attempts.py, etc.)
    |
Service Metier (metric_calculator.py, etc.)
    |
SQLAlchemy ORM
    |
SQLite (platonAAV.db)
    |
Reponse JSON -> Flet UI
```

---

## Installation

### Prérequis

- **Python** 3.10 ou supérieur
- **pip** (gestionnaire de paquets Python)

### Étapes d'installation

#### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd M-triques-et-Qualit-Analytics-Reporting-
```

#### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Dépendances principales :

- **FastAPI** : framework web asynchrone
- **Uvicorn** : serveur ASGI
- **Pydantic v2** : validation et sérialisation, utilisée côté backend ET côté client GUI
- **SQLAlchemy** : ORM SQL
- **Flet** (0.84+) : framework interface graphique desktop Python
- **Matplotlib / NetworkX** : génération de graphes d'ontologies
- **httpx / requests** : appels HTTP depuis la GUI vers l'API

#### 4. Peupler la base de données

```bash
python app/populate_gui_data.py
```

Ce script injecte 15 entrées par table (Enseignants, AAVs, Apprenants, Sessions, StatutApprentissage, Tentatives) avec des relations parent/enfant entre AAVs.

---

## Démarrage rapide

### Lancer le backend (FastAPI)

```bash
# Windows
.\venv\Scripts\uvicorn.exe app.main:app --port 8000

# macOS / Linux
uvicorn app.main:app --port 8000
```

### Lancer l'interface graphique (Flet)

```bash
# Windows
.\venv\Scripts\python.exe gui\src\main.py

# macOS / Linux
python gui/src/main.py
```

### Accéder à la documentation API

| Ressource | URL |
|-----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI Schema | http://127.0.0.1:8000/openapi.json |

---

## Interface Graphique Flet

L'application desktop est organisée autour d'une barre de navigation latérale donnant accès aux modules suivants :

| Module | Description |
|--------|-------------|
| Referentiel des AAV | Liste filtrée, fiche détaillée avec Markdown, graphe ontologique |
| Referentiel Apprenants | Sélection, fiche de progression, simulation de tentatives |
| Historique Tentatives | Suivi des tentatives par apprenant et par AAV |
| Statuts Acquisition | Niveau de maîtrise par apprenant/AAV |
| Alertes Critiques | Détection et visualisation des AAV problématiques |
| Analyse des Métriques | KPI de qualité par discipline |
| Exploration Ontologies | Graphes de dépendances interactifs |
| Génération de Rapports | Export JSON, CSV, PDF |
| Moteur d'Exercices | Simulation et navigation de parcours |
| Module Comparaison | Comparaison inter-disciplines |
| Activités Académiques | CRUD des activités pédagogiques |
| Pilotage Sessions | Administration des sessions (mode Professeur) |
| Pilotage Dashboard | Vue KPI globale (mode Professeur) |

### Mode Professeur

L'accès aux fonctions d'administration (création d'AAV, suppression, pilotage) est conditionné à l'authentification via le bouton **"Authentification Admin"** dans la barre latérale.

### Validation Pydantic côté client

Tous les formulaires de saisie (création AAV, nouveau profil apprenant, simulation de tentative) utilisent les schemas Pydantic du backend avant tout envoi HTTP. Les erreurs de validation s'affichent directement dans la fenêtre de dialogue sans fermer le formulaire.

---

## API Endpoints

### AAVs (Acquis d'Apprentissage Visés)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/aavs/` | Lister tous les AAV (filtrage par discipline) |
| `GET` | `/aavs/{aav_id}` | Détails complets d'un AAV |
| `POST` | `/aavs/` | Créer un nouvel AAV |
| `PUT` | `/aavs/{aav_id}` | Mettre à jour un AAV |
| `DELETE` | `/aavs/{aav_id}` | Supprimer un AAV |

### Apprenants

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/learners/` | Lister tous les apprenants |
| `GET` | `/learners/{id}` | Fiche d'un apprenant |
| `POST` | `/learners/` | Créer un profil apprenant |
| `PUT` | `/learners/{id}` | Modifier un profil |
| `DELETE` | `/learners/{id}` | Supprimer un profil |
| `GET` | `/learners/{id}/progress` | Niveau de maîtrise par AAV |
| `GET` | `/learners/{id}/learning-status` | Statuts d'apprentissage détaillés |

### Tentatives

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/attempts/` | Lister les tentatives (filtres disponibles) |
| `GET` | `/attempts/{id}` | Détails d'une tentative |
| `POST` | `/attempts/` | Enregistrer une tentative (recalcul maîtrise automatique) |
| `DELETE` | `/attempts/{id}` | Supprimer une tentative |
| `POST` | `/attempts/{id}/process` | Retraiter une tentative et recalculer la progression |

### Statuts d'Apprentissage

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/learning-status` | Lister tous les statuts |
| `POST` | `/learning-status` | Créer un statut apprenant/AAV |
| `PUT` | `/learning-status/{id}` | Mettre à jour un statut |

### Alertes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/alerts` | Lister toutes les alertes détectées |

**Types d'alerte :** `difficult`, `fragile`, `unused`, `blocking`

### Métriques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/metrics/aav/{aav_id}` | Métriques d'un AAV |
| `GET` | `/metrics/discipline/{discipline}` | Métriques par discipline |
| `GET` | `/metrics/learner/{learner_id}` | Progression d'un apprenant |

### Rapports

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/reports/aav/{aav_id}?format=json` | Rapport complet sur un AAV |
| `GET` | `/reports/learner/{learner_id}?format=pdf` | Rapport de progression |
| `GET` | `/reports/discipline/{discipline}?format=csv` | Rapport par discipline |

### Sessions et Activités

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/sessions/` | Lister les sessions |
| `GET` | `/activities/` | Lister les activités |
| `POST` | `/activities/` | Créer une activité |

---

## Tests

### Exécuter tous les tests

```bash
pytest
```

### Exécuter avec verbose

```bash
pytest -v
```

### Exécuter un fichier de test spécifique

```bash
pytest tests/test_metric.py -v
```

### Coverage

```bash
pytest --cov=app tests/
```

---

## Structure du projet

```
M-triques-et-Qualit-Analytics-Reporting-/
|
+-- app/
|   +-- main.py                      # Point d'entree FastAPI, declaration des routers
|   +-- database.py                  # Configuration SQLAlchemy et modeles ORM
|   +-- populate_gui_data.py         # Script de peuplement base de donnees (15 entrees/table)
|   |
|   +-- model/
|   |   +-- model.py                 # Schemas Pydantic v2 (AAVCreate, TentativeCreate, etc.)
|   |   +-- schemas.py               # Schemas complementaires
|   |
|   +-- services/
|   |   +-- metric_calculator.py     # Calcul des metriques de qualite
|   |   +-- dashboard_data.py        # Agregation des donnees pour le tableau de bord
|   |   +-- alert_detector.py        # Detection des AAV problematiques
|   |   +-- report_generator.py      # Generation multi-format JSON/CSV/PDF
|   |   +-- maitrise.py              # Calcul du niveau de maitrise
|   |
|   +-- routers/
|       +-- aavs.py                  # CRUD AAV (avec discipline, type_aav, enfants_ids)
|       +-- attempts.py              # Gestion tentatives et recalcul de maitrise
|       +-- statuts.py               # Statuts d'apprentissage par apprenant/AAV
|       +-- learners.py              # CRUD apprenants et progression
|       +-- alerts.py                # Detection et exposition des alertes
|       +-- metrics.py               # Exposition des metriques
|       +-- reports.py               # Generation et export de rapports
|       +-- dashboard.py             # Vue d'ensemble KPI
|       +-- comparaison.py           # Comparaison inter-disciplines
|       +-- sessions.py              # Gestion des sessions
|       +-- activitePedagogique.py   # CRUD activites pedagogiques
|
+-- gui/
|   +-- src/
|       +-- main.py                  # Point d'entree Flet, navigation et permissions
|       +-- pages/
|           +-- aavs_page.py         # Referentiel AAV, filtres, detail Markdown, graphe
|           +-- learners_page.py     # Suivi apprenants, dropdown selection, simulation
|           +-- aav_detail_page.py   # Fiche technique detaillee d'un AAV
|           +-- attempts_page.py     # Historique des tentatives
|           +-- statuts_page.py      # Statuts d'apprentissage
|           +-- alert_page.py        # Alertes pedagogiques
|           +-- dashboard_page.py    # Tableau de bord KPI
|           +-- reports_page.py      # Generation de rapports
|           +-- sessions_page.py     # Gestion des sessions
|           +-- ontologies_page.py   # Exploration des graphes d'ontologie
|           +-- sidebar.py           # Barre de navigation laterale
|           +-- ...                  # Autres pages modules
|
+-- tests/
|   +-- conftest.py                  # Fixtures pytest
|   +-- test_metric.py               # Tests metriques
|   +-- test_dashboard.py            # Tests tableau de bord
|   +-- test_generate.py             # Tests generation rapports
|   +-- test_services.py             # Tests services
|
+-- platonAAV.db                     # Base de donnees SQLite
+-- requirements.txt                 # Dependances Python
+-- pytest.ini                       # Configuration pytest
+-- description_groupe_7.yaml        # Metadata du projet
+-- README.md                        # Ce fichier
```

---

## Stack technologique

| Composant | Technologie | Version |
|-----------|------------|---------|
| Framework Web | FastAPI | 0.104.0+ |
| Serveur ASGI | Uvicorn | 0.24.0+ |
| ORM | SQLAlchemy | 2.0.0+ |
| Base de donnees | SQLite3 | Native |
| Validation | Pydantic | 2.5.0+ |
| Interface Desktop | Flet | 0.84.0+ |
| Graphes | NetworkX + Matplotlib | Latest |
| HTTP Client | httpx / requests | Latest |
| Tests | Pytest | 7.4.0+ |
| Python | 3.10+ | Requis |

---

## Notes techniques

### Validation Pydantic côté client (GUI)

La GUI Flet utilise directement les schemas Pydantic du backend avant tout appel HTTP :

```python
from app.model.model import AAVCreate, TentativeCreate, LearnerCreate

def valider(ev):
    """Valide les donnees du formulaire via Pydantic puis soumet a l'API."""
    try:
        aav_create = AAVCreate(
            nom=champ_nom.value,
            discipline=champ_disc.value,
            ...
        )
        r = httpx.post(f"{BASE_URL}/aavs/", json=aav_create.model_dump())
    except ValidationError as ve:
        err_text.value = f"Erreur : {ve.errors()[0]['msg']}"
```

### Génération PDF Native

Le projet inclut une implémentation originale de génération PDF dans `services/report_generator.py` créant des fichiers valides directement au format binaire, sans dépendances externes.

### Architecture ORM

Séparation stricte des modèles :

- `app/database.py` : SQLAlchemy ORM models (`AAVModel`, `ApprenantModel`, `TentativeModel`, etc.)
- `app/model/model.py` : Pydantic schemas (`AAVCreate`, `Tentative`, `LearnerCreate`, etc.)

### Recalcul automatique de la maîtrise

Lors de chaque `POST /attempts/`, le backend recalcule automatiquement le `niveau_maitrise` de l'apprenant sur l'AAV cible en appliquant l'algorithme de `calculer_maitrise()` sur l'historique complet des tentatives.

### Convention de code

```python
# Ordre des imports dans tous les fichiers GUI
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Imports standards puis internes
import flet as ft
from pydantic import ValidationError
from app.model.model import AAVCreate
```

- **Modeles ORM** : `PascalCaseModel` (ex : `AAVModel`)
- **Schemas Pydantic** : `PascalCase` (ex : `AAVCreate`)
- **Fonctions** : `snake_case` (ex : `calculer_maitrise`)
- **Constantes** : `UPPER_CASE` (ex : `BASE_URL`)
- **Docstrings** : format Google style en français

---

## Dépannage

### Erreur : "ModuleNotFoundError: No module named 'app'"

Le chemin racine du projet doit etre dans `sys.path`. Verifier que chaque fichier GUI commence par :

```python
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

### Erreur : "Database is locked"

Fermer les autres connexions a la base de donnees. SQLite supporte mal les acces concurrents depuis plusieurs processus.

### Le backend ne repond pas

Verifier que Uvicorn est bien en cours d'execution sur le port 8000 avant de lancer la GUI Flet.

### Reinitialiser la base de donnees

```bash
del platonAAV.db
python app/populate_gui_data.py
```

---

## Développeurs

Projet réalisé par le **Groupe 7** dans le cadre de l'unité d'enseignement **Métriques et Qualité**.

| Role | Nom |
|------|-----|
| Responsable | Walid RAMTANI |
| Contributeurs | Groupe 7 |

---

## Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Flet Documentation](https://flet.dev/docs/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Dernière mise à jour :** Avril 2026
