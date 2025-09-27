from fastapi import APIRouter, HTTPException
from app.schemas import TreeAnalysisRequest, AnalysisResponse, TreeAnalysisResult, TreeCharacteristic
from app.utils import base64_to_image, image_to_base64, draw_detections
from app.models.detection_model import TreeDetector
from app.models.classification_model import TreeClassifier
from app.models.health_analysis import HealthAnalyzer
from PIL import Image, ImageDraw
import numpy as np
import time
import base64
import io

router = APIRouter()

# Инициализация моделей
detector = TreeDetector()
classifier = TreeClassifier()
health_analyzer = HealthAnalyzer()

# Инициализируем детектор при запуске
@router.on_event("startup")
async def startup_event():
    """Инициализация моделей при запуске приложения"""
    print("Initializing models...")
    success = detector.load_model()
    if success:
        print("TreeDetector initialized successfully")
    else:
        print("TreeDetector initialization failed - using stub mode")
    print("All models initialized")

@router.get("/")
async def analysis_root():
    return {"message": "Analysis router is working"}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(request: TreeAnalysisRequest):
    start_time = time.time()
    
    try:
        # Конвертация base64 в изображение
        pil_image = base64_to_image(request.image_data)
        
        # Конвертация PIL Image в numpy array (теперь не обязательна, но оставим для совместимости)
        image_array = np.array(pil_image)
        
        # Детекция деревьев и кустарников
        detections = detector.detect(image_array)
        
        results = []
        for i, detection in enumerate(detections):
            # Извлечение региона для анализа
            x1, y1, x2, y2 = map(int, detection["bbox"])
            # Обеспечиваем, чтобы координаты не выходили за границы
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(pil_image.width, x2), min(pil_image.height, y2)
            
            if x2 > x1 and y2 > y1:
                # Используем PIL для извлечения ROI
                roi = pil_image.crop((x1, y1, x2, y2))
                
                # Классификация породы
                species = classifier.predict_species(roi)
                
                # Анализ состояния
                health_data = health_analyzer.analyze_health(roi, detection["class"])
                
                # Формирование результата
                characteristics = TreeCharacteristic(
                    species=species,
                    trunk_rot=health_data.get("trunk_rot"),
                    hollow=health_data.get("hollow"),
                    trunk_crack=health_data.get("trunk_crack"),
                    trunk_damage=health_data.get("trunk_damage"),
                    crown_damage=health_data.get("crown_damage"),
                    fruiting_bodies=health_data.get("fruiting_bodies"),
                    dried_branches_percent=health_data.get("dried_branches_percent"),
                    other_characteristics=health_data.get("other_characteristics")
                )
                
                results.append(TreeAnalysisResult(
                    tree_id=i+1,
                    characteristics=characteristics,
                    detection_confidence=detection["confidence"],
                    object_type=detection["class"]
                ))
        
        # Рисование bounding boxes на изображении (используем PIL вместо OpenCV)
        processed_image = draw_detections_pil(pil_image, detections)
        processed_image_base64 = image_to_base64(processed_image)
        
        processing_time = round(time.time() - start_time, 2)
        
        return AnalysisResponse(
            results=results,
            processed_image=processed_image_base64,
            processing_time=processing_time,
            objects_detected=len(detections)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def draw_detections_pil(pil_image: Image.Image, detections: list) -> Image.Image:
    """Рисует bounding boxes на изображении с использованием PIL"""
    # Создаем копию изображения чтобы не изменять оригинал
    image_copy = pil_image.copy()
    draw = ImageDraw.Draw(image_copy)
    
    for detection in detections:
        x1, y1, x2, y2 = detection["bbox"]
        class_name = detection["class"]
        confidence = detection["confidence"]
        
        # Выбираем цвет в зависимости от класса
        color = "green" if class_name == "tree" else "blue"
        
        # Рисуем bounding box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        
        # Рисуем метку
        label = f"{class_name} {confidence:.2f}"
        # Рисуем фон для текста
        text_bbox = draw.textbbox((x1, y1 - 20), label)
        draw.rectangle(text_bbox, fill=color)
        draw.text((x1, y1 - 20), label, fill="white")
    
    return image_copy

@router.get("/test")
async def test_endpoint():
    """Тестовый endpoint для проверки работы сервера"""
    return {
        "message": "Analysis endpoint is working", 
        "status": "OK",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze (POST)",
            "test": "/api/v1/test"
        }
    }

@router.get("/demo")
async def demo_analysis():
    """Демо-эндпоинт для тестирования без отправки изображения"""
    # Создаем тестовое изображение
    test_image = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(test_image)
    
    # Рисуем несколько "деревьев"
    draw.rectangle([100, 100, 200, 400], fill='brown', outline='black', width=2)
    draw.ellipse([50, 50, 250, 200], fill='green', outline='darkgreen', width=2)
    
    draw.rectangle([400, 150, 450, 350], fill='brown', outline='black', width=2)
    draw.ellipse([350, 100, 500, 250], fill='green', outline='darkgreen', width=2)
    
    # Конвертируем в base64
    buffered = io.BytesIO()
    test_image.save(buffered, format="JPEG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Создаем запрос
    request = TreeAnalysisRequest(image_data=image_base64)
    
    # Вызываем анализ
    return await analyze_image(request)

@router.get("/model-status")
async def model_status():
    """Проверка статуса модели"""
    return {
        "detector_loaded": detector.is_loaded,
        "detector_model_id": detector.model_id,
        "message": "Model is using Roboflow inference API" if detector.is_loaded else "Model is using stub implementation"
    }
