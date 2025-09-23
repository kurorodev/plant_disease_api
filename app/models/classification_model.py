
import random
from PIL import Image

class TreeClassifier:
    def __init__(self):
        self.species_classes = [
            "дуб", "береза", "сосна", "ель", "клен", 
            "липа", "тополь", "ива", "ясень", "рябина"
        ]
    
    def load_model(self, model_path: str):
        print(f"Loading classification model from {model_path} (stub implementation)")
    
    def predict_species(self, image: Image.Image) -> str:
        # Заглушка для демонстрации
        # В реальной реализации здесь будет модель классификации
        image_hash = hash(image.tobytes()) if image else 0
        return self.species_classes[image_hash % len(self.species_classes)]
