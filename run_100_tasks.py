import os

print("Generowanie 100 zadań...")
for i in range(100):
    os.system("uv run producer.py")