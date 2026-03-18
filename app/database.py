# app/database.py
import json
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path
from model.model import MetriqueQualiteAAV, Rapport, Enseignant
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from datetime import datetime
# Configuration
DATABASE_URL = "sqlite:///./platonAAV.db"
engine = create_engine(
    DATABASE_URL
    )

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass

# ============================================
# MODÈLES SQLALCHEMY
# ============================================

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

class AAVModel(Base):
    __tablename__ = "aav"
    id_aav = Column(Integer, primary_key=True)
    nom = Column(String(200), nullable=False)
    libelle_integration = Column(Text)
    discipline = Column(String(100), nullable=False)
    enseignement = Column(Text)
    id_enseignant = Column(Integer, ForeignKey("enseignant.id_enseignant"))
    type_aav = Column(String(50))
    description_markdown = Column(Text)
    prerequis_ids = Column(JSONEncodedDict)
    prerequis_externes_codes = Column(JSONEncodedDict)
    code_prerequis_interdisciplinaire = Column(Text)
    aav_enfant_ponderation = Column(JSONEncodedDict)
    type_evaluation = Column(String(100))
    ids_exercices = Column(JSONEncodedDict)
    prompts_fabrication_ids = Column(JSONEncodedDict)
    regles_progression = Column(JSONEncodedDict)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    enseignant = relationship("EnseignantModel", back_populates="aavs")

class OntologyReferenceModel(Base):
    __tablename__ = "ontology_reference"
    id_reference = Column(Integer, primary_key=True)
    discipline = Column(String(100), nullable=False)
    aavs_ids_actifs = Column(JSONEncodedDict, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class ApprenantModel(Base):
    __tablename__ = "apprenant"
    id_apprenant = Column(Integer, primary_key=True)
    nom_utilisateur = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(200))
    ontologie_reference_id = Column(Integer, ForeignKey("ontology_reference.id_reference"))
    statuts_actifs_ids = Column(JSONEncodedDict)
    codes_prerequis_externes_valides = Column(JSONEncodedDict)
    date_inscription = Column(TIMESTAMP, server_default=func.current_timestamp())
    derniere_connexion = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)

class StatutApprentissageModel(Base):
    __tablename__ = "statut_apprentissage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"), nullable=False, index=True)
    id_aav_cible = Column(Integer, ForeignKey("aav.id_aav"), nullable=False, index=True)
    niveau_maitrise = Column(Float, default=0.0)
    historique_tentatives_ids = Column(JSONEncodedDict)
    date_debut_apprentissage = Column(TIMESTAMP, server_default=func.current_timestamp())
    date_derniere_session = Column(TIMESTAMP)
    est_maitrise = Column(Boolean)

class TentativeModel(Base):
    __tablename__ = "tentative"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_exercice_ou_evenement = Column(Integer, nullable=False)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"), nullable=False, index=True)
    id_aav_cible = Column(Integer, ForeignKey("aav.id_aav"), nullable=False, index=True)
    score_obtenu = Column(Float)
    date_tentative = Column(TIMESTAMP, server_default=func.current_timestamp(), index=True)
    est_valide = Column(Boolean, default=False)
    temps_resolution_secondes = Column(Integer)
    meta_data = Column("metadata", JSONEncodedDict)

class ActivitePedagogiqueModel(Base):
    __tablename__ = "activite_pedagogique"
    id_activite = Column(Integer, primary_key=True)
    nom = Column(String(200))
    description = Column(Text)
    type_activite = Column(String(100))
    ids_exercices_inclus = Column(JSONEncodedDict)
    discipline = Column(String(100))
    niveau_difficulte = Column(String(50))
    duree_estimee_minutes = Column(Integer)
    created_by = Column(Integer)
    created_at = Column(TIMESTAMP)

class SessionApprenantModel(Base):
    __tablename__ = "session_apprenant"
    id_session = Column(Integer, primary_key=True)
    id_activite = Column(Integer, ForeignKey("activite_pedagogique.id_activite"))
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"))
    date_debut = Column(TIMESTAMP)
    date_fin = Column(TIMESTAMP)
    statut = Column(String(50))
    progression_pourcentage = Column(Float)

class PromptFabricationAAVModel(Base):
    __tablename__ = "prompt_fabrication_aav"
    id_prompt = Column(Integer, primary_key=True)
    cible_aav_id = Column(Integer, ForeignKey("aav.id_aav"))
    type_exercice_genere = Column(String(100))
    prompt_texte = Column(Text)
    version_prompt = Column(Integer)
    created_by = Column(Integer)
    date_creation = Column(TIMESTAMP)
    is_active = Column(Boolean)
    meta_data = Column("metadata", JSONEncodedDict)

