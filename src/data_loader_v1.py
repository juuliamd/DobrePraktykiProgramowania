import xml.etree.ElementTree as ET
import os
import random

def load_dataset(xml_file, images_dir):
    
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"Nie znaleziono pliku XML: {xml_file}")

    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    dataset = []
    missing_files = 0

    print(f"   [Loader] Sprawdzanie ścieżek w folderze: {images_dir}")

    for image in root.findall('image'):
        file_name = image.get('name')
        
        full_path = os.path.join(images_dir, file_name)
        
        
        if not os.path.exists(full_path):
            alternative_path = os.path.join(images_dir, 'images', file_name)
            if os.path.exists(alternative_path):
                full_path = alternative_path
            else:
                missing_files += 1
                if missing_files <= 3:
                    print(f"   ⚠️ BRAK PLIKU: {file_name} (Szukano w: {full_path})")
                continue 
        

        #box tablicy - szukanie elementu <box> z atrybutem label="plate"
        box = image.find("box[@label='plate']")
        if box is None:
            continue 

        xtl = float(box.get('xtl'))
        ytl = float(box.get('ytl'))
        xbr = float(box.get('xbr'))
        ybr = float(box.get('ybr'))
        
        plate_text_node = box.find("attribute[@name='plate number']")
        plate_text = plate_text_node.text if plate_text_node is not None else ""

        data_point = {
            "path": full_path,
            "bbox_gt": [int(xtl), int(ytl), int(xbr), int(ybr)],
            "text_gt": plate_text if plate_text else ""
        }
        dataset.append(data_point)

    if missing_files > 0:
        print(f"   ⚠️ Pominięto {missing_files} plików, których nie znaleziono na dysku.")

    return dataset

def split_dataset(dataset, split_ratio=0.3):
    random.shuffle(dataset)
    split_idx = int(len(dataset) * split_ratio)
    # Jeśli dataset jest pusty (bo złe ścieżki), zwróć puste listy
    if not dataset:
        return [], []
        
    test_set = dataset[:split_idx]
    train_set = dataset[split_idx:]
    return train_set, test_set