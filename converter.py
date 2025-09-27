import json
import base64

def image_to_json(image_path, output_file='data.json'):
    # Читаем изображение и кодируем в base64
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Создаем словарь с данными
    data = {
        "image_data": image_data
    }
    
    # Записываем в JSON файл
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Файл {output_file} успешно создан!")

# Использование
image_to_json('/home/demonpc/Projects/plant_disease_api/Санитарка/Zr5N0gUNybc.jpg')  # Укажите путь к вашему изображению
