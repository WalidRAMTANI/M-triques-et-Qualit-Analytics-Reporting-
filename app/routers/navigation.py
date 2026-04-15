from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.database import (
    get_db_connection, from_json, to_json,
    AAVModel, NavigationCacheModel, ApprenantModel, 
    OntologyReferenceModel, StatutApprentissageModel, RevisionHistoryModel
)
from app.model.model import AAV
from sqlalchemy import and_


router = APIRouter(
    tags=["Navigation"],
)

# ============================================================
# CACHE NAVIGATION
# ============================================================

def load_cache(session, id_apprenant, categorie):
    results = session.query(AAVModel).join(
        NavigationCacheModel, AAVModel.id_aav == NavigationCacheModel.id_aav
    ).filter(
        NavigationCacheModel.id_apprenant == id_apprenant,
        NavigationCacheModel.categorie == categorie,
        AAVModel.is_active == True
    ).all()

    return [AAV.model_validate(r) for r in results]



def save_cache(session, id_apprenant, aav_id, categorie, raison=None):
    # UPSERT if possible, otherwise use existing logic
    # In SQLite 3.24+ we could use ON CONFLICT, but SA uses another way
    existing = session.query(NavigationCacheModel).filter(
        and_(
            NavigationCacheModel.id_apprenant == id_apprenant,
            NavigationCacheModel.id_aav == aav_id,
            NavigationCacheModel.categorie == categorie
        )
    ).first()

    if existing:
        existing.dernier_calcul = datetime.now()
        existing.raison_blocage = raison
    else:
        new_entry = NavigationCacheModel(
            id_apprenant=id_apprenant,
            id_aav=aav_id,
            categorie=categorie,
            dernier_calcul=datetime.now(),
            raison_blocage=raison
        )
        session.add(new_entry)


# ============================================================
# ACCESSIBLE
# ============================================================
@router.get("/{id_apprenant}/accessible", response_model=List[AAV])
def get_accessible_aavs(id_apprenant: int):
    with get_db_connection() as session:
        cached = load_cache(session, id_apprenant, "accessible")
        if cached:
            return cached

        # Get learner's active AAV IDs from their ontology
        onto_data = session.query(OntologyReferenceModel.aavs_ids_actifs).join(
            ApprenantModel, ApprenantModel.ontologie_reference_id == OntologyReferenceModel.id_reference
        ).filter(ApprenantModel.id_apprenant == id_apprenant).first()

        if not onto_data or not onto_data.aavs_ids_actifs:
            return []

        aavs_ids = onto_data.aavs_ids_actifs
        accessibles = []

        # Get all relevant AAVs at once
        all_aavs = session.query(AAVModel).filter(
            and_(AAVModel.id_aav.in_(aavs_ids), AAVModel.is_active == True)
        ).all()

        # Get all status for this learner at once
        all_status = {s.id_aav_cible: s.niveau_maitrise for s in session.query(StatutApprentissageModel).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant
        ).all()}

        for aav in all_aavs:
            # déjà commencé → pas accessible
            maitrise = all_status.get(aav.id_aav, 0)
            if maitrise > 0:
                continue

            prerequis_ok = True
            prerequis_ids = aav.prerequis_ids or []
            
            for prereq_id in prerequis_ids:
                prereq_maitrise = all_status.get(prereq_id, 0)
                if prereq_maitrise < 0.8:
                    prerequis_ok = False
                    break

            if prerequis_ok:
                accessibles.append(AAV.model_validate(aav))
                save_cache(session, id_apprenant, aav.id_aav, "accessible")

        return accessibles

# ============================================================
# IN PROGRESS
# ============================================================

@router.get("/{id_apprenant}/in-progress")
def get_in_progress_aavs(id_apprenant: int):
    with get_db_connection() as session:
        cached = load_cache(session, id_apprenant, "in_progress")
        if cached:
            # We need to return raw dicts for this endpoint as it says 'return result' which was list of dicts
            return [AAV.model_validate(c).model_dump() for c in cached]

        results = session.query(AAVModel, StatutApprentissageModel.historique_tentatives_ids).join(
            StatutApprentissageModel, AAVModel.id_aav == StatutApprentissageModel.id_aav_cible
        ).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant,
            StatutApprentissageModel.niveau_maitrise > 0,
            StatutApprentissageModel.niveau_maitrise < 0.9,
            AAVModel.is_active == True
        ).all()

        final_result = []
        for aav, attempts in results:
            data = {c.name: getattr(aav, c.name) for c in aav.__table__.columns}
            data["historique_tentatives_ids"] = attempts or []
            final_result.append(data)
            save_cache(session, id_apprenant, aav.id_aav, "in_progress")

        return final_result



