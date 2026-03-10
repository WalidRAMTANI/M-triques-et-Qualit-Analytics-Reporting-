import sqlite3
import json
from datetime import datetime

def to_json(data):
    return json.dumps(data, ensure_ascii=False)

def remplissage_correct():
    # Connexion à ta base platonAAV.db
    conn = sqlite3.connect("platonAAV.db")
    cursor = conn.cursor()
    
    # Date au format ISO
    maintenant = datetime.now().isoformat()

    try:
        # 1. CRÉATION DU PROFESSEUR 
        # Colonnes selon ton database.py : id_enseignant, nom, email, discipline (JSON), date_creation
        disciplines_json = to_json(["Informatique", "Programmation Python"])
        
        cursor.execute("""
            INSERT OR REPLACE INTO enseignant (id_enseignant, nom, email, discipline, date_creation) 
            VALUES (1, 'Zola', 'emile.zola@platon.edu', ?, ?)
        """, (disciplines_json, maintenant))

        # 2. CRÉATION DE L'AAV (Liée au prof 1)
        # On respecte les contraintes : nom, discipline, id_enseignant, type_aav
        cursor.execute("""
            INSERT OR REPLACE INTO aav (id_aav, nom, discipline, id_enseignant, type_aav) 
            VALUES (1, 'Bases du Python', 'Informatique', 1, 'Atomique')
        """, )

        # 3. CRÉATION DE LA MÉTRIQUE
        # Table : metrique_qualite_aav
        cursor.execute("""
            INSERT OR REPLACE INTO metrique_qualite_aav (
                id_metrique, id_aav, score_covering_ressources, taux_succes_moyen, 
                est_utilisable, nb_tentatives_total, nb_apprenants_distincts, 
                ecart_type_scores, date_calcul, periode_debut, periode_fin
            ) VALUES (1, 1, 0.85, 0.72, 1, 150, 45, 0.12, ?, ?, ?)
        """, (maintenant, maintenant, maintenant))

        conn.commit()
        print("✅ Données insérées ! Professeur créé et AAV liée sans erreur.")

    except Exception as e:
        print(f"❌ Erreur réelle : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    remplissage_correct()