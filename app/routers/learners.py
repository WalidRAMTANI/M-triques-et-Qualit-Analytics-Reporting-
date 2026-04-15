# app/routers/aavs.py

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.model.model import Learner, LearnerCreate, LearnerUpdate
from app.model.model import LearningStatus, LearningStatusSummary
from app.model.model import ExternalPrerequisite, ExternalPrerequisiteCreate
from app.model.model import OntologyReference, OntologySwitchResponse
from app.model.model import ProgressResponse
from app.database import (
    get_db_connection, BaseRepository, to_json, from_json, 
    ApprenantModel, ExternalPrerequisiteValidationModel, StatutApprentissageModel,
    OntologyReferenceModel, AAVModel
)
from sqlalchemy import and_, func


router = APIRouter(
    tags=["Learners"],
    responses={
        404: {"description": "Apprenant non trouvé"},
        422: {"description": "Données invalides"}
    }
)

# Repository spécifique


class LearnerRepository(BaseRepository):
    def __init__(self):
        super().__init__(ApprenantModel)

    def get_by_id(self, id_value: int):
        """
        Récupère un apprenant uniquement s'il est actif.

        Args:
            id_value (int): L'identifiant de l'apprenant.

        Returns:
            Optional[dict]: Les données de l'apprenant ou None si inactif ou non trouvé.
        """
        with get_db_connection() as session:
            obj = session.query(ApprenantModel).filter(
                and_(ApprenantModel.id_apprenant == id_value, ApprenantModel.is_active == True)
            ).first()
            if not obj: return None
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


    def create(self, data: dict) -> int:
        """
        Crée un nouvel apprenant dans la base de données.
        """
        with get_db_connection() as session:
            # Generate ID if not provided
            if data.get('id_apprenant') is None:
                max_id = session.query(func.max(ApprenantModel.id_apprenant)).scalar() or 0
                data['id_apprenant'] = max_id + 1

            new_learner = ApprenantModel(
                id_apprenant=data['id_apprenant'],
                nom_utilisateur=data['nom_utilisateur'],
                email=data['email'],
                ontologie_reference_id=data.get('ontologie_reference_id'),
                statuts_actifs_ids=data.get('statuts_actifs_ids', []),
                codes_prerequis_externes_valides=data.get('codes_prerequis_externes_valides', []),
                derniere_connexion=data.get('derniere_connexion')
            )
            session.add(new_learner)
            session.commit()
            return data['id_apprenant']

    def update(self, id_apprenant: int, data: dict) -> bool:
        """
        Met à jour partiellement ou complètement un apprenant.

        Args:
            id_apprenant (int): L'identifiant de l'apprenant.
            data (dict): Les champs à mettre à jour.

        Returns:
            bool: True si la mise à jour a réussi, False sinon.
        """
        with get_db_connection() as session:
            obj = session.query(ApprenantModel).filter(ApprenantModel.id_apprenant == id_apprenant).first()
            if not obj:
                return False
            
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            session.commit()
            return True


# Instance du repository
repo = LearnerRepository()

# ============================================
# ENDPOINTS CRUD
# ============================================


@router.get("/", response_model=List[Learner])
def list_learners(
    nom: Optional[str] = Query(
        None,
        description="Filtrer par nom d'utilisateur"),
        limit: int = Query(
            100,
            ge=1,
            le=1000,
            description="Nombre maximum de résultats"),
        offset: int = Query(
            0,
            ge=0,
            description="Offset pour la pagination")):
    """
    Récupère la liste des apprenants actifs avec pagination.

    Args:
        nom (Optional[str]): Filtre optionnel sur le nom d'utilisateur.
        limit (int): Nombre maximum de résultats.
        offset (int): Offset pour la pagination.

    Returns:
        List[Learner]: La liste des apprenants trouvés.
    """
    with get_db_connection() as session:
        query = session.query(ApprenantModel).filter(ApprenantModel.is_active == True)
        
        if nom:
            query = query.filter(ApprenantModel.nom_utilisateur == nom)
        
        rows = query.offset(offset).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]


@router.get("/{id_apprenant}", response_model=Learner)
def get_learner(id_apprenant: int):
    """
    Récupère les détails d'un apprenant par son identifiant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.

    Returns:
        Learner: Les données de l'apprenant.

    Raises:
        HTTPException: 404 si l'apprenant n'est pas trouvé.
    """
    data = repo.get_by_id(id_apprenant)
    if not data:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")
    return Learner(**data)


