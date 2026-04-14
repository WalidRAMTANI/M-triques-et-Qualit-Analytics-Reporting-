import sqlite3
import json
import os

def fix_teacher():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(BASE_DIR), "platonAAV.db")
    print(f"Connexion à la base : {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Trouver les disciplines existantes
    cur.execute("SELECT DISTINCT discipline FROM aav")
    disciplines_db = [row[0] for row in cur.fetchall()]
    print(f"Disciplines trouvées dans les AAV : {disciplines_db}")
    
    # Mettre à jour l'enseignant 1 avec ces disciplines
    # On utilise JSON pour rester compatible avec le service
    disc_json = json.dumps(disciplines_db)
    
    cur.execute("UPDATE enseignant SET discipline = ? WHERE id_enseignant = 1", (disc_json,))
    conn.commit()
    
    cur.execute("SELECT * FROM enseignant WHERE id_enseignant = 1")
    try:
        print(f"Enseignant mis à jour : {cur.fetchone()}")
    except Exception as err:
        print(f"ERREUR DASHBOARD (ID {champ_recherche.value}) : {err}")
        text_info.value = f"Aucun enseignant trouvé pour l'ID {champ_recherche.value}"
    
    conn.close()

if __name__ == "__main__":
    fix_teacher()
