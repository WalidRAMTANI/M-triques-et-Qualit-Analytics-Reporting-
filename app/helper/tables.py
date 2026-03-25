# projet7/tables.py
"""
Séparation claire des tables par origine.
Ce fichier permet de visualiser et comprendre quelle table
appartient à quelle partie (commune vs Groupe 7).

Pour initialiser toutes les tables, utiliser directement :
    from database import init_database
    init_database()

Ce fichier est une référence documentaire sur la structure des tables.
"""

# ==============================================================
# RÉFÉRENCES — Structure des tables (documentation)
# ==============================================================

# TABLE COMMUNE — AAV (Groupe 1)
SCHEMA_AAV = """
    aav (
        id_aav INTEGER PRIMARY KEY,
        nom TEXT NOT NULL,
        libelle_integration TEXT,
        discipline TEXT NOT NULL,
        enseignement TEXT,
        type_aav TEXT,              -- 'Atomique' | 'Composite (Chapitre)'
        description_markdown TEXT,
        prerequis_ids TEXT,         -- JSON: [1, 2, 3]
        prerequis_externes_codes TEXT,
        code_prerequis_interdisciplinaire TEXT,
        aav_enfant_ponderation TEXT, -- JSON: [[1, 0.5], [2, 0.5]]
        type_evaluation TEXT,
        ids_exercices TEXT,          -- JSON: [101, 102, 103]
        prompts_fabrication_ids TEXT,-- JSON: [201, 202]
        regles_progression TEXT,     -- JSON object
        is_active BOOLEAN DEFAULT 1,
        version INTEGER DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
"""

# TABLE COMMUNE — OntologyReference (Groupe 1)
SCHEMA_ONTOLOGY_REFERENCE = """
    ontology_reference (
        id_reference INTEGER PRIMARY KEY,
        discipline TEXT NOT NULL,
        aavs_ids_actifs TEXT NOT NULL, -- JSON: [1, 2, 3, 4, 5]
        description TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
"""

# TABLE COMMUNE — Apprenant (Groupe 2)
SCHEMA_APPRENANT = """
    apprenant (
        id_apprenant INTEGER PRIMARY KEY,
        nom_utilisateur TEXT NOT NULL UNIQUE,
        email TEXT,
        ontologie_reference_id INTEGER,
        statuts_actifs_ids TEXT,             -- JSON: [1, 2, 3]
        codes_prerequis_externes_valides TEXT,-- JSON: ["CODE1"]
        date_inscription TIMESTAMP,
        derniere_connexion TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
"""

# TABLE COMMUNE — StatutApprentissage (Groupe 3)
SCHEMA_STATUT_APPRENTISSAGE = """
    statut_apprentissage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_apprenant INTEGER NOT NULL,
        id_aav_cible INTEGER NOT NULL,
        niveau_maitrise REAL DEFAULT 0.0,  -- entre 0 et 1
        historique_tentatives_ids TEXT,    -- JSON: [1, 2, 3, 4, 5]
        date_debut_apprentissage TIMESTAMP,
        date_derniere_session TIMESTAMP,
        est_maitrise BOOLEAN               -- généré: niveau_maitrise >= 0.9
    )
"""

# TABLE COMMUNE — Tentative (Groupe 3)
SCHEMA_TENTATIVE = """
    tentative (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_exercice_ou_evenement INTEGER NOT NULL,
        id_apprenant INTEGER NOT NULL,
        id_aav_cible INTEGER NOT NULL,
        score_obtenu REAL,          -- entre 0 et 1
        date_tentative TIMESTAMP,
        est_valide BOOLEAN DEFAULT 0,
        temps_resolution_secondes INTEGER,
        metadata TEXT               -- JSON: détails supplémentaires
    )
"""

# ==============================================================
# TABLES GROUPE 7 — Analytics & Reporting
# (source: groupe7_metriques_qualite.md)
# ==============================================================

# TABLE GROUPE 7 — Métriques qualité calculées par AAV
SCHEMA_METRIQUE_QUALITE_AAV = """
    metrique_qualite_aav (
        id_metrique INTEGER PRIMARY KEY,
        id_aav INTEGER,
        score_covering_ressources REAL,  -- Score [0.0, 1.0]
        taux_succes_moyen REAL,          -- Moyenne des scores des tentatives
        est_utilisable BOOLEAN,          -- True si qualité suffisante
        nb_tentatives_total INTEGER,
        nb_apprenants_distincts INTEGER,
        ecart_type_scores REAL,          -- Mesure la variabilité (AAV fragile)
        date_calcul TIMESTAMP,
        periode_debut TIMESTAMP,         -- Analysis period
        periode_fin TIMESTAMP
    )
"""

# GROUP 7 TABLE — Automatically generated alerts
SCHEMA_ALERTE_QUALITE = """
    alerte_qualite (
        id_alerte INTEGER PRIMARY KEY,
        type_alerte TEXT,   -- 'difficulte', 'inutilise', 'fragile', 'risque'
        id_cible INTEGER,   -- ID of the AAV or learner
        nom_cible TEXT,
        severite TEXT,      -- 'faible', 'moyenne', 'haute'
        description TEXT,
        suggestions TEXT,   -- JSON array
        date_detection TIMESTAMP,
        statut TEXT         -- 'nouveau', 'en_cours', 'resolu', 'ignore'
    )
"""

# GROUP 7 TABLE — On-demand generated reports
SCHEMA_RAPPORT_PERIODIQUE = """
    rapport_periodique (
        id_rapport INTEGER PRIMARY KEY,
        type_rapport TEXT,     -- 'discipline', 'aav', 'student'
        id_cible INTEGER,
        date_generation TIMESTAMP,
        periode_debut TIMESTAMP,
        periode_fin TIMESTAMP,
        contenu TEXT,          -- JSON with data
        format_fichier TEXT    -- 'json', 'csv', 'pdf'
    )
"""

SCHEMA_ENSEIGNANT = """
            CREATE TABLE IF NOT EXISTS enseignant (
            id_enseignant INTEGER PRIMARY KEY,
            nom TEXT ,
            email TEXT,
            discipline TEXT, --JSON array: ["Mathématiques", "Physique"]
            date_creation TIMESTAMP
            )
"""

# ==============================================================
# CATALOGUE COMPLET
# ==============================================================

TABLES_COMMUNES = {
    "aav": SCHEMA_AAV,
    "ontology_reference": SCHEMA_ONTOLOGY_REFERENCE,
    "apprenant": SCHEMA_APPRENANT,
    "statut_apprentissage": SCHEMA_STATUT_APPRENTISSAGE,
    "tentative": SCHEMA_TENTATIVE,
}


TABLES_GROUPE_7 = {
    "metrique_qualite_aav": SCHEMA_METRIQUE_QUALITE_AAV,
    "alerte_qualite": SCHEMA_ALERTE_QUALITE,
    "rapport_periodique": SCHEMA_RAPPORT_PERIODIQUE,
}
