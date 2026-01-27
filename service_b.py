from fastapi import FastAPI
from pydantic import BaseModel
import pika
import json
import os

app = FastAPI()

RABBIT_HOST = os.getenv('RABBIT_HOST', 'localhost')

class ImageRequest(BaseModel):
    url: str

@app.post("/analyze")
def analyze_request(request: ImageRequest):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='image_queue', durable=True) 
    channel.basic_publish(
        exchange='',
        routing_key='image_queue',
        body=json.dumps({'url': request.url}),
        properties=pika.BasicProperties(
            delivery_mode=2, 
        )
    )
    connection.close()
    return {"message": "Accepted", "url": request.url}