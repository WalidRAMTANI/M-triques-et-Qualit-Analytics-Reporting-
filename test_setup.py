"""
test_setup.py — Vérifie que la base de données et les tables se créent correctement.

Usage:
    python test_setup.py
"""

import sys
import sqlite3
from pathlib import Path

# ============================================
# ÉTAPE 1 : Vérifier que database.py s'importe
# ============================================

print("=" * 50)
print("TEST 1 : Import de database.py")
print("=" * 50)

try:
    from database import get_db_connection, init_database, DatabaseError, to_json, from_json, BaseRepository
    print("✅ Import OK")
except ImportError as e:
    print(f"❌ Import échoué : {e}")
    sys.exit(1)


# ============================================
# ÉTAPE 2 : Initialiser la base de données
# ============================================

print("\n" + "=" * 50)
print("TEST 2 : Création des tables (init_database)")
print("=" * 50)

try:
    init_database()
    print("✅ init_database() OK")
except Exception as e:
    print(f"❌ init_database() échoué : {e}")
    sys.exit(1)


# ============================================
# ÉTAPE 3 : Vérifier que toutes les tables existent
# ============================================

print("\n" + "=" * 50)
print("TEST 3 : Vérification des tables dans la DB")
print("=" * 50)

TABLES_ATTENDUES = [
    # Tables communes
    "aav",
    "ontology_reference",
    "apprenant",
    "statut_apprentissage",
    "tentative",
    # Tables Groupe 7
    "metrique_qualite_aav",
    "alerte_qualite",
    "rapport_periodique",
]

try:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables_existantes = {row["name"] for row in cursor.fetchall()}

    for table in TABLES_ATTENDUES:
        if table in tables_existantes:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table} MANQUANTE")

    if all(t in tables_existantes for t in TABLES_ATTENDUES):
        print("\n✅ Toutes les tables sont présentes !")
    else:
        print("\n❌ Des tables manquent !")

except Exception as e:
    print(f"❌ Erreur : {e}")
    sys.exit(1)


# ============================================
# ÉTAPE 4 : Tester to_json / from_json
# ============================================

print("\n" + "=" * 50)
print("TEST 4 : Utilitaires JSON")
print("=" * 50)

try:
    data = [1, 2, 3]
    json_str = to_json(data)
    result = from_json(json_str)
    assert result == data, f"Attendu {data}, obtenu {result}"
    print(f"  to_json([1,2,3])   → '{json_str}'  ✅")
    print(f"  from_json(...)     → {result}  ✅")

    assert to_json(None) is None, "to_json(None) devrait retourner None"
    assert from_json(None) is None, "from_json(None) devrait retourner None"
    print("  to_json(None) / from_json(None)  ✅")
except Exception as e:
    print(f"❌ Erreur JSON : {e}")
    sys.exit(1)


# ============================================
# ÉTAPE 5 : Tester BaseRepository
# ============================================

print("\n" + "=" * 50)
print("TEST 5 : BaseRepository (table aav)")
print("=" * 50)

try:
    repo = BaseRepository("aav", "id_aav")

    # Insertion d'un AAV de test
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO aav (id_aav, nom, discipline, type_evaluation)
            VALUES (9999, 'AAV Test', 'Mathématiques', 'Humaine')
        """)

    aav = repo.get_by_id(9999)
    assert aav is not None, "get_by_id(9999) devrait retourner un résultat"
    assert aav["nom"] == "AAV Test", f"Nom attendu 'AAV Test', obtenu '{aav['nom']}'"
    print(f"  get_by_id(9999) → nom='{aav['nom']}'  ✅")

    count = repo.count()
    print(f"  count() → {count} enregistrement(s)  ✅")

    deleted = repo.delete(9999)
    assert deleted, "delete(9999) devrait retourner True"
    assert repo.get_by_id(9999) is None, "L'AAV devrait être supprimé"
    print(f"  delete(9999) → OK  ✅")

except Exception as e:
    print(f"❌ Erreur BaseRepository : {e}")
    sys.exit(1)


# ============================================
# RÉSUMÉ FINAL
# ============================================

print("\n" + "=" * 50)
print("🎉 TOUS LES TESTS PASSENT — Setup OK !")
print("=" * 50)
print(f"\n📁 Base de données créée : {Path('platonAAV.db').resolve()}")
print("\nProchaine étape : lancer le serveur FastAPI avec :")
print("    uvicorn main:app --reload")
