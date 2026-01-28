from ultralytics import YOLO
import os

def train():
    print("--- ROZPOCZYNAM TRENING MODELU ---")
    
    # 1. Ładowanie modelu bazowego (wagi COCO)
    model = YOLO('yolov8n.pt') 
    
    # 2. Trening
    # epochs=20 -> wystarczy dla prostego obiektu jak prostokątna tablica
    # imgsz=640 -> standardowa rozdzielczość
    # device='cpu' -> jeśli GPU AMD nie działa z PyTorch CUDA (bezpieczniej)
    # Jeśli masz poprawnie skonfigurowane ROCm, usuń argument device='cpu'
    
    results = model.train(
        data='data.yaml',
        epochs=30,           # 30 epok powinno dać IoU > 0.8
        imgsz=640,
        batch=8,             # Mniejszy batch dla bezpieczeństwa RAM
        name='yolo_plate_detect',
        exist_ok=True
        # device='cpu'       <-- Odkomentuj jeśli będą błędy z GPU
    )
    
    print("\n✅ Trening zakończony!")
    print(f"Najlepszy model zapisano w: {results.save_dir}/weights/best.pt")
    
    # Eksport do formatu ONNX (dla szybkości na CPU w fazie testów)
    model.export(format='onnx')

if __name__ == "__main__":
    train()