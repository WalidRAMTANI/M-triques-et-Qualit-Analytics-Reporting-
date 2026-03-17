# app/database.py
import json
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    TIMESTAMP, ForeignKey, Text, Index, CheckConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

# Configuration
DATABASE_PATH = Path("platonAAV.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use a custom Base to support bracket access (compatibility with dict-based code/tests)
class BaseWithBracketAccess:
    def __getitem__(self, key):
        return getattr(self, key)
    
    def get(self, key, default=None):
        return getattr(self, key, default)

Base = declarative_base(cls=BaseWithBracketAccess)

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
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Erreur session SQLAlchemy: {str(e)}") from e
    finally:
        db.close()

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        with get_db_session() as db:
            return db.query(self.model).count()

class MetriqueQualiteAAVRepository(BaseRepository):
    def __init__(self):
        super().__init__(MetriqueQualiteAAVModel)

    def create(self, data) -> MetriqueQualiteAAVModel:
        with get_db_session() as db:
            if hasattr(data, "model_dump"):
                ndata = data.model_dump(exclude={"id_metrique"})
            elif hasattr(data, "dict"):
                ndata = data.dict(exclude={"id_metrique"})
            else:
                ndata = data.__dict__.copy()
                ndata.pop('_sa_instance_state', None)
                ndata.pop('id_metrique', None)

            db_obj = MetriqueQualiteAAVModel(**ndata)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

class RapportRepository(BaseRepository):
    def __init__(self):
        super().__init__(RapportPeriodiqueModel)

    def create(self, data) -> RapportPeriodiqueModel:
        with get_db_session() as db:
            if hasattr(data, "model_dump"):
                ndata = data.model_dump(exclude={"id_rapport"})
            else:
                ndata = data.__dict__.copy()
                ndata.pop('_sa_instance_state', None)
                ndata.pop('id_rapport', None)
            
            db_obj = RapportPeriodiqueModel(**ndata)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

class EnseignantRepository(BaseRepository):
    def __init__(self):
        super().__init__(EnseignantModel)

    def create(self, data) -> EnseignantModel:
        with get_db_session() as db:
            if hasattr(data, "model_dump"):
                ndata = data.model_dump(exclude={"id_enseignant"})
            else:
                ndata = {"nom": data.nom, "email": data.email, "discipline": data.discipline}
            
            db_obj = EnseignantModel(**ndata)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj