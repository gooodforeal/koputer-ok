"""
Сервис для генерации PDF файлов со сборками
"""

import io
import aiohttp
import os
import platform
from typing import Optional, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from app.models.build import Build
from app.models.component import Component, ComponentCategory

# Русские названия категорий для отображения
CATEGORY_NAMES = {
    ComponentCategory.PROCESSORY: 'Процессор (CPU)',
    ComponentCategory.VIDEOKARTY: 'Видеокарта (GPU)',
    ComponentCategory.MATERINSKIE_PLATY: 'Материнская плата',
    ComponentCategory.OPERATIVNAYA_PAMYAT: 'Оперативная память (RAM)',
    ComponentCategory.ZHESTKIE_DISKI: 'Накопитель (HDD)',
    ComponentCategory.SSD_NAKOPITELI: 'Накопитель (SSD)',
    ComponentCategory.BLOKI_PITANIYA: 'Блок питания (PSU)',
    ComponentCategory.KORPUSA: 'Корпус',
    ComponentCategory.OHLAZHDENIE: 'Охлаждение',
}

# Название сайта (можно вынести в конфиг)
SITE_NAME = "Компьютер.ок"

# Путь к локальной папке со шрифтами
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fonts')

# Путь к логотипу
SITE_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app', 'assets', 'logo.png')

# Функция для регистрации шрифтов NetflixSans из папки fonts
def register_cyrillic_font():
    """Регистрирует шрифты NetflixSans из локальной папки fonts"""
    
    regular_font = None
    bold_font = None
    
    # Пути к шрифтам NetflixSans
    regular_font_path = os.path.join(FONTS_DIR, 'NetflixSans-Rg.ttf')
    bold_font_path = os.path.join(FONTS_DIR, 'NetflixSans-Bd.ttf')
    
    # Регистрируем обычный шрифт
    if os.path.exists(regular_font_path):
        try:
            pdfmetrics.registerFont(TTFont('NetflixSans', regular_font_path))
            regular_font = 'NetflixSans'
            print(f"✓ Зарегистрирован обычный шрифт: NetflixSans-Rg.ttf")
        except Exception as e:
            print(f"✗ Ошибка при регистрации шрифта NetflixSans-Rg.ttf: {e}")
    else:
        print(f"✗ ОШИБКА: Файл {regular_font_path} не найден!")
    
    # Регистрируем жирный шрифт
    if os.path.exists(bold_font_path):
        try:
            pdfmetrics.registerFont(TTFont('NetflixSansBold', bold_font_path))
            bold_font = 'NetflixSansBold'
            print(f"✓ Зарегистрирован жирный шрифт: NetflixSans-Bd.ttf")
        except Exception as e:
            print(f"✗ Ошибка при регистрации шрифта NetflixSans-Bd.ttf: {e}")
    else:
        print(f"✗ ОШИБКА: Файл {bold_font_path} не найден!")
    
    # Если не найдены оба шрифта, выбрасываем исключение
    if not regular_font or not bold_font:
        raise FileNotFoundError(
            f"Шрифты NetflixSans не найдены в папке {FONTS_DIR}. "
            f"Убедитесь, что файлы NetflixSans-Rg.ttf и NetflixSans-Bd.ttf существуют."
        )
    
    print(f"\n📝 Итог: regular={regular_font}, bold={bold_font}\n")
    return regular_font, bold_font


