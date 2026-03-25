# app/database_models.py
"""
SQLAlchemy ORM database models for PlatonAAV application.

This module defines all data models using SQLAlchemy's declarative API.
Each model class represents a database table with columns defined as ORM attributes.
Key features:
- Automatic timestamp tracking (created_at, updated_at)
- Foreign key relationships for data integrity
- Indexes for query performance optimization
- JSON field support for flexible data storage
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AAV(Base):
    """
    Learning Outcomes (Acquis d'Apprentissage Visés) model.
    
    Represents learning outcomes or competencies that students should achieve.
    Each AAV can have prerequisites, evaluation methods, and associated exercises.
    
    Attributes:
        id_aav (int): Primary key
        nom (str): Name of the learning outcome
        libelle_integration (str): Integration label
        discipline (str): Teaching discipline
        enseignement (str): Teaching level/type
        type_aav (str): Type of learning outcome
        description_markdown (str): Markdown description
        prerequis_ids (str): JSON list of prerequisite AAV IDs
        prerequis_externes_codes (str): JSON list of external prerequisite codes
        code_prerequis_interdisciplinaire (str): Interdisciplinary prerequisite code
        aav_enfant_ponderation (str): JSON mapping of child AAVs with weights
        type_evaluation (str): Evaluation method type
        ids_exercices (str): JSON list of associated exercise IDs
        prompts_fabrication_ids (str): JSON list of generation prompt IDs
        regles_progression (str): JSON progression rules
        is_active (bool): Whether this AAV is currently active
        version (int): Version number for tracking changes
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = "aav"

    id_aav = Column(Integer, primary_key=True)
    nom = Column(String(200), nullable=False)
    libelle_integration = Column(String(500))
    discipline = Column(String(100), nullable=False)
    enseignement = Column(String(200))
    type_aav = Column(String(50))
    description_markdown = Column(Text)
    prerequis_ids = Column(Text)
    prerequis_externes_codes = Column(Text)
    code_prerequis_interdisciplinaire = Column(String(100))
    aav_enfant_ponderation = Column(Text)
    type_evaluation = Column(String(50))
    ids_exercices = Column(Text)
    prompts_fabrication_ids = Column(Text)
    regles_progression = Column(Text)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_aav_discipline", "discipline"),
        Index("idx_aav_type", "type_aav"),
        Index("idx_aav_active", "is_active"),
    )


class OntologyReference(Base):
    """
    Ontology reference model for domain knowledge organization.
    
    Manages references to external ontologies and knowledge bases
    organized by discipline and topic.
    
    Attributes:
        id_reference (int): Primary key
        discipline (str): Associated discipline
    """
    __tablename__ = "ontology_reference"

    id_reference = Column(Integer, primary_key=True)
    discipline = Column(String(100), nullable=False)
    aavs_ids_actifs = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Apprenant(Base):
    """
    Learner model representing students in the system.
    
    Tracks learner information, including active status, prerequisites,
    and ontology references for personalized learning paths.
    
    Attributes:
        id_apprenant (int): Primary key
        nom_utilisateur (str): Unique username
        email (str): Email address
        ontologie_reference_id (int): Foreign key to ontology reference
        statuts_actifs_ids (str): JSON list of active status IDs
        codes_prerequis_externes_valides (str): JSON list of validated external prerequisites
        date_inscription (datetime): Registration date
        derniere_connexion (datetime): Last login timestamp
        is_active (bool): Whether learner account is active
    """
    __tablename__ = "apprenant"

    id_apprenant = Column(Integer, primary_key=True)
    nom_utilisateur = Column(String(100), nullable=False, unique=True)
    email = Column(String(100))
    ontologie_reference_id = Column(Integer, ForeignKey("ontology_reference.id_reference", ondelete="SET NULL"))
    statuts_actifs_ids = Column(Text)
    codes_prerequis_externes_valides = Column(Text)
    date_inscription = Column(DateTime, default=datetime.utcnow)
    derniere_connexion = Column(DateTime)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_apprenant_username", "nom_utilisateur"),
    )


class StatutApprentissage(Base):
    """
    Learning status model tracking learner progress towards AAVs.
    
    Maintains mastery level for each learner-AAV combination,
    including attempt history and mastery thresholds.
    
    Attributes:
        id (int): Primary key
        id_apprenant (int): Foreign key to learner
        id_aav_cible (int): Foreign key to target AAV
        niveau_maitrise (float): Mastery level (0.0-1.0)
        historique_tentatives_ids (str): JSON list of attempt IDs
        date_debut_apprentissage (datetime): Learning start date
        date_derniere_session (datetime): Last session date
        est_maitrise (bool): Whether AAV is mastered (mastery >= 0.9)
    """
    __tablename__ = "statut_apprentissage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant", ondelete="CASCADE"), nullable=False)
    id_aav_cible = Column(Integer, ForeignKey("aav.id_aav", ondelete="CASCADE"), nullable=False)
    niveau_maitrise = Column(Float, default=0.0)
    historique_tentatives_ids = Column(Text)
    date_debut_apprentissage = Column(DateTime, default=datetime.utcnow)
    date_derniere_session = Column(DateTime)
    est_maitrise = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_statut_apprenant", "id_apprenant"),
        Index("idx_statut_aav", "id_aav_cible"),
    )


