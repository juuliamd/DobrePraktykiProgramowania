import csv
import time
import os
import shutil
from tempfile import NamedTemporaryFile

QUEUE_FILE = 'tasks.csv'
WORK_TIME = 30  #czas wykonywania pracy w sek
POLL_INTERVAL = 5  #czas oczekiwania na nowe zadanie


def update_task_status(target_task_id, new_status):
    temp_file = NamedTemporaryFile(mode='w', delete=False, newline='')
    updated = False

    with open(QUEUE_FILE, 'r', newline='') as csvfile, temp_file:
        reader = csv.reader(csvfile)
        writer = csv.writer(temp_file)

        for row in reader:
            if row and row[0] == target_task_id:
                writer.writerow([row[0], new_status])
                updated = True
            else:
                writer.writerow(row)

    shutil.move(temp_file.name, QUEUE_FILE)
    return updated


def process_tasks():
    print("Konsument uruchomiony. Oczekiwanie na zadania...")

    while True:
        task_to_process = None

        #szukanie zadania ze statusem 'pending'
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[1] == 'pending':
                        task_to_process = row[0]
                        break

        if task_to_process:
            #zmiana statusu na 'in progress'
            update_task_status(task_to_process, 'in_progress')
            print(f"Pobrano zadanie {task_to_process}. Status: in_progress. Praca w toku...")

            time.sleep(WORK_TIME)

            #zmiana statsuu na 'done'
            update_task_status(task_to_process, 'done')
            print(f"Zadanie {task_to_process} zakończone. Status: done.")

        else:
            print("Brak zadań 'pending'. Czekam 5s...")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    process_tasks()