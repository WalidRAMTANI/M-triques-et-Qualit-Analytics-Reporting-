import sqlite3
from datetime import datetime

def remplissage_test():
    # Connexion à ta base
    conn = sqlite3.connect("platonAAV.db")
    cursor = conn.cursor()
    
    # On prépare une date propre
    maintenant = datetime.now().isoformat()

    try:
        # 1. On crée une AAV fictive (pour que la base soit cohérente)
        cursor.execute("""
            INSERT OR IGNORE INTO aav (id_aav, nom, discipline, type_aav) 
            VALUES (1, 'Programmation Python', 'Informatique', 'Atomique')
        """)

        # 2. On crée TA métrique (Groupe 7) liée à l'AAV n°1
        cursor.execute("""
            INSERT OR IGNORE INTO metrique_qualite_aav (
                id_metrique, id_aav, score_covering_ressources, taux_succes_moyen, 
                est_utilisable, nb_tentatives_total, nb_apprenants_distincts, 
                ecart_type_scores, date_calcul, periode_debut, periode_fin
            ) VALUES (1, 1, 0.85, 0.72, 1, 150, 45, 0.12, ?, ?, ?)
        """, (maintenant, maintenant, maintenant))

        conn.commit()
        print("C'est bon ! Données insérées pour l'ID 1.")
    except Exception as e:
        print("Erreur lors de l'insertion :", e)
    finally:
        conn.close()

if __name__ == "__main__":
    remplissage_test()