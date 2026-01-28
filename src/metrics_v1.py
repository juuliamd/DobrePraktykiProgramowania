def calculate_iou(boxA, boxB):
    
    if not boxA or not boxB:
        return 0.0

    #współrzędne prostokąta przecięcia (Intersection)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # Obliczenie pola powierzchni przecięcia
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # Obliczenie pola powierzchni obu prostokątów
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    # Obliczenie IoU: Przecięcie / Suma
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)

    return iou

def calculate_final_grade(accuracy, total_time):
   
    
    # 1. Warunek krytyczny: Czas
    if total_time > 60.0:
        return 2.0
        
    # 2. Ocena na podstawie dokładności
    if accuracy < 60.0:
        return 2.0
    elif accuracy < 70.0:
        return 3.0
    elif accuracy < 80.0:
        return 3.5
    elif accuracy < 90.0:
        return 4.0
    elif accuracy < 95.0:
        return 4.5
    else:
        return 5.0