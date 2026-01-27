import sqlite3
import uuid

DB_NAME = 'queue.db'

def produce_task():
    task_id = str(uuid.uuid4())
    initial_status = 'pending'
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO tasks (id, status) VALUES (?, ?)", (task_id, initial_status))
        conn.commit()
        print(f"Dodano zadanie: {task_id} ze statusem {initial_status}")
    except sqlite3.Error as e:
        print(f"Błąd bazy danych: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    produce_task()