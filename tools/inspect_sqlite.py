import sqlite3
import sys

def inspect_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables found in database:")
    for table in tables:
        print(f" - {table[0]}")
        
    conn.close()

if __name__ == "__main__":
    inspect_db(sys.argv[1])
