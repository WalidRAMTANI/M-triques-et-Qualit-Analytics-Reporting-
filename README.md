# Groupe 7 — Métriques Qualité AAV

API d'analytics et de reporting pour les équipes pédagogiques, permettant de suivre et d'analyser les Acquis d'Apprentissage Visés (AAV).

Ce projet fournit des outils pour mesurer la progression des apprenants, détecter les points de blocage et générer des rapports détaillés sur l'état de l'ontologie pédagogique.

## 🚀 Fonctionnalités Clés

- **Système d'Alertes** : Détection automatique des AAV problématiques (difficiles, fragiles, inutilisés ou bloquants).
- **Génération de Rapports** : Création de rapports personnalisés par AAV, par apprenant ou par discipline.
  - Formats supportés : **JSON**, **CSV** et **PDF** (généré nativement).
- **Calcul de Métriques** : Taux de succès, couverture pédagogique, utilisabilité et progression.
- **Tableau de Bord** : Vue globale des indicateurs de performance (KPI) pour le suivi pédagogique.
- **Comparaisons** : Analyse comparative entre différentes disciplines ou cohorts d'apprenants.

## 🛠️ Installation et Configuration

### Prérequis

- Python 3.9+
- SQLite3

### Installation

1. **Cloner le répertoire**

   ```bash
   git clone <url-du-repo>
   cd "projet7 copie 2"
   ```

2. **Créer un environnement virtuel**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Sur macOS/Linux
   # Ou .\venv\Scripts\activate sur Windows
   ```

3. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialiser la base de données**
   La base de données SQLite (`platonAAV.db`) est automatiquement initialisée au premier lancement de l'application via `main.py`.

## 🏃 Utilisation

Pour démarrer le serveur de développement :

```bash
uvicorn app.main:app --reload
```

- **Documentation Swagger UI** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentation Redoc** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 🧪 Tests

Pour exécuter la suite de tests unitaires et d'intégration :

```bash
pytest
```

## 📂 Architecture du Projet

```text
.
├── main.py               # Point d'entrée FastAPI
├── database.py           # Configuration et accès SQLite
├── routers/              # Endpoints de l'API par module
│   ├── alerts.py
│   ├── reports.py
│   ├── metrics.py
│   └── dashboard.py
├── services/             # Logique métier et calculs
│   ├── alert_detector.py
│   ├── report_generator.py  # Inclut un générateur PDF natif
│   └── metric_calculator.py
├── model/                # Schémas Pydantic et modèles de données
├── tests/                # Tests automatisés
└── donnees_test.sql      # Jeu de données pour les tests et démos
```

## pour lancer le server, il faut activer l'environnement virtuel et lancer la commande suivante :

```bash
python3 -m venv venv && source venv/bin/activate && pip install fastapi uvicorn pydantic pytest && pytest tests/ && uvicorn app.main:app --reload
```

## 📝 Note Technique : Génération PDF

Le projet inclut une implémentation originale dans `services/report_generator.py` permettant de générer des fichiers PDF valides directement au format binaire, sans dépendance à des librairies externes comme ReportLab ou FPDF.

---

python3 -m venv venv && source venv/bin/activate && pip install fastapi uvicorn pydantic sqlalchemy pytest && pytest tests/ && uvicorn app.main:app --reload

_Développé par le Groupe 7 dans le cadre de l'unité d'enseignement Métriques et Qualité._
