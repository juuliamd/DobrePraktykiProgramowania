import os
import time

if os.path.exists("queue.db"):
    os.remove("queue.db")
    print("Usunięto starą bazę danych.")


os.system("python setup_db.py")

print("Rozpoczynam generowanie 100 zadań...")

for i in range(100):
    os.system("python producer.py")

print("Zakończono generowanie zadań!")