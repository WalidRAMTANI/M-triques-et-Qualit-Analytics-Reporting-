import sqlite3
import os
from app.database import init_database, DB_PATH

def setup():
    print(f"Initializing database at {DB_PATH}...")
    init_database()
    
    sql_file = "app/donnees_test.sql"
    if os.path.exists(sql_file):
        print(f"Loading data from {sql_file}...")
        conn = sqlite3.connect(DB_PATH)
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
            # Split by semicolon to execute individually, or just use executescript
            # Be careful with semicolons inside strings, but executescript is usually fine for dumps
            try:
                conn.executescript(sql)
                conn.commit()
                print("Data loaded successfully.")
            except Exception as e:
                print(f"Error loading data: {e}")
        conn.close()
    else:
        print(f"Data file {sql_file} not found.")

if __name__ == "__main__":
    setup()
