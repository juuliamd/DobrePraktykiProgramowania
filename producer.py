import csv
import uuid


QUEUE_FILE = 'tasks.csv'


def produce_task():
    task_id = str(uuid.uuid4())
    initial_status = 'pending'  # [cite: 67]

    with open(QUEUE_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([task_id, initial_status])

    print(f"Dodano zadanie: {task_id}")


if __name__ == "__main__":
    produce_task()