class Tentative(Base):
    """
    Attempt/Try model recording individual exercise attempts.
    
    Captures each learner's attempt at an exercise, including score,
    validation status, and time taken.
    
    Attributes:
        id (int): Primary key
        id_exercice_ou_evenement (int): Exercise ID
        id_apprenant (int): Foreign key to learner
        id_aav_cible (int): Foreign key to target AAV
        score_obtenu (float): Score achieved (0.0-1.0)
        date_tentative (datetime): Attempt timestamp
        est_valide (bool): Whether attempt is valid/graded
        temps_resolution_secondes (int): Time taken to solve in seconds
        metadata_json (str): Additional attempt metadata as JSON
    """
    __tablename__ = "tentative"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_exercice_ou_evenement = Column(Integer, nullable=False)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant", ondelete="CASCADE"), nullable=False)
    id_aav_cible = Column(Integer, ForeignKey("aav.id_aav", ondelete="CASCADE"), nullable=False)
    score_obtenu = Column(Float)
    date_tentative = Column(DateTime, default=datetime.utcnow)
    est_valide = Column(Boolean, default=False)
    temps_resolution_secondes = Column(Integer)
    metadata_json = Column(Text)


class ActivitePedagogique(Base):
    """
    Pedagogical Activity model (Group 4) representing learning activities.
    
    Represents structured learning activities composed of exercises,
    designed to develop specific AAVs with defined difficulty and duration.
    
    Attributes:
        id_activite (int): Primary key
        nom (str): Activity name
        description (str): Activity description
        type_activite (str): Type (pilotee, prof_definie, revision)
        ids_exercices_inclus (str): JSON list of included exercise IDs
        discipline (str): Associated discipline
        niveau_difficulte (str): Difficulty level
        duree_estimee_minutes (int): Estimated duration in minutes
        created_by (int): Creator user ID
        created_at (datetime): Creation timestamp
    """
    __tablename__ = "activite_pedagogique"

    id_activite = Column(Integer, primary_key=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text)
    type_activite = Column(String(50))
    ids_exercices_inclus = Column(Text)
    discipline = Column(String(100))
    niveau_difficulte = Column(String(50))
    duree_estimee_minutes = Column(Integer)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class SessionApprenant(Base):
    """
    Learner session model (Group 4) tracking learning activity sessions.
    
    Records each learner's engagement with pedagogical activities,
    including timing, progress, and completion status.
    
    Attributes:
        id_session (int): Primary key
        id_activite (int): Foreign key to activity
        id_apprenant (int): Foreign key to learner
        date_debut (datetime): Session start time
        date_fin (datetime): Session end time
        statut (str): Status (en_cours, terminee, abandonnee)
        progression_pourcentage (float): Completion percentage (0-100)
    """
    __tablename__ = "session_apprenant"

    id_session = Column(Integer, primary_key=True, autoincrement=True)
    id_activite = Column(Integer, ForeignKey("activite_pedagogique.id_activite"), nullable=False)
    id_apprenant = Column(Integer, ForeignKey("apprenant.id_apprenant"), nullable=False)
    debut_session = Column(DateTime)
    fin_session = Column(DateTime)
    statut = Column(String(50))
    progression_pourcentage = Column(Float, default=0.0)
    bilan_session = Column(Text)


class ExerciceDetail(Base):
    """
    Exercise detail model (Group 4) defining individual exercises.
    
    Represents specific exercises targeting one or more AAVs with
    defined content, evaluation type, and difficulty level.
    
    Attributes:
        id_exercice (int): Primary key
        titre (str): Exercise title
        id_aav_cible (int): Foreign key to target AAV
        type_evaluation (str): Evaluation type (QCM, code, essay, etc.)
        contenu (str): Exercise content as JSON
        difficulte (float): Difficulty rating
    """
    __tablename__ = "exercice_detail"

    id_exercice = Column(Integer, primary_key=True)
    titre = Column(String(200))
    id_aav_cible = Column(Integer, ForeignKey("aav.id_aav"), nullable=False)
    type_evaluation = Column(String(50))
    contenu = Column(Text)
    difficulte = Column(Float)
    nom = Column(String(200))
    description = Column(Text)
