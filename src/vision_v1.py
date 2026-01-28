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
        img = cv2.resize(img, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 19, 9)
        binary = cv2.copyMakeBorder(binary, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
        return binary

    def heuristic_polish_fix(self, text):
        if not text: return text
        chars = list(text)
        length = len(chars)
        # znaki 1 i 2
        start_map = {
            '5': 'S', '8': 'B', '0': 'O', '1': 'I', '2': 'Z', 
            '4': 'A', '6': 'G', '7': 'Z'
        }
        #znaki końcowe
        end_map = {
            'S': '5', 'O': '0', 'I': '1', 'B': '8', 'Z': '7', 'J': '1', 'L': '1'
        }
        
        for i in range(min(2, length)):
            if chars[i] in start_map:
                chars[i] = start_map[chars[i]]
                
        for i in range(2, length):
            if chars[i] in end_map:
                chars[i] = end_map[chars[i]]
                
        return "".join(chars)

    def extract_plate_pattern(self, raw_text):
        text = raw_text.upper().replace(" ", "").replace("-", "").replace(".", "").replace(":", "")
        text = re.sub(r'[^A-Z0-9]', '', text)
        
        if len(text) <= 8:
            match = re.search(r'^.{0,2}PL', text)
            if match: text = text[match.end():]
            if len(text) > 8: text = text[:8]
            return self.heuristic_polish_fix(text)

        candidates = []
        
        for length in [7, 8]:
            for i in range(len(text) - length + 1):
                window = text[i : i+length]
                
                if window.startswith("PL"): continue
                
                fixed = self.heuristic_polish_fix(window)
                
                score = 0
                
                if fixed[0].isalpha(): score += 2
                if fixed[1].isalpha(): score += 2
                if fixed[-1].isdigit(): score += 1
                if "PL" in fixed: score -= 5
                
                candidates.append((score, fixed))
        
        if not candidates:
            return text[:8]
            
        candidates.sort(key=lambda x: (x[0], len(x[1])), reverse=True)
        
        return candidates[0][1]

    def process_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return None, None

        results = self.detector(img, verbose=False, conf=self.conf_thres)[0]
        
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
            x1 = max(0, x1 - 5)
            y1 = max(0, y1 - 5)
            x2 = min(w_img, x2 + 5)
            y2 = min(h_img, y2 + 5)

            crop = img[y1:y2, x1:x2]
            processed_crop = self.preprocess_plate(crop)
            
            try:
                ocr_res = self.reader.readtext(processed_crop, detail=0)
                raw_text = "".join(ocr_res)
                clean = self.extract_plate_pattern(raw_text)
                return clean, best_box
            except Exception:
                return "", best_box
        
        return None, None