@router.post("/", response_model=Learner, status_code=201)
def create_learner(learner: LearnerCreate):
    """
    Enregistre un nouvel apprenant dans le système.

    Args:
        learner (LearnerCreate): Les données de l'apprenant à créer.

    Returns:
        Learner: L'apprenant créé.

    Raises:
        HTTPException: 400 si l'ID existe déjà, 500 en cas d'erreur serveur.
    """
    if learner.id_apprenant is not None:
        exists = repo.get_by_id(learner.id_apprenant)
        if exists:
            raise HTTPException(
                status_code=400,
                detail=f"Il existe déjà un apprenant avec l'ID {learner.id_apprenant}")

    try:
        new_id = repo.create(learner.model_dump())
        created = repo.get_by_id(new_id)
        return Learner(**created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_apprenant}", response_model=Learner)
def update_learner_full(id_apprenant: int, learner: LearnerCreate):
    """
    Met à jour complètement les informations d'un apprenant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.
        learner (LearnerCreate): Les nouvelles données complètes.

    Returns:
        Learner: L'apprenant mis à jour.
    """
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(status_code=404, detail="L'apprenant n'existe pas")

    with get_db_connection() as session:
        obj = session.query(ApprenantModel).filter(ApprenantModel.id_apprenant == id_apprenant).first()
        obj.nom_utilisateur = learner.nom_utilisateur
        obj.email = learner.email
        obj.ontologie_reference_id = learner.ontologie_reference_id
        obj.statuts_actifs_ids = learner.statuts_actifs_ids
        obj.codes_prerequis_externes_valides = learner.codes_prerequis_externes_valides
        session.commit()

    updated = repo.get_by_id(id_apprenant)
    return Learner(**updated)


@router.patch("/{id_apprenant}", response_model=Learner)
def update_learner_partial(id_apprenant: int, learner: LearnerUpdate):
    """
    Met à jour partiellement les informations d'un apprenant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.
        learner (LearnerUpdate): Les champs à modifier.

    Returns:
        Learner: L'apprenant mis à jour.
    """
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(
            status_code=404,
            detail="L'apprenant n'existe pas"
        )

    update_data = {k: v for k, v in learner.model_dump().items()
                   if v is not None}

    if update_data:
        repo.update(id_apprenant, update_data)

    updated = repo.get_by_id(id_apprenant)
    return Learner(**updated)


@router.delete("/{id_apprenant}", status_code=204)
def delete_learner(id_apprenant: int):
    """
    Désactive un apprenant (suppression logique).

    Args:
        id_apprenant (int): L'identifiant de l'apprenant à désactiver.

    Returns:
        None: Retourne un code 204 en cas de succès.
    """
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(
            status_code=404,
            detail="L'apprenant n'existe pas"
        )

    with get_db_connection() as session:
        obj = session.query(ApprenantModel).filter(ApprenantModel.id_apprenant == id_apprenant).first()
        if obj:
            obj.is_active = False
            session.commit()

    return None

# ============================================
# ENDPOINTS : Prérequis Externes
# ============================================


@router.get("/{id_apprenant}/external-prerequisites",
            response_model=List[ExternalPrerequisite])
def get_external_prerequisites(id_apprenant: int):
    """
    Récupère la liste des prérequis externes validés par un apprenant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.

    Returns:
        List[ExternalPrerequisite]: La liste des prérequis validés.
    """
    # Vérifier que l'apprenant existe
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    with get_db_connection() as session:
        rows = session.query(ExternalPrerequisiteValidationModel).filter(
            ExternalPrerequisiteValidationModel.id_apprenant == id_apprenant
        ).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]


@router.post("/{id_apprenant}/external-prerequisites",
             response_model=ExternalPrerequisite, status_code=201)
