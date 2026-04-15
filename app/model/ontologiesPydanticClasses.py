from pydantic import BaseModel, ConfigDict
from typing import Optional

class OntologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_reference: int
    discipline: Optional[str]
    aavs_ids_actifs: Optional[list] = []
    description: Optional[str]


class OntologyCreate(BaseModel):
    discipline: str
    aavs_ids_actifs: Optional[list] = []
    description: Optional[str] = None
    
class OntologyUpdate(BaseModel):
    discipline: Optional[str] = None
    aavs_ids_actifs: Optional[list] = None
    description: Optional[str] = None
   

