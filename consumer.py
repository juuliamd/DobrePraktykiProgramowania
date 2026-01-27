import sqlite3
import time

DB_NAME = 'queue.db'
WORK_TIME = 30  # Czas trwania rozmowy 
POLL_INTERVAL = 5 # Co ile sprawdzać bazę 

def process_tasks():
    print("Konsument SQL uruchomiony. Oczekiwanie na zadania...")
    
    while True: # Pętla nieskończona [cite: 62]
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        task_id = None
        
        try:
            # 1. Szukamy zadania 'pending'
            cursor.execute("SELECT id FROM tasks WHERE status='pending' LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                candidate_id = row[0]
                cursor.execute("""
                    UPDATE tasks 
                    SET status='in_progress' 
                    WHERE id=? AND status='pending'
                """, (candidate_id,))
                
                conn.commit()
                
                if cursor.rowcount == 1:
                    task_id = candidate_id
            
            conn.close()
            
            if task_id:
                print(f"Pobrano zadanie {task_id}. Status: in_progress. Rozmowa w toku...")
                
   
                time.sleep(WORK_TIME)
                
    
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
                conn.commit()
                conn.close()
                
                print(f"Zadanie {task_id} zakończone. Status: done.")
            else:
                print("Brak wolnych zadań 'pending'. Czekam...")
                time.sleep(POLL_INTERVAL)
                
        except sqlite3.Error as e:
            print(f"Błąd SQL: {e}")
            if conn: conn.close()
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    process_tasks()