def add_external_prerequisite(id_apprenant: int,
                              prerequisite: ExternalPrerequisiteCreate):
    """
    Valide un nouveau prérequis externe pour un apprenant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.
        prerequisite (ExternalPrerequisiteCreate): Le code et les détails du prérequis.

    Returns:
        ExternalPrerequisite: Le prérequis validé.
    """
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    with get_db_connection() as session:
        existing = session.query(ExternalPrerequisiteValidationModel).filter(
            ExternalPrerequisiteValidationModel.id_apprenant == id_apprenant,
            ExternalPrerequisiteValidationModel.code_prerequis == prerequisite.code_prerequis
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Le prérequis '{prerequisite.code_prerequis}' est déjà validé")

        new_prereq = ExternalPrerequisiteValidationModel(
            id_apprenant=id_apprenant,
            code_prerequis=prerequisite.code_prerequis,
            validated_by=prerequisite.validated_by,
            notes=prerequisite.notes
        )
        session.add(new_prereq)
        session.commit()
        session.refresh(new_prereq)
        return ExternalPrerequisite(**{c.name: getattr(new_prereq, c.name) for c in new_prereq.__table__.columns})


@router.delete("/{id_apprenant}/external-prerequisites/{code}",
               status_code=204)
def delete_external_prerequisite(id_apprenant: int, code: str):
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    with get_db_connection() as session:
        obj = session.query(ExternalPrerequisiteValidationModel).filter(
            and_(
                ExternalPrerequisiteValidationModel.id_apprenant == id_apprenant,
                ExternalPrerequisiteValidationModel.code_prerequis == code
            )
        ).first()
        
        if not obj:
            raise HTTPException(status_code=404, detail=f"Le prérequis '{code}' n'existe pas")
        
        session.delete(obj)
        session.commit()
    
    return None

# ============================================
# ENDPOINTS : Statuts d'Apprentissage
# ============================================


@router.get("/{id_apprenant}/learning-status",
            response_model=List[LearningStatus])
def get_learning_status(id_apprenant: int):
    """
    Récupère l'état d'apprentissage de l'apprenant sur tous les AAVs.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.

    Returns:
        List[LearningStatus]: Liste des statuts d'apprentissage.
    """
    # Vérifier que l'apprenant existe
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    with get_db_connection() as session:
        rows = session.query(StatutApprentissageModel).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant
        ).all()

        result = []
        for r in rows:
            data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            # Désérialiser le JSON des tentatives
            data['historique_tentatives_ids'] = from_json(
                data.get('historique_tentatives_ids') or '[]')
            result.append(LearningStatus(**data))

        return result


@router.get("/{id_apprenant}/learning-status/summary",
            response_model=LearningStatusSummary)
def get_learning_status_summary(id_apprenant: int):
    """
    Calcule un résumé statistique de la progression de l'apprenant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.

    Returns:
        LearningStatusSummary: Statistiques (total, maîtrise, en cours, etc.).
    """
    # Vérifier que l'apprenant existe
    exists = repo.get_by_id(id_apprenant)
    if not exists:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    with get_db_connection() as session:
        statuts = session.query(StatutApprentissageModel).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant
        ).all()

        total = len(statuts)
        maitrise = sum(1 for s in statuts if s.niveau_maitrise >= 0.9)
        en_cours = sum(1 for s in statuts if 0 < s.niveau_maitrise < 0.9)
        non_commence = sum(1 for s in statuts if s.niveau_maitrise == 0)

        taux = round((maitrise / total * 100), 2) if total > 0 else 0.0

        return LearningStatusSummary(
            id_apprenant=id_apprenant,
            total=total,
            maitrise=maitrise,
            en_cours=en_cours,
            non_commence=non_commence,
            taux_maitrise_global=taux
        )

# ============================================
# ENDPOINTS : Ontologie
# ============================================


@router.get("/{id_apprenant}/ontologie", response_model=OntologyReference)
def get_ontologie(id_apprenant: int):
    """
    Récupère l'ontologie de référence assignée à l'apprenant.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.

    Returns:
        OntologyReference: Détails de l'ontologie.
    """
    # Vérifier que l'apprenant existe
    apprenant = repo.get_by_id(id_apprenant)
    if not apprenant:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    # Vérifier qu'il a une ontologie assignée
    if not apprenant.get('ontologie_reference_id'):
        raise HTTPException(
            status_code=404,
            detail="Cet apprenant n'a pas d'ontologie de référence assignée"
        )

    with get_db_connection() as session:
        onto = session.query(OntologyReferenceModel).filter(
            OntologyReferenceModel.id_reference == apprenant['ontologie_reference_id']
        ).first()

        if not onto:
            raise HTTPException(
                status_code=404,
                detail="L'ontologie référencée n'existe plus en base"
            )

        data = {c.name: getattr(onto, c.name) for c in onto.__table__.columns}
        data['aavs_ids_actifs'] = from_json(
            data.get('aavs_ids_actifs') or '[]')
        return OntologyReference(**data)


@router.post("/{id_apprenant}/ontologie/{id_reference}/switch",
             response_model=OntologySwitchResponse)
