
from fastapi import APIRouter, HTTPException
from app.schemas import TreeAnalysisRequest, AnalysisResponse, TreeAnalysisResult, TreeCharacteristic
from app.utils import base64_to_image, image_to_base64, draw_detections
from app.models.detection_model import TreeDetector
from app.models.classification_model import TreeClassifier
from app.models.health_analysis import HealthAnalyzer
from PIL import Image
import numpy as np
import time
import base64

router = APIRouter()

# Инициализация моделей
detector = TreeDetector()
classifier = TreeClassifier()
health_analyzer = HealthAnalyzer()

@router.get("/")
async def analysis_root():
    return {"message": "Analysis router is working"}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(request: TreeAnalysisRequest):
    start_time = time.time()
    
    try:
        # Конвертация base64 в изображение
        pil_image = base64_to_image(request.image_data)
        
        # Конвертация PIL Image в numpy array
        image_array = np.array(pil_image)
        
        # Детекция деревьев и кустарников
        detections = detector.detect(image_array)
        
        results = []
        for i, detection in enumerate(detections):
            # Извлечение региона для анализа
            x1, y1, x2, y2 = map(int, detection["bbox"])
            # Обеспечиваем, чтобы координаты не выходили за границы
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image_array.shape[1], x2), min(image_array.shape[0], y2)
            
            if x2 > x1 and y2 > y1:
                roi = image_array[y1:y2, x1:x2]
                roi_pil = Image.fromarray(roi)
                
                # Классификация породы
                species = classifier.predict_species(roi_pil)
                
                # Анализ состояния
                health_data = health_analyzer.analyze_health(roi_pil, detection["class"])
                
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
                    characteristics=characteristics
                ))
        
        # Рисование bounding boxes на изображении
        processed_image = draw_detections(image_array, detections)
        processed_image_pil = Image.fromarray(processed_image)
        processed_image_base64 = image_to_base64(processed_image_pil)
        
        processing_time = time.time() - start_time
        
        return AnalysisResponse(
            results=results,
            processed_image=processed_image_base64,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

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
    # Создаем простое тестовое изображение программно
    from PIL import ImageDraw
    
    # Создаем тестовое изображение
    test_image = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(test_image)
    
    # Рисуем несколько "деревьев"
    draw.rectangle([100, 100, 200, 400], fill='brown', outline='black', width=2)
    draw.ellipse([50, 50, 250, 200], fill='green', outline='darkgreen', width=2)
    
    draw.rectangle([400, 150, 450, 350], fill='brown', outline='black', width=2)
    draw.ellipse([350, 100, 500, 250], fill='green', outline='darkgreen', width=2)
    
    # Конвертируем в base64
    buffered = base64.b64encode(test_image.tobytes())
    image_base64 = buffered.decode()
    
    # Создаем запрос
    request = TreeAnalysisRequest(image_data=image_base64)
    
    # Вызываем анализ
    return await analyze_image(request)
