from fastapi import APIRouter,HTTPException

from app.db import get_db_connection
from app.schemas.ontologiesPydanticClasses import OntologyCreate, OntologyResponse


router = APIRouter(prefix="/ontologies", tags=["ontologies"])

@router.get("/", summary="Liste des ontologies de référence", response_model = list[OntologyResponse])
def get_ontologies():
    with get_db_connection() as con:
        rows = con.execute("SELECT * FROM ontology_reference").fetchall()

        return [OntologyResponse.model_validate(dict(row)) for row in rows]


@router.get("/{id_reference}", summary="Récupération d'une ontologie ", response_model = OntologyResponse)
def get_single_ontology(id_reference: int):
    with get_db_connection() as con:
        row = con.execute("SELECT * FROM ontology_reference where id_reference = ?", (id_reference,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ontology not found")
        return OntologyResponse.model_validate(dict(row))
    
@router.post("/", summary="Création d'une ontologie", response_model=OntologyResponse, status_code = 201)
def create_ontology(ontology: OntologyCreate):
    with get_db_connection() as con:
        cursor = con.execute(""" 
                    INSERT INTO ontology_reference(  
                        discipline, 
                        aavs_ids_actifs,
                        description
                    )
                    VALUES(?,?,?)
                    """,
                    (ontology.discipline, ontology.aavs_ids_actifs, ontology.description) )
        
        new_id = cursor.lastrowid
        row = con.execute(
            "SELECT * FROM ontology_reference WHERE id_reference = ?",
            (new_id,),
        ).fetchone()

        if not row :
            raise HTTPException(status_code=500, detail="Failed to get the new ontology")
        
        return OntologyResponse.model_validate(dict(row))



@router.put("/{id_reference}", summary="Mise à jour d'une ontologie")
def update_ontology(id_reference: int, ontology: OntologyCreate):
    pass

@router.delete("/{id_reference}", summary="Suppression d'une ontologie")
def delete_ontology(id_reference: int):
    pass