def switch_ontologie(id_apprenant: int, id_reference: int):
    """
    Change l'ontologie de référence d'un apprenant après vérification des prérequis.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.
        id_reference (int): L'identifiant de la nouvelle ontologie.

    Returns:
        OntologySwitchResponse: Confirmation du changement.
    """
    # Vérifier que l'apprenant existe
    apprenant_dict = repo.get_by_id(id_apprenant)
    if not apprenant_dict:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    with get_db_connection() as session:
        # Vérifier que la nouvelle ontologie existe
        nouvelle_onto = session.query(OntologyReferenceModel).filter(
            OntologyReferenceModel.id_reference == id_reference
        ).first()

        if not nouvelle_onto:
            raise HTTPException(
                status_code=404,
                detail=f"L'ontologie {id_reference} n'existe pas")

        # Vérifier compatibilité des prérequis externes
        codes_valides = apprenant_dict.get('codes_prerequis_externes_valides') or []
        aavs_ids = nouvelle_onto.aavs_ids_actifs or []

        if aavs_ids:
            aav_rows = session.query(AAVModel).filter(AAVModel.id_aav.in_(aavs_ids)).all()

            prerequis_requis = set()
            for aav in aav_rows:
                codes = from_json(aav.prerequis_externes_codes or '[]')
                prerequis_requis.update(codes)

            manquants = prerequis_requis - set(codes_valides)
            if manquants:
                raise HTTPException(
                    status_code=400,
                    detail=f"Prérequis externes manquants pour cette ontologie : {list(manquants)}")

        # Tout est bon : effectuer le changement
        apprenant_obj = session.query(ApprenantModel).filter(ApprenantModel.id_apprenant == id_apprenant).first()
        ancienne_ontologie_id = apprenant_obj.ontologie_reference_id
        apprenant_obj.ontologie_reference_id = id_reference
        session.commit()

    return OntologySwitchResponse(
        success=True,
        message="Ontologie changée avec succès",
        id_apprenant=id_apprenant,
        ancienne_ontologie_id=ancienne_ontologie_id,
        nouvelle_ontologie_id=id_reference
    )

# ============================================
# ENDPOINT : Progression
# ============================================


@router.get("/{id_apprenant}/progress", response_model=ProgressResponse)
def get_progress(id_apprenant: int):
    """
    Calcule le taux de progression global d'un apprenant dans son ontologie.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.

    Returns:
        ProgressResponse: Taux de progression (0-100%).
    """
    # Vérifier que l'apprenant existe
    apprenant_dict = repo.get_by_id(id_apprenant)
    if not apprenant_dict:
        raise HTTPException(status_code=404, detail="Apprenant non trouvé")

    # Vérifier qu'il a une ontologie assignée. Si non, on renvoie une progression de 0.
    if not apprenant_dict.get('ontologie_reference_id'):
        return ProgressResponse(
            id_apprenant=id_apprenant,
            ontologie_reference_id=0,
            total_aavs=0,
            aavs_maitrise=0,
            taux_progression=0.0
        )

    with get_db_connection() as session:
        # Récupérer les AAVs actifs de l'ontologie
        onto = session.query(OntologyReferenceModel).filter(
            OntologyReferenceModel.id_reference == apprenant_dict['ontologie_reference_id']
        ).first()

        if not onto:
            raise HTTPException(
                status_code=404,
                detail="L'ontologie référencée n'existe plus en base"
            )

        aavs_ids = onto.aavs_ids_actifs or []
        total_aavs = len(aavs_ids)

        if total_aavs == 0:
            return ProgressResponse(
                id_apprenant=id_apprenant,
                ontologie_reference_id=apprenant_dict['ontologie_reference_id'],
                total_aavs=0,
                aavs_maitrise=0,
                taux_progression=0.0
            )

        # Compter combien de ces AAVs sont maîtrisés par l'apprenant (niveau >= 0.9)
        nb_maitrise = session.query(func.count(StatutApprentissageModel.id)).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant,
            StatutApprentissageModel.id_aav_cible.in_(aavs_ids),
            StatutApprentissageModel.niveau_maitrise >= 0.9
        ).scalar() or 0

        taux = round(nb_maitrise / total_aavs * 100, 2)

        return ProgressResponse(
            id_apprenant=id_apprenant,
            ontologie_reference_id=apprenant_dict['ontologie_reference_id'],
            total_aavs=total_aavs,
            aavs_maitrise=nb_maitrise,
            taux_progression=taux
        )
