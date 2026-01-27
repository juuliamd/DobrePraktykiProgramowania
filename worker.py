import pika
import json
import time
from detection import count_people_in_image

def callback(ch, method, properties, body):
  
    data = json.loads(body)
    url = data.get('url')

    print("\n" + "-"*60)
    print(f" [📥] ODEBRANO ZADANIE")
    print(f"      URL: {url}")
    print("      Rozpoczynam analizę obrazu...")

    start_time = time.time()
    
    people_count = count_people_in_image(url)
    
    duration = time.time() - start_time

 
    if people_count > 0:
        print(f" [✅] SUKCES: Wykryto {people_count} osób.")
    else:

        print(f" [0️⃣] WYNIK ZERO: Nie wykryto osób (lub wystąpił błąd pobierania).")

    print(f" [⏱️] Czas przetwarzania: {duration:.2f}s")
    print("-" * 60)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='image_queue')

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='image_queue', on_message_callback=callback)

    print(' [*] Worker jest gotowy i oczekuje na wiadomości. Naciśnij CTRL+C aby wyjść.')
    channel.start_consuming()

if __name__ == "__main__":
    try:
        start_worker()
    except KeyboardInterrupt:
        print("\n [!] Zatrzymano workera.")