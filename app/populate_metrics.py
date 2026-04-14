import sqlite3
import random
from datetime import datetime, timedelta

def populate_metrics():
    conn = sqlite3.connect('platonAAV.db')
    cur = conn.cursor()

    # Get some AAV IDs
    cur.execute("SELECT id_aav FROM aav LIMIT 20")
    aav_ids = [row[0] for row in cur.fetchall()]

    if not aav_ids:
        print("No AAVs found in database.")
        conn.close()
        return

    print(f"Populating metrics for {len(aav_ids)} AAVs...")

    for id_aav in aav_ids:
        # Create a few metrics per AAV for history
        for i in range(3):
            date_calcul = datetime.now() - timedelta(days=i*7)
            cur.execute("""
                INSERT INTO metrique_qualite_aav (
                    id_aav, score_covering_ressources, taux_succes_moyen, 
                    est_utilisable, nb_tentatives_total, nb_apprenants_distincts, 
                    ecart_type_scores, date_calcul
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_aav,
                round(random.uniform(0.5, 1.0), 2),
                round(random.uniform(0.3, 0.9), 2),
                random.choice([0, 1]),
                random.randint(10, 100),
                random.randint(5, 30),
                round(random.uniform(0.05, 0.2), 3),
                date_calcul.isoformat()
            ))

    conn.commit()
    conn.close()
    print("Populate complete.")

if __name__ == "__main__":
    populate_metrics()
