import sqlite3
import os
from database import init_database, DATABASE_PATH

def setup():
    # 1. On s'assure que le fichier SQL existe avant de commencer
    sql_file = "donnees_test.sql"
    if not os.path.exists(sql_file):
        print(f"❌ Erreur : Le fichier {sql_file} est introuvable dans le dossier.")
        return

    # 2. On recrée les tables proprement
    print("Initialisation des tables...")
    init_database()

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            # On active les clés étrangères pour la cohérence
            conn.execute("PRAGMA foreign_keys = ON;")
            
            # 3. ON AJOUTE LE PROF (Obligatoire pour les jointures)
            # On vérifie s'il existe déjà pour ne pas planter
            conn.execute("""
                INSERT OR IGNORE INTO enseignant (id_enseignant, nom, email, discipline) 
                VALUES (1, 'Professeur Platon', 'platon@univ.fr', 'Programmation')
            """)

            # 4. ON LIT LE DUMP SQL
            print(f"Injection des données depuis {sql_file}...")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
                
            # On exécute tout d'un coup
            conn.executescript(sql_script)
            
            # 5. MISE À JOUR CRUCIALE : Lier les AAV au prof ID 1
            # Ton dump n'a pas de id_enseignant, on les force sur l'ID 1 pour que le dashboard marche
            conn.execute("UPDATE aav SET id_enseignant = 1 WHERE discipline = 'Programmation'")
            
            conn.commit()
            print(f"✅ Succès : Base de données prête et liée au prof ID 1.")

    except Exception as e:
        print(f"❌ Erreur lors de l'injection : {e}")

if __name__ == "__main__":
    setup()