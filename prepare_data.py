import os
import shutil
import yaml
import xml.etree.ElementTree as ET
import random
from src.config_v1 import ANNOTATIONS_FILE, IMAGES_DIR

def convert_xml_to_yolo():
    print("--- 1. KONWERSJA DANYCH DO FORMATU YOLO ---")
    
    #tworzenie struktury folderów dla YOLO
    base_dir = os.getcwd()
    datasets_dir = os.path.join(base_dir, 'datasets')
    
    dirs = {
        'images_train': os.path.join(datasets_dir, 'images', 'train'),
        'images_val': os.path.join(datasets_dir, 'images', 'val'),
        'labels_train': os.path.join(datasets_dir, 'labels', 'train'),
        'labels_val': os.path.join(datasets_dir, 'labels', 'val')
    }
    
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
        
    #parsing XML
    tree = ET.parse(ANNOTATIONS_FILE)
    root = tree.getroot()
    
    #Lista wszystkich par (obraz, box)
    data_items = []
    
    for image in root.findall('image'):
        file_name = image.get('name')
        width = float(image.get('width'))
        height = float(image.get('height'))
        
        box = image.find("box[@label='plate']")
        if box is None: continue
        
        #Pobieranie koordów
        xtl = float(box.get('xtl'))
        ytl = float(box.get('ytl'))
        xbr = float(box.get('xbr'))
        ybr = float(box.get('ybr'))
        
        #konwersja na YOLO: (class, x_center, y_center, w, h) - wartości 0-1
        dw = 1.0 / width
        dh = 1.0 / height
        
        x_center = (xtl + xbr) / 2.0
        y_center = (ytl + ybr) / 2.0
        w = xbr - xtl
        h = ybr - ytl
        
        x_center *= dw
        width_norm = w * dw
        y_center *= dh
        height_norm = h * dh
        
        #Class ID 0 dla tablicy
        yolo_line = f"0 {x_center:.6f} {y_center:.6f} {width_norm:.6f} {height_norm:.6f}"
        
        data_items.append({
            'file_name': file_name,
            'yolo_line': yolo_line
        })

    #Podział na train/val (80% / 20%)
    random.shuffle(data_items)
    split_idx = int(len(data_items) * 0.8)
    train_set = data_items[:split_idx]
    val_set = data_items[split_idx:]
    
    print(f"   Znaleziono {len(data_items)} próbek.")
    print(f"   Trening: {len(train_set)}, Walidacja: {len(val_set)}")

    #Kopiowanie plików i tworzenie etykiet
    def process_set(dataset, img_dest, lbl_dest):
        for item in dataset:
            src_path = os.path.join(IMAGES_DIR, item['file_name'])
            
            if not os.path.exists(src_path):
                 base, _ = os.path.splitext(item['file_name'])
                 for ext in ['.jpg', '.JPG', '.jpeg', '.png']:
                     if os.path.exists(os.path.join(IMAGES_DIR, base + ext)):
                         src_path = os.path.join(IMAGES_DIR, base + ext)
                         item['file_name'] = base + ext 
                         break
            
            if os.path.exists(src_path):
                shutil.copy(src_path, os.path.join(img_dest, item['file_name']))
                
                
                txt_name = os.path.splitext(item['file_name'])[0] + ".txt"
                with open(os.path.join(lbl_dest, txt_name), "w") as f:
                    f.write(item['yolo_line'])

    process_set(train_set, dirs['images_train'], dirs['labels_train'])
    process_set(val_set, dirs['images_val'], dirs['labels_val'])

    #Tworzenie pliku data.yaml dla YOLO
    yaml_content = {
        'path': datasets_dir,
        'train': 'images/train',
        'val': 'images/val',
        'names': {0: 'license_plate'}
    }
    
    with open('data.yaml', 'w') as f:
        yaml.dump(yaml_content, f)
        
    print("✅ Dane przygotowane. Utworzono 'data.yaml' oraz folder 'datasets'.")

if __name__ == "__main__":
    convert_xml_to_yolo()