class ExerciceInstanceModel(Base):
    __tablename__ = "exercice_instance"
    id_exercice = Column(Integer, primary_key=True)
    id_prompt_source = Column(Integer, ForeignKey("prompt_fabrication_aav.id_prompt"))
    titre = Column(String(200))
    id_aav_cible = Column(Integer, ForeignKey("aav.id_aav"))
    type_evaluation = Column(String(100))
    contenu = Column(Text)
    difficulte = Column(String(50))
    date_generation = Column(TIMESTAMP)
    nb_utilisations = Column(Integer)
    taux_succes_moyen = Column(Float)

class DiagnosticRemediationModel(Base):
    __tablename__ = "diagnostic_remediation"
    id_diagnostic = Column(Integer, primary_key=True)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"))
    id_aav_source = Column(Integer, ForeignKey("aav.id_aav"))
    aav_racines_defaillants = Column(JSONEncodedDict)
    score_obtenu = Column(Float)
    date_diagnostic = Column(TIMESTAMP)
    profondeur_analyse = Column(Integer)
    recommandations = Column(JSONEncodedDict)

class MetriqueQualiteAAVModel(Base):
    __tablename__ = "metrique_qualite_aav"
    id_metrique = Column(Integer, primary_key=True)
    id_aav = Column(Integer, ForeignKey("aav.id_aav"), index=True)
    score_covering_ressources = Column(Float)
    taux_succes_moyen = Column(Float)
    est_utilisable = Column(Boolean)
    nb_tentatives_total = Column(Integer)
    nb_apprenants_distincts = Column(Integer)
    ecart_type_scores = Column(Float)
    date_calcul = Column(TIMESTAMP, index=True)
    periode_debut = Column(TIMESTAMP)
    periode_fin = Column(TIMESTAMP)

class AlerteQualiteModel(Base):
    __tablename__ = "alerte_qualite"
    id_alerte = Column(Integer, primary_key=True)
    type_alerte = Column(String(50), index=True)
    id_cible = Column(Integer)
    nom_cible = Column(String(200))
    severite = Column(String(20))
    description = Column(Text)
    suggestions = Column(JSONEncodedDict)
    date_detection = Column(TIMESTAMP)
    statut = Column(String(20), index=True)

class RapportPeriodiqueModel(Base):
    __tablename__ = "rapport_periodique"
    id_rapport = Column(Integer, primary_key=True)
    type_rapport = Column(String(50), index=True)
    id_cible = Column(Integer)
    date_generation = Column(TIMESTAMP, index=True)
    periode_debut = Column(TIMESTAMP)
    periode_fin = Column(TIMESTAMP)
    format = Column(String(20))
    contenu = Column(JSONEncodedDict)
    format_fichier = Column(String(50))

class EnseignantModel(Base):
    __tablename__ = "enseignant"
    id_enseignant = Column(Integer, primary_key=True)
    nom = Column(String(200))
    email = Column(String(200))
    discipline = Column(JSONEncodedDict)
    date_creation = Column(TIMESTAMP)

    aavs = relationship("AAVModel", back_populates="enseignant")

# ============================================
# INITIALISATION
# ============================================

def init_database():
    Base.metadata.create_all(engine)
    print("Base de données initialisée avec succès")

