import os

#Ścieżki
BASE_DIR = os.getcwd()
IMAGES_DIR = os.path.join(BASE_DIR, 'photos')      # Folder ze zdjęciami
ANNOTATIONS_FILE = os.path.join(BASE_DIR, 'annotations.xml')

#Parametry modelu
MODEL_NAME = 'best.pt'
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.25

#Parametry oceny
TEST_SPLIT = 0.6  # 60% danych do testów