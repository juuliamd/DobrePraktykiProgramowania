import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import re

class ALPRPipeline:
    def __init__(self, model_path, conf_thres=0.25):
        self.detector = YOLO(model_path) 
        self.conf_thres = conf_thres
        self.reader = easyocr.Reader(['pl'], gpu=False, verbose=False) 

    def preprocess_plate(self, img):
        #Skala 1.6 zamiast 2.0 - szybszy ocr
        #INTER_LINEAR zamiast INTER_CUBIC - szybsze
       
        img = cv2.resize(img, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_LINEAR)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #gaussian bo jest szybszy
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive Threshold (przy cieniach)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 19, 9)
        
        # Padding
        binary = cv2.copyMakeBorder(binary, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
        return binary

    def heuristic_polish_fix(self, text):
        """
        Naprawia błędy OCR bazując na pozycji znaku.
        """
        if not text: return text
        chars = list(text)
        length = len(chars)
        
        #Indeks 0, 1 -> Litery
        first_map = {
            '5': 'S', '8': 'B', '0': 'O', '1': 'I', '2': 'Z', 
            '4': 'A', '6': 'G', '7': 'Z', 'X': 'K'
        }
        for i in range(min(2, length)):
            if chars[i] in first_map:
                chars[i] = first_map[chars[i]]

        #Indeks 2+ -> Cyfry
        rest_map = {
            'S': '5', 'O': '0', 'I': '1', 'B': '8', 'G': '6', 
            'Z': '7', 'L': '1', 'J': '1'
        }
        for i in range(2, length):
            if chars[i] in rest_map:
                chars[i] = rest_map[chars[i]]
                
        return "".join(chars)

    def clean_text_final(self, text):
        text = text.upper().replace(" ", "").replace("-", "").replace(".", "")
        text = re.sub(r'[^A-Z0-9]', '', text) 
        
        #usuwanie I na początku
        if text.startswith("I"):
            text = text[1:]
            
        # PL Anchor Logic
        match = re.search(r'^.{0,3}PL', text)
        if match:
            text = text[match.end():]
            
        #max 8 znaków
        if len(text) > 8:
            text = text[:8]
            
        #BF
        text = self.heuristic_polish_fix(text)
            
        return text

    def process_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return None, None

        results = self.detector.predict(img, verbose=False, conf=self.conf_thres)[0]
        
        best_box = None
        max_conf = 0

        for box in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = box
            if conf > max_conf:
                max_conf = conf
                best_box = [int(x1), int(y1), int(x2), int(y2)]

        if best_box:
            x1, y1, x2, y2 = best_box
            h_img, w_img, _ = img.shape
            box_h = y2 - y1
            box_w = x2 - x1
            
            #cięcie 
            new_x1 = int(x1 + box_w * 0.12)
            new_y1 = int(y1 + box_h * 0.05)
            new_x2 = int(x2 - box_w * 0.02)
            new_y2 = int(y2 - box_h * 0.20)
            
            x1 = max(0, new_x1); y1 = max(0, new_y1)
            x2 = min(w_img, new_x2); y2 = min(h_img, new_y2)

            if x1 >= x2 or y1 >= y2: return "", best_box

            crop = img[y1:y2, x1:x2]
            processed_crop = self.preprocess_plate(crop)
            
            try:
                ocr_res = self.reader.readtext(processed_crop, detail=0)
                raw_text = "".join(ocr_res)
                clean = self.clean_text_final(raw_text)
                return clean, best_box
            except Exception:
                return "", best_box
        
        return None, None