# ============================================================
# BLOCKED
# ============================================================

@router.get("/{id_apprenant}/blocked")
def get_blocked_aavs(id_apprenant: int):
    with get_db_connection() as session:
        blocked = []
        all_aavs = session.query(AAVModel).filter(AAVModel.is_active == True).all()
        
        all_status = {s.id_aav_cible: s.niveau_maitrise for s in session.query(StatutApprentissageModel).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant
        ).all()}

        for aav in all_aavs:
            prerequis = aav.prerequis_ids or []
            missing = []

            for prereq_id in prerequis:
                maitrise = all_status.get(prereq_id, 0)
                if maitrise < 0.8:
                    missing.append(prereq_id)

            if missing:
                data = {c.name: getattr(aav, c.name) for c in aav.__table__.columns}
                data["blocked_prerequisites"] = missing
                blocked.append(data)
                save_cache(session, id_apprenant, aav.id_aav, "blocked", missing)

        return blocked


# ============================================================
# REVIEWABLE
# ============================================================

@router.get("/{id_apprenant}/reviewable", response_model=List[AAV])
def get_reviewable_aavs(id_apprenant: int):
    with get_db_connection() as session:
        cached = load_cache(session, id_apprenant, "reviewable")
        if cached:
            return cached

        reviewable = []

        # récupérer les AAV maîtrisés
        results = session.query(AAVModel).join(
            StatutApprentissageModel, AAVModel.id_aav == StatutApprentissageModel.id_aav_cible
        ).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant,
            StatutApprentissageModel.niveau_maitrise >= 0.8,
            AAVModel.is_active == True
        ).all()

        now = datetime.now()

        for aav in results:
            # chercher l'historique de révision
            revision = session.query(RevisionHistoryModel).filter(
                and_(
                    RevisionHistoryModel.id_apprenant == id_apprenant,
                    RevisionHistoryModel.id_aav == aav.id_aav
                )
            ).first()

            # cas 1 : jamais révisé
            if not revision:
                reviewable.append(AAV.model_validate(aav))
                continue

            prochaine_revision = revision.prochaine_revision_prevue

            if prochaine_revision:
                # cas 2 : révision due
                if prochaine_revision <= now:
                    reviewable.append(AAV.model_validate(aav))
                    save_cache(session, id_apprenant, aav.id_aav, "reviewable")

        return reviewable


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/{id_apprenant}/dashboard")
def navigation_dashboard(id_apprenant: int):

    accessible = get_accessible_aavs(id_apprenant)
    in_progress = get_in_progress_aavs(id_apprenant)
    blocked = get_blocked_aavs(id_apprenant)
    reviewable = get_reviewable_aavs(id_apprenant)

    return {
        "accessible_count": len(accessible),
        "in_progress_count": len(in_progress),
        "blocked_count": len(blocked),
        "reviewable_count": len(reviewable),
        "recommended_next": accessible[:3]
    }

@router.get("/{id_apprenant}")
def get_all_navigation_aavs(id_apprenant: int):
    with get_db_connection() as session:
        result = []
        rows = session.query(
            AAVModel, StatutApprentissageModel.niveau_maitrise, StatutApprentissageModel.date_derniere_session
        ).join(
            StatutApprentissageModel, AAVModel.id_aav == StatutApprentissageModel.id_aav_cible
        ).filter(
            StatutApprentissageModel.id_apprenant == id_apprenant,
            AAVModel.is_active == True
        ).all()

        for aav, maitrise, date_session in rows:
            data = {c.name: getattr(aav, c.name) for c in aav.__table__.columns}
            data["niveau_maitrise"] = maitrise
            data["date_derniere_session"] = date_session
            result.append(data)

        return result