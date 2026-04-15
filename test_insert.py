import json
from app.model.model import Rapport
from app.database import RapportRepository
from datetime import datetime

rap = Rapport(
    type_rapport="aav",
    id_cible=1,
    periode_debut=datetime.now(),
    periode_fin=datetime.now(),
    format="pdf",
    date_generation=datetime.now(),
    contenu='{"test": 123}',
    format_fichier="pdf"
)

try:
    RapportRepository().create(rap)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
