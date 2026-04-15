import sqlite3
from pathlib import Path

# Chemin vers la base de données
DB_PATH = Path(__file__).resolve().parents[1] / "platonAAV.db"

def init_db():
    """
    Initialise et peuple la base de données avec des données d'exemple réalistes.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Insertion des Ontologies
    cursor.execute("DELETE FROM ontology_reference")
    ontologies = [
        (1, "Programmation", "[]", "Concepts de base, structures de données et POO."),
        (2, "Base de données", "[]", "Conception SQL, modélisation et optimisation."),
        (3, "Tests Logiciels", "[]", "Unit testing, intégration et assurance qualité.")
    ]
    cursor.executemany("INSERT INTO ontology_reference (id_reference, discipline, aavs_ids_actifs, description) VALUES (?, ?, ?, ?)", ontologies)

    # 2. Insertion des AAV (Acquis d'Apprentissage Visés)
    cursor.execute("DELETE FROM aav")
    aavs = [
        (101, "Variables et Types", "Programmation", "L1 Informatique", "Savoir manipuler les types primitifs."),
        (102, "Boucles et Contrôle", "Programmation", "L1 Informatique", "Maîtriser les structures de contrôle for/while."),
        (103, "Fonctions et Portée", "Programmation", "L1 Informatique", "Définir des fonctions avec paramètres et retour."),
        (201, "Modèle Conceptuel", "Base de données", "L2 Informatique", "Savoir dessiner un MCD propre."),
        (301, "Tests Unitaires", "Tests Logiciels", "L3 Informatique", "Écrire des cas de tests pour des fonctions simples.")
    ]
    cursor.executemany("INSERT INTO aav (id_aav, nom, discipline, enseignement, description_markdown) VALUES (?, ?, ?, ?, ?)", aavs)

    # 3. Insertion des Apprenants
    cursor.execute("DELETE FROM apprenant")
    learners = [
        (1, "Alice Martin", "alice@univ.fr", 1),
        (2, "Bob Durand", "bob@univ.fr", 1),
        (3, "Charlie Leroy", "charlie@univ.fr", 2)
    ]
    cursor.executemany("INSERT INTO apprenant (id_apprenant, nom_utilisateur, email, ontologie_reference_id) VALUES (?, ?, ?, ?)", learners)

    # 4. Insertion des Activités Pédagogiques
    cursor.execute("DELETE FROM activite_pedagogique")
    activites = [
        (1, "TP Python n°1", "initiation", "Installation et variables", "Programmation", "Facile"),
        (2, "TD SQL avancé", "revision", "Requêtes complexes et jointures", "Base de données", "Moyen")
    ]
    cursor.executemany("INSERT INTO activite_pedagogique (id_activite, nom, type_activite, description, discipline, niveau_difficulte) VALUES (?, ?, ?, ?, ?, ?)", activites)

    # 5. Insertion des Sessions
    cursor.execute("DELETE FROM session_apprenant")
    sessions = [
        (1, 1, 1, "2024-04-01 10:00:00", "2024-04-01 12:00:00", "closed", 100.0, "Bonne progression globale."),
        (2, 1, 2, "2024-04-15 14:00:00", None, "open", 10.0, None)
    ]
    cursor.executemany("INSERT INTO session_apprenant (id_session, id_activite, id_apprenant, date_debut, date_fin, statut, progression_pourcentage, bilan_session) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sessions)

    # 6. Insertion des Tentatives
    cursor.execute("DELETE FROM tentative")
    attempts = [
        (1, 1, 1, 101, 0.85, "2024-04-01 10:15:00", 1),
        (2, 1, 1, 102, 0.30, "2024-04-01 10:45:00", 0),
        (3, 1, 1, 102, 0.95, "2024-04-01 11:30:00", 1)
    ]
    cursor.executemany("INSERT INTO tentative (id, id_exercice_ou_evenement, id_apprenant, id_aav_cible, score_obtenu, date_tentative, est_valide) VALUES (?, ?, ?, ?, ?, ?, ?)", attempts)

    conn.commit()
    conn.close()
    print("Base de données mise à jour avec des données complètes et conformes au schéma.")

if __name__ == "__main__":
    init_db()
