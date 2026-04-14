from fastapi import APIRouter,HTTPException

from app.database import get_db_connection, OntologyReferenceModel
from app.model.ontologiesPydanticClasses import OntologyCreate, OntologyResponse



router = APIRouter(prefix="/ontologies", tags=["ontologies"])

@router.get("/", summary="Liste des ontologies de référence", response_model = list[OntologyResponse])
def get_ontologies():
    with get_db_connection() as session:
        rows = session.query(OntologyReferenceModel).all()
        return [OntologyResponse.model_validate(row) for row in rows]



@router.get("/{id_reference}", summary="Récupération d'une ontologie ", response_model = OntologyResponse)
def get_single_ontology(id_reference: int):
    with get_db_connection() as session:
        row = session.query(OntologyReferenceModel).filter(OntologyReferenceModel.id_reference == id_reference).first()
        if not row:
            raise HTTPException(status_code=404, detail="Ontology not found")
        return OntologyResponse.model_validate(row)

    
@router.post("/", summary="Création d'une ontologie", response_model=OntologyResponse, status_code = 201)
def create_ontology(ontology: OntologyCreate):
    with get_db_connection() as session:
        new_onto = OntologyReferenceModel(
            discipline=ontology.discipline,
            aavs_ids_actifs=ontology.aavs_ids_actifs,
            description=ontology.description
        )
        session.add(new_onto)
        session.commit()
        session.refresh(new_onto)
        return OntologyResponse.model_validate(new_onto)




@router.put("/{id_reference}", summary="Mise à jour d'une ontologie")
def update_ontology(id_reference: int, ontology: OntologyCreate):
    pass

@router.delete("/{id_reference}", summary="Suppression d'une ontologie")
def delete_ontology(id_reference: int):
    pass