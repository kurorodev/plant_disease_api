
import random
from PIL import Image
import numpy as np

class TreeDetector:
    def __init__(self):
        self.classes = ["tree", "shrub"]
    
    def load_model(self, model_path: str):
        print(f"Loading detection model from {model_path} (stub implementation)")
    
    def detect(self, image: np.ndarray) -> list:
        # Заглушка для демонстрации - возвращаем фиктивные bounding boxes
        if isinstance(image, Image.Image):
            width, height = image.size
        else:
            height, width = image.shape[:2]
        
        # Генерируем случайные bounding boxes для демонстрации
        detections = []
        num_detections = random.randint(1, 3)
        
        for i in range(num_detections):
            # Случайные координаты и размеры
            w = random.randint(100, min(300, width-1))
            h = random.randint(100, min(400, height-1))
            x = random.randint(0, max(1, width - w))
            y = random.randint(0, max(1, height - h))
            
            detections.append({
                "class": random.choice(self.classes),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "bbox": [x, y, x + w, y + h]
            })
        
        return detections
