# app/routeurs/promptFabricationAAV.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.model.model import PromptFabricationAAV, PromptCreate, PromptUpdate
from app.database import get_db_connection, BaseRepository, to_json, PromptFabricationAAVModel, AAVModel



router = APIRouter(
    tags=["Prompts"],
    responses={
        404: {"description": "Prompt non trouvé"},
        422: {"description": "Données invalides"},
    }
)


class PromptRepository(BaseRepository):
    """Repository dédié aux prompts de fabrication AAV."""

    def __init__(self):
        super().__init__(PromptFabricationAAVModel)

    def create(self, data: dict) -> int:
        """Crée un prompt et retourne son ID."""
        with get_db_connection() as session:
            new_prompt = PromptFabricationAAVModel(
                cible_aav_id=data["cible_aav_id"],
                type_exercice_genere=data.get("type_exercice_genere"),
                prompt_texte=data["prompt_texte"],
                version_prompt=data.get("version_prompt", 1),
                created_by=data.get("created_by"),
                is_active=data.get("is_active", True),
                metadata=data.get("metadata")
            )
            session.add(new_prompt)
            session.commit()
            session.refresh(new_prompt)
            return new_prompt.id_prompt


    def update(self, id_prompt: int, data: dict) -> bool:
        """Met à jour un prompt (partiellement ou complètement)."""
        with get_db_connection() as session:
            obj = session.query(PromptFabricationAAVModel).filter(PromptFabricationAAVModel.id_prompt == id_prompt).first()
            if not obj:
                return False
            
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            session.commit()
            return True



# Instance du repository
repo = PromptRepository()


# ============================================
# FONCTION UTILITAIRE PRIVÉE
# ============================================

def _get_aav(id_aav: int) -> Optional[dict]:
    """Récupère un AAV par son ID, retourne None s'il n'existe pas."""
    with get_db_connection() as session:
        obj = session.query(AAVModel).filter(AAVModel.id_aav == id_aav).first()
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns} if obj else None



# ============================================
# ENDPOINTS CRUD
# ============================================

@router.get("/", response_model=List[PromptFabricationAAV])
def list_prompts(
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de résultats"),
    offset: int = Query(0, ge=0, description="Offset pour la pagination")
):
    """Liste tous les prompts de fabrication."""
    with get_db_connection() as session:
        query = session.query(PromptFabricationAAVModel)
        if is_active is not None:
            query = query.filter(PromptFabricationAAVModel.is_active == is_active)
        
        rows = query.offset(offset).limit(limit).all()
        return [PromptFabricationAAV.model_validate(r) for r in rows]



@router.get("/{id_prompt}", response_model=PromptFabricationAAV)
def get_prompt(id_prompt: int):
    """Récupère un prompt spécifique par son identifiant."""
    with get_db_connection() as session:
        obj = session.query(PromptFabricationAAVModel).filter(PromptFabricationAAVModel.id_prompt == id_prompt).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Prompt non trouvé")
        return PromptFabricationAAV.model_validate(obj)


@router.post("/", response_model=PromptFabricationAAV, status_code=201)
def create_prompt(prompt: PromptCreate):
    """Crée un nouveau prompt de fabrication."""
    if not _get_aav(prompt.cible_aav_id):
        raise HTTPException(
            status_code=404,
            detail=f"AAV {prompt.cible_aav_id} non trouvé"
        )
    try:
        new_id = repo.create(prompt.model_dump())
        created = repo.get_by_id(new_id)
        return PromptFabricationAAV(**created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_prompt}", response_model=PromptFabricationAAV)
def update_prompt_full(id_prompt: int, prompt: PromptCreate):
    """Remplace complètement un prompt (tous les champs)."""
    if not repo.get_by_id(id_prompt):
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    repo.update(id_prompt, prompt.model_dump())
    return PromptFabricationAAV(**repo.get_by_id(id_prompt))


@router.patch("/{id_prompt}", response_model=PromptFabricationAAV)
def update_prompt_partial(id_prompt: int, prompt: PromptUpdate):
    """Met à jour partiellement un prompt."""
    if not repo.get_by_id(id_prompt):
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    update_data = {
        k: v for k, v in prompt.model_dump().items() if v is not None
    }
    if update_data:
        repo.update(id_prompt, update_data)
    return PromptFabricationAAV(**repo.get_by_id(id_prompt))


@router.delete("/{id_prompt}", status_code=204)
def delete_prompt(id_prompt: int):
    """Désactive (soft delete) un prompt. Retourne 204 No Content."""
    if not repo.get_by_id(id_prompt):
        raise HTTPException(status_code=404, detail="Prompt non trouvé")
    with get_db_connection() as session:
        obj = session.query(PromptFabricationAAVModel).filter(PromptFabricationAAVModel.id_prompt == id_prompt).first()
        if obj:
            obj.is_active = False
            session.commit()
    return None

