import requests
import threading
import time

API_URL = "http://127.0.0.1:8000/analyze_img"
IMG_URL = "https://images.pexels.com/photos/109919/pexels-photo-109919.jpeg"

def send_request(i):
    try:
        response = requests.post(API_URL, json={"url": IMG_URL}, timeout=5)
        print(f"[{i}] Odpowiedź API: {response.status_code} (Czas: {response.elapsed.total_seconds():.2f}s)")
    except Exception as e:
        print(f"[{i}] Błąd: {e}")

REQUEST_COUNT = 20

print(f"Wysyłanie {REQUEST_COUNT} zapytań na raz...")
threads = []
start_time = time.time()

for i in range(REQUEST_COUNT):
    t = threading.Thread(target=send_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

total_time = time.time() - start_time
print(f"Wysłano wszystkie zapytania w czasie: {total_time:.2f}s")