@contextmanager
def get_db_connection():
    """
    Context manager SQLAlchemy — équivalent de votre version SQLite3.
    
    Usage:
        with get_db_connection() as session:
            results = session.execute(text("SELECT * FROM aav")).fetchall()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()       # Commit automatique si tout va bien
    except Exception as e:
        session.rollback()     # Rollback en cas d'erreur
        raise DatabaseError(f"Erreur base de données: {str(e)}") from e
    finally:
        session.close()        # Fermeture

def init_database():
    """
    Initializes the database with common tables.
    Each group adds their own tables here.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Activer les clés étrangères (désactivées par défaut en SQLite)
        cursor.execute("PRAGMA foreign_keys = ON")

        # ============================================
        # TABLE COMMUNE: AAV (Groupe 1)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aav (
                id_aav INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                libelle_integration TEXT,
                discipline TEXT NOT NULL,
                enseignement TEXT,
                id_enseignant INTEGER, -- clé étrangere (enseignant) 
                type_aav TEXT CHECK(type_aav IN ('Atomique', 'Composite (Chapitre)')),
                description_markdown TEXT,
                prerequis_ids TEXT,  -- Stocké en JSON: [1, 2, 3]
                prerequis_externes_codes TEXT,  -- JSON: ["CODE1", "CODE2"]
                code_prerequis_interdisciplinaire TEXT,
                aav_enfant_ponderation TEXT,  -- JSON: [[1, 0.5], [2, 0.5]]
                type_evaluation TEXT CHECK(type_evaluation IN (
                    'Humaine', 'Calcul Automatisé', 'Compréhension par Chute',
                    'Validation par Invention', 'Exercice de Critique',
                    'Évaluation par les Pairs', 'Agrégation (Composite)'
                
                )),
                ids_exercices TEXT,  -- JSON: [101, 102, 103]
                prompts_fabrication_ids TEXT,  -- JSON: [201, 202]
                regles_progression TEXT,  -- JSON object
                is_active BOOLEAN DEFAULT 1,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_enseignant) REFERENCES enseignant(id_enseignant)
            )
        """)

        # Index pour accélérer les recherches fréquentes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aav_discipline ON aav(discipline)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aav_type ON aav(type_aav)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aav_active ON aav(is_active)")

        # ============================================
        # TABLE COMMUNE: OntologyReference (Groupe 1)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ontology_reference (
                id_reference INTEGER PRIMARY KEY,
                discipline TEXT NOT NULL,
                aavs_ids_actifs TEXT NOT NULL,  -- JSON: [1, 2, 3, 4, 5]
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ============================================
        # TABLE COMMUNE: Apprenant (Groupe 2)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apprenant (
                id_apprenant INTEGER PRIMARY KEY,
                nom_utilisateur TEXT NOT NULL UNIQUE,
                email TEXT,
                ontologie_reference_id INTEGER,
                statuts_actifs_ids TEXT,  -- JSON: [1, 2, 3]
                codes_prerequis_externes_valides TEXT,  -- JSON: ["CODE1"]
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                derniere_connexion TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (ontologie_reference_id) REFERENCES ontology_reference(id_reference)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_apprenant_username ON apprenant(nom_utilisateur)")

        # ============================================
        # TABLE COMMUNE: StatutApprentissage (Groupe 3)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statut_apprentissage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_apprenant INTEGER NOT NULL,
                id_aav_cible INTEGER NOT NULL,
                niveau_maitrise REAL
                    CHECK (niveau_maitrise >= 0 AND niveau_maitrise <= 1)
                    DEFAULT 0.0,
                historique_tentatives_ids TEXT,  -- JSON: [1, 2, 3, 4, 5]
                date_debut_apprentissage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_derniere_session TIMESTAMP,
                est_maitrise BOOLEAN GENERATED ALWAYS AS (niveau_maitrise >= 0.9) STORED,
                UNIQUE(id_apprenant, id_aav_cible),
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant)
                    ON DELETE CASCADE,
                FOREIGN KEY (id_aav_cible) REFERENCES aav(id_aav)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_statut_apprenant ON statut_apprentissage(id_apprenant)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_statut_aav ON statut_apprentissage(id_aav_cible)")

        # ============================================
        # TABLE COMMUNE: Tentative (Groupe 3)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tentative (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_exercice_ou_evenement INTEGER NOT NULL,
                id_apprenant INTEGER NOT NULL,
                id_aav_cible INTEGER NOT NULL,
                score_obtenu REAL
                    CHECK (score_obtenu >= 0 AND score_obtenu <= 1),
                date_tentative TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                est_valide BOOLEAN DEFAULT 0,
                temps_resolution_secondes INTEGER,
                metadata TEXT,  -- JSON: details supplémentaires
                FOREIGN KEY (id_apprenant) REFERENCES apprenant(id_apprenant)
                    ON DELETE CASCADE,
                FOREIGN KEY (id_aav_cible) REFERENCES aav(id_aav)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tentative_apprenant ON tentative(id_apprenant)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tentative_aav ON tentative(id_aav_cible)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tentative_date ON tentative(date_tentative)")

        # ============================================
        # TABLES AUTRES GROUPES (Nécessaires pour le dump de test)
        # ============================================

        # Table: activite_pedagogique (Groupe 4)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activite_pedagogique (
                id_activite INTEGER PRIMARY KEY,
                nom TEXT,
                description TEXT,
                type_activite TEXT,
                ids_exercices_inclus TEXT,
                discipline TEXT,
                niveau_difficulte TEXT,
                duree_estimee_minutes INTEGER,
                created_by INTEGER,
                created_at TIMESTAMP
            )
        """)

        # Table: session_apprenant (Groupe 4)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_apprenant (
                id_session INTEGER PRIMARY KEY,
                id_activite INTEGER,
                id_apprenant INTEGER,
                date_debut TIMESTAMP,
                date_fin TIMESTAMP,
                statut TEXT,
                progression_pourcentage REAL
            )
        """)

        # Table: prompt_fabrication_aav (Groupe 8)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_fabrication_aav (
                id_prompt INTEGER PRIMARY KEY,
                cible_aav_id INTEGER,
                type_exercice_genere TEXT,
                prompt_texte TEXT,
                version_prompt INTEGER,
                created_by INTEGER,
                date_creation TIMESTAMP,
                is_active BOOLEAN,
                metadata TEXT
            )
        """)

        # Table: exercice_instance (Groupe 8)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercice_instance (
                id_exercice INTEGER PRIMARY KEY,
                id_prompt_source INTEGER,
                titre TEXT,
                id_aav_cible INTEGER,
                type_evaluation TEXT,
                contenu TEXT,
                difficulte TEXT,
                date_generation TIMESTAMP,
                nb_utilisations INTEGER,
                taux_succes_moyen REAL
            )
        """)

        # Table: diagnostic_remediation (Groupe 6)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnostic_remediation (
                id_diagnostic INTEGER PRIMARY KEY,
                id_apprenant INTEGER,
                id_aav_source INTEGER,
                aav_racines_defaillants TEXT,
                score_obtenu REAL,
                date_diagnostic TIMESTAMP,
                profondeur_analyse INTEGER,
                recommandations TEXT
            )
        """)

        # ============================================
        # TABLES GROUPE 7: Analytics & Reporting
        # (spécifiques à ce groupe — groupe7_metriques_qualite.md)
        # ============================================

        # Table 1 : Métriques calculées par AAV
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrique_qualite_aav (
                id_metrique INTEGER PRIMARY KEY,
                id_aav INTEGER,
                score_covering_ressources REAL,
                taux_succes_moyen REAL,
                est_utilisable BOOLEAN,
                nb_tentatives_total INTEGER,
                nb_apprenants_distincts INTEGER,
                ecart_type_scores REAL,
                date_calcul TIMESTAMP,
                periode_debut TIMESTAMP,
                periode_fin TIMESTAMP
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrique_aav ON metrique_qualite_aav(id_aav)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrique_date ON metrique_qualite_aav(date_calcul)")

        # Table 2 : Alertes générées automatiquement
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerte_qualite (
                id_alerte INTEGER PRIMARY KEY,
                type_alerte TEXT,  -- 'difficulte', 'inutilise', 'fragile', 'risque'
                id_cible INTEGER,  -- ID de l'AAV ou de l'apprenant
                nom_cible TEXT,
                severite TEXT,     -- 'faible', 'moyenne', 'haute'
                description TEXT,
                suggestions TEXT,  -- JSON array
                date_detection TIMESTAMP,
                statut TEXT        -- 'nouveau', 'en_cours', 'resolu', 'ignore'
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerte_type ON alerte_qualite(type_alerte)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerte_statut ON alerte_qualite(statut)")

        # Table 3 : Rapports générés à la demande
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rapport_periodique (
                id_rapport INTEGER PRIMARY KEY,
                type_rapport TEXT,
                id_cible INTEGER,
                date_generation TIMESTAMP,
                periode_debut TIMESTAMP,
                periode_fin TIMESTAMP,
                format TEXT,
                contenu TEXT,       -- JSON avec les données
                format_fichier TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rapport_type ON rapport_periodique(type_rapport)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rapport_date ON rapport_periodique(date_generation)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enseignant (
            id_enseignant INTEGER PRIMARY KEY,
            nom TEXT ,
            email TEXT,
            discipline TEXT, --JSON array: ["Mathématiques", "Physique"]
            date_creation TIMESTAMP
            )
            """)

        conn.commit()
        print("Base de données initialisée avec succès")


# ============================================
# Fonctions utilitaires pour le JSON
# ============================================

def to_json(data: Any) -> Optional[str]:
    return json.dumps(data, ensure_ascii=False) if data is not None else None

def from_json(json_str: Optional[str]) -> Any:
    return json.loads(json_str) if json_str is not None else None

# ============================================
# PATTER REPOSITORY
# ============================================

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, id_value: int) -> Optional[Any]:
        with get_db_session() as db:
            return db.get(self.model, id_value)

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Any]:
        with get_db_session() as db:
            return db.query(self.model).offset(offset).limit(limit).all()

    def delete(self, id_value: int) -> bool:
        with get_db_session() as db:
            obj = db.get(self.model, id_value)
            if obj:
                db.delete(obj)
                db.commit()
                return True
            return False

    def count(self) -> int:
        """Returns the total number of records in the table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return cursor.fetchone()[0]

# Repository spécifique

class MetriqueQualiteAAVRepository(BaseRepository):
    def __init__(self):
        super().__init__(MetriqueQualiteAAVModel)

    def create(self, data: MetriqueQualiteAAV) -> MetriqueQualiteAAV:
        """Creates a MetriqueQualiteAAV and returns it with its new ID."""
        with get_db_connection() as session:
            result = session.execute(
                text("SELECT MAX(id_metrique) FROM metrique_qualite_aav")
            )
            max_id = result.scalar() or 0

            session.execute(
                text("""
                    INSERT INTO metrique_qualite_aav (
                        id_metrique,
                        id_aav,
                        score_covering_ressources,
                        taux_succes_moyen,
                        est_utilisable,
                        nb_tentatives_total,
                        nb_apprenants_distincts,
                        ecart_type_scores,
                        date_calcul,
                        periode_debut,
                        periode_fin
                    ) VALUES (
                        :id_metrique,
                        :id_aav,
                        :score_covering_ressources,
                        :taux_succes_moyen,
                        :est_utilisable,
                        :nb_tentatives_total,
                        :nb_apprenants_distincts,
                        :ecart_type_scores,
                        :date_calcul,
                        :periode_debut,
                        :periode_fin
                    )
                """),
                {
                    "id_metrique": max_id + 1,
                    "id_aav": data.id_aav,
                    "score_covering_ressources": data.score_covering_ressources,
                    "taux_succes_moyen": data.taux_succes_moyen,
                    "est_utilisable": data.est_utilisable,
                    "nb_tentatives_total": data.nb_tentatives_total,
                    "nb_apprenants_distincts": data.nb_apprenants_distincts,
                    "ecart_type_scores": data.ecart_type_scores,
                    "date_calcul": data.date_calcul.isoformat(),
                    "periode_debut": data.periode_debut.isoformat(),
                    "periode_fin": data.periode_fin.isoformat(),
                }
            )

        data.id_metrique = max_id + 1
        return data

class RapportRepository(BaseRepository):
    def __init__(self):
        super().__init__(RapportPeriodiqueModel)

    def create(self, data: Rapport) -> Rapport:
        """Create a report and return it."""
        now = datetime.now().isoformat()

        periode_debut = data.periode_debut.isoformat() if data.periode_debut is not None else now
        periode_fin   = data.periode_fin.isoformat()   if data.periode_fin   is not None else now

        with get_db_connection() as session:
            max_id = session.execute(
                text("SELECT MAX(id_rapport) FROM rapport_periodique")
            ).scalar() or 0

            session.execute(
                text("""
                    INSERT INTO rapport_periodique (
                        id_rapport,
                        type_rapport,
                        id_cible,
                        date_generation,
                        periode_debut,
                        periode_fin,
                        format,
                        contenu,
                        format_fichier
                    ) VALUES (
                        :id_rapport,
                        :type_rapport,
                        :id_cible,
                        :date_generation,
                        :periode_debut,
                        :periode_fin,
                        :format,
                        :contenu,
                        :format_fichier
                    )
                """),
                {
                    "id_rapport":       max_id + 1,
                    "type_rapport":     data.type_rapport,
                    "id_cible":         data.id_cible,
                    "date_generation":  data.date_generation.isoformat(),
                    "periode_debut":    periode_debut,
                    "periode_fin":      periode_fin,
                    "format":           data.format,
                    "contenu":          data.contenu,
                    "format_fichier":   data.format_fichier,
                }
            )

        data.periode_debut = periode_debut
        data.periode_fin   = periode_fin
        data.id_rapport    = max_id + 1
        return data
from sqlalchemy import text

class EnseignantRepository(BaseRepository):
    def __init__(self):
        super().__init__("enseignant", "id_enseignant")

    def create(self, data: Enseignant) -> Enseignant:
        with get_db_connection() as session:
            result = session.execute(
                text("""
                    INSERT INTO enseignant (nom, email, discipline)
                    VALUES (:nom, :email, :discipline)
                """),
                {
                    "nom":        data.nom,
                    "email":      data.email,
                    "discipline": to_json(data.disciplines),
                }
            )
            data.id_enseignant = result.lastrowid

        return data