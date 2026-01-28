import time
import pandas as pd
import sys
import os  # <--- Tego brakowało! Naprawia błąd NameError
from src.config_v1 import ANNOTATIONS_FILE, IMAGES_DIR, TEST_SPLIT
from src.data_loader_v1 import load_dataset, split_dataset
from src.vision_v12 import ALPRPipeline
from src.metrics_v1 import calculate_iou, calculate_final_grade


def normalize_plate(text):
    """
    Zamienia znaki, które OCR często myli, na jeden standard.
    Dzięki temu 0 i O są traktowane tak samo.
    """
    if not text: return ""
    text = text.upper().replace(" ", "").replace("-", "")
    # Mapa pomyłek: Zamieniamy wszystko na cyfry lub litery tam gdzie to możliwe
    # Tutaj strategia: zamieniamy ryzykowne znaki na unikalne tokeny lub po prostu ignorujemy różnicę O/0
    text = text.replace("0", "O") # Traktuj zero jak O
    text = text.replace("8", "B") # Traktuj osiem jak B
    text = text.replace("I", "1") # Traktuj I jak 1
    text = text.replace("Z", "2") # Czasem Z myli się z 2
    return text

def main():
    print("--- ROZPOCZYNAM ALPR SYSTEM (AMD/CPU OPTIMIZED) ---")
    
    # 1. Ładowanie danych
    print(f"1. Wczytywanie adnotacji...")
    try:
        full_data = load_dataset(ANNOTATIONS_FILE, IMAGES_DIR)
    except FileNotFoundError as e:
        print(f"\n❌ BŁĄD: {e}")
        sys.exit(1)
    
    if len(full_data) == 0:
        print("\n❌ BŁĄD KRYTYCZNY: Nie załadowano żadnych danych.")
        print("   Sprawdź czy folder 'photos' zawiera zdjęcia i czy nazwy pasują do XML.")
        sys.exit(1)

    _, test_set = split_dataset(full_data, split_ratio=TEST_SPLIT)
    
    
    
    # Zabezpieczenie na wypadek małej ilości danych
    if not test_set and full_data:
        test_set = full_data[:10]

    # Ograniczenie do 100 zdjęć zgodnie z wymogami
    target_count = min(100, len(test_set))
    test_subset = test_set[:target_count]
    print(f"   Gotowe do testu na: {target_count} zdjęciach.")

    # 2. Inicjalizacja Pipeline
    print("2. Ładowanie modeli (YOLOv8n + EasyOCR)...")
    # Tłumienie ostrzeżeń PyTorch dla czystości konsoli (opcjonalne)
    os.environ["YOLO_VERBOSE"] = "False"
    pipeline = ALPRPipeline('best.pt')  # Używamy wytrenowanego modelu

    # 3. Pętla przetwarzania
    results = []
    correct_ocr_count = 0
    
    print("3. Start przetwarzania...")
    start_time_global = time.time()

    for idx, data in enumerate(test_subset):
        try:
            pred_text, pred_box = pipeline.process_image(data['path'])
            
            iou = 0.0
            is_correct = False
            
            if pred_box:
                iou = calculate_iou(pred_box, data['bbox_gt'])
                
                # Porównanie tekstów (ignorujemy spacje i wielkość liter)
                if pred_text and data['text_gt']:
                    gt_clean = data['text_gt'].replace(" ", "").replace("-", "").upper()
                    pred_clean = pred_text.replace(" ", "").replace("-", "").upper()
                    
                    if pred_clean == gt_clean:
                        is_correct = True
                        correct_ocr_count += 1
            
            results.append({
                "File": os.path.basename(data['path']), # Tu był błąd
                "GT": data['text_gt'],
                "Pred": pred_text,
                "IoU": round(iou, 2),
                "OK": is_correct
            })
            
            # Log postępu co 10 zdjęć
            if (idx + 1) % 10 == 0:
                print(f"   Przetworzono {idx + 1}/{target_count}...")
                
        except Exception as e:
            print(f"   ⚠️ Błąd przy pliku {os.path.basename(data['path'])}: {e}")
            continue

    total_time = time.time() - start_time_global
    
    # 4. Raport
    if target_count > 0:
        accuracy_percent = (correct_ocr_count / target_count) * 100
        avg_iou = sum(r['IoU'] for r in results) / target_count
        
        print("\n" + "="*30)
        print("       WYNIKI KOŃCOWE")
        print("="*30)
        print(f"Czas ({target_count} fot):  {total_time:.2f} s")
        print(f"Średnie IoU:      {avg_iou:.2f}")
        print(f"Dokładność OCR:   {accuracy_percent:.1f}%")
        
        # Wyliczenie oceny
        final_grade = calculate_final_grade(accuracy_percent, total_time)
        print("-" * 30)
        print(f"PROPONOWANA OCENA: {final_grade}")
        print("-" * 30)
        
        # Zapis do CSV
        output_csv = "wyniki_testu.csv"
        pd.DataFrame(results).to_csv(output_csv, index=False)
        print(f"\nSzczegóły zapisano w pliku: {output_csv}")
    else:
        print("Brak wyników do wyświetlenia.")

if __name__ == "__main__":
    main()