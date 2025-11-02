"""
Утилиты для транслитерации русских символов в латиницу
"""
import re
from typing import Optional


def transliterate_ru_to_en(text: str) -> str:
    """
    Транслитерирует русские символы в латиницу
    
    Args:
        text: Текст для транслитерации
        
    Returns:
        Транслитерированный текст
    """
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    result = ''
    for char in text:
        if char in translit_map:
            result += translit_map[char]
        elif char.isalnum() or char in (' ', '_', '-', '.'):
            result += char
        else:
            result += '_'
    return result


def safe_filename(text: str, max_length: int = 80, prefix: Optional[str] = None) -> str:
    """
    Создает безопасное имя файла из текста с транслитерацией
    
    Args:
        text: Исходный текст для преобразования
        max_length: Максимальная длина имени файла (без расширения)
        prefix: Префикс для имени файла (например, "build_123_")
        
    Returns:
        Безопасное имя файла
    """
    # Транслитерируем текст
    safe_text = transliterate_ru_to_en(text)
    
    # Очищаем от недопустимых символов
    safe_text = re.sub(r'[^\w\-_\.]', '_', safe_text)
    safe_text = re.sub(r'_+', '_', safe_text).strip('_')
    
    # Если prefix передан, учитываем его длину при ограничении
    if prefix:
        # Вычисляем доступную длину для safe_text
        prefix_length = len(prefix)
        available_length = max(0, max_length - prefix_length)
        safe_text = safe_text[:available_length]
        filename = f"{prefix}{safe_text}" if safe_text else prefix.rstrip('_')
    else:
        # Ограничиваем длину без префикса
        safe_text = safe_text[:max_length]
        filename = safe_text if safe_text else 'file'
    
    return filename

