# app/database.py
import json
from contextlib import contextmanager
from typing import Optional, List, Any
from datetime import datetime

from sqlalchemy import (
    create_engine, text,
    Column, Integer, String, Float, Boolean, Text,
    ForeignKey, TIMESTAMP, TypeDecorator
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "platonAAV.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass


# ============================================
# SQLALCHEMY MODELS
# All database models using SQLAlchemy ORM
# ============================================

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    impl = Text
    cache_ok = True

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
    id_session = Column(Integer, primary_key=True, autoincrement=True)
    id_activite = Column(Integer, ForeignKey("activite_pedagogique.id_activite"))
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"))
    date_debut = Column(TIMESTAMP)
    date_fin = Column(TIMESTAMP)
    statut = Column(String(50))
    progression_pourcentage = Column(Float)
    bilan_session = Column(Text)  # JSON-encoded summary of the session


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


class ExternalPrerequisiteValidationModel(Base):
    __tablename__ = "external_prerequisite_validation"
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"), primary_key=True)
    code_prerequis = Column(String(100), primary_key=True)
    validated_by = Column(String(100))
    notes = Column(Text)
    date_validation = Column(TIMESTAMP, server_default=func.current_timestamp())


class TentativeExerciceModel(Base):
    __tablename__ = "tentative_exercice"
    id_tentative = Column(Integer, primary_key=True, autoincrement=True)
    id_exercice = Column(Integer, ForeignKey("exercice_instance.id_exercice"), nullable=False)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"))
    reponse_donnee = Column(Text)
    score_obtenu = Column(Float)
    feedback_genere = Column(Text)
    date_tentative = Column(TIMESTAMP, server_default=func.current_timestamp())



class NavigationCacheModel(Base):
    __tablename__ = "navigation_cache"
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"), primary_key=True)
    id_aav = Column(Integer, ForeignKey("aav.id_aav"), primary_key=True)
    categorie = Column(String(50), primary_key=True)
    dernier_calcul = Column(TIMESTAMP, server_default=func.current_timestamp())
    raison_blocage = Column(JSONEncodedDict)


class RevisionHistoryModel(Base):
    __tablename__ = "revision_history"
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"), primary_key=True)
    id_aav = Column(Integer, ForeignKey("aav.id_aav"), primary_key=True)
    prochaine_revision_prevue = Column(TIMESTAMP)
    date_derniere_revision = Column(TIMESTAMP)



# ============================================
# CONNEXION / SESSION
# ============================================

@contextmanager
def get_db_connection():
    """
    Context manager providing a compatibility wrapper around SQLAlchemy session.
    Supports both ORM usage and raw SQL usage with .cursor() and ? placeholders.
    """
    session = SessionLocal()
    
    class ConnectionWrapper:
        def __init__(self, session):
            self.session = session
            self.result = None

        def cursor(self):
            return self

        def execute(self, sql, params=None):
            """
            Exécute une requête SQL brute avec support des placeholders '?'.
            Convertit les '?' en paramètres nommés pour SQLAlchemy.

            Args:
                sql (str): La requête SQL.
                params (Optional[Union[dict, list, tuple, Any]]): Les paramètres de la requête.

            Returns:
                ConnectionWrapper: L'instance elle-même pour chaînage.
            """
            from sqlalchemy import text
            import re
            
            # Handle ? placeholders by converting them to :p0, :p1...
            if params:
                if isinstance(params, (list, tuple)):
                    count = [0]
                    def replace_func(m):
                        res = f":p{count[0]}"
                        count[0] += 1
                        return res
                    sql = re.sub(r'\?', replace_func, sql)
                    params = {f"p{i}": v for i, v in enumerate(params)}
                elif not isinstance(params, dict):
                    # Single param case
                    sql = re.sub(r'\?', ":p0", sql)
                    params = {"p0": params}
                
                self.result = self.session.execute(text(sql), params)
            else:
                self.result = self.session.execute(text(sql))
            return self

        def fetchone(self):
            """Récupère une seule ligne du résultat sous forme de dictionnaire."""
            if not self.result: return None
            row = self.result.fetchone()
            return row._mapping if row else None

        def fetchall(self):
            """Récupère toutes les lignes du résultat sous forme d'une liste de dictionnaires."""
            if not self.result: return []
            return [r._mapping for r in self.result.fetchall()]

        @property
        def lastrowid(self):
            return self.result.lastrowid if self.result else None

        def scalar(self):
            """Récupère une seule valeur du résultat (la première colonne de la première ligne)."""
            if getattr(self.result, 'scalar', None):
                return self.result.scalar()
            elif self.result:
                row = self.result.fetchone()
                if row:
                    return row[0]
            return None

        def commit(self):
            self.session.commit()

        def rollback(self):
            self.session.rollback()

        def close(self):
            self.session.close()

        # Support ORM session methods
        def query(self, *args, **kwargs):
            return self.session.query(*args, **kwargs)
        
        def get(self, *args, **kwargs):
            return self.session.get(*args, **kwargs)
        
        def add(self, *args, **kwargs):
            return self.session.add(*args, **kwargs)
        
        def delete(self, *args, **kwargs):
            return self.session.delete(*args, **kwargs)
        
        def flush(self, *args, **kwargs):
            return self.session.flush(*args, **kwargs)

        def refresh(self, *args, **kwargs):
            return self.session.refresh(*args, **kwargs)


    wrapper = ConnectionWrapper(session)
    try:
        yield wrapper
        session.commit()
    except Exception as e:
        session.rollback()
        raise DatabaseError(f"Database error: {str(e)}") from e
    finally:
        session.close()


# FastAPI dependency for database session injection
def get_db():
    """
    FastAPI dependency that provides database session.
    
    Usage in routers:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Database error: {str(e)}") from e
    finally:
        db.close()


# Alias for backward compatibility
get_db_session = get_db_connection


# ============================================
# INITIALIZATION
# ============================================

def init_database():
    """Create all tables defined in ORM models."""
    Base.metadata.create_all(engine)
    print("Database initialized successfully")


# ============================================
# JSON UTILITY FUNCTIONS
# ============================================

def to_json(data: Any) -> Optional[str]:
    """Sérialise une donnée Python en chaîne JSON (UTF-8)."""
    return json.dumps(data, ensure_ascii=False) if data is not None else None


def from_json(json_str: Any) -> Any:
    """Désérialise une chaîne JSON en objet Python (ou retourne tel quel si déjà décodé)."""
    if json_str is None:
        return None
    if isinstance(json_str, (list, dict)):
        return json_str
    try:
        return json.loads(json_str)
    except (ValueError, TypeError):
        return json_str


# ============================================
# REPOSITORIES
# ============================================

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, id_value: int) -> Optional[Any]:
        """Récupère une entité par son identifiant via l'ORM."""
        with get_db_connection() as db:
            return db.get(self.model, id_value)

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Any]:
        """Récupère toutes les entités avec pagination."""
        with get_db_connection() as db:
            return db.query(self.model).offset(offset).limit(limit).all()

    def delete(self, id_value: int) -> bool:
        with get_db_connection() as db:
            obj = db.get(self.model, id_value)
            if obj:
                db.delete(obj)
                return True
            return False

    def count(self) -> int:
        """Returns the total number of records in the table."""
        with get_db_connection() as session:
            return session.execute(
                f"SELECT COUNT(*) FROM {self.model.__tablename__}"
            ).scalar() or 0


