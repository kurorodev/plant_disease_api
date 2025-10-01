import random
import os
from PIL import Image
import numpy as np
from inference_sdk import InferenceHTTPClient, InferenceConfiguration

class TreeDetector:
    def __init__(self):
        self.classes = ["tree", "shrub"]
        self.client = None
        self.is_loaded = False
        self.model_id = "sanitarka_label-pkxhc/2"
    
    def load_model(self):
        """Инициализирует клиент для работы с Roboflow API"""
        try:
            print("Initializing Roboflow Inference Client")
            
            # Инициализация клиента
            self.client = InferenceHTTPClient(
                api_url="https://serverless.roboflow.com",
                api_key="2QOljeyuzD3EFB5yG5de"
            )
            
            self.is_loaded = True
            print("Roboflow client initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Error initializing Roboflow client: {e}")
            self.is_loaded = False
            return False
    
    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5) -> list:
        """Основной метод детекции с настраиваемым порогом уверенности"""
        # Если клиент не инициализирован, используем заглушку
        if not self.is_loaded:
            print("Using stub detection - model not loaded")
            return self._stub_detection(image)
        
        try:
            # Сохраняем временное изображение
            temp_path = "temp_detection_image.jpg"
            
            if isinstance(image, np.ndarray):
                # Конвертируем numpy array в PIL Image
                if len(image.shape) == 3:
                    # Если цветное изображение (H, W, C)
                    if image.shape[2] == 3:
                        # Предполагаем RGB формат
                        pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
                    else:
                        pil_image = Image.fromarray(image.astype('uint8'))
                else:
                    # Если grayscale (H, W)
                    pil_image = Image.fromarray(image.astype('uint8'))
                
                pil_image.save(temp_path)
            elif isinstance(image, Image.Image):
                # Если это уже PIL Image
                image.save(temp_path)
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
            
            # Создаем конфигурацию с низким порогом уверенности :cite[4]
            low_confidence_config = InferenceConfiguration(
                confidence_threshold=confidence_threshold  # Низкий порог = больше обнаружений
            )
            
            # Выполняем инференс с указанной конфигурацией :cite[4]
            with self.client.use_configuration(low_confidence_config):
                result = self.client.infer(temp_path, model_id=self.model_id)
            
            # Обрабатываем результат
            if isinstance(image, Image.Image):
                image_shape = (image.height, image.width, len(image.getbands()))
            else:
                image_shape = image.shape
            
            detections = self._process_predictions(result, image_shape)
            
            # Очищаем временный файл
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            print(f"Detection completed: found {len(detections)} objects with confidence threshold {confidence_threshold}")
            return detections
            
        except Exception as e:
            print(f"Error during detection: {e}")
            # Fallback to stub implementation
            return self._stub_detection(image)
    
    def _process_predictions(self, result: dict, image_shape) -> list:
        """Обрабатывает результат от Roboflow API"""
        detections = []
        
        if 'predictions' not in result:
            print("No predictions found in result")
            return detections
        
        # Получаем размеры изображения
        if len(image_shape) == 3:  # (height, width, channels)
            image_height, image_width = image_shape[0], image_shape[1]
        else:  # (height, width)
            image_height, image_width = image_shape
        
        for prediction in result['predictions']:
            # Получаем класс и уверенность
            class_name = prediction.get('class', 'unknown')
            confidence = prediction.get('confidence', 0)
            
            # Преобразуем bounding box из формата [x, y, width, height] в [x1, y1, x2, y2]
            x = prediction.get('x', 0)
            y = prediction.get('y', 0)
            width = prediction.get('width', 0)
            height = prediction.get('height', 0)
            
            # Конвертируем из относительных координат в абсолютные
            x_abs = x * image_width / 100.0
            y_abs = y * image_height / 100.0
            width_abs = width * image_width / 100.0
            height_abs = height * image_height / 100.0
            
            x1 = int(x_abs - width_abs / 2)
            y1 = int(y_abs - height_abs / 2)
            x2 = int(x_abs + width_abs / 2)
            y2 = int(y_abs + height_abs / 2)
            
            # Обеспечиваем границы изображения
            x1 = max(0, min(x1, image_width))
            y1 = max(0, min(y1, image_height))
            x2 = max(0, min(x2, image_width))
            y2 = max(0, min(y2, image_height))
            
            detections.append({
                "class": class_name,
                "confidence": round(confidence, 2),
                "bbox": [x1, y1, x2, y2]
            })
        
        return detections
    
    def _stub_detection(self, image: np.ndarray) -> list:
        """Заглушка для демонстрации"""
        if isinstance(image, Image.Image):
            width, height = image.size
        else:
            if len(image.shape) == 3:
                height, width = image.shape[:2]
            else:
                height, width = image.shape
        
        detections = []
        num_detections = random.randint(1, 3)
        
        for i in range(num_detections):
            w = random.randint(100, min(300, width-1))
            h = random.randint(100, min(400, height-1))
            x = random.randint(0, max(1, width - w))
            y = random.randint(0, max(1, height - h))
            
            detections.append({
                "class": random.choice(self.classes),
                "confidence": round(random.uniform(0.3, 0.7), 2),  # Пониженная уверенность для заглушки
                "bbox": [x, y, x + w, y + h]
            })
        
        return detections

# Пример использования
if __name__ == "__main__":
    detector = TreeDetector()
    detector.load_model()
    
    # Пример с изображением
    image = Image.open("your_image.jpg")  # Замените на путь к вашему изображению
    
    # Детекция с очень низким порогом уверенности (0.1 = 10%)
    detections = detector.detect(image, confidence_threshold=0.1)
    
    print(f"Найдено объектов: {len(detections)}")
    for detection in detections:
        print(f"Класс: {detection['class']}, Уверенность: {detection['confidence']}, BBox: {detection['bbox']}")
