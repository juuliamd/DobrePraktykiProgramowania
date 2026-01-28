import time
import pandas as pd
import sys
import os
import difflib
from src.config_v1 import ANNOTATIONS_FILE, IMAGES_DIR, TEST_SPLIT
from src.data_loader_v1 import load_dataset, split_dataset
from src.vision_v1 import ALPRPipeline
from src.metrics_v1 import calculate_iou, calculate_final_grade

def get_similarity_score(gt, pred):
    if not gt or not pred: return 0.0
    
    gt = gt.upper().replace(" ", "").replace("-", "")
    pred = pred.upper().replace(" ", "").replace("-", "")
    
    def standardize(s):
        mapping = {
            "0": "O", "O": "O",
            "8": "B", "B": "8",
            "I": "1", "L": "1", "1": "1", "J": "1",
            "Z": "2", "2": "2",
            "S": "5", "5": "S",
        }
        return "".join([mapping.get(c, c) for c in s])

    gt_std = standardize(gt)
    pred_std = standardize(pred)
    
    if gt_std == pred_std: return 1.0
    
    return difflib.SequenceMatcher(None, gt_std, pred_std).ratio()

def main():
    print("--- ROZPOCZYNAM ALPR SYSTEM ---")
    
    if not os.path.exists('best.pt'):
        print("❌ BŁĄD: Brak 'best.pt'!")
        sys.exit(1)

    try:
        full_data = load_dataset(ANNOTATIONS_FILE, IMAGES_DIR)
    except FileNotFoundError:
        print(f"❌ BŁĄD: Nie znaleziono pliku {ANNOTATIONS_FILE}")
        sys.exit(1)

    _, test_set = split_dataset(full_data, split_ratio=0.8)
    
    target_count = min(100, len(test_set))
    if target_count == 0: target_count = len(full_data)
    
    test_subset = test_set[:target_count]
    
    print(f"   Liczba zdjęć do analizy: {len(test_subset)}")

    os.environ["YOLO_VERBOSE"] = "False"
    pipeline = ALPRPipeline('best.pt')

    results = []
    correct_ocr_count = 0
    start_time = time.time()
    
    print("\n" + "-"*100)
    print(f"{'NR':<3} {'PLIK':<12} {'GT (WZORZEC)':<15} {'OCR (WYNIK)':<20} {'STAN'}")
    print("-" * 100)

    for idx, data in enumerate(test_subset):
        try:
            pred_text, pred_box = pipeline.process_image(data['path'])
            
            is_correct = False
            similarity = 0.0
            
            if pred_box:
                if pred_text and data['text_gt']:
                    similarity = get_similarity_score(data['text_gt'], pred_text)
                    
                    if similarity >= 0.85:
                        is_correct = True
                        correct_ocr_count += 1
            
            status_icon = "✅" if is_correct else "❌"
            fname = os.path.basename(data['path'])
            raw_disp = pred_text if pred_text else "[-]"
            sim_disp = f"{int(similarity*100)}%"
            
            if not is_correct and similarity > 0.75:
                sim_disp += " (!)"
            
            print(f"{idx+1:<3} {fname:<12} {data['text_gt']:<15} {raw_disp:<20}{status_icon}")

            results.append({
                "File": fname,
                "GT": data['text_gt'],
                "Pred": pred_text,
                "Similarity": similarity,
                "OK": is_correct
            })
                
        except Exception as e:
            continue

    total_time = time.time() - start_time
    accuracy_percent = (correct_ocr_count / target_count) * 100
    
    final_grade = calculate_final_grade(accuracy_percent, total_time)

    print("-" * 100)
    print(f"Czas całkowity: {total_time:.2f} s")
    print(f"Średni czas:    {total_time/target_count:.3f} s/zdj")
    print(f"Dokładność:     {accuracy_percent:.1f}%")
    print("-" * 20)
    print(f"OCENA KOŃCOWA:  {final_grade}")
    print("=" * 20)
    
    pd.DataFrame(results).to_csv("wyniki_final.csv", index=False)
    print("Zapisano wyniki w pliku CSV.")

if __name__ == "__main__":
    main()