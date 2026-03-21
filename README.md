# Groupe 7 — Métriques Qualité AAV

**Plateforme d'Analytics et de Reporting pour la Gestion Pédagogique des Acquis d'Apprentissage Visés (AAV)**

Une API REST moderne construite avec **FastAPI** et **SQLAlchemy** pour suivre, analyser et rapporter la progression des apprenants dans un système d'apprentissage structuré autour des Acquis d'Apprentissage Visés (AAV).

---

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Architecture](#architecture)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [API Endpoints](#api-endpoints)
- [Tests](#tests)
- [Structure du projet](#structure-du-projet)
- [Stack technologique](#stack-technologique)
- [Notes techniques](#notes-techniques)
- [Développeurs](#développeurs)

---

## 🎯 Vue d'ensemble

Ce projet fournit une solution complète pour les équipes pédagogiques afin de :

- **Monitorer** la progression des apprenants vers les objectifs d'apprentissage (AAV)
- **Détecter** automatiquement les AAV problématiques (trop difficiles, fragiles, ignorés)
- **Analyser** les patterns d'apprentissage et les points de blocage
- **Générer** des rapports détaillés en JSON, CSV et PDF
- **Visualiser** les KPI et les métriques de qualité via un tableau de bord

---

## ✨ Fonctionnalités principales

### 🚨 Système d'Alertes Intelligentes
- Détection automatique des AAV **problématiques**
- Catégories d'alerte :
  - **Difficiles** : AAV avec faible taux de succès
  - **Fragiles** : AAV où les apprenants progressent mais rechutent
  - **Inutilisés** : AAV sans tentatives récentes
  - **Bloquants** : AAV prérequis critiques non maîtrisés

### 📊 Calcul de Métriques
- **Taux de succès** : % d'apprenants ayant maîtrisé l'AAV
- **Couverture pédagogique** : % d'AAV utilisés dans les activités
- **Utilisabilité** : Nombre de tentatives et d'apprenants engagés
- **Progression** : Évolution du niveau de maîtrise dans le temps

### 📄 Génération de Rapports
- Formats supportés : **JSON**, **CSV**, **PDF** (généré nativement sans dépendances externes)
- Types de rapports :
  - Par AAV (détails complets, métriques, apprenants concernés)
  - Par apprenant (progression personnalisée, lacunes identifiées)
  - Par discipline (couverture, efficacité pédagogique)
  - Périodiques (snapshots temporels)

### 📈 Tableau de Bord
- Vue d'ensemble des KPI (indicateurs de performance clés)
- Graphiques et statistiques globales
- Filtrage par discipline et cohort
- Data exportable

### 🔄 Comparaisons Analytiques
- Comparer disciplines entre elles
- Analyser les différences de progression entre groupes
- Identifier les meilleures pratiques pédagogiques

---

## 🏗️ Architecture

### Architecture en couches

```
┌─────────────────────────────────────┐
│     API REST - FastAPI              │
│  (Routers: alerts, reports, etc.)   │
├─────────────────────────────────────┤
│     Services (Métier)               │
│  (Calculs, génération, détection)   │
├─────────────────────────────────────┤
│     Data Access Layer               │
│  (SQLAlchemy ORM, Repositories)     │
├─────────────────────────────────────┤
│     Base de données                 │
│  (SQLite - platonAAV.db)            │
└─────────────────────────────────────┘
```

### Flux de données

```
Requête HTTP
    ↓
Router (aavs.py, alerts.py, etc.)
    ↓
Service (alert_detector.py, metric_calculator.py, etc.)
    ↓
Database Models (SQLAlchemy ORM)
    ↓
SQLite Database
    ↓
Response JSON/CSV/PDF
```

---

## 🛠️ Installation

### Prérequis

- **Python** 3.9 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel, pour cloner le dépôt)

### Étapes d'installation

#### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd projet_python
```

#### 2. Créer un environnement virtuel

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les dépendances principales sont :
- **FastAPI** (0.104.0+) : Framework web asynchrone
- **Uvicorn** (0.24.0+) : Serveur ASGI
- **Pydantic** (2.5.0+) : Validation et sérialisation
- **SQLAlchemy** (2.0.0+) : ORM SQL
- **Pytest** (7.4.0+) : Framework de test

#### 4. Initialiser la base de données

La base de données SQLite (`platonAAV.db`) est **automatiquement créée** au premier lancement du serveur.

```bash
# La création se fait lors du démarrage :
uvicorn app.main:app --reload
```

---

## 🚀 Démarrage rapide

### Lancer le serveur de développement

```bash
# Depuis le répertoire racine
uvicorn app.main:app --reload
```

**Résultat :**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Accéder à l'API

| Ressource | URL |
|-----------|-----|
| 📚 **Swagger UI** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| 📖 **ReDoc** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |
| 🔧 **OpenAPI Schema** | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) |

### Commande de démarrage complète (one-liner)

**Installation complète + Tests + Serveur :**

macOS / Linux:
```bash
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
pytest --cov=app tests/ && \
uvicorn app.main:app --reload
```

Windows:
```bash
python -m venv venv && ^
.\venv\Scripts\activate && ^
pip install -r requirements.txt && ^
pytest --cov=app tests/ && ^
uvicorn app.main:app --reload
```

**Explications :**
1. `python3 -m venv venv` - Crée l'environnement virtuel
2. `source venv/bin/activate` - Active l'environnement virtuel
3. `pip install -r requirements.txt` - Installe toutes les dépendances
4. `pytest --cov=app tests/` - Lance tous les tests avec rapport de couverture
5. `uvicorn app.main:app --reload` - Lance le serveur de développement

---

## 📡 API Endpoints

### 🎓 AAVs (Acquis d'Apprentissage Visés)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/aavs` | Récupérer tous les AAV (filtrage par discipline possible) |
| `GET` | `/aavs/{aav_id}` | Détails complets d'un AAV spécifique |
| `POST` | `/aavs/` | Créer un nouvel AAV |
| `PUT` | `/aavs/{aav_id}` | Mettre à jour un AAV |
| `DELETE` | `/aavs/{aav_id}` | Supprimer un AAV |

**Exemple :**
```bash
curl http://127.0.0.1:8000/aavs?discipline=Mathématiques
```

### 🚨 Alertes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/alerts` | Lister toutes les alertes détectées |
| `GET` | `/alerts?type=difficult` | Filtrer par type d'alerte |
| `GET` | `/alerts/{alert_id}` | Détails d'une alerte |

**Types d'alerte :** `difficult`, `fragile`, `unused`, `blocking`

### 📊 Métriques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/metrics/aav/{aav_id}` | Calculer les métriques d'un AAV |
| `GET` | `/metrics/discipline/{discipline}` | Métriques par discipline |
| `GET` | `/metrics/learner/{learner_id}` | Progression d'un apprenant |

**Métriques retournées :**
- `success_rate` : Taux de succès (0.0 - 1.0)
- `coverage` : Couverture pédagogique
- `usability` : Utilisabilité (nombre d'apprenants)
- `progression` : Progression temporelle

### 📄 Rapports

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/reports/aav/{aav_id}?format=json` | Rapport complet sur un AAV |
| `GET` | `/reports/learner/{learner_id}?format=pdf` | Progression personnalisée |
| `GET` | `/reports/discipline/{discipline}?format=csv` | Données de discipline |

**Formats supportés :** `json`, `csv`, `pdf`

### 📈 Tableau de Bord

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/dashboard` | Vue d'ensemble des KPI |
| `GET` | `/dashboard/health` | État général de l'ontologie |

### 🔄 Comparaisons

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/metrics/compare` | Comparer deux disciplines |
| `GET` | `/metrics/compare?d1=Math&d2=Français` | Comparaison détaillée |

### 📚 Sessions et Activités

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/sessions` | Lister les sessions |
| `GET` | `/activities` | Lister les activités pédagogiques |
| `POST` | `/activities/` | Créer une activité |

---

## 🧪 Tests

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

### Coverage (couverture de tests)

```bash
pytest --cov=app tests/
```

---

## 📂 Structure du projet

```
projet_python/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # Point d'entrée FastAPI
│   ├── database.py                # Configuration SQLAlchemy & ORM models
│   │
│   ├── model/
│   │   ├── __init__.py
│   │   └── model.py               # Schémas Pydantic (API)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── metric_calculator.py   # Calcul des métriques (24 fonctions)
│   │   ├── dashboard_data.py      # Préparation données dashboard
│   │   ├── alert_detector.py      # Détection des alertes
│   │   └── report_generator.py    # Génération de rapports JSON/CSV/PDF
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── aavs.py                # CRUD AAV
│   │   ├── alerts.py              # Endpoints alertes
│   │   ├── metrics.py             # Endpoints métriques
│   │   ├── reports.py             # Endpoints rapports
│   │   ├── dashboard.py           # Endpoints tableau de bord
│   │   ├── comparaison.py         # Endpoints comparaisons
│   │   ├── sessions.py            # Endpoints sessions
│   │   ├── types.py               # Endpoints types
│   │   └── activitePedagogique.py # CRUD activités
│   │
│   ├── helper/
│   │   ├── __init__.py
│   │   └── tables.py              # Utilitaires helper
│   │
│   └── __pycache__/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures pytest
│   ├── test_metric.py             # Tests métriques
│   ├── test_dashboard.py          # Tests dashboard
│   ├── test_generate.py           # Tests génération rapports
│   └── test_services.py           # Tests services
│
├── platonAAV.db                   # Base de données SQLite
├── donnees_test.sql               # Jeu de données test/démo
├── requirements.txt               # Dépendances Python
├── pytest.ini                     # Configuration pytest
├── description_groupe_7.yaml      # Metadata du projet
└── README.md                      # Ce fichier
```

### Descriptions des répertoires clés

#### `/app/services/`
**Contient la logique métier isolée des endpoints API**
- `metric_calculator.py` : 24 fonctions de calcul de métriques
- `dashboard_data.py` : Agrégation et structuration des données pour le tableau de bord
- `alert_detector.py` : Algorithmes de détection des problèmes pédagogiques
- `report_generator.py` : Génération multi-format (JSON, CSV, PDF natif)

#### `/app/routers/`
**Endpoints RESTful organisés par domaine**
- Chaque router encapsule les endpoints d'un domaine métier
- Utilise les services pour la logique
- Retourne les schémas Pydantic validés

#### `/app/model/`
**Schémas de données pour API**
- Basés sur Pydantic v2
- Séparation claire : ORM models dans `database.py`, schémas API dans `model.py`
- Évite les boucles circulaires d'import

---

## 💻 Stack technologique

| Composant | Technologie | Version |
|-----------|------------|---------|
| **Framework Web** | FastAPI | 0.104.0+ |
| **Serveur ASGI** | Uvicorn | 0.24.0+ |
| **ORM** | SQLAlchemy | 2.0.0+ |
| **Base de données** | SQLite3 | Native |
| **Validation** | Pydantic | 2.5.0+ |
| **Tests** | Pytest | 7.4.0+ |
| **Python** | 3.9+ | Requis |

### Pourquoi ces technologies ?

- **FastAPI** : Framework moderne, asynchrone, avec documentation auto-générée
- **SQLAlchemy** : ORM puissant, migrations faciles, requêtes complexes
- **Pydantic** : Validation robuste avec messages d'erreur clairs
- **SQLite** : Base légère, portable, sans serveur externe
- **Pytest** : Framework de test flexible avec fixtures et plugins

---

## 🔧 Notes techniques

### Génération PDF Native

Le projet inclut une implémentation originale de génération PDF dans `services/report_generator.py` qui crée des fichiers PDF valides **directement au format binaire**, sans dépendre de librairies externes comme ReportLab ou FPDF.

**Avantages :**
- ✅ Zéro dépendance supplémentaire
- ✅ Contrôle complet sur le format
- ✅ Rapports structurés et professionnels

### Architecture ORM

**Séparation des modèles :**
- `app/database.py` : SQLAlchemy ORM models (AAVModel, ApprenantModel, etc.)
- `app/model/model.py` : Pydantic schemas (AAV, Apprenant, etc.)

**Bénéfices :**
- Évite les boucles circulaires d'import
- Schémas API indépendants de la structure DB
- Validation robuste côté API

### Documentation des Services

Chaque fonction de service inclut :
- **Docstring détaillée** en français/anglais
- **Type hints** complets (entrées et sorties)
- **Exemples d'usage** quand pertinent
- **Notes** sur les dépendances

Exemple :
```python
def calculate_success_rate(aav_id: int, db: Session) -> float:
    """
    Calcule le taux de succès d'un AAV.
    
    Le taux de succès est le pourcentage d'apprenants ayant maîtrisé l'AAV
    (niveau de maîtrise >= 0.9).
    
    Args:
        aav_id (int): Identifiant de l'AAV
        db (Session): Session SQLAlchemy
    
    Returns:
        float: Taux de succès (0.0 à 1.0)
    
    Example:
        >>> success = calculate_success_rate(42, db_session)
        >>> print(f"Success rate: {success:.1%}")
    """
```

---

## 📊 Jeu de données

### Données de test incluses

Le fichier `donnees_test.sql` contient un jeu de données complet pour :
- Tester les fonctionnalités
- Démontrer les rapports et alertes
- Valider les métriques

Charger les données :
```bash
sqlite3 platonAAV.db < donnees_test.sql
```

---

## 🐛 Dépannage

### Erreur : "ModuleNotFoundError: No module named 'app'"

**Solution :** Vérifier que vous êtes dans le répertoire racine du projet.
```bash
cd /Users/ramtani/Desktop/projet_python
```

### Erreur : "Database is locked"

**Solution :** Fermer les autres connexions à la base de données. SQLite supporte mal les accès concurrents.

### Tests qui échouent

**Solution :** Réinitialiser la base de données :
```bash
rm platonAAV.db
pytest  # Recréera la DB avec les données de test
```

### Ports déjà utilisés

**Solution :** Utiliser un autre port :
```bash
uvicorn app.main:app --reload --port 8001
```

---

## 📝 Convention de code

### Imports

```python
# Format : absolu depuis app/
from app.database import SessionLocal, AAVModel
from app.services.metric_calculator import calculate_success_rate
from app.model.model import AAV, MetriqueQualiteAAV
```

### Nommage

- **Modèles ORM** : `PascalCaseModel` (ex: `AAVModel`)
- **Schémas Pydantic** : `PascalCase` (ex: `AAV`)
- **Fonctions** : `snake_case` (ex: `calculate_success_rate`)
- **Constantes** : `UPPER_CASE`

### Docstrings

Utiliser le format Google style :
```python
def ma_fonction(param1: int, param2: str) -> bool:
    """Courte description.
    
    Description longue si nécessaire.
    
    Args:
        param1: Description du param
        param2: Description du param
    
    Returns:
        Description du retour
    """
```

---

## 👥 Développeurs

Projet développé par le **Groupe 7** dans le cadre de l'unité d'enseignement **Métriques et Qualité**.

| Rôle | Nom |
|------|-----|
| Responsable | Walid RAMTANI |
| Contributeurs | Groupe 7 |

---

## 📄 Licence

Ce projet est développé à titre académique. Les conditions d'utilisation sont définies par votre institution pédagogique.

---

## 🔗 Ressources utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Dernière mise à jour :** 21 mars 2026

