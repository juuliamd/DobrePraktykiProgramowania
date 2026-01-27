import requests
import threading
import time

API_URL = "http://127.0.0.1:8000/analyze_img"

TEST_DATA = [
    ("Tłum na ulicy (Pexels)", "https://images.pexels.com/photos/109919/pexels-photo-109919.jpeg"),
    ("Przejście dla pieszych (Londyn)", "https://upload.wikimedia.org/wikipedia/commons/e/e6/Westminster_Bridge_London_2_June_2013.jpg"),
    ("Pojedyncza osoba (Portret)", "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg"),
    ("Mała grupa przyjaciół", "https://images.pexels.com/photos/853168/pexels-photo-853168.jpeg"),
    ("Pusty las (BRAK LUDZI - test negatywny)", "https://images.pexels.com/photos/15286/pexels-photo.jpg"),
    ("Tłum na koncercie (Trudne)", "https://images.pexels.com/photos/1763075/pexels-photo-1763075.jpeg"),
    ("Błędny link (Test błędu 404)", "https://google.com/nie-ma-takiego-zdjecia.jpg"),
]

def send_request(name, url):
    print(f"🚀 Wysyłanie: {name}...")
    try:
        start = time.time()
        response = requests.post(API_URL, json={"url": url}, timeout=5)
        duration = time.time() - start
        
        if response.status_code == 200:
            print(f"✅ API przyjęło: {name} (czas odp: {duration:.2f}s)")
        else:
            print(f"⚠️ API zwróciło błąd dla {name}: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Błąd połączenia dla {name}: {e}")

print(f"--- ROZPOCZYNAM TEST BATCHOWY ({len(TEST_DATA)} zdjęć) ---")

threads = []


for name, url in TEST_DATA:
    t = threading.Thread(target=send_request, args=(name, url))
    threads.append(t)
    t.start()
    time.sleep(0.1) 


for t in threads:
    t.join()

print("\n🏁 Wszystkie zadania zostały wysłane do kolejki RabbitMQ.")
print("👉 TERAZ SPÓJRZ NA TERMINAL WORKERA, ABY ZOBACZYĆ WYNIKI ANALIZY!")