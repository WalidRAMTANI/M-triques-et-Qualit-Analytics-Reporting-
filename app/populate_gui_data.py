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

        # 2. Add Enseignants (15)
        enseignants = []
        for i in range(1, 16):
            enseignants.append(EnseignantModel(id_enseignant=i, nom=f"Prof {i}", email=f"prof{i}@edu.fr", discipline=json.dumps(["Math", "Physique"]), date_creation=datetime.now()))
        db.add_all(enseignants)
        db.commit()

        # 3. Add AAVs (15)
        aavs = []
        for i in range(1, 16):
            prereqs = [i-1] if i > 1 else []
            enfants = [i+1] if i < 15 else []
            aavs.append(AAVModel(id_aav=i, nom=f"AAV {i}", libelle_integration=f"AAV-L{i}", discipline="Mathématiques", enseignement="L1", id_enseignant=max(1, i%15), type_aav="Compétence", description_markdown=f"# Cours {i}\nLe cours numero {i}", prerequis_ids=prereqs, aav_enfant_ponderation=enfants, is_active=True, version=1))
        db.add_all(aavs)
        db.commit()

        # 4. Add Ontology References (10+)
        ontologies = []
        for i in range(1, 16):
            ontologies.append(OntologyReferenceModel(id_reference=i, discipline="Sciences", aavs_ids_actifs=[1,2,3,4,5], description=f"Onto {i}"))
        db.add_all(ontologies)
        db.commit()

        # 5. Add Apprenants (15)
        apprenants = []
        for i in range(1, 16):
            apprenants.append(ApprenantModel(id_apprenant=i, nom_utilisateur=f"eleve{i}", email=f"elev{i}@edu.fr", ontologie_reference_id=1, statuts_actifs_ids=[1, 2], is_active=True))
        db.add_all(apprenants)
        db.commit()

        # 6. Add Statuts Apprentissage (15)
        statuts = []
        for i in range(1, 16):
            statuts.append(StatutApprentissageModel(id_apprenant=i, id_aav_cible=max(1, i%15), niveau_maitrise=0.1*(i%10), est_maitrise=(i>5), historique_tentatives_ids=[], date_debut_apprentissage=datetime.now()))
        db.add_all(statuts)
        db.commit()

        # 7. Add Tentatives (15)
        tentatives = []
        for i in range(1, 16):
            tentatives.append(TentativeModel(id_exercice_ou_evenement=100+i, id_apprenant=i, id_aav_cible=max(1, i%15), score_obtenu=(i%10)*0.1, est_valide=(i%2==0)))
        db.add_all(tentatives)
        db.commit()

        # 8. Add Activites Pedagogiques (15)
        activites = []
        for i in range(1, 16):
            activites.append(ActivitePedagogiqueModel(id_activite=i, nom=f"Activite {i}", description=f"Desc {i}", type_activite="TP", discipline="Test", niveau_difficulte="Facile", duree_estimee_minutes=45))
        db.add_all(activites)
        db.commit()

        # 9. Add Sessions (15)
        sessions = []
        for i in range(1, 16):
            sessions.append(SessionApprenantModel(id_session=i, id_activite=i, id_apprenant=i, date_debut=datetime.now() - timedelta(hours=i), statut="closed", progression_pourcentage=90.0, bilan_session=json.dumps({"total_attempts": i, "valid_attempts": i//2, "average_score": 0.8})))
        db.add_all(sessions)
        db.commit()

        # 10. Add Prompts (15)
        prompts = []
        for i in range(1, 16):
            prompts.append(PromptFabricationAAVModel(id_prompt=i, cible_aav_id=i, type_exercice_genere="QCM", prompt_texte=f"Prompt {i}", is_active=True))
        db.add_all(prompts)
        db.commit()

        # 11. Add Exercices (15)
        exercices = []
        for i in range(1, 16):
            exercices.append(ExerciceInstanceModel(id_exercice=i, id_prompt_source=i, titre=f"Exo {i}", id_aav_cible=i, type_evaluation="QCM", contenu=f"Contenu exo {i}", difficulte="Facile", nb_utilisations=10, taux_succes_moyen=0.75))
        db.add_all(exercices)
        db.commit()

        # 12. Add Metriques Qualite (15)
        metriques = []
        for i in range(1, 16):
            metriques.append(MetriqueQualiteAAVModel(id_metrique=i, id_aav=i, score_covering_ressources=0.8, taux_succes_moyen=0.35, est_utilisable=True, nb_tentatives_total=50, nb_apprenants_distincts=12, ecart_type_scores=0.15, date_calcul=datetime.now(), periode_debut=datetime.now()-timedelta(days=30), periode_fin=datetime.now()))
        db.add_all(metriques)
        db.commit()

        # 13. Add Alertes (15)
        alertes = []
        for i in range(1, 16):
            alertes.append(AlerteQualiteModel(id_alerte=i, type_alerte="Difficulté élevée", nom_cible=f"AAV {i}", severite="High" if i%2==0 else "Medium", description="Taux de succès faible.", statut="active", date_detection=datetime.now()))
        db.add_all(alertes)
        db.commit()

        # 14. Add Rapports (15)
        rapports = []
        for i in range(1, 16):
            rapports.append(RapportPeriodiqueModel(id_rapport=i, type_rapport="Hebdomadaire", id_cible=i, date_generation=datetime.now(), format="PDF", contenu={"stats": "ok"}, format_fichier=f"rapport_{i}.pdf"))
        db.add_all(rapports)
        db.commit()

        print("Base de données peuplée avec succès !")
    except Exception as e:
        print(f"Erreur lors du peuplage : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()
