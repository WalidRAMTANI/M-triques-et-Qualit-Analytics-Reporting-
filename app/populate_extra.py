import sqlite3
import os

def populate_dashboard_data():
    db_path = 'platonAAV.db'
    if not os.path.exists(db_path):
        print(f"Base de données {db_path} introuvable.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Ajouter un enseignant test s'il n'existe pas
    cur.execute("SELECT COUNT(*) FROM enseignant WHERE id_enseignant=1")
    if cur.fetchone()[0] == 0:
        print("Ajout de l'enseignant test ID: 1...")
        cur.execute("""
            INSERT INTO enseignant (id_enseignant, nom, email, discipline, date_creation)
            VALUES (?, ?, ?, ?, ?)
        """, (1, "Prof. William", "william@univ.fr", '["Informatique"]', "2026-01-01"))
    
    conn.commit()
    conn.close()
    print("Population des données Dashboard terminée.")

if __name__ == "__main__":
    populate_dashboard_data()
