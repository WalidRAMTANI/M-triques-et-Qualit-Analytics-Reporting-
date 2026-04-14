import sys
import os
from datetime import datetime, timedelta
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import (
    SessionLocal, init_database,
    AAVModel, EnseignantModel, ApprenantModel, OntologyReferenceModel,
    StatutApprentissageModel, TentativeModel, ActivitePedagogiqueModel,
    SessionApprenantModel, PromptFabricationAAVModel, ExerciceInstanceModel,
    MetriqueQualiteAAVModel, AlerteQualiteModel, RapportPeriodiqueModel
)

def populate():
    db = SessionLocal()
    try:
        # 1. Initialize DB (create tables)
        init_database()

        # Clear existing data to avoid PK conflicts
        db.query(StatutApprentissageModel).delete()
        db.query(TentativeModel).delete()
        db.query(SessionApprenantModel).delete()
        db.query(ExerciceInstanceModel).delete()
        db.query(PromptFabricationAAVModel).delete()
        db.query(AAVModel).delete()
        db.query(EnseignantModel).delete()
        db.query(ApprenantModel).delete()
        db.query(OntologyReferenceModel).delete()
        db.query(ActivitePedagogiqueModel).delete()
        db.query(MetriqueQualiteAAVModel).delete()
        db.query(AlerteQualiteModel).delete()
        db.query(RapportPeriodiqueModel).delete()
        db.commit()

        # 2. Add Enseignants
        prof1 = EnseignantModel(id_enseignant=1, nom="Dr. Alice Smith", email="alice.smith@edu.fr", discipline=json.dumps(["Mathématiques", "Informatique"]), date_creation=datetime.now())
        prof2 = EnseignantModel(id_enseignant=2, nom="Prof. Bob Johnson", email="bob.johnson@edu.fr", discipline=json.dumps(["Physique", "Data Science"]), date_creation=datetime.now())
        db.add_all([prof1, prof2])
        db.commit()

        # 3. Add AAVs
        aav1 = AAVModel(id_aav=1, nom="Algèbre Linéaire", libelle_integration="ALG-L1", discipline="Mathématiques", enseignement="L1 MIASHS", id_enseignant=1, type_aav="Compétence", description_markdown="# Cours d'Algèbre\nMatrices et systèmes linéaires.", is_active=True, version=1)
        aav2 = AAVModel(id_aav=2, nom="Programmation Python", libelle_integration="PY-L1", discipline="Informatique", enseignement="L1 MIASHS", id_enseignant=1, type_aav="Compétence", description_markdown="# Intro Python\nVariables, boucles, fonctions.", is_active=True, version=1)
        aav3 = AAVModel(id_aav=3, nom="Mécanique du Point", libelle_integration="PHYS-L1", discipline="Physique", enseignement="L1 Physique", id_enseignant=2, type_aav="Compétence", description_markdown="# Newton\nLois du mouvement.", is_active=True, version=1)
        db.add_all([aav1, aav2, aav3])
        db.commit()

        # 4. Add Ontology References
        ont1 = OntologyReferenceModel(id_reference=1, discipline="Sciences", aavs_ids_actifs=[1, 2, 3], description="Tronc commun sciences L1")
        db.add(ont1)
        db.commit()

        # 5. Add Apprenants
        stud1 = ApprenantModel(id_apprenant=1, nom_utilisateur="eleve1", email="eleve1@edu.fr", ontologie_reference_id=1, statuts_actifs_ids=[1, 2], is_active=True)
        stud2 = ApprenantModel(id_apprenant=2, nom_utilisateur="eleve2", email="eleve2@edu.fr", ontologie_reference_id=1, statuts_actifs_ids=[1, 3], is_active=True)
        db.add_all([stud1, stud2])
        db.commit()

        # 6. Add Statuts Apprentissage
        stat1 = StatutApprentissageModel(id_apprenant=1, id_aav_cible=1, niveau_maitrise=0.45, est_maitrise=False, date_debut_apprentissage=datetime.now())
        stat2 = StatutApprentissageModel(id_apprenant=1, id_aav_cible=2, niveau_maitrise=0.85, est_maitrise=True, date_debut_apprentissage=datetime.now())
        stat3 = StatutApprentissageModel(id_apprenant=2, id_aav_cible=1, niveau_maitrise=0.10, est_maitrise=False, date_debut_apprentissage=datetime.now())
        db.add_all([stat1, stat2, stat3])
        db.commit()

        # 7. Add Tentatives
        t1 = TentativeModel(id_exercice_ou_evenement=101, id_apprenant=1, id_aav_cible=1, score_obtenu=0.5, est_valide=True)
        t2 = TentativeModel(id_exercice_ou_evenement=102, id_apprenant=2, id_aav_cible=1, score_obtenu=0.1, est_valide=False)
        db.add_all([t1, t2])
        db.commit()

        # 8. Add Activites Pedagogiques
        act1 = ActivitePedagogiqueModel(id_activite=1, nom="TP Python Tableaux", description="Manipuler des listes en Python", type_activite="TP", discipline="Informatique", niveau_difficulte="Facile", duree_estimee_minutes=45)
        db.add(act1)
        db.commit()

        # 9. Add Sessions
        sess1 = SessionApprenantModel(id_session=1, id_activite=1, id_apprenant=1, date_debut=datetime.now() - timedelta(hours=1), statut="closed", progression_pourcentage=100.0, bilan_session=json.dumps({"total_attempts": 5, "valid_attempts": 4, "average_score": 0.8}))
        db.add(sess1)
        db.commit()

        # 10. Add Prompts & Exercises
        pr1 = PromptFabricationAAVModel(id_prompt=1, cible_aav_id=2, type_exercice_genere="QCM", prompt_texte="Génère un QCM sur les listes Python.", is_active=True)
        db.add(pr1)
        db.commit()
        ex1 = ExerciceInstanceModel(id_exercice=1, id_prompt_source=1, titre="QCM Listes", id_aav_cible=2, type_evaluation="QCM", contenu="Quelle fonction ajoute un élément à une liste ?", difficulte="Facile", nb_utilisations=10, taux_succes_moyen=0.75)
        db.add(ex1)
        db.commit()

        # 11. Add MetriqueQualite
        met1 = MetriqueQualiteAAVModel(id_metrique=1, id_aav=1, score_covering_ressources=0.8, taux_succes_moyen=0.35, est_utilisable=True, nb_tentatives_total=50, nb_apprenants_distincts=12, ecart_type_scores=0.15, date_calcul=datetime.now(), periode_debut=datetime.now()-timedelta(days=30), periode_fin=datetime.now())
        db.add(met1)
        db.commit()

        # 12. Add Alertes
        al1 = AlerteQualiteModel(id_alerte=1, type_alerte="Difficulté élevée", nom_cible="Algèbre Linéaire", severite="High", description="Le taux de succès est tombé à 35%.", statut="active", date_detection=datetime.now())
        al2 = AlerteQualiteModel(id_alerte=2, type_alerte="AAV Inutilisée", nom_cible="Mécanique du Point", severite="Medium", description="Aucune tentative enregistrée sur cette AAV depuis 30 jours.", statut="active", date_detection=datetime.now())
        db.add_all([al1, al2])
        db.commit()

        # 13. Add Rapports
        rep1 = RapportPeriodiqueModel(id_rapport=1, type_rapport="Hebdomadaire", id_cible=1, date_generation=datetime.now(), format="PDF", contenu={"stats": "ok"}, format_fichier="rapport_hebdo_2024.pdf")
        db.add(rep1)
        db.commit()

        print("Base de données peuplée avec succès !")
    except Exception as e:
        print(f"Erreur lors du peuplage : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()
