"""
Загрузчик шаблонов для email писем
"""
import os
from pathlib import Path
from typing import Optional


class TemplateLoader:
    """Класс для загрузки и рендеринга шаблонов email"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Инициализация загрузчика шаблонов
        
        Args:
            templates_dir: Путь к директории с шаблонами. 
                          Если не указан, используется celery_workers/templates
        """
        if templates_dir is None:
            # Определяем путь к папке templates относительно текущего файла
            current_dir = Path(__file__).parent
            templates_dir = current_dir / "templates"
        
        self.templates_dir = Path(templates_dir)
    
    def load_template(self, template_name: str) -> str:
        """
        Загружает шаблон из файла
        
        Args:
            template_name: Имя файла шаблона (например, "login_email.html")
            
        Returns:
            str: Содержимое шаблона
            
        Raises:
            FileNotFoundError: Если шаблон не найден
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон {template_name} не найден в {self.templates_dir}")
        
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Загружает и рендерит шаблон с переданными переменными
        
        Args:
            template_name: Имя файла шаблона
            **kwargs: Переменные для подстановки в шаблон
            
        Returns:
            str: Отрендеренный шаблон
        """
        template_content = self.load_template(template_name)
        
        # Простая замена переменных в формате {{variable_name}}
        rendered = template_content
        for key, value in kwargs.items():
            # Заменяем все вхождения переменной
            placeholder = f"{{{{{key}}}}}"
            # Убеждаемся, что значение не None
            str_value = str(value) if value is not None else ""
            rendered = rendered.replace(placeholder, str_value)
        
        return rendered


# Глобальный экземпляр загрузчика шаблонов
template_loader = TemplateLoader()