class MetriqueQualiteAAVRepository(BaseRepository):
    def __init__(self):
        super().__init__(MetriqueQualiteAAVModel)

    def create(self, data):
        """Creates a MetriqueQualiteAAV and returns it with its new ID."""
        with get_db_connection() as session:
            max_id = session.execute(
                "SELECT MAX(id_metrique) FROM metrique_qualite_aav"
            ).scalar() or 0

            session.execute(
                """
                    INSERT INTO metrique_qualite_aav (
                        id_metrique, id_aav, score_covering_ressources,
                        taux_succes_moyen, est_utilisable, nb_tentatives_total,
                        nb_apprenants_distincts, ecart_type_scores,
                        date_calcul, periode_debut, periode_fin
                    ) VALUES (
                        :id_metrique, :id_aav, :score_covering_ressources,
                        :taux_succes_moyen, :est_utilisable, :nb_tentatives_total,
                        :nb_apprenants_distincts, :ecart_type_scores,
                        :date_calcul, :periode_debut, :periode_fin
                    )
                """,
                {
                    "id_metrique":              max_id + 1,
                    "id_aav":                   data.id_aav,
                    "score_covering_ressources": data.score_covering_ressources,
                    "taux_succes_moyen":        data.taux_succes_moyen,
                    "est_utilisable":           data.est_utilisable,
                    "nb_tentatives_total":      data.nb_tentatives_total,
                    "nb_apprenants_distincts":  data.nb_apprenants_distincts,
                    "ecart_type_scores":        data.ecart_type_scores,
                    "date_calcul":              data.date_calcul.isoformat(),
                    "periode_debut":            data.periode_debut.isoformat(),
                    "periode_fin":              data.periode_fin.isoformat(),
                }
            )

        data.id_metrique = max_id + 1
        return data


class RapportRepository(BaseRepository):
    def __init__(self):
        super().__init__(RapportPeriodiqueModel)

    def create(self, data):
        """Create a report and return it."""
        now = datetime.now().isoformat()
        periode_debut = data.periode_debut.isoformat() if data.periode_debut is not None else now
        periode_fin   = data.periode_fin.isoformat()   if data.periode_fin   is not None else now

        with get_db_connection() as session:
            max_id = session.execute(
                "SELECT MAX(id_rapport) FROM rapport_periodique"
            ).scalar() or 0

            session.execute(
                """
                    INSERT INTO rapport_periodique (
                        id_rapport, type_rapport, id_cible, date_generation,
                        periode_debut, periode_fin, format, contenu, format_fichier
                    ) VALUES (
                        :id_rapport, :type_rapport, :id_cible, :date_generation,
                        :periode_debut, :periode_fin, :format, :contenu, :format_fichier
                    )
                """,
                {
                    "id_rapport":      max_id + 1,
                    "type_rapport":    data.type_rapport,
                    "id_cible":        data.id_cible,
                    "date_generation": data.date_generation.isoformat(),
                    "periode_debut":   periode_debut,
                    "periode_fin":     periode_fin,
                    "format":          data.format,
                    "contenu":         data.contenu,
                    "format_fichier":  data.format_fichier,
                }
            )

        data.periode_debut = periode_debut
        data.periode_fin   = periode_fin
        data.id_rapport    = max_id + 1
        return data


class EnseignantRepository(BaseRepository):
    def __init__(self):
        super().__init__(EnseignantModel)

    def create(self, data):
        with get_db_connection() as session:
            result = session.execute(
                """
                    INSERT INTO enseignant (nom, email, discipline)
                    VALUES (:nom, :email, :discipline)
                """,
                {
                    "nom":        data.nom,
                    "email":      data.email,
                    "discipline": to_json(data.disciplines),
                }
            )
            data.id_enseignant = result.lastrowid

        return data