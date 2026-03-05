
import sqlite3
import os
from pathlib import Path

# Path to the database and SQL file
DB_PATH = Path("platonAAV.db")
SQL_FILE = Path("donnees_test.sql")

def reset_and_import():
    if not DB_PATH.exists():
        print(f"❌ Database {DB_PATH} not found. Please run init_database first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("🔨 Creating missing tables found in SQL file...")
    # Create missing tables referenced in the SQL dump
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS activite_pedagogique (
        id_activite INTEGER PRIMARY KEY,
        nom TEXT,
        description TEXT,
        type_activite TEXT,
        ids_exercices_inclus TEXT,
        discipline TEXT,
        niveau_difficulte TEXT,
        duree_estimee_minutes INTEGER,
        created_by INTEGER,
        created_at TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS session_apprenant (
        id_session INTEGER PRIMARY KEY,
        id_activite INTEGER,
        id_apprenant INTEGER,
        date_debut TIMESTAMP,
        date_fin TIMESTAMP,
        statut TEXT,
        progression_pourcentage REAL
    );
    CREATE TABLE IF NOT EXISTS prompt_fabrication_aav (
        id_prompt INTEGER PRIMARY KEY,
        cible_aav_id INTEGER,
        type_exercice_genere TEXT,
        prompt_texte TEXT,
        version_prompt INTEGER,
        created_by INTEGER,
        date_creation TIMESTAMP,
        is_active BOOLEAN,
        metadata TEXT
    );
    CREATE TABLE IF NOT EXISTS exercice_instance (
        id_exercice INTEGER PRIMARY KEY,
        id_prompt_source INTEGER,
        titre TEXT,
        id_aav_cible INTEGER,
        type_evaluation TEXT,
        contenu TEXT,
        difficulte TEXT,
        date_generation TIMESTAMP,
        nb_utilisations INTEGER,
        taux_succes_moyen REAL
    );
    CREATE TABLE IF NOT EXISTS diagnostic_remediation (
        id_diagnostic INTEGER PRIMARY KEY,
        id_apprenant INTEGER,
        id_aav_source INTEGER,
        aav_racines_defaillants TEXT,
        score_obtenu REAL,
        date_diagnostic TIMESTAMP,
        profondeur_analyse INTEGER,
        recommandations TEXT
    );
    """)
    conn.commit()

    print("🧹 Cleaning existing data...")
    # List of all tables to clear (including the ones we just added)
    tables = [
        "metrique_qualite_aav", "alerte_qualite", "rapport_periodique",
        "tentative", "statut_apprentissage", "apprenant", 
        "ontology_reference", "aav",
        "activite_pedagogique", "session_apprenant", "prompt_fabrication_aav",
        "exercice_instance", "diagnostic_remediation"
    ]
    
    cur.execute("PRAGMA foreign_keys = OFF;")
    for table in tables:
        try:
            cur.execute(f"DELETE FROM {table};")
        except sqlite3.OperationalError:
            print(f"⚠️ Table {table} does not exist, skipping.")
    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    print("✅ Tables cleared.")

    print(f"📥 Importing {SQL_FILE}...")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    try:
        cur.executescript(sql_script)
        conn.commit()
        print("✅ Data imported successfully!")
    except Exception as e:
        print(f"❌ Error during import: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_and_import()
