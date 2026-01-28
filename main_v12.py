import time
import pandas as pd
import sys
import os
import difflib
from src.config_v1 import ANNOTATIONS_FILE, IMAGES_DIR, TEST_SPLIT
from src.data_loader_v1 import load_dataset, split_dataset
from src.vision_v12 import ALPRPipeline
from src.metrics_v1 import calculate_iou, calculate_final_grade

def get_similarity_score(gt, pred):
    if not gt or not pred: return 0.0
    gt = gt.upper().replace(" ", "").replace("-", "")
    pred = pred.upper().replace(" ", "").replace("-", "")
    return difflib.SequenceMatcher(None, gt, pred).ratio()

def main():
    print("--- ROZPOCZYNAM ALPR SYSTEM (I-REMOVE + FIX) ---")
    
    if not os.path.exists('best.pt'):
        print("❌ BŁĄD: Brak 'best.pt'!")
        sys.exit(1)

    full_data = load_dataset(ANNOTATIONS_FILE, IMAGES_DIR)
    _, test_set = split_dataset(full_data, split_ratio=TEST_SPLIT)
    
    target_count = min(100, len(test_set))
    if target_count == 0: target_count = len(full_data)
    test_subset = test_set[:target_count]
    
    os.environ["YOLO_VERBOSE"] = "False"
    pipeline = ALPRPipeline('best.pt')

    results = []
    correct_ocr_count = 0
    start_time = time.time()
    
    print("\n" + "-"*95)
    print(f"{'NR':<3} {'PLIK':<10} {'GT (WZORZEC)':<15} {'OCR (FINAL)':<20}{'WYNIK'}")
    print("-" * 95)

    for idx, data in enumerate(test_subset):
        try:
            pred_text, pred_box = pipeline.process_image(data['path'])
            is_correct = False
            similarity = 0.0
            
            if pred_box:
                iou = calculate_iou(pred_box, data['bbox_gt'])
                if pred_text and data['text_gt']:
                    similarity = get_similarity_score(data['text_gt'], pred_text)
                    
                    # PRÓG 85%
                    if similarity >= 0.85:
                        is_correct = True
                        correct_ocr_count += 1
            
            status_icon = "✅" if is_correct else "❌"
            fname = os.path.basename(data['path'])
            raw_disp = pred_text if pred_text else "[-]"
            sim_disp = f"{int(similarity*100)}%"
            
            print(f"{idx+1:<3} {fname:<10} {data['text_gt']:<15} {raw_disp:<20}  {status_icon}")

            results.append({
                "File": fname,
                "GT": data['text_gt'],
                "Pred": pred_text,
                #"Similarity": similarity,
                "OK": is_correct
            })
                
        except Exception:
            continue

    total_time = time.time() - start_time
    accuracy_percent = (correct_ocr_count / target_count) * 100
    final_grade = calculate_final_grade(accuracy_percent, total_time)

    print("-" * 95)
    print(f"Czas całkowity: {total_time:.2f} s")
    print(f"Dokładność:     {accuracy_percent:.1f}%")
    print("-" * 20)
    print(f"OCENA KOŃCOWA:  {final_grade}")
    print("=" * 20)
    
    pd.DataFrame(results).to_csv("wyniki_final.csv", index=False)

if __name__ == "__main__":
    main()