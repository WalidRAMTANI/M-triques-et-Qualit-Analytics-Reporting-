from pydantic import BaseModel
from typing import Optional

class OntologyResponse(BaseModel):
    id_reference: int
    discipline: Optional[str]
    aavs_ids_actifs: Optional[str]
    description: Optional[str]


class OntologyCreate(BaseModel):
    discipline: str
    aavs_ids_actifs: Optional[str] = None
    description: Optional[str] = None
    
class OntologyUpdate(BaseModel):
    discipline: Optional[str] = None
    aavs_ids_actifs: Optional[str] = None
    description: Optional[str] = None
   

