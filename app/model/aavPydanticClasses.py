from pydantic import BaseModel

class AAVResponse(BaseModel):
    id_aav: int
    nom: str | None
    libelle_integration: str | None
    discipline: str | None
    enseignement: str | None
    description_markdown: str | None
    type_aav: str | None
    


class AAVCreate(BaseModel):
    nom: str
    libelle_integration: str
    discipline: str
    enseignement: str
    description_markdown: str | None = None
    type_aav: str
    
    prerequis_ids: str | None = None
    prerequis_externes_codes: str | None = None
    code_prerequis_interdisciplinaire: str | None = None
    aav_enfant_ponderation: str | None = None
    type_evaluation: str | None = None 
    ids_exercices: str | None = None
    prompts_fabrication_ids: str | None = None
    regles_progression: str | None = None

class AAVUpdate(BaseModel):
    nom: str 
    libelle_integration: str | None = None
    discipline: str 
    enseignement: str | None = None
    description_markdown: str | None = None
    type_aav: str 
    
    prerequis_ids: str | None = None
    prerequis_externes_codes: str | None = None
    code_prerequis_interdisciplinaire: str | None = None
    aav_enfant_ponderation: str | None = None
    type_evaluation: str | None = None 
    ids_exercices: str | None = None
    prompts_fabrication_ids: str | None = None
    regles_progression: str | None = None

class AAVPatch(BaseModel):
    nom: str | None = None
    libelle_integration: str | None = None
    discipline: str | None = None
    enseignement: str | None = None
    description_markdown: str | None = None
    type_aav: str | None = None
    
    prerequis_ids: str | None = None
    prerequis_externes_codes: str | None = None
    code_prerequis_interdisciplinaire: str | None = None
    aav_enfant_ponderation: str | None = None
    type_evaluation: str | None = None 
    ids_exercices: str | None = None
    prompts_fabrication_ids: str | None = None
    regles_progression: str | None = None
    