async def download_image(url: str, session: aiohttp.ClientSession) -> Optional[io.BytesIO]:
    """Загружает изображение по URL и возвращает BytesIO"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                image_data = await response.read()
                return io.BytesIO(image_data)
    except Exception as e:
        print(f"Ошибка при загрузке изображения {url}: {e}")
    return None


async def create_build_pdf(build: Build, output: io.BytesIO) -> None:
    """
    Создает PDF файл со сборкой
    
    Args:
        build: Модель сборки с загруженными компонентами
        output: BytesIO объект для записи PDF
    """
    # Регистрируем шрифты с поддержкой кириллицы
    regular_font, bold_font = register_cyrillic_font()
    
    # Создаем документ
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Стили
    styles = getSampleStyleSheet()
    
    # Настраиваем стили с кириллическими шрифтами и уменьшенным межбуквенным интервалом
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=14,
        alignment=TA_LEFT,
        fontName=bold_font,
        leading=30,
        wordWrap='CJK'  # Правильный перенос слов
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6,
        spaceBefore=10,
        fontName=bold_font,
        leading=16,
        wordWrap='CJK'
    )
    
    stats_header_style = ParagraphStyle(
        'StatsHeader',
        parent=heading_style,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1f2937'),
        alignment=TA_JUSTIFY,
        spaceAfter=5,
        fontName=regular_font,
        leading=12,
        wordWrap='CJK'
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=3,
        fontName=regular_font,
        leading=11,
        wordWrap='CJK'
    )
    
    # Стиль для таблиц
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1f2937'),
        fontName=regular_font,
        leading=11,
        wordWrap='CJK'
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        fontName=bold_font,
        leading=12,
        alignment=TA_CENTER,
        wordWrap='CJK'
    )
    
    # Список элементов для PDF
    story = []
    
    # Заголовок с логотипом (если есть) или название сайта - красивый дизайн
    logo_image = None
    if SITE_LOGO_PATH and os.path.exists(SITE_LOGO_PATH):
        try:
            pil_logo = PILImage.open(SITE_LOGO_PATH)
            # Конвертируем RGBA в RGB если нужно
            if pil_logo.mode == 'RGBA':
                rgb_logo = PILImage.new('RGB', pil_logo.size, (255, 255, 255))
                rgb_logo.paste(pil_logo, mask=pil_logo.split()[3])
                pil_logo = rgb_logo
            
            # Изменяем размер логотипа (максимальная высота 40mm)
            logo_max_height = 40*mm
            img_width, img_height = pil_logo.size
            
            # Вычисляем размеры для PDF (предполагаем 96 DPI: 1 пиксель ≈ 0.264583 мм)
            pixels_per_mm = 96 / 25.4
            img_height_mm = img_height / pixels_per_mm
            
            # Если логотип больше максимальной высоты, уменьшаем
            if img_height_mm > logo_max_height:
                ratio = logo_max_height / img_height_mm
                logo_height_mm = logo_max_height
                logo_width_mm = (img_width / pixels_per_mm) * ratio
                new_width_px = int(img_width * ratio)
                new_height_px = int(img_height * ratio)
                pil_logo = pil_logo.resize((new_width_px, new_height_px), PILImage.Resampling.LANCZOS)
            else:
                logo_height_mm = img_height_mm
                logo_width_mm = img_width / pixels_per_mm
            
            logo_buffer = io.BytesIO()
            pil_logo.save(logo_buffer, format='PNG')
            logo_buffer.seek(0)
            logo_image = Image(logo_buffer, width=logo_width_mm, height=logo_height_mm)
        except Exception as e:
            print(f"Ошибка при загрузке логотипа {SITE_LOGO_PATH}: {e}")
            logo_image = None
    
    # Формируем заголовок с логотипом и названием
    if logo_image:
        header_table_data = [[logo_image, Paragraph(SITE_NAME, title_style)]]
        header_table = Table(header_table_data, colWidths=[60*mm, A4[0] - 40*mm - 60*mm])
    else:
        header_table_data = [[Paragraph(SITE_NAME, title_style)]]
        header_table = Table(header_table_data, colWidths=[A4[0] - 40*mm])
    
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Выравнивание по левому краю
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),  # Отступ слева
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#3b82f6')),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8*mm))
    
    # Название сборки
    story.append(Paragraph(f"<b>{build.title}</b>", title_style))
    story.append(Spacer(1, 6*mm))
    
    # Информация об авторе и дате - красивый блок
    author_info = f"Автор: {build.author.name if build.author else 'Неизвестно'}"
    date_info = f"Дата создания: {build.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    table_width = A4[0] - 40*mm
    info_data = [
        [
            Paragraph("👤", ParagraphStyle('Icon', parent=info_style, fontSize=12)),
            Paragraph(author_info, info_style),
            Paragraph("📅", ParagraphStyle('Icon', parent=info_style, fontSize=12)),
            Paragraph(date_info, info_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[8*mm, (table_width - 16*mm) / 2, 8*mm, (table_width - 16*mm) / 2])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (3, 0), (3, 0), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 6*mm))
    
    # Описание сборки - в красивом блоке
    desc_data = [
        [Paragraph("<b>Описание</b>", heading_style)],
        [Paragraph(build.description, normal_style)]
    ]
    desc_table = Table(desc_data, colWidths=[A4[0] - 40*mm])
    desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f9ff')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 6*mm))
    
    # Дополнительная информация (если есть) - в красивом блоке
    if build.additional_info:
        add_info_data = [
            [Paragraph("<b>Дополнительная информация</b>", heading_style)],
            [Paragraph(build.additional_info, normal_style)]
        ]
        add_info_table = Table(add_info_data, colWidths=[A4[0] - 40*mm])
        add_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffbeb')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fcd34d')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(add_info_table)
        story.append(Spacer(1, 6*mm))
    
    # Компоненты сборки
    story.append(Paragraph("Комплектующие", heading_style))
    story.append(Spacer(1, 4*mm))
    
    if build.components:
        # Создаем сессию для загрузки изображений
        async with aiohttp.ClientSession() as session:
            # Группируем компоненты по категориям
            components_by_category = {}
            for component in build.components:
                category_name = CATEGORY_NAMES.get(component.category, component.category.value)
                if category_name not in components_by_category:
                    components_by_category[category_name] = []
                components_by_category[category_name].append(component)
            
            table_width = A4[0] - 40*mm
            image_size = 25*mm  # Уменьшенный размер изображений
            
            # Подготавливаем данные для таблицы
            table_data = []
            # Заголовок таблицы
            table_data.append([
                Paragraph("<b>Категория</b>", table_header_style),
                Paragraph("<b>Изображение</b>", table_header_style),
                Paragraph("<b>Название</b>", table_header_style),
                Paragraph("<b>Цена</b>", table_header_style)
            ])
            
            # Загружаем изображения для всех компонентов
            component_images = {}
            for category_name, components in sorted(components_by_category.items()):
                for component in components:
                    component_image = None
                    
                    if component.image:
                        image_bytes = await download_image(component.image, session)
                        if image_bytes:
                            try:
                                pil_image = PILImage.open(image_bytes)
                                img_width, img_height = pil_image.size
                                max_size_px = 120  # Уменьшено с 200
                                
                                if img_width > max_size_px or img_height > max_size_px:
                                    ratio = min(max_size_px / img_width, max_size_px / img_height)
                                    new_width = int(img_width * ratio)
                                    new_height = int(img_height * ratio)
                                    pil_image = pil_image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                                
                                img_buffer = io.BytesIO()
                                if pil_image.mode == 'RGBA':
                                    rgb_image = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                                    rgb_image.paste(pil_image, mask=pil_image.split()[3])
                                    pil_image = rgb_image
                                pil_image.save(img_buffer, format='PNG')
                                img_buffer.seek(0)
                                component_image = Image(img_buffer, width=image_size, height=image_size)
                            except Exception as e:
                                print(f"Ошибка при обработке изображения {component.image}: {e}")
                    
                    if component_image is None:
                        placeholder = PILImage.new('RGB', (120, 120), color=(245, 245, 245))
                        placeholder_bytes = io.BytesIO()
                        placeholder.save(placeholder_bytes, format='PNG')
                        placeholder_bytes.seek(0)
                        component_image = Image(placeholder_bytes, width=image_size, height=image_size)
                    
                    component_images[component.id] = component_image
            
            # Заполняем таблицу данными
            for category_name, components in sorted(components_by_category.items()):
                for idx, component in enumerate(components):
                    # Объединяем ячейку категории для всех компонентов одной категории
                    category_cell = Paragraph(category_name, table_text_style) if idx == 0 else ''
                    
                    component_name = Paragraph(component.name, table_text_style)
                    price_text = f"{component.price:,} ₽" if component.price else "Не указана"
                    price_cell = Paragraph(price_text, table_text_style)
                    
                    table_data.append([
                        category_cell,
                        component_images[component.id],
                        component_name,
                        price_cell
                    ])
            
            # Создаем таблицу
            category_col_width = 40*mm
            image_col_width = 30*mm
            name_col_width = table_width - category_col_width - image_col_width - 35*mm
            price_col_width = 35*mm
            
            components_table = Table(
                table_data,
                colWidths=[category_col_width, image_col_width, name_col_width, price_col_width],
                repeatRows=1  # Повторять заголовок на каждой странице
            )
            
            # Красивый стиль таблицы
            components_table.setStyle(TableStyle([
                # Заголовок
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Границы
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),
                
                # Чередование фона строк
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                
                # Выравнивание и отступы
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Категория
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Изображение
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Название
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Цена
                
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                
                # Минимальная высота строк
                ('MINIMUMHEIGHT', (0, 1), (-1, -1), 30*mm),
            ]))
            
            story.append(components_table)
            story.append(Spacer(1, 5*mm))
    
    # Итоговая стоимость - красивый блок
    if build.total_price > 0:
        story.append(Spacer(1, 6*mm))
        table_width = A4[0] - 40*mm
        
        total_text = Paragraph("<b>Итоговая стоимость сборки</b>", heading_style)
        total_price_text = Paragraph(f"<b>{build.total_price:,.0f} ₽</b>", ParagraphStyle(
            'TotalPrice',
            parent=heading_style,
            fontSize=20,
            textColor=colors.HexColor('#059669')
        ))
        
        total_data = [
            [total_text, total_price_text]
        ]
        total_table = Table(total_data, colWidths=[table_width * 0.6, table_width * 0.4])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#3b82f6')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#eff6ff')]),
        ]))
        story.append(total_table)
    
    # Статистика сборки - красивый блок
    story.append(Spacer(1, 6*mm))
    table_width = A4[0] - 40*mm
    
    stats_data = [
        [
            Paragraph("<b>Статистика</b>", stats_header_style),
            '', '', ''
        ],
        [
            Paragraph("Средний рейтинг", info_style),
            Paragraph(f"<b>{build.average_rating:.1f}</b>", table_text_style),
            Paragraph("Количество оценок", info_style),
            Paragraph(f"<b>{build.ratings_count}</b>", table_text_style)
        ],
        [
            Paragraph("Просмотров", info_style),
            Paragraph(f"<b>{build.views_count}</b>", table_text_style),
            '',
            ''
        ]
    ]
    
    stats_table = Table(stats_data, colWidths=[table_width / 4, table_width / 4, table_width / 4, table_width / 4])
    stats_table.setStyle(TableStyle([
        # Заголовок
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('SPAN', (0, 0), (-1, 0)),
        
        # Границы
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a8a')),
        
        # Чередование строк
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Выравнивание
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(stats_table)
    
    # Футер
    story.append(Spacer(1, 10*mm))
    footer = Paragraph(f"<i>Сгенерировано {build.created_at.strftime('%d.%m.%Y %H:%M')} | {SITE_NAME}</i>", info_style)
    story.append(footer)
    
    # Собираем PDF
    doc.build(story)

