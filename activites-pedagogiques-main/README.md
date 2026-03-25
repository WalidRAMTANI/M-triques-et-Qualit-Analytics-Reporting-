# Python Projet Groupe 4 L3 

## Participants :
Phan Tran
Sergei Poliakov

## Description :
Ce projet implémante une API REST permettant de gérer les **activités pédagogiques**, **exercices**, et
**sessions** pour les apprenants.

Elle permet de notamment :
- créer et gérer des activités pédagogiques
- associer des exercices à une activité
- lancer des sessions pour les apprenants
- enregistrer les tentatives et la progression

## Lancer le serveur (depuis la racine) :

### 1️⃣ Activer l'environnement virtuel
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2️⃣ Installation des dépendances (si nécessaire)
```bash
pip3 install -r requirements.txt
```

### 3️⃣ Lancer le serveur en mode développement
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 📍 Accéder à l'application:
- **API Documentation (Swagger)**: http://127.0.0.1:8000/docs
- **Alternative Documentation (ReDoc)**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

### 4️⃣ Lancer en production (optionnel)
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Endpoints principaux :

#### Activités pédagogiques
    GET /activities 
    POST /activities
    GET /activities/{id_activite}
    PUT /activities/{id_activite}
    PATCH /activities/{id_activite}
    DELETE /activities/{id_activite}

#### Types d'Activités
    GET /activities/types

#### Gestion des Exercices d'une Activité
    GET /activities/{id_activite}/exercises
    POST /activities/{id_activite}/exercises/{id_exercise}
    PUT /activities/{id_activite}/exercises/reorder
    DELETE /activities/{id_activite}/exercises/{id_exercise}

#### Endpoints Apprenants (Activités)
    POST /activities/{id_activite}/start - Démarre une session avec message
    POST /activities/{id_activite}/submit-attempt - Soumet une tentative
    POST /activities/{id_activite}/complete - Finalise la session avec bilan

#### Sessions apprenant (Alternatives/Supplémentaires)
    GET /sessions/
    POST /sessions/
    GET /sessions/{id_session}/bilan
    POST /sessions/{id_session}/start
    POST /sessions/{id_session}/submit-attempt
    PATCH /sessions/{id_session}/cloturer

#### Types
    GET /types/

## Lancer tests (depuis la racine) :
    python tests/test_groupe4.py
    python tests/test_groupe4.py --url http://localhost:8000
    pytest
