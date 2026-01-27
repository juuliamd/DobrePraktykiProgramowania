import sqlite3

DB_NAME = 'queue.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Baza danych '{DB_NAME}' została zainicjalizowana.")

if __name__ == "__main__":
    init_db()