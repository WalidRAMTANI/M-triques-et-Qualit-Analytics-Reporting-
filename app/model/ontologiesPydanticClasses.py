from pydantic import BaseModel

class OntologyResponse(BaseModel):
    id_reference: int
    discipline: str | None
    aavs_ids_actifs: str | None
    description: str | None


class OntologyCreate(BaseModel):
    discipline: str
    aavs_ids_actifs: str | None = None
    description: str | None = None
    
class OntologyUpdate(BaseModel):
    discipline: str | None = None
    aavs_ids_actifs: str | None = None
    description: str | None = None
   

