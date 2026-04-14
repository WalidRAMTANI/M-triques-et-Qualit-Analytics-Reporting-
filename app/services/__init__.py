from .maitrise import calculer_maitrise

def calculer_maitrise_reelle(id_apprenant: int, id_aav: int) -> float:
    return 0.5

def determiner_difficulte_cible(maitrise: float) -> str:
    if maitrise < 0.4: return "debutant"
    if maitrise < 0.8: return "intermediaire"
    return "avance"

def selectionner_sequence_exercices(id_apprenant: int, id_aav: int, nb_exercices: int = 3) -> list:
    return []
