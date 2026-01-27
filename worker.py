import pika
import json
import time
import requests
import os
import sys
from detection import count_people_in_image

SERVICE_A_URL = os.getenv('SERVICE_A_URL', 'http://service-a:8000/results')
RABBIT_HOST = os.getenv('RABBIT_HOST', 'rabbitmq')

def send_to_service_a(url, count):
    """
    Logika Retry: Próbuj wysłać, jeśli serwis leży, czekaj i próbuj ponownie.
    Zwraca True tylko jeśli uda się wysłać.
    """
    payload = {"url": url, "count": count}
    
    for i in range(5):
        try:
            r = requests.post(SERVICE_A_URL, json=payload, timeout=5)
            if r.status_code == 200:
                print(f" [Worker] Wysłano do A: {count}")
                return True
        except requests.exceptions.RequestException:
            print(f" [Worker] Serwis A nie odpowiada (próba {i+1}/5)...")
            time.sleep(2) 
            
    return False

def callback(ch, method, properties, body):
    data = json.loads(body)
    url = data.get('url')
    print(f" [Worker] Przetwarzam: {url}")

    count = count_people_in_image(url)

    success = send_to_service_a(url, count)

    if success:
        print(" [Worker] Sukces -> ACK")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print(" [Worker] Błąd krytyczny komunikacji -> NACK (do ponowienia)")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)

def start():
    time.sleep(10) 
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='image_queue', durable=True)
    
    channel.basic_qos(prefetch_count=1)
   
    channel.basic_consume(queue='image_queue', on_message_callback=callback, auto_ack=False)
    
    print(" [*] Worker wystartował. Czekam na pracę...")
    channel.start_consuming()

if __name__ == "__main__":
    start()